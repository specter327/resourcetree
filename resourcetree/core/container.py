from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from .resource import Resource


class Container(Resource):
    """A resource that owns direct parent/child relationships."""

    TYPE = "container"

    def __init__(
        self,
        name: str,
        parent: Container | None = None,
        uid: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        self._children: list[Resource] = []
        super().__init__(name=name, parent=parent, uid=uid, metadata=metadata)

    @property
    def children(self) -> tuple[Resource, ...]:
        """Read-only snapshot of direct children."""
        return tuple(self._children)

    def to_dict(self) -> dict[str, Any]:
        """Serialize this subtree without recursive Python calls."""
        root_data = self._to_dict_shallow()
        visited: set[int] = set()
        stack: list[tuple[Container, dict[str, Any]]] = [(self, root_data)]

        while stack:
            container, container_data = stack.pop()
            identity = id(container)
            if identity in visited:
                raise ValueError("cycle or duplicate reference detected in resource hierarchy")
            visited.add(identity)

            children_data: list[dict[str, Any]] = []
            container_data["children"] = children_data
            for child in container._children:
                if not isinstance(child, Resource):
                    raise TypeError("container children must be Resource instances")
                if id(child) in visited:
                    raise ValueError("cycle or duplicate reference detected in resource hierarchy")
                child_data = child._to_dict_shallow()
                children_data.append(child_data)
                if isinstance(child, Container):
                    stack.append((child, child_data))
            # Descendants are processed after all siblings have been attached.

        return root_data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Container:
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")
        if data.get("type") != cls.TYPE:
            raise ValueError(f"expected resource type {cls.TYPE!r}")

        container = cls(
            name=data["name"],
            uid=data["uid"],
            metadata=data.get("metadata"),
        )
        from datetime import datetime
        created_at = datetime.fromisoformat(data["created_at"])
        updated_at = datetime.fromisoformat(data["updated_at"])

        from ..serialization.model import resource_from_dict
        for child_data in data.get("children", []):
            container.append_child(resource_from_dict(child_data))

        # Rebuilding child links touches the container; restore its serialized state last.
        container.created_at = created_at
        container.updated_at = updated_at
        return container

    def _append_child_unchecked(self, resource: Resource) -> None:
        if resource._parent is not None:
            previous_parent = resource._parent
            for index, child in enumerate(previous_parent._children):
                if child is resource:
                    del previous_parent._children[index]
                    break
            previous_parent.touch()
        self._children.append(resource)
        resource._parent = self
        self.touch()

    def _remove_child_unchecked(self, resource: Resource) -> bool:
        for index, child in enumerate(self._children):
            if child is resource:
                del self._children[index]
                resource._parent = None
                self.touch()
                return True
        return False

    def append_child(self, resource: Resource) -> Resource:
        if not isinstance(resource, Resource):
            raise TypeError("resource must be a Resource instance")
        if self._tree is not None:
            self._tree._attach_child(self, resource)
            return resource
        if resource._tree is not None:
            raise ValueError("a resource managed by ResourceTree cannot be moved outside it")
        self._validate_attachment(resource)
        if resource._parent is self:
            return resource
        self._append_child_unchecked(resource)
        return resource

    def _validate_attachment(self, resource: Resource) -> None:
        if resource is self:
            raise ValueError("a container cannot contain itself")
        current: Resource | None = self
        while current is not None:
            if current is resource:
                raise ValueError("adding this resource would create a cycle")
            current = current.parent
        if resource._tree is not None:
            raise ValueError("resource already belongs to a ResourceTree")

    def remove_child(self, resource: Resource) -> bool:
        if self._tree is not None:
            return self._tree._detach_child(self, resource)
        if resource._tree is not None:
            raise ValueError("managed resources must be removed through their ResourceTree")
        return self._remove_child_unchecked(resource)

    def find(self, name: str) -> Resource | None:
        return next((child for child in self._children if child.name == name), None)

    def walk(self) -> Iterator[Resource]:
        """Depth-first traversal of this container and its descendants."""
        visited: set[int] = set()
        stack: list[Resource] = [self]
        while stack:
            resource = stack.pop()
            identity = id(resource)
            if identity in visited:
                raise ValueError("cycle or duplicate reference detected in resource hierarchy")
            visited.add(identity)
            yield resource
            if isinstance(resource, Container):
                stack.extend(reversed(resource._children))

    def search(self, pattern: str, *, flags: int = 0) -> list[Resource]:
        expression = re.compile(pattern, flags)
        return [resource for resource in self.walk() if expression.search(resource.name)]
