from abc import ABC, abstractmethod
from typing import Any, Dict

from app.core.constants import RuleAction, RuleSeverity
from app.models.domain import ActionResult, RuleContext, ValidationMessage


class BaseActionHandler(ABC):
    """Abstract interface for all rule action handlers."""

    @abstractmethod
    def validate_payload(self, payload: Dict[str, Any]) -> None:
        """Validates the action payload schema before execution. Raises ValueError if invalid."""
        pass

    @abstractmethod
    def execute(self, context: RuleContext, payload: Dict[str, Any]) -> ActionResult:
        """Executes the action against the RuleContext and returns an ActionResult."""
        pass


class RequireOptionHandler(BaseActionHandler):
    def validate_payload(self, payload: Dict[str, Any]) -> None:
        if "option_id" not in payload:
            raise ValueError("REQUIRE_OPTION payload missing 'option_id'")

    def execute(self, context: RuleContext, payload: Dict[str, Any]) -> ActionResult:
        option_id = payload["option_id"]
        if option_id not in context.configuration.selected_feature_options:
            context.configuration.selected_feature_options.append(option_id)
            return ActionResult(
                success=True,
                message=f"Required option '{option_id}' added.",
                affected_entities=[option_id],
                configuration_changes={"selected_feature_options": {"added": [option_id]}},
            )
        return ActionResult(
            success=True,
            message=f"Required option '{option_id}' was already selected.",
        )


class ExcludeOptionHandler(BaseActionHandler):
    def validate_payload(self, payload: Dict[str, Any]) -> None:
        if "option_id" not in payload:
            raise ValueError("EXCLUDE_OPTION payload missing 'option_id'")

    def execute(self, context: RuleContext, payload: Dict[str, Any]) -> ActionResult:
        option_id = payload["option_id"]
        if option_id in context.configuration.selected_feature_options:
            context.configuration.selected_feature_options.remove(option_id)
            return ActionResult(
                success=True,
                message=f"Excluded option '{option_id}' removed.",
                affected_entities=[option_id],
                configuration_changes={"selected_feature_options": {"removed": [option_id]}},
            )
        return ActionResult(
            success=True,
            message=f"Excluded option '{option_id}' was not selected.",
        )


class AddComponentHandler(BaseActionHandler):
    def validate_payload(self, payload: Dict[str, Any]) -> None:
        if "component_id" not in payload:
            raise ValueError("ADD_COMPONENT payload missing 'component_id'")

    def execute(self, context: RuleContext, payload: Dict[str, Any]) -> ActionResult:
        comp_id = payload["component_id"]
        if comp_id not in context.configuration.resolved_components:
            context.configuration.resolved_components.append(comp_id)
            return ActionResult(
                success=True,
                message=f"Component '{comp_id}' added.",
                affected_entities=[comp_id],
                configuration_changes={"resolved_components": {"added": [comp_id]}},
            )
        return ActionResult(
            success=True,
            message=f"Component '{comp_id}' was already resolved.",
        )


class RemoveComponentHandler(BaseActionHandler):
    def validate_payload(self, payload: Dict[str, Any]) -> None:
        if "component_id" not in payload:
            raise ValueError("REMOVE_COMPONENT payload missing 'component_id'")

    def execute(self, context: RuleContext, payload: Dict[str, Any]) -> ActionResult:
        comp_id = payload["component_id"]
        if comp_id in context.configuration.resolved_components:
            context.configuration.resolved_components.remove(comp_id)
            return ActionResult(
                success=True,
                message=f"Component '{comp_id}' removed.",
                affected_entities=[comp_id],
                configuration_changes={"resolved_components": {"removed": [comp_id]}},
            )
        return ActionResult(
            success=True,
            message=f"Component '{comp_id}' was not present.",
        )


class AbortValidationHandler(BaseActionHandler):
    def validate_payload(self, payload: Dict[str, Any]) -> None:
        if "reason" not in payload:
            raise ValueError("ABORT_VALIDATION payload missing 'reason'")

    def execute(self, context: RuleContext, payload: Dict[str, Any]) -> ActionResult:
        reason = payload["reason"]
        
        msg = ValidationMessage(
            severity=RuleSeverity.ERROR,
            code="RULE_ABORT",
            message=reason,
            source_entity_id=context.current_rule.id
        )
        
        # Ensure validation_results structure exists
        if context.configuration.validation_results is None:
            # We import ValidationResult dynamically here or rely on the engine to init it.
            # It's better if engine handles the aggregate init, but we can do it here.
            pass
            
        return ActionResult(
            success=False, # It aborted
            message=f"Validation aborted: {reason}",
            warnings=["Validation aborted by rule"],
        )


class SetPriceMultiplierHandler(BaseActionHandler):
    def validate_payload(self, payload: Dict[str, Any]) -> None:
        if "multiplier" not in payload:
            raise ValueError("SET_PRICE_MULTIPLIER payload missing 'multiplier'")

    def execute(self, context: RuleContext, payload: Dict[str, Any]) -> ActionResult:
        multiplier = payload["multiplier"]
        return ActionResult(
            success=True,
            message=f"Price multiplier set to {multiplier}.",
            # The pricing engine will consume this later; we could store it in config metadata for now
            configuration_changes={"metadata": {"price_multiplier": multiplier}}
        )


class ActionRegistry:
    """Dynamic dispatcher mapping RuleAction enums to BaseActionHandler implementations."""

    def __init__(self) -> None:
        self._handlers: Dict[RuleAction, BaseActionHandler] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(RuleAction.REQUIRE_OPTION, RequireOptionHandler())
        self.register(RuleAction.EXCLUDE_OPTION, ExcludeOptionHandler())
        self.register(RuleAction.ADD_COMPONENT, AddComponentHandler())
        self.register(RuleAction.REMOVE_COMPONENT, RemoveComponentHandler())
        self.register(RuleAction.ABORT_VALIDATION, AbortValidationHandler())
        self.register(RuleAction.SET_PRICE_MULTIPLIER, SetPriceMultiplierHandler())

    def register(self, action: RuleAction, handler: BaseActionHandler) -> None:
        self._handlers[action] = handler

    def get_handler(self, action: RuleAction) -> BaseActionHandler:
        if action not in self._handlers:
            raise NotImplementedError(f"No handler registered for action: {action.value}")
        return self._handlers[action]
