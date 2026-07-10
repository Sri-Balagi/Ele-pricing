from app.core.constants import DataFile
from app.models.domain import PricingCatalogue
from app.repositories.base import BaseRepository


class PricingRepository(BaseRepository[PricingCatalogue]):
    """
    Repository for loading the structured pricing.json file.
    """

    def __init__(self) -> None:
        super().__init__(model_class=PricingCatalogue, data_file=DataFile.PRICING)
