"""Generic, domain-neutral resource tree model."""

from .core.resource import Resource
from .core.container import Container
from .core.asset import Asset
from .core.tree import ResourceTree

__version__ = "0.4.0"

__all__ = ["Resource", "Container", "Asset", "ResourceTree", "__version__"]
