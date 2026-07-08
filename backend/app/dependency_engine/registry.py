"""
Dependency Registry.

Sits between DependencyRepository and the graph layer. Caches validated
dependency definitions and exposes typed lookups and adjacency access.

Responsibilities:
  - Load and validate dependencies on first access
  - Cache validated dependency list
  - Expose source-keyed and target-keyed adjacency maps
  - Expose lookup by ID
  - Support forced reload for administrative tooling
"""

from typing import Dict, List, Optional

from app.models.domain import Dependency, ProductCatalogue
from app.dependency_engine.repository import DependencyRepository
from app.dependency_engine.validator import DependencyValidator


class DependencyRegistry:
    """Caches validated dependencies and provides adjacency lookups."""

    def __init__(
        self,
        catalogue: ProductCatalogue,
        repository: Optional[DependencyRepository] = None,
    ) -> None:
        self._catalogue = catalogue
        self._repository = repository or DependencyRepository()
        self._validator = DependencyValidator(catalogue)

        # Caches
        self._dependencies: List[Dependency] = []
        self._by_id: Dict[str, Dependency] = {}
        self._adjacency: Dict[str, List[Dependency]] = {}       # source_id → [Dependency]
        self._reverse_adjacency: Dict[str, List[Dependency]] = {}  # target_id → [Dependency]
        self._is_loaded = False

    # ── Loading ───────────────────────────────────────────────────────────────

    def load_and_validate(self) -> None:
        """Loads, validates, and indexes all dependencies."""
        raw = self._repository.get_all()
        validated = self._validator.validate(raw)

        self._dependencies = validated
        self._by_id = {d.id: d for d in validated}
        self._adjacency = {}
        self._reverse_adjacency = {}

        for dep in validated:
            self._adjacency.setdefault(dep.source_id, []).append(dep)
            self._reverse_adjacency.setdefault(dep.target_id, []).append(dep)

        self._is_loaded = True

    def force_reload(self) -> None:
        """Forces cache invalidation and full reload."""
        self._is_loaded = False
        self.load_and_validate()

    def _ensure_loaded(self) -> None:
        if not self._is_loaded:
            self.load_and_validate()

    # ── Lookups ───────────────────────────────────────────────────────────────

    def get_all(self) -> List[Dependency]:
        self._ensure_loaded()
        return list(self._dependencies)

    def get_by_id(self, dep_id: str) -> Optional[Dependency]:
        self._ensure_loaded()
        return self._by_id.get(dep_id)

    def get_outgoing(self, source_id: str) -> List[Dependency]:
        """Returns all dependencies where source_id is the origin."""
        self._ensure_loaded()
        return list(self._adjacency.get(source_id, []))

    def get_incoming(self, target_id: str) -> List[Dependency]:
        """Returns all dependencies where target_id is the destination."""
        self._ensure_loaded()
        return list(self._reverse_adjacency.get(target_id, []))
