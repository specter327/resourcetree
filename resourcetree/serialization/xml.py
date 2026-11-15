"""XML representation for resourcetree model dictionaries.

The XML vocabulary preserves the JSON-compatible values used by the model:
dictionaries, lists, strings, integers, finite floats, booleans and null.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from typing import Any
from xml.sax.saxutils import escape, quoteattr


_ROOT_TAG = "resourcetree"


def _write_value(value: Any) -> str:
    """Encode nested values with an explicit stack instead of recursion."""
    output: list[str] = []
    active: set[int] = set()
    stack: list[tuple[str, Any]] = [("value", value)]

    while stack:
        action, current = stack.pop()
        if action == "raw":
            output.append(current)
            continue
        if action == "exit":
            active.remove(current)
            continue

        if isinstance(current, dict):
            identity = id(current)
            if identity in active:
                raise ValueError("cyclic values cannot be serialized")
            active.add(identity)
            output.append('<value type="dict">')
            stack.append(("raw", "</value>"))
            stack.append(("exit", identity))
            entries = list(current.items())
            for key, item in reversed(entries):
                if not isinstance(key, str):
                    raise TypeError("XML dictionary keys must be strings")
                stack.append(("raw", "</entry>"))
                stack.append(("value", item))
                stack.append(("raw", f"<entry key={quoteattr(key)}>"))
            continue

        if isinstance(current, list):
            identity = id(current)
            if identity in active:
                raise ValueError("cyclic values cannot be serialized")
            active.add(identity)
            output.append('<value type="list">')
            stack.append(("raw", "</value>"))
            stack.append(("exit", identity))
            for item in reversed(current):
                stack.append(("raw", "</item>"))
                stack.append(("value", item))
                stack.append(("raw", "<item>"))
            continue

        if current is None:
            output.append('<value type="null" />')
        elif isinstance(current, bool):
            output.append(f'<value type="bool">{"true" if current else "false"}</value>')
        elif isinstance(current, int):
            output.append(f'<value type="int">{current}</value>')
        elif isinstance(current, float):
            if not math.isfinite(current):
                raise TypeError("serialized floats must be finite")
            output.append(f'<value type="float">{repr(current)}</value>')
        elif isinstance(current, str):
            output.append(f'<value type="str">{escape(current)}</value>')
        else:
            raise TypeError(f"unsupported XML value type: {type(current).__name__}")

    return "".join(output)


def _read_value(node: ET.Element) -> Any:
    """Decode XML value nodes in post-order without recursive Python calls."""
    built: dict[int, Any] = {}
    stack: list[tuple[ET.Element, bool]] = [(node, False)]

    while stack:
        current, expanded = stack.pop()
        kind = current.get("type")

        if not expanded and kind in {"dict", "list"}:
            stack.append((current, True))
            for wrapper in reversed(list(current)):
                expected_tag = "entry" if kind == "dict" else "item"
                if wrapper.tag != expected_tag or len(wrapper) != 1:
                    message = "invalid XML dictionary entry" if kind == "dict" else "invalid XML list item"
                    raise ValueError(message)
                stack.append((wrapper[0], False))
            continue

        if kind == "dict":
            result: dict[str, Any] = {}
            for entry in current:
                if entry.tag != "entry" or "key" not in entry.attrib or len(entry) != 1:
                    raise ValueError("invalid XML dictionary entry")
                key = entry.attrib["key"]
                if key in result:
                    raise ValueError(f"duplicate XML dictionary key: {key!r}")
                result[key] = built[id(entry[0])]
            built[id(current)] = result
            continue

        if kind == "list":
            result = []
            for item in current:
                if item.tag != "item" or len(item) != 1:
                    raise ValueError("invalid XML list item")
                result.append(built[id(item[0])])
            built[id(current)] = result
            continue

        if len(current):
            raise ValueError("scalar XML values cannot contain child elements")
        text = current.text or ""
        if kind == "null":
            result = None
        elif kind == "str":
            result = text
        elif kind == "bool":
            if text not in {"true", "false"}:
                raise ValueError("invalid XML boolean")
            result = text == "true"
        elif kind == "int":
            result = int(text)
        elif kind == "float":
            result = float(text)
            if not math.isfinite(result):
                raise ValueError("serialized floats must be finite")
        else:
            raise ValueError(f"unknown XML value type: {kind!r}")
        built[id(current)] = result

    return built[id(node)]


def dumps(data: dict[str, Any]) -> str:
    """Encode a model dictionary as XML without recursive traversal."""
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    body = _write_value(data)
    return "<?xml version='1.0' encoding='utf-8'?>\n<resourcetree>" + body + "</resourcetree>"


def loads(value: str) -> dict[str, Any]:
    """Decode XML into a model dictionary."""
    root = ET.fromstring(value)
    if root.tag != _ROOT_TAG or len(root) != 1 or root[0].tag != "value":
        raise ValueError("invalid resourcetree XML document")
    data = _read_value(root[0])
    if not isinstance(data, dict):
        raise ValueError("serialized resource data must be an XML dictionary")
    return data
