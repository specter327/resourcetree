"""JSON representation for resourcetree model dictionaries."""

import json
import math
from typing import Any


def _validate_value(value: Any) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise TypeError("serialized floats must be finite")
        return
    if isinstance(value, list):
        for item in value:
            _validate_value(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("dictionary keys must be strings")
            _validate_value(item)
        return
    raise TypeError(f"unsupported serialized value type: {type(value).__name__}")


def dumps(data: dict[str, Any], *, indent: int | None = 2) -> str:
    """Encode a model dictionary as JSON."""
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    _validate_value(data)
    return json.dumps(data, ensure_ascii=False, indent=indent, allow_nan=False)


def _reject_constant(value: str):
    raise ValueError(f"invalid JSON numeric constant: {value}")


def loads(value: str) -> dict[str, Any]:
    """Decode JSON into a model dictionary."""
    data = json.loads(value, parse_constant=_reject_constant)
    if not isinstance(data, dict):
        raise ValueError("serialized resource data must be a JSON object")
    _validate_value(data)
    return data
