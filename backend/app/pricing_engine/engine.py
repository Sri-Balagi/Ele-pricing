import time

from app.core.engine_base import BaseEngine
from app.models.domain import PricingReport, PricingSummary
from app.pricing_engine.bom_resolver import BOMCostResolver
from app.pricing_engine.calculator import PricingCalculationError, PricingCalculator
from app.pricing_engine.context import PricingContext
from app.pricing_engine.logger import PricingLogger
from app.pricing_engine.tax_calculator import TaxCalculator


class PricingEngine(BaseEngine[PricingContext, PricingReport]):
    """
    Main orchestrator for Dynamic Pricing (Milestone 4).
    Calculates final base, component, feature costs, and taxes.
    """

    def __init__(self):
        self._calculator = PricingCalculator()
        self._tax_calculator = TaxCalculator()
        self._bom_resolver = BOMCostResolver()
        self._logger = PricingLogger()
        self._startup_context = None  # type: ignore

    def validate_startup(self) -> "EngineStartupReport":
        import time

        from app.models.domain import EngineStartupReport

        t0 = time.perf_counter()
        ready = True
        warnings = []
        errors = []
        # PricingEngine requires context at runtime, but we can do a dummy check or simply assume OK until resolve.
        # However, we can check if there are no errors so far.
        return EngineStartupReport(
            engine_name="PricingEngine",
            ready=ready,
            warnings=warnings,
            errors=errors,
            execution_time_ms=(time.perf_counter() - t0) * 1000,
        )

    def resolve(self, context: PricingContext) -> PricingReport:
        t0 = time.perf_counter()
        report = context.report
        config = context.configuration
        corr_id = context.correlation_id

        self._logger.before_pricing(corr_id, config.configuration_id)

        # Load registry if needed
        if not context.pricing_registry._is_loaded:
            context.pricing_registry.load_and_validate()

        current_step = 1

        try:
            # 1. Category Base Price
            category_cost, step = self._calculator.calculate_category_cost(
                context, current_step
            )
            report.pricing_steps.append(step)
            current_step += 1

            # 1.5. Floor Coverage Cost
            floor_cost, floor_step = self._calculator.calculate_floor_coverage_cost(
                context, current_step
            )
            if floor_step:
                report.pricing_steps.append(floor_step)
                current_step += 1

            # 2. Feature Costs
            feature_cost, f_steps = self._calculator.calculate_feature_costs(
                context, current_step
            )
            report.pricing_steps.extend(f_steps)
            current_step += len(f_steps)
            report.metrics.features_priced = len(f_steps)

            # 3. Component Costs
            component_cost, c_steps = self._calculator.calculate_component_costs(
                context, current_step
            )
            report.pricing_steps.extend(c_steps)
            current_step += len(c_steps)
            report.metrics.components_priced = len(c_steps)

            # 4. Subtotal
            subtotal = category_cost + feature_cost + floor_cost
            report.metrics.subtotal = subtotal

            # 5. Tax Calculation
            self._logger.before_tax(corr_id, float(subtotal))
            tax_amount, t_step = self._tax_calculator.calculate_tax(
                context, subtotal, current_step
            )
            if t_step:
                report.pricing_steps.append(t_step)
            self._logger.after_tax(
                corr_id, float(tax_amount), float(subtotal + tax_amount)
            )
            report.metrics.taxes = tax_amount

            # 6. Final Total
            total_after_tax = subtotal + tax_amount
            report.metrics.total = total_after_tax

            # 7. BOM Unit Costs
            self._logger.before_bom(corr_id)
            items_priced = self._bom_resolver.populate_unit_costs(
                context, category_cost, floor_cost, feature_cost
            )
            self._logger.after_bom(corr_id, items_priced)

            # 8. Pricing Summary
            self._logger.before_summary(corr_id)
            currency = context.pricing_registry.get_currency()

            summary = PricingSummary(
                currency=currency,
                category_cost=category_cost,
                component_cost=component_cost,
                feature_cost=feature_cost,
                floor_coverage_cost=floor_cost,
                base_price=category_cost,
                component_costs=component_cost,
                feature_costs=feature_cost,
                subtotal_before_tax=subtotal,
                tax_amount=tax_amount,
                total_after_tax=total_after_tax,
                taxes=tax_amount,
                total=total_after_tax,
            )
            config.pricing_summary = summary

            # The ConfigurationPipeline now owns status transitions.

            self._logger.after_summary(corr_id, summary)

        except PricingCalculationError as exc:
            self._logger.validation_error(corr_id, str(exc))
            report.errors.append(f"PRICING_ERROR: {exc}")
            report.summary = (
                f"Pricing aborted due to missing price record for: {exc.entity_id}"
            )
            # Configuration status remains unchanged

        except Exception as exc:
            self._logger.validation_error(corr_id, f"Unexpected error: {exc}")
            report.errors.append(f"UNEXPECTED_ERROR: {exc}")
            report.summary = "Pricing aborted due to unexpected error."

        if not report.errors:
            report.summary = "Pricing calculation completed successfully."

        t1 = time.perf_counter()
        report.metrics.execution_time_ms = (t1 - t0) * 1000

        self._logger.after_pricing(
            corr_id, config.configuration_id, float(report.metrics.total)
        )
        return report
