"""JSON and XML adapters for the model's dictionary representation."""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from typing import Any


def to_json(data: dict[str, Any], *, indent: int | None = 4) -> str:
    return json.dumps(data, ensure_ascii=False, indent=indent)


def from_json(value: str) -> dict[str, Any]:
    data = json.loads(value)
    if not isinstance(data, dict):
        raise ValueError("serialized resource data must be a JSON object")
    return data


def _append_xml(parent: ET.Element, value: Any) -> None:
    if value is None:
        parent.set("type", "null")
    elif isinstance(value, bool):
        parent.set("type", "bool")
        parent.text = "true" if value else "false"
    elif isinstance(value, int):
        parent.set("type", "int")
        parent.text = str(value)
    elif isinstance(value, float):
        parent.set("type", "float")
        parent.text = repr(value)
    elif isinstance(value, str):
        parent.set("type", "str")
        parent.text = value
    elif isinstance(value, list):
        parent.set("type", "list")
        for item in value:
            child = ET.SubElement(parent, "item")
            _append_xml(child, item)
    elif isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise TypeError("XML dictionary keys must be strings")
        parent.set("type", "dict")
        for key, item in value.items():
            child = ET.SubElement(parent, "item", key=key)
            _append_xml(child, item)
    else:
        raise TypeError(f"unsupported XML value type: {type(value).__name__}")


def _read_xml(element: ET.Element) -> Any:
    value_type = element.get("type")
    if value_type == "null":
        return None
    if value_type == "bool":
        return element.text == "true"
    if value_type == "int":
        return int(element.text or "0")
    if value_type == "float":
        return float(element.text or "0")
    if value_type == "str":
        return element.text or ""
    if value_type == "list":
        return [_read_xml(child) for child in element]
    if value_type == "dict":
        return {child.attrib["key"]: _read_xml(child) for child in element}
    raise ValueError(f"unsupported or missing XML value type: {value_type!r}")


def to_xml(data: dict[str, Any], *, root_tag: str = "resource") -> str:
    if not isinstance(root_tag, str) or not root_tag:
        raise ValueError("root_tag must be a non-empty string")
    root = ET.Element(root_tag)
    _append_xml(root, data)
    return ET.tostring(root, encoding="unicode", xml_declaration=False)


def from_xml(value: str) -> dict[str, Any]:
    root = ET.fromstring(value)
    data = _read_xml(root)
    if not isinstance(data, dict):
        raise ValueError("serialized resource data must have an XML dictionary root")
    return data
