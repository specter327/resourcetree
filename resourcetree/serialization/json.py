"""JSON representation for resourcetree model dictionaries."""

import json
import math
from typing import Any


def _validate_value(value: Any) -> None:
    """Validate JSON-compatible values iteratively and reject cyclic containers."""
    active: set[int] = set()
    stack: list[tuple[Any, bool]] = [(value, False)]
    while stack:
        current, exiting = stack.pop()
        if exiting:
            active.remove(id(current))
            continue
        if current is None or isinstance(current, (str, bool, int)):
            continue
        if isinstance(current, float):
            if not math.isfinite(current):
                raise TypeError("serialized floats must be finite")
            continue
        if isinstance(current, (list, dict)):
            identity = id(current)
            if identity in active:
                raise ValueError("cyclic values cannot be serialized")
            active.add(identity)
            stack.append((current, True))
            if isinstance(current, list):
                stack.extend((item, False) for item in reversed(current))
            else:
                for key, item in reversed(tuple(current.items())):
                    if not isinstance(key, str):
                        raise TypeError("dictionary keys must be strings")
                    stack.append((item, False))
            continue
        raise TypeError(f"unsupported serialized value type: {type(current).__name__}")


def _encode(data: Any, indent: int | None) -> str:
    output: list[str] = []
    active: set[int] = set()
    stack: list[tuple[str, Any, int]] = [("value", data, 0)]

    while stack:
        action, value, depth = stack.pop()
        if action == "raw":
            output.append(value)
            continue
        if action == "close":
            active.remove(id(value))
            if indent is not None:
                output.append("\n" + " " * (depth * indent))
            output.append("}" if isinstance(value, dict) else "]")
            continue

        if isinstance(value, dict):
            if not value:
                output.append("{}")
                continue
            identity = id(value)
            if identity in active:
                raise ValueError("cyclic values cannot be serialized")
            active.add(identity)
            output.append("{")
            stack.append(("close", value, depth))
            entries = list(value.items())
            for index in range(len(entries) - 1, -1, -1):
                key, item = entries[index]
                stack.append(("value", item, depth + 1))
                stack.append(("raw", ": " if indent is not None else ":", depth + 1))
                stack.append(("raw", json.dumps(key, ensure_ascii=False), depth + 1))
                prefix = ("\n" + " " * ((depth + 1) * indent)) if indent is not None else ""
                if index:
                    prefix = ("," if indent is None else "," + prefix)
                stack.append(("raw", prefix, depth + 1))
            if indent is not None:
                # The first entry's prefix also opens the pretty-printed line.
                pass
            continue

        if isinstance(value, list):
            if not value:
                output.append("[]")
                continue
            identity = id(value)
            if identity in active:
                raise ValueError("cyclic values cannot be serialized")
            active.add(identity)
            output.append("[")
            stack.append(("close", value, depth))
            for index in range(len(value) - 1, -1, -1):
                stack.append(("value", value[index], depth + 1))
                prefix = ("\n" + " " * ((depth + 1) * indent)) if indent is not None else ""
                if index:
                    prefix = ("," if indent is None else "," + prefix)
                stack.append(("raw", prefix, depth + 1))
            continue

        output.append(json.dumps(value, ensure_ascii=False, allow_nan=False))

    return "".join(output)


def dumps(data: dict[str, Any], *, indent: int | None = 2) -> str:
    """Encode a model dictionary as JSON without recursive traversal."""
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if indent is not None and (not isinstance(indent, int) or isinstance(indent, bool)):
        raise TypeError("indent must be an integer or None")
    if indent is not None and indent < 0:
        indent = 0
    _validate_value(data)
    return _encode(data, indent)


def _reject_constant(value: str):
    raise ValueError(f"invalid JSON numeric constant: {value}")


def loads(value: str) -> dict[str, Any]:
    """Decode JSON into a model dictionary."""
    data = json.loads(value, parse_constant=_reject_constant)
    if not isinstance(data, dict):
        raise ValueError("serialized resource data must be a JSON object")
    _validate_value(data)
    return data
