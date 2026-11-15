"""JSON representation for resourcetree model dictionaries."""

import json
from typing import Any


def dumps(data: dict[str, Any], *, indent: int | None = 2) -> str:
    """Encode a model dictionary as JSON."""
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    return json.dumps(data, ensure_ascii=False, indent=indent)


def loads(value: str) -> dict[str, Any]:
    """Decode JSON into a model dictionary."""
    data = json.loads(value)
    if not isinstance(data, dict):
        raise ValueError("serialized resource data must be a JSON object")
    return data
