import logging
from typing import Any

logger = logging.getLogger(__name__)


class PricingLogger:
    """
    Structured lifecycle logging for the Pricing Engine.
    """

    def before_pricing(self, correlation_id: str, configuration_id: str) -> None:
        logger.info(
            "[%s] Starting Pricing Engine for Configuration %s",
            correlation_id,
            configuration_id,
        )

    def before_tax(self, correlation_id: str, subtotal: float) -> None:
        logger.debug(
            "[%s] Calculating tax on subtotal: %.2f",
            correlation_id,
            subtotal,
        )

    def after_tax(self, correlation_id: str, tax_amount: float, total: float) -> None:
        logger.debug(
            "[%s] Tax calculated: %.2f | Total after tax: %.2f",
            correlation_id,
            tax_amount,
            total,
        )

    def before_bom(self, correlation_id: str) -> None:
        logger.debug("[%s] Populating BOM unit costs...", correlation_id)

    def after_bom(self, correlation_id: str, items_priced: int) -> None:
        logger.debug(
            "[%s] Populated %d BOM items with unit costs.", correlation_id, items_priced
        )

    def before_summary(self, correlation_id: str) -> None:
        logger.debug("[%s] Generating final PricingSummary...", correlation_id)

    def after_summary(self, correlation_id: str, summary: Any) -> None:
        logger.info("[%s] PricingSummary generated successfully.", correlation_id)

    def after_pricing(
        self, correlation_id: str, configuration_id: str, total: float
    ) -> None:
        logger.info(
            "[%s] Pricing Engine completed for Configuration %s. Total: %.2f",
            correlation_id,
            configuration_id,
            total,
        )

    def validation_error(self, correlation_id: str, message: str) -> None:
        logger.error("[%s] Validation error: %s", correlation_id, message)
