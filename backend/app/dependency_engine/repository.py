"""
Dependency Repository.

Loads raw Dependency records from dependencies.json using the shared
DataLoader / BaseRepository infrastructure. No business logic here.
"""

from app.core.constants import DataFile
from app.models.domain import Dependency
from app.repositories.base import BaseRepository


class DependencyRepository(BaseRepository[Dependency]):
    """Repository for loading Dependency entities from JSON storage."""

    def __init__(self) -> None:
        super().__init__(model_class=Dependency, data_file=DataFile.DEPENDENCIES)
