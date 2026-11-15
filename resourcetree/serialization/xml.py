"""XML representation for resourcetree model dictionaries.

The XML vocabulary preserves the JSON-compatible values used by the model:
dictionaries, lists, strings, integers, finite floats, booleans and null.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from typing import Any


_ROOT_TAG = "resourcetree"


def _write_value(parent: ET.Element, value: Any) -> None:
    if isinstance(value, dict):
        node = ET.SubElement(parent, "value", {"type": "dict"})
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("XML dictionary keys must be strings")
            entry = ET.SubElement(node, "entry", {"key": key})
            _write_value(entry, item)
    elif isinstance(value, list):
        node = ET.SubElement(parent, "value", {"type": "list"})
        for item in value:
            entry = ET.SubElement(node, "item")
            _write_value(entry, item)
    elif value is None:
        ET.SubElement(parent, "value", {"type": "null"})
    elif isinstance(value, bool):
        node = ET.SubElement(parent, "value", {"type": "bool"})
        node.text = "true" if value else "false"
    elif isinstance(value, int):
        node = ET.SubElement(parent, "value", {"type": "int"})
        node.text = str(value)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise TypeError("serialized floats must be finite")
        node = ET.SubElement(parent, "value", {"type": "float"})
        node.text = repr(value)
    elif isinstance(value, str):
        node = ET.SubElement(parent, "value", {"type": "str"})
        node.text = value
    else:
        raise TypeError(f"unsupported XML value type: {type(value).__name__}")


def _read_value(node: ET.Element) -> Any:
    kind = node.get("type")
    if kind == "dict":
        result: dict[str, Any] = {}
        for entry in node:
            if entry.tag != "entry" or "key" not in entry.attrib or len(entry) != 1:
                raise ValueError("invalid XML dictionary entry")
            key = entry.attrib["key"]
            if key in result:
                raise ValueError(f"duplicate XML dictionary key: {key!r}")
            result[key] = _read_value(entry[0])
        return result
    if kind == "list":
        result = []
        for item in node:
            if item.tag != "item" or len(item) != 1:
                raise ValueError("invalid XML list item")
            result.append(_read_value(item[0]))
        return result
    if len(node):
        raise ValueError("scalar XML values cannot contain child elements")
    text = node.text or ""
    if kind == "null":
        return None
    if kind == "str":
        return text
    if kind == "bool":
        if text not in {"true", "false"}:
            raise ValueError("invalid XML boolean")
        return text == "true"
    if kind == "int":
        return int(text)
    if kind == "float":
        value = float(text)
        if not math.isfinite(value):
            raise ValueError("serialized floats must be finite")
        return value
    raise ValueError(f"unknown XML value type: {kind!r}")


def dumps(data: dict[str, Any]) -> str:
    """Encode a model dictionary as XML."""
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    root = ET.Element(_ROOT_TAG)
    _write_value(root, data)
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def loads(value: str) -> dict[str, Any]:
    """Decode XML into a model dictionary."""
    root = ET.fromstring(value)
    if root.tag != _ROOT_TAG or len(root) != 1 or root[0].tag != "value":
        raise ValueError("invalid resourcetree XML document")
    data = _read_value(root[0])
    if not isinstance(data, dict):
        raise ValueError("serialized resource data must be an XML dictionary")
    return data
