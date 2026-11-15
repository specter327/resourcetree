from __future__ import annotations

from typing import Any, Self

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

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["type"] = "Asset"
        data["data"] = self.data
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        if not isinstance(data, dict) or data.get("type") != "Asset":
            raise ValueError("dictionary does not describe an Asset")
        asset = cls(
            name=data["name"],
            uid=data["uid"],
            data=data.get("data"),
            metadata=data.get("metadata"),
        )
        from datetime import datetime
        asset.created_at = datetime.fromisoformat(data["created_at"])
        asset.updated_at = datetime.fromisoformat(data["updated_at"])
        return asset
