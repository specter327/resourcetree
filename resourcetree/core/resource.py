from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from uuid6 import uuid7

if TYPE_CHECKING:
    from .container import Container


class Resource:
    """Dominio-neutral node in a resource hierarchy.

    A Resource owns identity and descriptive metadata only. It does not
    perform I/O or assume that it represents a filesystem object.
    """

    def __init__(
        self,
        name: str,
        parent: Container | None = None,
        uid: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string")

        self.uid = uid or str(uuid7())
        self.name = name
        self.parent: Container | None = None
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at
        self.metadata: dict[str, Any] = dict(metadata or {})

        if parent is not None:
            parent.append_child(self)

    def touch(self) -> None:
        """Update the resource's in-memory modification timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def path(self) -> str:
        """Return the logical hierarchy path (not a physical system path)."""
        if self.parent is None:
            return "/" + self.name
        return self.parent.path().rstrip("/") + "/" + self.name

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.path()} {self.uid}>"
