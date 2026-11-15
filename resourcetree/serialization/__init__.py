"""Serialization helpers for the resourcetree model."""

from .json import dumps as json_dumps
from .json import loads as json_loads
from .model import object_from_dict, resource_from_dict
from .xml import dumps as xml_dumps
from .xml import loads as xml_loads

__all__ = [
    "json_dumps",
    "json_loads",
    "xml_dumps",
    "xml_loads",
    "object_from_dict",
    "resource_from_dict",
]
