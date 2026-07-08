"""
Dependency Validator.

Validates the raw Dependency data (catalogue level) before any graph is
built. This is distinct from GraphValidator which validates the constructed
graph's structural integrity.

Responsibilities:
  - Ensure every source_id and target_id references a real catalogue entity
  - Detect duplicate dependency IDs
  - Reject self-referencing dependencies (source == target)
"""

from typing import List

from app.models.domain import Dependency, ProductCatalogue


class DependencyValidationError(Exception):
    """Raised when raw dependency data fails catalogue-level validation."""
    pass


class DependencyValidator:
    """Validates raw Dependency records against the Product Catalogue."""

    def __init__(self, catalogue: ProductCatalogue) -> None:
        self._known_components = {c.id for c in catalogue.components}
        self._known_options = {o.id for o in catalogue.feature_options}
        self._known_entities = self._known_components | self._known_options

    def validate(self, dependencies: List[Dependency]) -> List[Dependency]:
        """
        Validates all dependencies. Returns the validated list.
        Raises DependencyValidationError on any structural failure.
        """
        seen_ids: set[str] = set()
        errors: List[str] = []

        for dep in dependencies:
            # Duplicate IDs
            if dep.id in seen_ids:
                errors.append(f"Duplicate dependency ID: '{dep.id}'")
            seen_ids.add(dep.id)

            # Self-loop at catalogue level (source == target)
            if dep.source_id == dep.target_id:
                errors.append(
                    f"Dependency '{dep.id}' is a self-loop: source and target are both '{dep.source_id}'"
                )

            # Unknown source
            if dep.source_id not in self._known_entities:
                errors.append(
                    f"Dependency '{dep.id}' references unknown source entity '{dep.source_id}'"
                )

            # Unknown target
            if dep.target_id not in self._known_entities:
                errors.append(
                    f"Dependency '{dep.id}' references unknown target entity '{dep.target_id}'"
                )

        if errors:
            raise DependencyValidationError(
                f"Dependency catalogue validation failed with {len(errors)} error(s):\n"
                + "\n".join(f"  • {e}" for e in errors)
            )

        return dependencies
