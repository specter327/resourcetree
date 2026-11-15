"""Shared serialization methods; independent of the resource hierarchy."""
from __future__ import annotations

from typing import Any, Self


class Serializable:
    def to_json(self, *, indent: int | None = 4) -> str:
        from .formats import to_json
        return to_json(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, value: str) -> Self:
        from .formats import from_json
        return cls.from_dict(from_json(value))

    def to_xml(self, *, root_tag: str = "resource") -> str:
        from .formats import to_xml
        return to_xml(self.to_dict(), root_tag=root_tag)

    @classmethod
    def from_xml(cls, value: str) -> Self:
        from .formats import from_xml
        return cls.from_dict(from_xml(value))

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        raise NotImplementedError
