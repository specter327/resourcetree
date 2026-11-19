from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from typing import Any

from uuid6 import uuid7

from .container import Container
from .resource import Resource


class ResourceTree:
    """Optional manager for a forest of resources.

    Container owns hierarchy. ResourceTree owns membership and a derived global
    index. Resources and containers remain usable without a ResourceTree.
    """

    TYPE = "resource_tree"

    def __init__(
        self,
        *,
        roots: Iterable[Resource] | None = None,
        name: str | None = None,
        uid: str | None = None,
    ) -> None:
        initial_roots = list(roots) if roots is not None else []
        if uid is not None and (not isinstance(uid, str) or not uid):
            raise ValueError("uid must be a non-empty string")
        if name is not None and (not isinstance(name, str) or not name):
            raise ValueError("name must be a non-empty string")

        self._uid = uid if uid is not None else str(uuid7())
        self.name = name if name is not None else (
            initial_roots[0].name if len(initial_roots) == 1 else "ResourceTree"
        )
        self._roots: list[Resource] = []
        self._resources: dict[str, Resource] = {}
        if initial_roots:
            self.add_roots(initial_roots)

    @property
    def uid(self) -> str:
        """Stable tree identifier; immutable after construction."""
        return self._uid

    @property
    def roots(self) -> tuple[Resource, ...]:
        return tuple(self._roots)

    @property
    def resources(self) -> dict[str, Resource]:
        """Return a copy of the global resource index."""
        return dict(self._resources)

    def to_dict(self) -> dict[str, Any]:
        """Return the tree identity and its roots; the index is rebuilt on load."""
        return {
            "type": self.TYPE,
            "uid": self.uid,
            "name": self.name,
            "roots": [root.to_dict() for root in self._roots],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResourceTree:
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")
        if data.get("type") != cls.TYPE:
            raise ValueError(f"expected resource type {cls.TYPE!r}")

        from ..serialization.model import resource_from_dict
        roots = [resource_from_dict(item) for item in data.get("roots", [])]
        return cls(name=data["name"], uid=data["uid"], roots=roots)

    def to_json(self, *, indent: int | None = 2) -> str:
        from ..serialization.json import dumps
        return dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, value: str) -> ResourceTree:
        from ..serialization.json import loads
        return cls.from_dict(loads(value))

    def to_xml(self) -> str:
        from ..serialization.xml import dumps
        return dumps(self.to_dict())

    @classmethod
    def from_xml(cls, value: str) -> ResourceTree:
        from ..serialization.xml import loads
        return cls.from_dict(loads(value))

    def _validate_node(self, resource: Resource) -> None:
        """Validate specialization-specific constraints for one collected node.

        Subclasses can narrow the accepted resource types without replacing the
        generic hierarchy traversal or duplicating its integrity checks.
        """

    def _collect(self, resource: Resource) -> list[Resource]:
        if not isinstance(resource, Resource):
            raise TypeError("resource must be a Resource instance")
        nodes: list[Resource] = []
        visited_objects: set[int] = set()
        visited_uids: set[str] = set()
        stack: list[tuple[Resource, Container | None]] = [(resource, resource.parent)]
        while stack:
            node, expected_parent = stack.pop()
            identity = id(node)
            if identity in visited_objects:
                raise ValueError("cycle or duplicate reference detected in resource hierarchy")
            visited_objects.add(identity)
            if not isinstance(node, Resource):
                raise TypeError("resource hierarchy can contain only Resource instances")
            self._validate_node(node)
            if node.parent is not expected_parent:
                raise ValueError("inconsistent parent/child relationship")
            if expected_parent is not None and sum(
                child is node for child in expected_parent._children
            ) != 1:
                raise ValueError("inconsistent parent/child relationship")
            if node.uid in visited_uids:
                raise ValueError(f"duplicate resource uid: {node.uid}")
            visited_uids.add(node.uid)
            if node._tree is not None and node._tree is not self:
                raise ValueError("resource already belongs to another ResourceTree")
            nodes.append(node)
            if isinstance(node, Container):
                child_ids: set[int] = set()
                for child in node._children:
                    if id(child) in child_ids:
                        raise ValueError("duplicate child reference")
                    child_ids.add(id(child))
                    if child.parent is not node:
                        raise ValueError("inconsistent parent/child relationship")
                stack.extend((child, node) for child in reversed(node._children))
        return nodes

    def _validate_new_nodes(self, nodes: list[Resource]) -> None:
        for node in nodes:
            existing = self._resources.get(node.uid)
            if existing is not None and existing is not node:
                raise ValueError(f"duplicate resource uid: {node.uid}")
            if existing is node:
                raise ValueError(f"resource already registered: {node.uid}")

    def add_root(self, resource: Resource) -> Resource:
        self.add_roots([resource])
        return resource

    def add_roots(self, resources: Iterable[Resource]) -> tuple[Resource, ...]:
        candidates = list(resources)
        if len({id(item) for item in candidates}) != len(candidates):
            raise ValueError("duplicate root reference")
        all_nodes: list[Resource] = []
        for resource in candidates:
            if not isinstance(resource, Resource):
                raise TypeError("root must be a Resource instance")
            if resource.parent is not None:
                raise ValueError("a root resource cannot have a parent")
            nodes = self._collect(resource)
            self._validate_new_nodes(nodes)
            all_nodes.extend(nodes)
        seen: dict[str, Resource] = {}
        for node in all_nodes:
            previous = seen.get(node.uid)
            if previous is not None and previous is not node:
                raise ValueError(f"duplicate resource uid: {node.uid}")
            seen[node.uid] = node
        for resource in candidates:
            self._roots.append(resource)
        for node in all_nodes:
            node._tree = self
            self._resources[node.uid] = node
        return tuple(candidates)

    def register(self, resource: Resource, parent: Container | None = None) -> str:
        if parent is None:
            self.add_root(resource)
        else:
            if not isinstance(parent, Container):
                raise TypeError("parent must be a Container")
            self._attach_child(parent, resource)
        return resource.uid

    def _attach_child(self, parent: Container, resource: Resource) -> None:
        if self._resources.get(parent.uid) is not parent:
            raise ValueError("parent must belong to this ResourceTree")
        if not isinstance(resource, Resource):
            raise TypeError("resource must be a Resource instance")
        if resource._tree is self and resource._parent is parent:
            return
        if resource._tree is not None and resource._tree is not self:
            raise ValueError("resource already belongs to another ResourceTree")
        if resource._tree is self:
            raise ValueError("moving registered resources requires an explicit move operation")
        parent._validate_attachment(resource)
        nodes = self._collect(resource)
        self._validate_new_nodes(nodes)
        parent._append_child_unchecked(resource)
        for node in nodes:
            node._tree = self
            self._resources[node.uid] = node

    def _detach_child(self, parent: Container, resource: Resource) -> bool:
        if self._resources.get(parent.uid) is not parent:
            raise ValueError("parent does not belong to this ResourceTree")
        if resource.parent is not parent or self._resources.get(resource.uid) is not resource:
            return False
        nodes = list(self._walk_subtree(resource))
        parent._remove_child_unchecked(resource)
        for node in nodes:
            self._resources.pop(node.uid, None)
            node._tree = None
        return True

    @staticmethod
    def _walk_subtree(resource: Resource) -> Iterator[Resource]:
        visited: set[int] = set()
        stack = [resource]
        while stack:
            node = stack.pop()
            if id(node) in visited:
                raise ValueError("cycle or duplicate reference detected")
            visited.add(id(node))
            yield node
            if isinstance(node, Container):
                stack.extend(reversed(node._children))

    def get(self, uid: str) -> Resource | None:
        return self._resources.get(uid)

    def contains(self, resource: Resource | str) -> bool:
        if isinstance(resource, str):
            return resource in self._resources
        return isinstance(resource, Resource) and self._resources.get(resource.uid) is resource

    def walk(self, *, order: str = "pre") -> Iterator[Resource]:
        """Iterate every resource in this forest in preorder or postorder."""
        from ..operations.walk import walk
        return walk(self, order=order)

    def search(self, pattern: str, *, flags: int = 0) -> list[Resource]:
        expression = re.compile(pattern, flags)
        return [resource for resource in self.walk() if expression.search(resource.name)]

    def remove_root(self, resource: Resource) -> bool:
        if not any(root is resource for root in self._roots) or self._resources.get(resource.uid) is not resource:
            return False
        nodes = list(self._walk_subtree(resource))
        self._roots.remove(resource)
        for node in nodes:
            self._resources.pop(node.uid, None)
            node._tree = None
        return True

    def remove(self, resource: Resource | str) -> bool:
        if isinstance(resource, str):
            target = self._resources.get(resource)
        else:
            target = self._resources.get(resource.uid) if isinstance(resource, Resource) else None
            if target is not resource:
                return False
        if target is None:
            return False
        if target in self._roots:
            return self.remove_root(target)
        parent = target.parent
        return self._detach_child(parent, target) if parent is not None else False

    def mount(self, entrypoint: Container, tree: ResourceTree) -> tuple[Resource, ...]:
        """Atomically transfer every source root beneath a destination container."""
        if tree is self:
            raise ValueError("a ResourceTree cannot be mounted into itself")
        if self._resources.get(entrypoint.uid) is not entrypoint:
            raise ValueError("entrypoint must belong to this ResourceTree")
        source_roots = list(tree._roots)
        if not source_roots:
            raise ValueError("the source ResourceTree is empty")

        collected: list[Resource] = []
        for root in source_roots:
            if root.parent is not None:
                raise ValueError("source root has a parent")
            nodes = tree._collect(root)
            for node in nodes:
                existing = self._resources.get(node.uid)
                if existing is not None and existing is not node:
                    raise ValueError(f"duplicate resource uid: {node.uid}")
            collected.extend(nodes)
        if len({node.uid for node in collected}) != len(collected):
            raise ValueError("duplicate resource uid across source roots")

        for root in source_roots:
            entrypoint._append_child_unchecked(root)
        for node in collected:
            tree._resources.pop(node.uid, None)
            node._tree = self
            self._resources[node.uid] = node
        tree._roots.clear()
        return tuple(source_roots)

    def __len__(self) -> int:
        return len(self._resources)

    def __repr__(self) -> str:
        return f"ResourceTree(uid={self.uid!r}, name={self.name!r}, roots={len(self._roots)}, resources={len(self)})"
