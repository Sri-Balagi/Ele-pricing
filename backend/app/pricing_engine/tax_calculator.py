from decimal import Decimal, ROUND_HALF_UP

from app.pricing_engine.context import PricingContext
from app.models.domain import PricingStep

class TaxCalculator:
    """
    Separate module for calculating taxes.
    Only computes taxes based on subtotal.
    """

    def calculate_tax(self, context: PricingContext, subtotal: Decimal, step_number: int) -> tuple[Decimal, PricingStep | None]:
        """
        Calculates the tax amount based on the registry's TaxConfiguration.
        """
        tax_config = context.pricing_registry.get_tax_configuration()

        if not tax_config.enabled:
            return Decimal("0.00"), None

        # Formula: subtotal * (rate / 100)
        rate_multiplier = tax_config.rate / Decimal("100")
        tax_amount = (subtotal * rate_multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        step = PricingStep(
            step_number=step_number,
            entity_id=None,
            description=f"Applied {tax_config.tax_name} ({tax_config.rate}%)",
            amount=tax_amount,
            timestamp=context.execution_timestamp
        )

        return tax_amount, step
