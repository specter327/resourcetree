from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from uuid6 import uuid7

if TYPE_CHECKING:
    from .container import Container
    from .tree import ResourceTree


class Resource:
    """Domain-neutral resource with identity and optional hierarchy membership."""

    def __init__(
        self,
        name: str,
        parent: Container | None = None,
        uid: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
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

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def path(self) -> str:
        if self.parent is None:
            return "/" + self.name
        return self.parent.path().rstrip("/") + "/" + self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Resource):
            return NotImplemented
        return self.uid == other.uid

    def __hash__(self) -> int:
        return hash(self.uid)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.path()} {self.uid}>"
