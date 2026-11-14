from __future__ import annotations

from typing import Any

from .resource import Resource


class Asset(Resource):
    """A generic terminal resource; its payload is domain-defined."""

    def __init__(
        self,
        name: str,
        parent=None,
        uid: str | None = None,
        data: Any = None,
        metadata: dict | None = None,
    ) -> None:
        super().__init__(name=name, parent=parent, uid=uid, metadata=metadata)
        self.data = data
