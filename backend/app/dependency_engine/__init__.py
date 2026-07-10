"""
Dependency Resolution Engine.

Public API: DependencyResolver is the single entry point.
All other modules are internal implementation details.

Usage:
    from app.dependency_engine import DependencyResolver

    resolver = DependencyResolver(catalogue)
    report = resolver.resolve(configuration)
"""

from app.dependency_engine.cycle_detector import CircularDependencyError
from app.dependency_engine.graph_validator import GraphValidationError
from app.dependency_engine.resolver import DependencyResolver
from app.dependency_engine.validator import DependencyValidationError

__all__ = [
    "CircularDependencyError",
    "DependencyResolver",
    "DependencyValidationError",
    "GraphValidationError",
]
