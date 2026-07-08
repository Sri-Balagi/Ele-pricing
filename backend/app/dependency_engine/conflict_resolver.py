"""
Conflict Resolver.

Detects EXCLUDES violations during dependency resolution.

A conflict occurs when an entity that should be excluded is already present
in the active configuration (either from user selection or a previous
REQUIRES resolution).

Responsibilities:
  - Produce a structured DependencyConflict record
  - Append the conflict to DependencyResolutionReport.conflicts
  - Append a ValidationMessage to Configuration.validation_results
  - Mark validation_results.is_valid = False
"""

import logging

from app.core.constants import RuleSeverity
from app.models.domain import (
    DependencyConflict,
    DependencyEdge,
    DependencyResolutionContext,
    ValidationMessage,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class ConflictResolver:
    """Detects and records EXCLUDES violations."""

    def check(
        self,
        edge: DependencyEdge,
        active_set: set[str],
        context: DependencyResolutionContext,
    ) -> bool:
        """
        Checks whether the target of an EXCLUDES edge is in the active set.

        Returns:
            True if a conflict was found (and recorded), False otherwise.
        """
        target_id = edge.dependency.target_id
        source_id = edge.dependency.source_id

        if target_id not in active_set:
            return False

        reason = (
            f"'{source_id}' strictly excludes '{target_id}', "
            f"but '{target_id}' is present in the configuration "
            f"(dependency '{edge.dependency.id}')."
        )

        conflict = DependencyConflict(
            dependency_id=edge.dependency.id,
            source_entity_id=source_id,
            target_entity_id=target_id,
            reason=reason,
        )
        context.report.conflicts.append(conflict)
        context.report.warnings.append(f"CONFLICT: {reason}")

        # Ensure ValidationResult exists and mark invalid
        if context.configuration.validation_results is None:
            context.configuration.validation_results = ValidationResult(is_valid=True)

        context.configuration.validation_results.errors.append(
            ValidationMessage(
                severity=RuleSeverity.ERROR,
                code="DEP_CONFLICT",
                message=reason,
                source_entity_id=edge.dependency.id,
            )
        )
        context.configuration.validation_results.is_valid = False

        logger.warning("Dependency conflict: %s", reason)
        return True
