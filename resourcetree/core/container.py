from __future__ import annotations

import re
from collections.abc import Iterator

from .resource import Resource


class Container(Resource):
    """A generic resource that can contain other resources."""

    def __init__(
        self,
        name: str,
        parent: Container | None = None,
        uid: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        self.children: list[Resource] = []
        super().__init__(name=name, parent=parent, uid=uid, metadata=metadata)

    def append_child(self, resource: Resource) -> Resource:
        if not isinstance(resource, Resource):
            raise TypeError("resource must be a Resource instance")
        if resource is self:
            raise ValueError("a container cannot contain itself")

        current: Container | None = self
        while current is not None:
            if current is resource:
                raise ValueError("adding this resource would create a cycle")
            current = current.parent

        if resource.parent is self and resource in self.children:
            return resource
        if resource.parent is not None:
            resource.parent.remove_child(resource)

        self.children.append(resource)
        resource.parent = self
        self.touch()
        return resource

    def remove_child(self, resource: Resource) -> bool:
        if resource not in self.children:
            return False
        self.children.remove(resource)
        resource.parent = None
        self.touch()
        return True

    def find(self, name: str) -> Resource | None:
        """Find a direct child by its name."""
        return next((child for child in self.children if child.name == name), None)

    def walk(self) -> Iterator[Resource]:
        """Yield this container and all descendants in depth-first order."""
        yield self
        for child in self.children:
            if isinstance(child, Container):
                yield from child.walk()
            else:
                yield child

    def search(self, pattern: str, *, flags: int = 0) -> list[Resource]:
        """Search this subtree using a regular expression over resource names."""
        expression = re.compile(pattern, flags)
        return [resource for resource in self.walk() if expression.search(resource.name)]
