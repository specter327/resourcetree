from __future__ import annotations

from typing import Any

from .resource import Resource


class Asset(Resource):
    """A generic terminal resource; its payload is domain-defined."""

    TYPE = "asset"

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

    def _to_dict_shallow(self) -> dict[str, Any]:
        result = super()._to_dict_shallow()
        result["data"] = self.data
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Asset:
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")
        if data.get("type") != cls.TYPE:
            raise ValueError(f"expected resource type {cls.TYPE!r}")
        from ..serialization.model import resource_from_dict

        resource = resource_from_dict(data, resource_types={cls.TYPE: cls})
        if not isinstance(resource, cls):
            raise TypeError(f"serialized resource did not reconstruct as {cls.__name__}")
        return resource
