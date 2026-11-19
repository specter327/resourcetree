"""Iterative traversal and ancestor navigation for generic resource hierarchies."""
from __future__ import annotations

from collections.abc import Iterator

from ..core.container import Container
from ..core.resource import Resource


def _normalize_order(order: str) -> str:
    aliases = {"pre": "pre", "preorder": "pre", "post": "post", "postorder": "post"}
    if not isinstance(order, str):
        raise TypeError("order must be 'pre' or 'post'")
    try:
        return aliases[order.lower()]
    except KeyError as error:
        raise ValueError("order must be 'pre' or 'post'") from error


def walk(source: Resource | "ResourceTree", *, order: str = "pre") -> Iterator[Resource]:
    """Yield a resource hierarchy iteratively in depth-first preorder or postorder."""
    from ..core.tree import ResourceTree

    normalized = _normalize_order(order)
    if isinstance(source, ResourceTree):
        starts = source.roots
        for root in starts:
            if not isinstance(root, Resource):
                raise TypeError("resource tree roots must be Resource instances")
            if root.parent is not None:
                raise ValueError("resource tree roots must not have parents")
    elif isinstance(source, Resource):
        starts = (source,)
        parent = source.parent
        if parent is not None:
            if not isinstance(parent, Container):
                raise TypeError("resource parent must be a Container")
            if sum(child is source for child in parent.children) != 1:
                raise ValueError("inconsistent parent/child relationship")
    else:
        raise TypeError("source must be a Resource or ResourceTree")

    visited: set[int] = set()
    for start in starts:
        stack: list[tuple[Resource, bool]] = [(start, False)]
        while stack:
            node, expanded = stack.pop()
            if expanded:
                yield node
                continue
            if not isinstance(node, Resource):
                raise TypeError("resource hierarchy can contain only Resource instances")
            identity = id(node)
            if identity in visited:
                raise ValueError("cycle or duplicate reference detected in resource hierarchy")
            visited.add(identity)

            if normalized == "post":
                stack.append((node, True))
            else:
                yield node

            if isinstance(node, Container):
                children = node.children
                child_ids: set[int] = set()
                for child in children:
                    if not isinstance(child, Resource):
                        raise TypeError("container children must be Resource instances")
                    if id(child) in child_ids:
                        raise ValueError("duplicate child reference")
                    child_ids.add(id(child))
                    if child.parent is not node:
                        raise ValueError("inconsistent parent/child relationship")
                stack.extend((child, False) for child in reversed(children))


def ancestors(
    resource: Resource,
    *,
    include_self: bool = False,
    order: str = "up",
) -> Iterator[Resource]:
    """Yield parents from the immediate parent upward, or root-to-parent."""
    if not isinstance(resource, Resource):
        raise TypeError("resource must be a Resource instance")
    if not isinstance(include_self, bool):
        raise TypeError("include_self must be a bool")
    if order not in {"up", "down"}:
        raise ValueError("order must be 'up' or 'down'")

    chain: list[Resource] = []
    current: Resource | None = resource if include_self else resource.parent
    visited: set[int] = set()
    while current is not None:
        if not isinstance(current, Resource):
            raise TypeError("resource parent chain must contain Resource instances")
        if id(current) in visited:
            raise ValueError("cycle detected in resource parent chain")
        visited.add(id(current))
        chain.append(current)
        parent = current.parent
        if parent is not None:
            if not isinstance(parent, Container):
                raise TypeError("resource parent must be a Container")
            if sum(child is current for child in parent.children) != 1:
                raise ValueError("inconsistent parent/child relationship")
        current = parent

    yield from (chain if order == "up" else reversed(chain))


def direct(resource: Resource) -> Iterator[Resource]:
    """Backward-compatible preorder traversal alias."""
    yield from walk(resource)


def inverse(resource: Resource) -> Iterator[Resource]:
    """Backward-compatible root-to-resource parent-chain alias."""
    yield from ancestors(resource, include_self=True, order="down")


__all__ = ["walk", "ancestors", "direct", "inverse"]
