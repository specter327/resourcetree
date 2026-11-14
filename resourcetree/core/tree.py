from __future__ import annotations

from typing import Iterator

from uuid6 import uuid7

from .container import Container
from .resource import Resource


class ResourceTree:
    """A logical tree of generic resources.

    ResourceTree manages a root and an index of all reachable resources.
    It has no knowledge of filesystems, paths on disk, networks or I/O.
    """

    def __init__(
        self,
        root: Container | str | None = None,
        *,
        name: str | None = None,
        uid: str | None = None,
    ) -> None:
        if isinstance(root, str):
            root = Container(root)
        if root is not None and not isinstance(root, Container):
            raise TypeError("root must be a Container, a name, or None")

        self.uid = uid or str(uuid7())
        self.root: Container | None = root
        self.name = name or (root.name if root is not None else "ResourceTree")
        self.resources: dict[str, Resource] = {}
        if root is not None:
            self._index_subtree(root)

    def _index_subtree(self, resource: Resource) -> None:
        if resource.uid in self.resources and self.resources[resource.uid] is not resource:
            raise ValueError(f"duplicate resource uid: {resource.uid}")
        self.resources[resource.uid] = resource
        if isinstance(resource, Container):
            for child in resource.children:
                if child.parent is not resource:
                    raise ValueError("inconsistent parent/child relationship")
                self._index_subtree(child)

    def register(self, resource: Resource, parent: Container | None = None) -> str:
        if not isinstance(resource, Resource):
            raise TypeError("resource must be a Resource instance")
        if resource.uid in self.resources:
            raise ValueError(f"resource already registered: {resource.uid}")

        if self.root is None:
            if parent is not None:
                raise ValueError("a root resource cannot have a parent")
            if not isinstance(resource, Container):
                raise TypeError("the root resource must be a Container")
            if resource.parent is not None:
                raise ValueError("the root resource cannot already have a parent")
            self.root = resource
            self.name = self.name if self.name != "ResourceTree" else resource.name
        else:
            if parent is None:
                raise ValueError("parent is required when the tree already has a root")
            if self.resources.get(parent.uid) is not parent:
                raise ValueError("parent must belong to this ResourceTree")
            parent.append_child(resource)

        self._index_subtree(resource)
        return resource.uid

    def get(self, uid: str) -> Resource | None:
        return self.resources.get(uid)

    def contains(self, resource: Resource | str) -> bool:
        uid = resource if isinstance(resource, str) else resource.uid
        return uid in self.resources

    def walk(self) -> Iterator[Resource]:
        if self.root is not None:
            yield from self._walk(self.root)

    @staticmethod
    def _walk(resource: Resource) -> Iterator[Resource]:
        yield resource
        if isinstance(resource, Container):
            for child in resource.children:
                yield from ResourceTree._walk(child)

    def search(self, pattern: str, *, flags: int = 0) -> list[Resource]:
        """Return resources whose names match a regular expression."""
        import re

        expression = re.compile(pattern, flags)
        return [resource for resource in self.walk() if expression.search(resource.name)]

    def remove(self, resource: Resource | str) -> bool:
        uid = resource if isinstance(resource, str) else resource.uid
        target = self.resources.get(uid)
        if target is None:
            return False
        if target is self.root:
            self.root = None
            self.resources.clear()
            return True

        parent = target.parent
        if parent is not None:
            parent.remove_child(target)
        for node in self._walk(target):
            self.resources.pop(node.uid, None)
        return True

    def mount(self, entrypoint: Container, tree: ResourceTree) -> Container:
        """Attach another tree's root below a container in this tree.

        Mounting transfers the root subtree; the source tree becomes empty.
        """
        if tree is self:
            raise ValueError("a ResourceTree cannot be mounted into itself")
        if self.resources.get(entrypoint.uid) is not entrypoint:
            raise ValueError("entrypoint must belong to this ResourceTree")
        if tree.root is None:
            raise ValueError("the source ResourceTree has no root")
        mounted_root = tree.root
        entrypoint.append_child(mounted_root)
        self._index_subtree(mounted_root)
        tree.root = None
        tree.resources.clear()
        return mounted_root

    def __len__(self) -> int:
        return len(self.resources)

    def __repr__(self) -> str:
        return f"ResourceTree(uid={self.uid!r}, name={self.name!r}, resources={len(self)})"
