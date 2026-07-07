"""
Dependency Engine Module.

Provides graph-based engineering dependency resolution, cycle detection,
and topological sorting for the configuration lifecycle.
"""

from app.dependency_engine.engine import DependencyEngine
from app.dependency_engine.graph import (
    CircularDependencyError,
    GraphBuilder,
)

__all__ = [
    "DependencyEngine",
    "GraphBuilder",
    "CircularDependencyError",
]
