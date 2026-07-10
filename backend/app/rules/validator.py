from app.core.constants import RuleAction, RuleTriggerType
from app.models.domain import ProductCatalogue, Rule


class RuleValidator:
    """Validates structural and logical integrity of loaded rules before execution."""

    def __init__(self, catalogue: ProductCatalogue):
        self.catalogue = catalogue
        self.known_components = {c.id for c in catalogue.components}
        self.known_options = {o.id for o in catalogue.feature_options}
        self.known_features = {f.id for f in catalogue.features}

    def validate_rules(self, rules: list[Rule]) -> list[Rule]:
        valid_rules = []
        seen_ids = set()

        for rule in rules:
            if not rule.enabled:
                continue

            if rule.id in seen_ids:
                raise ValueError(f"Duplicate Rule ID detected: {rule.id}")
            seen_ids.add(rule.id)

            if not isinstance(rule.trigger_type, RuleTriggerType):
                raise ValueError(
                    f"Rule {rule.id} has unsupported trigger type: {rule.trigger_type}"
                )

            if not isinstance(rule.action, RuleAction):
                raise ValueError(
                    f"Rule {rule.id} has unsupported action type: {rule.action}"
                )

            self._validate_payload(rule)
            valid_rules.append(rule)

        return valid_rules

    def _validate_payload(self, rule: Rule) -> None:
        payload = rule.action_payload
        action = rule.action

        if action in (RuleAction.ADD_COMPONENT, RuleAction.REMOVE_COMPONENT):
            comp_id = payload.get("component_id")
            if not comp_id:
                raise ValueError(
                    f"Rule {rule.id} ({action.value}) missing 'component_id' in payload."
                )
            if comp_id not in self.known_components:
                raise ValueError(
                    f"Rule {rule.id} references unknown component '{comp_id}'."
                )

        elif action in (RuleAction.REQUIRE_OPTION, RuleAction.EXCLUDE_OPTION):
            opt_id = payload.get("option_id")
            if not opt_id:
                raise ValueError(
                    f"Rule {rule.id} ({action.value}) missing 'option_id' in payload."
                )
            if opt_id not in self.known_options:
                raise ValueError(
                    f"Rule {rule.id} references unknown option '{opt_id}'."
                )
