import logging
from decimal import ROUND_HALF_UP, Decimal

from app.pricing_engine.context import PricingContext

logger = logging.getLogger(__name__)


class BOMCostResolver:
    """
    Maps resolved components to their unit costs in the BOM.
    Populates BOMItem.unit_cost and BOMItem.pricing_record_id.
    """

    def populate_unit_costs(self, context: PricingContext, category_cost: Decimal, floor_cost: Decimal, feature_cost: Decimal) -> int:
        """
        Iterates over the existing BillOfMaterials in Configuration
        and populates the unit_cost. Dynamically scales BASE and FEATURE components.
        """
        if not context.configuration.bill_of_materials:
            return 0

        # Pass 1: Calculate raw total of BASE components and FEATURE components
        base_items = []
        feature_items = []
        base_components_raw_total = Decimal("0.00")
        feature_components_raw_total = Decimal("0.00")
        
        for item in context.configuration.bill_of_materials.items:
            origin_val = getattr(item.origin_type, "value", str(item.origin_type))
            record = context.pricing_registry.get_pricing_record(item.component_id)
            if origin_val == "BASE":
                base_items.append(item)
                if record:
                    base_components_raw_total += record.price
            else:
                feature_items.append(item)
                if record:
                    feature_components_raw_total += record.price

        target_base_total = category_cost + floor_cost
        target_feature_total = feature_cost

        base_scale_factor = Decimal("1.0")
        if base_components_raw_total > 0:
            base_scale_factor = target_base_total / base_components_raw_total

        feature_scale_factor = Decimal("1.0")
        if feature_components_raw_total > 0:
            feature_scale_factor = target_feature_total / feature_components_raw_total
        elif target_feature_total > 0:
            # Fallback if somehow raw components are 0 but feature cost is not
            feature_scale_factor = target_feature_total / max(Decimal("1.0"), Decimal(len(feature_items)))

        items_priced = 0
        for item in context.configuration.bill_of_materials.items:
            origin_val = getattr(item.origin_type, "value", str(item.origin_type))
            record = context.pricing_registry.get_pricing_record(item.component_id)
            
            if origin_val == "BASE":
                if record:
                    scaled_cost = record.price * base_scale_factor
                    item.unit_cost = scaled_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    item.pricing_record_id = record.entity_id
                else:
                    item.unit_cost = Decimal("0.00")
                items_priced += 1
            else:
                if record:
                    scaled_cost = record.price * feature_scale_factor
                    item.unit_cost = scaled_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    item.pricing_record_id = record.entity_id
                else:
                    # Fallback flat distribution if no pricing record exists for component
                    if feature_components_raw_total == 0 and target_feature_total > 0:
                         item.unit_cost = feature_scale_factor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    else:
                         item.unit_cost = Decimal("0.00")
                items_priced += 1

        # Fix any rounding discrepancy for base components
        if base_items:
            current_sum = sum((i.unit_cost for i in base_items if i.unit_cost is not None), Decimal("0.00"))
            diff = target_base_total - current_sum
            if diff != Decimal("0.00") and base_items[0].unit_cost is not None:
                base_items[0].unit_cost += diff

        # Fix any rounding discrepancy for feature components
        if feature_items:
            current_sum = sum((i.unit_cost for i in feature_items if i.unit_cost is not None), Decimal("0.00"))
            diff = target_feature_total - current_sum
            if diff != Decimal("0.00") and feature_items[0].unit_cost is not None:
                feature_items[0].unit_cost += diff

        return items_priced
