"""
Dependency Activation Engine.

Evaluates condition_expression strings on each graph edge and sets
is_active accordingly. Activation state is written only into the
per-request graph copy held by DependencyResolutionContext.

The shared cached graph (in GraphCache) is NEVER mutated.

Design guarantees:
  - Thread-safe: each request operates on its own graph copy
  - No cross-configuration contamination
  - DSL reused from the Rule Engine (ConditionParser + ConditionEvaluator)
  - Edges without condition_expression remain active (is_active=True)
  - DSL parse/eval failures deactivate the edge (fail-safe)
"""

import logging

from app.models.domain import (
    Configuration,
    DependencyGraph,
    ProductCatalogue,
    RuleContext,
    RuleTriggerType,
)
from app.rules.dsl import ConditionEvaluator, ConditionParser

logger = logging.getLogger(__name__)


class DependencyActivationEngine:
    """Evaluates DSL conditions on graph edges, setting is_active per request context."""

    def __init__(self) -> None:
        self._parser = ConditionParser()
        self._evaluator = ConditionEvaluator()

    def activate(
        self,
        graph: DependencyGraph,
        configuration: Configuration,
        catalogue: ProductCatalogue,
        correlation_id: str,
        execution_timestamp: str,
    ) -> None:
        """
        Evaluates all conditional edges in the graph (in-place on the provided copy).
        Edges with no condition remain is_active=True.
        Edges that fail DSL evaluation are set to is_active=False.

        Args:
            graph: The per-request graph copy from GraphCache. Mutated directly.
            configuration: Current configuration state (read-only for DSL eval).
            catalogue: Product catalogue (read-only).
            correlation_id: Trace ID for logging.
            execution_timestamp: ISO timestamp for logging context.
        """
        # Build a minimal RuleContext for DSL evaluation only
        context = RuleContext(
            configuration=configuration,
            catalogue=catalogue,
            current_rule=None,
            trigger_type=RuleTriggerType.ON_SELECTION,
            execution_timestamp=execution_timestamp,
            correlation_id=correlation_id,
        )

        for source_id, edges in graph.adjacency_list.items():
            for edge in edges:
                expr = edge.dependency.condition_expression
                if not expr:
                    # No condition — always active
                    edge.is_active = True
                    continue

                try:
                    ast_node = self._parser.parse(expr)
                    edge.is_active = self._evaluator.evaluate(ast_node, context)
                    logger.debug(
                        "Edge %s→%s condition '%s' evaluated to %s",
                        source_id,
                        edge.dependency.target_id,
                        expr,
                        edge.is_active,
                    )
                except Exception as exc:
                    # Fail-safe: deactivate on error
                    edge.is_active = False
                    logger.warning(
                        "Edge %s (dep '%s') condition evaluation failed: %s — edge deactivated",
                        edge.dependency.id,
                        expr,
                        exc,
                    )
