from typing import Any

from app.core.constants import DataFile
from app.models.domain import PricingCatalogue
from app.repositories.base import BaseRepository

class PricingRepository(BaseRepository[PricingCatalogue]):
    """
    Repository for loading the structured pricing.json file.
    """

    def _get_filename(self) -> str:
        return DataFile.PRICING.value

    def _parse(self, data: Any) -> PricingCatalogue:
        """Parse raw JSON into the PricingCatalogue model."""
        return PricingCatalogue.model_validate(data)
