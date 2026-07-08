import logging
from typing import Optional

from app.models.domain import PricingCatalogue, PricingRecord, TaxConfiguration
from app.pricing_engine.repository import PricingRepository
from app.pricing_engine.validator import PricingValidator

logger = logging.getLogger(__name__)


class PricingRegistry:
    """
    Caches validated pricing records for fast O(1) lookups during configuration pricing.
    Serves as the single source of truth for pricing calculations.
    """

    def __init__(self, repository: PricingRepository, validator: PricingValidator):
        self._repository = repository
        self._validator = validator
        
        # O(1) lookup cache
        self._record_cache: dict[str, PricingRecord] = {}
        self._tax_config: Optional[TaxConfiguration] = None
        self._catalogue_version: str = ""
        self._currency: str = "EUR"
        
        self._is_loaded = False

    def load_and_validate(self) -> None:
        """Loads pricing data from repository, validates it, and builds lookup cache."""
        if self._is_loaded:
            return

        logger.info("Loading pricing catalogue...")
        catalogue: PricingCatalogue = self._repository.get_all()
        
        warnings = self._validator.validate(catalogue)
        for w in warnings:
            logger.warning("Pricing Validator Warning: %s", w)

        self._tax_config = catalogue.tax_configuration
        self._catalogue_version = catalogue.catalogue_version
        self._currency = catalogue.currency

        self._record_cache.clear()
        for record in catalogue.pricing_records:
            self._record_cache[record.entity_id] = record

        self._is_loaded = True
        logger.info(
            "Pricing registry loaded successfully (Version: %s, Currency: %s, Records: %d).",
            self._catalogue_version,
            self._currency,
            len(self._record_cache)
        )

    def get_pricing_record(self, entity_id: str) -> Optional[PricingRecord]:
        """Fetch a pricing record by entity_id (O(1)). Returns None if not found."""
        if not self._is_loaded:
            self.load_and_validate()
        return self._record_cache.get(entity_id)

    def get_tax_configuration(self) -> TaxConfiguration:
        """Get the global tax configuration."""
        if not self._is_loaded:
            self.load_and_validate()
        assert self._tax_config is not None, "Tax configuration missing."
        return self._tax_config

    def get_currency(self) -> str:
        if not self._is_loaded:
            self.load_and_validate()
        return self._currency
    
    # Extension point: Future cache invalidation method (e.g. invalidate())
    def invalidate(self) -> None:
        """Clear cache. Implement future Cache Extension point here."""
        self._is_loaded = False
        self._record_cache.clear()
        self._tax_config = None
