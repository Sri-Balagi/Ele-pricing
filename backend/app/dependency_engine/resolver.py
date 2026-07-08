"""
Dependency Resolver.

The master orchestrator for the Dependency Resolution Engine.
This module fires lifecycle events and delegates to the correct
specialist modules in the approved pipeline order.

Pipeline:
  1. GraphCache.get_or_build          (version-based)
  2. DependencyActivationEngine       (DSL condition evaluation)
  3. GraphValidator                   (structural validation)
  4. CycleDetector / TraversalEngine  (topological sort + BFS)
  5. TopologicalResolutionStrategy    (per-node dispatch)
       └─ ResolutionExecutor          (per-edge mutation)
            └─ ConflictResolver       (EXCLUDES violations)
  6. DependencyResolutionReport       (populated throughout)

Design principles:
  - DependencyResolver NEVER touches Configuration directly
  - Catalogue is treated as read-only throughout
  - Each resolution request gets a fresh DependencyResolutionContext
  - GraphCache topology is reused; only edge is_active changes per run
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.models.domain import (
    Configuration,
    DependencyGraph,
    DependencyResolutionContext,
    DependencyResolutionMetrics,
    DependencyResolutionReport,
    ProductCatalogue,
)
from app.dependency_engine.activation import DependencyActivationEngine
from app.dependency_engine.cycle_detector import CircularDependencyError
from app.dependency_engine.executor import ResolutionExecutor
from app.dependency_engine.graph_cache import GraphCache
from app.dependency_engine.graph_validator import GraphValidationError, GraphValidator
from app.dependency_engine.logger import ResolutionLogger
from app.dependency_engine.registry import DependencyRegistry
from app.dependency_engine.repository import DependencyRepository
from app.dependency_engine.strategies import TopologicalResolutionStrategy
from app.dependency_engine.traversal import TraversalEngine


class DependencyResolver:
    """
    Master orchestrator for the Dependency Resolution Engine.
    Pure delegation — never mutates Configuration directly.
    """

    def __init__(
        self,
        catalogue: ProductCatalogue,
        repository: Optional[DependencyRepository] = None,
        strategy: Optional[TopologicalResolutionStrategy] = None,
    ) -> None:
        self._catalogue = catalogue

        # Infrastructure
        self._registry = DependencyRegistry(catalogue, repository)
        self._registry.load_and_validate()

        # Sub-modules
        self._graph_cache = GraphCache()
        self._graph_validator = GraphValidator()
        self._activation_engine = DependencyActivationEngine()
        self._traversal_engine = TraversalEngine()
        self._executor = ResolutionExecutor()
        self._strategy = strategy or TopologicalResolutionStrategy()
        self._log = ResolutionLogger()

    def resolve(self, configuration: Configuration) -> DependencyResolutionReport:
        """
        Runs the full dependency resolution pipeline for the given configuration.

        Returns:
            DependencyResolutionReport — complete audit trail, never raises on
            conflicts (they are recorded in the report). Raises on cycles.
        """
        start_time = time.perf_counter()
        correlation_id = str(uuid.uuid4())
        execution_timestamp = datetime.now(timezone.utc).isoformat()
        catalogue_version = self._catalogue.metadata.catalogue_version

        # Initialise a fresh report for this run
        report = DependencyResolutionReport(configuration_id=configuration.configuration_id)

        # ── Phase 1: Graph ────────────────────────────────────────────────────
        self._log.before_graph(correlation_id, catalogue_version)

        graph = self._graph_cache.get_or_build(self._catalogue, self._registry)

        # Update topology metrics
        total_edges = sum(len(edges) for edges in graph.adjacency_list.values())
        report.metrics.total_nodes = len(graph.nodes)
        report.metrics.total_edges = total_edges

        # ── Phase 2: Activation ───────────────────────────────────────────────
        self._activation_engine.activate(
            graph, configuration, self._catalogue, correlation_id, execution_timestamp
        )

        # ── Phase 3: Graph Validation ─────────────────────────────────────────
        try:
            graph_warnings = self._graph_validator.validate(graph)
        except GraphValidationError as exc:
            report.warnings.append(f"GRAPH_VALIDATION_ERROR: {exc}")
            report.summary = f"Graph validation failed: {exc}"
            return report

        for w in graph_warnings:
            report.warnings.append(f"GRAPH_WARNING: {w}")

        active_edges = sum(
            1
            for edges in graph.adjacency_list.values()
            for e in edges
            if e.is_active
        )
        report.metrics.active_edges = active_edges

        self._log.after_graph(correlation_id, len(graph.nodes), total_edges, graph_warnings)

        # ── Phase 4: Traversal ────────────────────────────────────────────────
        self._log.before_traversal(correlation_id)

        try:
            topo_order, reachable_set = self._traversal_engine.get_traversal_order(
                graph, configuration
            )
        except CircularDependencyError as exc:
            report.cycles_detected = exc.guilty_nodes
            report.warnings.append(f"CIRCULAR_DEPENDENCY: {exc}")
            report.summary = f"Resolution aborted: circular dependency in {exc.guilty_nodes}"
            self._finalise_metrics(report, start_time)
            return report

        report.metrics.active_nodes = len(reachable_set)
        self._log.after_traversal(correlation_id, len(topo_order), len(reachable_set))

        # ── Phase 5: Resolution ───────────────────────────────────────────────
        self._log.before_resolution(correlation_id, type(self._strategy).__name__)

        context = DependencyResolutionContext(
            configuration=configuration,
            catalogue=self._catalogue,
            graph=graph,
            report=report,
            correlation_id=correlation_id,
            execution_timestamp=execution_timestamp,
        )

        self._strategy.execute(topo_order, reachable_set, context, self._executor)

        self._log.after_resolution(
            correlation_id,
            report.metrics.resolved_nodes,
            report.metrics.skipped_nodes,
            len(report.conflicts),
        )

        # ── Phase 6: Finalise ─────────────────────────────────────────────────
        self._finalise_metrics(report, start_time)

        components_added = len(report.components_added)
        options_added = len(report.options_added)
        conflicts = len(report.conflicts)
        time_ms = report.metrics.execution_time_ms

        report.summary = (
            f"Resolved {report.metrics.resolved_nodes} nodes in {time_ms:.2f}ms. "
            f"Added {components_added} components, {options_added} options. "
            f"Conflicts: {conflicts}. "
            f"Warnings: {len(report.warnings)}."
        )

        return report

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _finalise_metrics(
        self, report: DependencyResolutionReport, start_time: float
    ) -> None:
        report.metrics.execution_time_ms = (time.perf_counter() - start_time) * 1000
