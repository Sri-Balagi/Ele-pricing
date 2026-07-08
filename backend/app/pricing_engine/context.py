import logging
from typing import Any

from app.models.domain import (
    Configuration,
    ProductCatalogue,
    PricingReport,
)

class PricingContext:
    """
    Dedicated runtime context for the Pricing Engine.
    Never reuses RuleContext or DependencyResolutionContext.
    """

    def __init__(
        self,
        configuration: Configuration,
        catalogue: ProductCatalogue,
        pricing_registry: Any,  # Typed as Any here to avoid circular imports, will be PricingRegistry
        correlation_id: str,
        execution_timestamp: str,
        report: PricingReport | None = None,
    ):
        self.configuration = configuration
        self.catalogue = catalogue
        self.pricing_registry = pricing_registry
        self.correlation_id = correlation_id
        self.execution_timestamp = execution_timestamp
        self.report = report or PricingReport(configuration_id=configuration.configuration_id)
