"""Reconstruction helpers for the built-in resource model."""

from typing import Any


def resource_from_dict(data: dict[str, Any]):
    """Reconstruct one built-in resource based on its explicit type field."""
    if not isinstance(data, dict):
        raise TypeError("resource data must be a dictionary")

    resource_type = data.get("type")
    if resource_type == "resource":
        from ..core.resource import Resource
        return Resource.from_dict(data)
    if resource_type == "asset":
        from ..core.asset import Asset
        return Asset.from_dict(data)
    if resource_type == "container":
        from ..core.container import Container
        return Container.from_dict(data)
    raise ValueError(f"unknown resource type: {resource_type!r}")


def object_from_dict(data: dict[str, Any]):
    """Reconstruct a built-in model object from its dictionary representation."""
    if not isinstance(data, dict):
        raise TypeError("model data must be a dictionary")
    if data.get("type") == "resource_tree":
        from ..core.tree import ResourceTree
        return ResourceTree.from_dict(data)
    return resource_from_dict(data)
