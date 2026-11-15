"""Reconstruction helpers for the built-in resource model.

The materializer is iterative so hierarchy depth is not coupled to Python's
recursion limit. Specializations own reconstruction of their domain types.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _build_resource(data: dict[str, Any], resource_types: dict[str, type] | None = None):
    if not isinstance(data, dict):
        raise TypeError("resource data must be a dictionary")

    resource_type = data.get("type")
    if resource_types and resource_type in resource_types:
        resource_class = resource_types[resource_type]
    else:
        from ..core.asset import Asset
        from ..core.container import Container
        from ..core.resource import Resource

        resource_class = {
            Resource.TYPE: Resource,
            Asset.TYPE: Asset,
            Container.TYPE: Container,
        }.get(resource_type)

    if resource_class is None:
        raise ValueError(f"unknown resource type: {resource_type!r}")

    uid = data.get("uid")
    name = data.get("name")
    metadata = data.get("metadata", {})
    if not isinstance(uid, str) or not uid:
        raise ValueError("resource uid must be a non-empty string")
    if not isinstance(name, str) or not name:
        raise ValueError("resource name must be a non-empty string")
    if not isinstance(metadata, dict):
        raise TypeError("resource metadata must be a dictionary")

    created_value = data.get("created_at")
    updated_value = data.get("updated_at")
    if not isinstance(created_value, str) or not isinstance(updated_value, str):
        raise TypeError("resource timestamps must be ISO-8601 strings")
    try:
        created_at = datetime.fromisoformat(created_value)
        updated_at = datetime.fromisoformat(updated_value)
    except ValueError as error:
        raise ValueError("resource timestamps must be valid ISO-8601 values") from error

    from ..core.asset import Asset
    from ..core.container import Container
    from ..core.resource import Resource

    if issubclass(resource_class, Container):
        children = data.get("children")
        if not isinstance(children, list):
            raise TypeError("container children must be a list")
        resource = resource_class(name=name, uid=uid, metadata=metadata)
    elif issubclass(resource_class, Asset):
        if "children" in data:
            raise ValueError("assets cannot contain child resources")
        resource = resource_class(
            name=name, uid=uid, data=data.get("data"), metadata=metadata
        )
        children = None
    elif issubclass(resource_class, Resource):
        if "children" in data:
            raise ValueError("resources cannot contain child resources")
        resource = resource_class(name=name, uid=uid, metadata=metadata)
        children = None
    else:
        raise TypeError("resource reconstruction classes must inherit Resource")

    return resource, children, created_at, updated_at


def resource_from_dict(
    data: dict[str, Any],
    *,
    resource_types: dict[str, type] | None = None,
):
    """Reconstruct a built-in resource hierarchy without recursive calls.

    resource_types lets a specialization select its own root class without
    making the generic core import that specialization. Specialized descendants
    must be reconstructed by the specialization's own materializer.
    """
    root, root_children, root_created, root_updated = _build_resource(
        data, resource_types
    )
    seen_objects = {id(data)}
    seen_uids = {root.uid}
    timestamps = [(root, root_created, root_updated)]
    stack = [(root, root_children)] if root_children is not None else []

    while stack:
        parent, children = stack.pop()
        for child_data in reversed(children):
            if not isinstance(child_data, dict):
                raise TypeError("resource children must be dictionaries")
            identity = id(child_data)
            if identity in seen_objects:
                raise ValueError("cycle or repeated resource payload detected")
            seen_objects.add(identity)

            child, grandchildren, created_at, updated_at = _build_resource(
                child_data
            )
            if child.uid in seen_uids:
                raise ValueError(f"duplicate resource uid: {child.uid}")
            seen_uids.add(child.uid)
            parent._append_child_unchecked(child)
            timestamps.append((child, created_at, updated_at))
            if grandchildren is not None:
                stack.append((child, grandchildren))

    # Attachment touches ancestors; restore every serialized timestamp only
    # after the complete hierarchy has been linked.
    for resource, created_at, updated_at in timestamps:
        resource.created_at = created_at
        resource.updated_at = updated_at

    return root


def object_from_dict(data: dict[str, Any]):
    """Reconstruct a built-in model object from its dictionary representation."""
    if not isinstance(data, dict):
        raise TypeError("model data must be a dictionary")
    if data.get("type") == "resource_tree":
        from ..core.tree import ResourceTree
        return ResourceTree.from_dict(data)
    return resource_from_dict(data)
