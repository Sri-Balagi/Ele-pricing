import time
import uuid
from datetime import datetime, timezone

from app.core.constants import RuleTriggerType
from app.models.domain import (
    Configuration,
    ExecutionReport,
    ProductCatalogue,
    RuleContext,
    RuleMetrics,
    RuleResult,
)
from app.rules.action_handlers import ActionRegistry
from app.rules.dsl import ConditionEvaluator, ConditionParser
from app.rules.registry import RuleRegistry


class RuleEvaluator:
    """Orchestrates the evaluation of rules against a configuration."""

    def __init__(
        self,
        catalogue: ProductCatalogue,
        rule_registry: RuleRegistry,
        action_registry: ActionRegistry,
    ) -> None:
        self.catalogue = catalogue
        self.rule_registry = rule_registry
        self.action_registry = action_registry
        self.parser = ConditionParser()
        self.condition_evaluator = ConditionEvaluator()

    def evaluate(
        self, configuration: Configuration, trigger_type: RuleTriggerType
    ) -> ExecutionReport:
        """Runs the rule engine pipeline for the given configuration and trigger type."""
        
        start_time = time.perf_counter()
        correlation_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        metrics = RuleMetrics()
        executed_rules = []
        skipped_rules = []
        failed_rules = []

        # Pull from registry (already sorted and validated)
        rules = self.rule_registry.get_rules_by_trigger(trigger_type)
        metrics.rules_loaded = len(rules)

        execution_history = []

        for rule in rules:
            context = RuleContext(
                configuration=configuration,
                catalogue=self.catalogue,
                current_rule=rule,
                trigger_type=trigger_type,
                execution_timestamp=timestamp,
                correlation_id=correlation_id,
                execution_depth=0,
                execution_history=execution_history.copy(),
            )

            # Fire BeforeRule
            self._fire_event("BeforeRule", context)

            try:
                # Parse & Evaluate Condition
                ast_node = self.parser.parse(rule.condition)
                is_met = self.condition_evaluator.evaluate(ast_node, context)
            except Exception as e:
                # Log parsing/eval failures and continue
                metrics.rules_failed += 1
                failed_rules.append(rule.id)
                configuration.rule_results.append(
                    RuleResult(
                        rule_id=rule.id,
                        triggered=False,
                        message=f"Condition evaluation failed: {e}",
                    )
                )
                self._fire_event("AfterRule", context)
                continue

            if is_met:
                self._fire_event("BeforeAction", context)
                try:
                    handler = self.action_registry.get_handler(rule.action)
                    handler.validate_payload(rule.action_payload)
                    result = handler.execute(context, rule.action_payload)

                    # Execution success
                    metrics.rules_executed += 1
                    executed_rules.append(rule.id)
                    execution_history.append(rule.id)

                    configuration.rule_results.append(
                        RuleResult(
                            rule_id=rule.id,
                            triggered=True,
                            action_taken=rule.action.value,
                            message=result.message,
                        )
                    )

                    self._fire_event("AfterAction", context)

                    # Check halt flag
                    if rule.stop_processing:
                        self._fire_event("AfterRule", context)
                        break

                except Exception as e:
                    metrics.rules_failed += 1
                    failed_rules.append(rule.id)
                    configuration.rule_results.append(
                        RuleResult(
                            rule_id=rule.id,
                            triggered=True,
                            action_taken=rule.action.value,
                            message=f"Action execution failed: {e}",
                        )
                    )
                    self._fire_event("AfterAction", context)
            else:
                metrics.rules_skipped += 1
                skipped_rules.append(rule.id)
                configuration.rule_results.append(
                    RuleResult(
                        rule_id=rule.id,
                        triggered=False,
                        message="Condition not met.",
                    )
                )

            self._fire_event("AfterRule", context)

        metrics.total_execution_time_ms = (time.perf_counter() - start_time) * 1000

        return ExecutionReport(
            configuration_id=configuration.configuration_id,
            trigger=trigger_type.value,
            executed_rules=executed_rules,
            skipped_rules=skipped_rules,
            failed_rules=failed_rules,
            execution_time_ms=metrics.total_execution_time_ms,
            summary=f"Evaluated {metrics.rules_loaded} rules in {metrics.total_execution_time_ms:.2f}ms",
            metrics=metrics,
        )

    def _fire_event(self, event_name: str, context: RuleContext) -> None:
        """Internal hook for future tracing and lifecycle events."""
        # E.g., logging to a tracing system or telemetry
        pass
