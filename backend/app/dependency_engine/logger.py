"""
Resolution Logger.

Provides structured logging for every lifecycle event fired by
DependencyResolver. Log entries include the correlation_id for
cross-request tracing.

Lifecycle events:
  BeforeGraph        — before GraphCache.get_or_build
  AfterGraph         — after graph is built and validated
  BeforeTraversal    — before activation + cycle detection
  AfterTraversal     — after topological order is obtained
  BeforeResolution   — before strategy.execute begins
  AfterResolution    — after all nodes have been processed
  BeforeNode         — before a node's edges are resolved
  AfterNode          — after a node's edges are resolved
"""

import logging

logger = logging.getLogger(__name__)


class ResolutionLogger:
    """Emits structured log entries at each dependency engine lifecycle event."""

    def before_graph(self, correlation_id: str, catalogue_version: str) -> None:
        logger.info(
            "[%s] BeforeGraph — catalogue_version='%s'",
            correlation_id,
            catalogue_version,
        )

    def after_graph(
        self,
        correlation_id: str,
        node_count: int,
        edge_count: int,
        warnings: list[str],
    ) -> None:
        logger.info(
            "[%s] AfterGraph — nodes=%d edges=%d graph_warnings=%d",
            correlation_id,
            node_count,
            edge_count,
            len(warnings),
        )
        for w in warnings:
            logger.warning("[%s] GraphWarning: %s", correlation_id, w)

    def before_traversal(self, correlation_id: str) -> None:
        logger.info(
            "[%s] BeforeTraversal — running activation + cycle detection",
            correlation_id,
        )

    def after_traversal(
        self, correlation_id: str, topo_len: int, reachable: int
    ) -> None:
        logger.info(
            "[%s] AfterTraversal — topo_order=%d reachable=%d",
            correlation_id,
            topo_len,
            reachable,
        )

    def before_resolution(self, correlation_id: str, strategy_name: str) -> None:
        logger.info(
            "[%s] BeforeResolution — strategy='%s'",
            correlation_id,
            strategy_name,
        )

    def after_resolution(
        self, correlation_id: str, resolved: int, skipped: int, conflicts: int
    ) -> None:
        logger.info(
            "[%s] AfterResolution — resolved=%d skipped=%d conflicts=%d",
            correlation_id,
            resolved,
            skipped,
            conflicts,
        )

    def before_node(self, correlation_id: str, node_id: str) -> None:
        logger.debug("[%s] BeforeNode — '%s'", correlation_id, node_id)

    def after_node(self, correlation_id: str, node_id: str) -> None:
        logger.debug("[%s] AfterNode  — '%s'", correlation_id, node_id)
