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


def _decode_iterative(value: str) -> Any:
    """Parse JSON containers with an explicit stack; scalar decoding stays stdlib."""
    if not isinstance(value, str):
        raise TypeError("JSON input must be a string")

    decoder = json.JSONDecoder(parse_constant=_reject_constant)
    length = len(value)
    index = 0

    def skip_whitespace(position: int) -> int:
        while position < length and value[position] in " \t\r\n":
            position += 1
        return position

    def parse_value(position: int):
        position = skip_whitespace(position)
        if position >= length:
            raise ValueError("unexpected end of JSON input")
        token = value[position]
        if token == "{":
            return {}, position + 1, "object"
        if token == "[":
            return [], position + 1, "array"
        parsed, end = decoder.raw_decode(value, position)
        return parsed, end, None

    root, index, root_kind = parse_value(index)
    stack: list[dict[str, Any]] = []
    if root_kind is not None:
        stack.append({"kind": root_kind, "value": root, "state": "initial"})

    while stack:
        frame = stack[-1]
        kind = frame["kind"]
        container = frame["value"]
        index = skip_whitespace(index)

        if kind == "object":
            state = frame["state"]
            if state in {"initial", "key_required"}:
                if index < length and value[index] == "}":
                    if state == "key_required":
                        raise ValueError("trailing comma in JSON object")
                    index += 1
                    stack.pop()
                    continue
                if index >= length or value[index] != '"':
                    raise ValueError(f"expected JSON object key at position {index}")
                key, index = decoder.raw_decode(value, index)
                if not isinstance(key, str):
                    raise ValueError("JSON object keys must be strings")
                frame["key"] = key
                frame["state"] = "colon"
                continue
            if state == "colon":
                if index >= length or value[index] != ":":
                    raise ValueError(f"expected ':' at position {index}")
                index += 1
                frame["state"] = "value"
                continue
            if state == "value":
                parsed, index, child_kind = parse_value(index)
                container[frame["key"]] = parsed
                frame.pop("key")
                frame["state"] = "comma_or_end"
                if child_kind is not None:
                    stack.append({"kind": child_kind, "value": parsed, "state": "initial"})
                continue
            if state == "comma_or_end":
                if index < length and value[index] == ",":
                    index += 1
                    frame["state"] = "key_required"
                    continue
                if index < length and value[index] == "}":
                    index += 1
                    stack.pop()
                    continue
                raise ValueError(f"expected ',' or '}}' at position {index}")

        else:
            state = frame["state"]
            if state in {"initial", "value_required"}:
                if index < length and value[index] == "]":
                    if state == "value_required":
                        raise ValueError("trailing comma in JSON array")
                    index += 1
                    stack.pop()
                    continue
                parsed, index, child_kind = parse_value(index)
                container.append(parsed)
                frame["state"] = "comma_or_end"
                if child_kind is not None:
                    stack.append({"kind": child_kind, "value": parsed, "state": "initial"})
                continue
            if state == "comma_or_end":
                if index < length and value[index] == ",":
                    index += 1
                    frame["state"] = "value_required"
                    continue
                if index < length and value[index] == "]":
                    index += 1
                    stack.pop()
                    continue
                raise ValueError(f"expected ',' or ']' at position {index}")

    index = skip_whitespace(index)
    if index != length:
        raise ValueError(f"extra data after JSON value at position {index}")
    return root


def loads(value: str) -> dict[str, Any]:
    """Decode JSON into a model dictionary without recursive container parsing."""
    data = _decode_iterative(value)
    if not isinstance(data, dict):
        raise ValueError("serialized resource data must be a JSON object")
    _validate_value(data)
    return data
