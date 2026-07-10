from app.core.constants import RuleTriggerType
from app.models.domain import ProductCatalogue, Rule
from app.rules.repository import RuleRepository
from app.rules.validator import RuleValidator


class RuleRegistry:
    """Manages enabled rules, trigger-based indexing, and cached lookups."""

    def __init__(
        self, catalogue: ProductCatalogue, repository: RuleRepository | None = None
    ) -> None:
        self.repository = repository or RuleRepository()
        self.validator = RuleValidator(catalogue)
        self._rules_by_trigger: dict[RuleTriggerType, list[Rule]] = {}
        self._is_loaded = False

    def load_and_validate(self) -> None:
        """Loads rules from the repository, validates them, and indexes them."""
        raw_rules = self.repository.get_all()
        valid_rules = self.validator.validate_rules(raw_rules)

        # Index by trigger type
        self._rules_by_trigger = {trigger: [] for trigger in RuleTriggerType}
        for rule in valid_rules:
            self._rules_by_trigger[rule.trigger_type].append(rule)

        # Sort by priority (lower number = higher priority / runs first)
        for trigger in RuleTriggerType:
            self._rules_by_trigger[trigger].sort(key=lambda r: r.priority)

        self._is_loaded = True

    def get_rules_by_trigger(self, trigger_type: RuleTriggerType) -> list[Rule]:
        """Returns the sorted list of valid rules for the given trigger."""
        if not self._is_loaded:
            self.load_and_validate()
        return self._rules_by_trigger.get(trigger_type, [])

    def force_reload(self) -> None:
        """Forces the registry to reload rules from the underlying repository/cache."""
        self._is_loaded = False
        self.load_and_validate()
