import logging
from decimal import ROUND_HALF_UP, Decimal

from app.pricing_engine.context import PricingContext

logger = logging.getLogger(__name__)


class BOMCostResolver:
    """
    Maps resolved components to their unit costs in the BOM.
    Populates BOMItem.unit_cost and BOMItem.pricing_record_id.
    """

    def populate_unit_costs(self, context: PricingContext) -> int:
        """
        Iterates over the existing BillOfMaterials in Configuration
        and populates the unit_cost from the PricingRegistry.
        Returns the number of items populated.
        """
        if not context.configuration.bill_of_materials:
            return 0

        items_priced = 0
        for item in context.configuration.bill_of_materials.items:
            record = context.pricing_registry.get_pricing_record(item.component_id)
            if record:
                item.unit_cost = record.price.quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                item.pricing_record_id = record.entity_id
                items_priced += 1
            else:
                logger.warning(
                    "No pricing record found for BOM item: %s", item.component_id
                )

        return items_priced
