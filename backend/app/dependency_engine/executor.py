"""
Resolution Executor.

Applies a single dependency edge to the Configuration. DependencyResolver
and TopologicalResolutionStrategy never touch Configuration directly —
all mutations go through this module.

Supported actions:
  REQUIRES   → add target to configuration + ConfigurationMutation + ResolutionStep(mutated=True)
  DETERMINES → identical behaviour to REQUIRES
  EXCLUDES   → delegate to ConflictResolver + ResolutionStep(mutated=True)
  RECOMMENDS → warning + ResolutionStep(mutated=False)

Every applied action produces a ResolutionStep in the report's execution_order.
"""

import logging
from datetime import datetime, timezone

from app.core.constants import DependencyType
from app.models.domain import (
    ConfigurationMutation,
    DependencyEdge,
    DependencyResolutionContext,
    ResolutionStep,
)
from app.dependency_engine.conflict_resolver import ConflictResolver

logger = logging.getLogger(__name__)


class ResolutionExecutor:
    """Applies a single dependency edge to the Configuration aggregate."""

    def __init__(self) -> None:
        self._conflict_resolver = ConflictResolver()

    def apply(
        self,
        edge: DependencyEdge,
        context: DependencyResolutionContext,
    ) -> None:
        """
        Applies the edge according to its dependency_type.

        Args:
            edge: The active dependency edge to apply.
            context: Current resolution context (Configuration is mutable here).
        """
        dep = edge.dependency
        dep_type = dep.dependency_type
        target_id = dep.target_id
        source_id = dep.source_id
        timestamp = datetime.now(timezone.utc).isoformat()

        # Build the active set once per call for lookup efficiency
        active_set: set[str] = (
            set(context.configuration.selected_feature_options)
            | set(context.configuration.resolved_components)
        )

        step_number = len(context.report.execution_order) + 1

        if dep_type in (DependencyType.REQUIRES, DependencyType.DETERMINES):
            self._apply_requires(
                target_id, source_id, dep, active_set, context, step_number, timestamp
            )

        elif dep_type == DependencyType.EXCLUDES:
            self._apply_excludes(
                edge, active_set, context, step_number, timestamp
            )

        elif dep_type == DependencyType.RECOMMENDS:
            self._apply_recommends(
                target_id, source_id, dep, active_set, context, step_number, timestamp
            )

    # ── REQUIRES / DETERMINES ─────────────────────────────────────────────────

    def _apply_requires(
        self, target_id, source_id, dep, active_set, context, step_number, timestamp
    ) -> None:
        node_type = context.graph.nodes.get(target_id)
        entity_type = node_type.entity_type if node_type else "UNKNOWN"

        if target_id not in active_set:
            # Mutate configuration
            if entity_type == "COMPONENT":
                context.configuration.resolved_components.append(target_id)
                context.report.components_added.append(target_id)
            elif entity_type == "OPTION":
                context.configuration.selected_feature_options.append(target_id)
                context.report.options_added.append(target_id)

            # Append mutation log
            context.configuration.mutations.append(
                ConfigurationMutation(
                    timestamp=timestamp,
                    source_engine="DEPENDENCY_ENGINE",
                    entity_id=target_id,
                    mutation_type="ADDED",
                    reason=(
                        f"Required by '{source_id}' via dependency '{dep.id}' "
                        f"({dep.dependency_type})"
                    ),
                )
            )

            logger.info(
                "REQUIRES: added %s '%s' (triggered by '%s', dep '%s')",
                entity_type,
                target_id,
                source_id,
                dep.id,
            )

        context.report.execution_order.append(
            ResolutionStep(
                step_number=step_number,
                entity_id=target_id,
                dependency_id=dep.id,
                action_performed=dep.dependency_type,
                mutated=target_id not in active_set,
                timestamp=timestamp,
            )
        )

    # ── EXCLUDES ──────────────────────────────────────────────────────────────

    def _apply_excludes(
        self, edge, active_set, context, step_number, timestamp
    ) -> None:
        dep = edge.dependency
        self._conflict_resolver.check(edge, active_set, context)

        context.report.execution_order.append(
            ResolutionStep(
                step_number=step_number,
                entity_id=dep.target_id,
                dependency_id=dep.id,
                action_performed=dep.dependency_type,
                mutated=True,
                timestamp=timestamp,
            )
        )

    # ── RECOMMENDS ────────────────────────────────────────────────────────────

    def _apply_recommends(
        self, target_id, source_id, dep, active_set, context, step_number, timestamp
    ) -> None:
        if target_id not in active_set:
            warning = (
                f"RECOMMENDATION: '{source_id}' recommends '{target_id}' "
                f"(dep '{dep.id}') — not enforced."
            )
            context.report.warnings.append(warning)
            logger.info(warning)

        # Always record a step, never mutated
        context.report.execution_order.append(
            ResolutionStep(
                step_number=step_number,
                entity_id=target_id,
                dependency_id=dep.id,
                action_performed=dep.dependency_type,
                mutated=False,
                timestamp=timestamp,
            )
        )
