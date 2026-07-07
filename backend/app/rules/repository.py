from app.core.constants import DataFile
from app.models.domain import Rule
from app.repositories.base import BaseRepository


class RuleRepository(BaseRepository[Rule]):
    """Repository for managing Rule entities."""

    def __init__(self) -> None:
        super().__init__(model_class=Rule, data_file=DataFile.RULES)
