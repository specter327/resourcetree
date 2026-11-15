from __future__ import annotations

import re
from collections.abc import Iterator

from .resource import Resource


class Container(Resource):
    """A resource that owns direct parent/child relationships."""

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
