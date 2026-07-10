from decimal import Decimal, ROUND_HALF_UP

from app.pricing_engine.context import PricingContext
from app.models.domain import PricingStep
from app.core.exceptions import PricingCalculationException

class PricingCalculationError(PricingCalculationException):
    """Raised when a calculation fails, e.g., missing price record."""
    def __init__(self, message: str, entity_id: str):
        super().__init__(message=message)
        self.entity_id = entity_id

class PricingCalculator:
    """
    Pure calculation module for determining category, feature, and component costs.
    No mutation.
    """

    def calculate_category_cost(self, context: PricingContext, step_counter: int) -> tuple[Decimal, PricingStep]:
        """Calculates base price for the selected category."""
        category_id = context.configuration.selected_category
        if not category_id:
            raise PricingCalculationError("No category selected in configuration.", "UNKNOWN")

        record = context.pricing_registry.get_pricing_record(category_id)
        if not record:
            raise PricingCalculationError(f"Missing pricing record for category: {category_id}", category_id)

        # Monetary Precision: Decimal & ROUND_HALF_UP
        cost = record.price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        step = PricingStep(
            step_number=step_counter,
            entity_id=category_id,
            description=f"Added base category price for {category_id}",
            amount=cost,
            timestamp=context.execution_timestamp
        )
        return cost, step

    def calculate_feature_costs(self, context: PricingContext, start_step: int) -> tuple[Decimal, list[PricingStep]]:
        """Calculates sum of costs for all selected feature options."""
        total = Decimal("0.00")
        steps = []
        current_step = start_step

        for option_id in context.configuration.selected_feature_options:
            if option_id.startswith("STOPS-"):
                continue

            record = context.pricing_registry.get_pricing_record(option_id)
            if not record:
                # Missing mandatory pricing record! Fail fast.
                raise PricingCalculationError(f"Missing pricing record for feature option: {option_id}", option_id)

            cost = record.price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if cost > 0:
                steps.append(PricingStep(
                    step_number=current_step,
                    entity_id=option_id,
                    description=f"Added feature cost for {option_id}",
                    amount=cost,
                    timestamp=context.execution_timestamp
                ))
                total += cost
                current_step += 1

        return total, steps

    def calculate_component_costs(self, context: PricingContext, start_step: int) -> tuple[Decimal, list[PricingStep]]:
        """Calculates sum of costs for all resolved components."""
        total = Decimal("0.00")
        steps = []
        current_step = start_step

        for comp_id in context.configuration.resolved_components:
            record = context.pricing_registry.get_pricing_record(comp_id)
            if not record:
                raise PricingCalculationError(f"Missing pricing record for component: {comp_id}", comp_id)

            cost = record.price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if cost > 0:
                steps.append(PricingStep(
                    step_number=current_step,
                    entity_id=comp_id,
                    description=f"Added component cost for {comp_id}",
                    amount=cost,
                    timestamp=context.execution_timestamp
                ))
                total += cost
                current_step += 1

        return total, steps

    def calculate_floor_coverage_cost(self, context: PricingContext, start_step: int) -> tuple[Decimal, PricingStep | None]:
        """Calculates dynamic additional cost based on number of stops."""
        category_id = context.configuration.selected_category
        total = Decimal("0.00")
        step = None

        stops = 0
        for opt in context.configuration.selected_feature_options:
            if opt.startswith("STOPS-"):
                try:
                    stops = int(opt.replace("STOPS-", ""))
                except ValueError:
                    pass
                break
        
        if stops > 0:
            additional_floors = 0
            unit_cost = 0
            
            if category_id == "CAT-A":
                additional_floors = max(0, stops - 2)
                unit_cost = 2000
            elif category_id == "CAT-B":
                additional_floors = max(0, stops - 4)
                unit_cost = 3800
            elif category_id == "CAT-C":
                additional_floors = max(0, stops - 8)
                unit_cost = 8500
                
            if additional_floors > 0:
                cost = Decimal(str(additional_floors * unit_cost))
                total = cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                step = PricingStep(
                    step_number=start_step,
                    entity_id=f"FLOOR-COVERAGE-{stops}",
                    description=f"Added floor coverage cost for {additional_floors} additional floors ({stops} total stops)",
                    amount=total,
                    timestamp=context.execution_timestamp
                )

        return total, step
