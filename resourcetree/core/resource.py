from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from uuid6 import uuid7

if TYPE_CHECKING:
    from .container import Container
    from .tree import ResourceTree


class Resource:
    """Domain-neutral resource with identity and optional hierarchy membership."""

    TYPE = "resource"

    def __init__(self, name: str, parent: Container | None = None, uid: str | None = None,
                 metadata: dict[str, Any] | None = None) -> None:
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string")
        if uid is not None and (not isinstance(uid, str) or not uid):
            raise ValueError("uid must be a non-empty string")
        self._uid = uid if uid is not None else str(uuid7())
        self.name = name
        self._parent: Container | None = None
        self._tree: ResourceTree | None = None
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at
        self.metadata: dict[str, Any] = dict(metadata) if metadata is not None else {}
        if parent is not None:
            parent.append_child(self)

    @property
    def uid(self) -> str:
        """Stable resource identifier; immutable after construction."""
        return self._uid

    @property
    def parent(self) -> Container | None:
        """Parent container, or None when this resource is a root."""
        return self._parent

    @property
    def tree(self) -> ResourceTree | None:
        """ResourceTree membership, if this resource is managed by one."""
        return self._tree

    def walk(self, *, order: str = "pre"):
        """Iterate this resource and its descendants in preorder or postorder."""
        from ..operations.walk import walk
        return walk(self, order=order)

    def ancestors(self, *, include_self: bool = False, order: str = "up"):
        """Iterate parent resources toward the root, or root-to-parent."""
        from ..operations.walk import ancestors
        return ancestors(self, include_self=include_self, order=order)

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def path(self) -> str:
        """Return the logical hierarchy path without recursive parent calls."""
        from .container import Container
        segments: list[str] = []
        visited: set[int] = set()
        current: Resource | None = self
        while current is not None:
            identity = id(current)
            if identity in visited:
                raise ValueError("cycle detected in resource parent relationships")
            visited.add(identity)
            segments.append(current.name)
            parent = current.parent
            if parent is not None:
                if not isinstance(parent, Container):
                    raise TypeError("resource parent must be a Container")
                if sum(child is current for child in parent._children) != 1:
                    raise ValueError("inconsistent parent/child relationship")
            current = parent
        return "/" + "/".join(reversed(segments))

    def _to_dict_shallow(self) -> dict[str, Any]:
        """Return this resource's own fields, excluding descendant resources."""
        return {"type": self.TYPE, "uid": self.uid, "name": self.name,
                "created_at": self.created_at.isoformat(), "updated_at": self.updated_at.isoformat(),
                "metadata": self.metadata.copy()}

    def to_dict(self) -> dict[str, Any]:
        return self._to_dict_shallow()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Resource:
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")
        if data.get("type") != cls.TYPE:
            raise ValueError(f"expected resource type {cls.TYPE!r}")
        from ..serialization.model import resource_from_dict
        resource = resource_from_dict(data, resource_types={cls.TYPE: cls})
        if not isinstance(resource, cls):
            raise TypeError(f"serialized resource did not reconstruct as {cls.__name__}")
        return resource

    def to_json(self, *, indent: int | None = 2) -> str:
        from ..serialization.json import dumps
        return dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, value: str) -> Resource:
        from ..serialization.json import loads
        return cls.from_dict(loads(value))

    def to_xml(self) -> str:
        from ..serialization.xml import dumps
        return dumps(self.to_dict())

    @classmethod
    def from_xml(cls, value: str) -> Resource:
        from ..serialization.xml import loads
        return cls.from_dict(loads(value))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Resource):
            return NotImplemented
        return self.uid == other.uid

    def __hash__(self) -> int:
        return hash(self.uid)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.path()} {self.uid}>"
