"""
Graph Cache.

Caches the immutable DependencyGraph topology keyed by catalogue_version.
Only the static topology (nodes + edges) is cached. Runtime state (is_active,
metrics, mutations) is NEVER stored here.

Invalidation strategy: version-based.
  - If catalogue_version matches the cached version, the stored graph is returned.
  - If catalogue_version changes, the cache is cleared and the graph is rebuilt.
  - An explicit invalidate() method is available for administrative tooling.

Thread-safety: callers are responsible for external locking if needed.
This prototype runs single-threaded, so no internal locking is applied.
"""

import copy
from typing import Optional

from app.models.domain import DependencyGraph, ProductCatalogue
from app.dependency_engine.graph_builder import GraphBuilder
from app.dependency_engine.registry import DependencyRegistry


class GraphCache:
    """Version-keyed cache for DependencyGraph topology."""

    def __init__(self) -> None:
        self._cached_graph: Optional[DependencyGraph] = None
        self._cached_version: Optional[str] = None

    def get_or_build(
        self,
        catalogue: ProductCatalogue,
        registry: DependencyRegistry,
    ) -> DependencyGraph:
        """
        Returns the cached graph if the catalogue version is unchanged.
        Rebuilds and caches a new graph if the version has changed.

        Returns a deep copy so callers can safely mutate is_active state
        without contaminating the cached topology.
        """
        current_version = catalogue.metadata.catalogue_version

        if self._cached_graph is None or self._cached_version != current_version:
            builder = GraphBuilder(catalogue)
            self._cached_graph = builder.build(registry)
            self._cached_version = current_version

        # Always return a deep copy — callers own their runtime copy
        return copy.deepcopy(self._cached_graph)

    def invalidate(self) -> None:
        """Explicitly clears the cache. For administrative tooling only."""
        self._cached_graph = None
        self._cached_version = None

    @property
    def cached_version(self) -> Optional[str]:
        """Returns the currently cached catalogue version, or None if empty."""
        return self._cached_version

    @property
    def is_warm(self) -> bool:
        """True if the cache holds a graph."""
        return self._cached_graph is not None
