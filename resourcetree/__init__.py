"""
resourcetree

Generic hierarchical resource tree framework.
"""


from .core.resource import Resource
from .core.container import Container
from .core.asset import Asset


__version__ = "0.1.0"


__all__ = [
    "Resource",
    "Container",
    "Asset",
]