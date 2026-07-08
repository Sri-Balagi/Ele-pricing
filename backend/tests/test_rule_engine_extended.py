import pytest
from app.models.domain import (
    Component,
    Configuration,
    ConfigurationStatus,
    FeatureOption,
    ProductCatalogue,
    Rule,
    RuleAction,
    RuleContext,
    RuleTriggerType,
    CatalogMetadata,
)
from app.rules.evaluator import RuleEvaluator
from app.rules.registry import RuleRegistry
from app.rules.action_handlers import ActionRegistry

# Mock repository for rules
class MockRuleRepository:
    def __init__(self, rules):
        self._rules = rules
    def get_all(self):
        return self._rules

@pytest.fixture
def empty_catalogue():
    return ProductCatalogue(
        metadata=CatalogMetadata(
            catalogue_version="1.0", schema_version="1.0",
            created_date="2026-07-08T00:00:00Z",
            last_updated="2026-07-08T00:00:00Z",
            prototype_version="1.0",
        ),
        categories=[], feature_groups=[], features=[],
        components=[
            Component(id="COMP_A", category="Cabin", name="A", unit="pcs"),
            Component(id="COMP_B", category="Cabin", name="B", unit="pcs"),
            Component(id="COMP_C", category="Cabin", name="C", unit="pcs"),
        ],
        feature_options=[
            FeatureOption(id="OPT_1", feature_id="F1", display_name="O1", internal_value="1"),
            FeatureOption(id="OPT_2", feature_id="F1", display_name="O2", internal_value="2"),
            FeatureOption(id="OPT_3", feature_id="F1", display_name="O3", internal_value="3"),
        ],
        mappings=[],
        dependencies=[],
        rules=[],
    )

@pytest.fixture
def base_config():
    return Configuration(
        configuration_id="TEST-CFG",
        status=ConfigurationStatus.DRAFT,
        selected_feature_options=[],
        resolved_components=[],
    )

def test_complex_nested_conditions(empty_catalogue, base_config):
    # Rule with condition: (OPT_1 OR OPT_2) AND NOT OPT_3
    # DSL string: "(has_option('OPT_1') or has_option('OPT_2')) and not has_option('OPT_3')"
    rule = Rule(
        id="R_COMPLEX",
        name="Complex Rule",
        trigger_type=RuleTriggerType.ON_SELECTION,
        priority=100,
        condition="(has_option('OPT_1') or has_option('OPT_2')) and not has_option('OPT_3')",
        action=RuleAction.ADD_COMPONENT,
        action_payload={"component_id": "COMP_A"}
    )
    
    registry = RuleRegistry(empty_catalogue, MockRuleRepository([rule]))
    registry.validator.validate_rules = lambda r: r
    registry.load_and_validate()
    
    evaluator = RuleEvaluator(empty_catalogue, registry, ActionRegistry())
    
    # Test case 1: OPT_1 alone -> True
    base_config.selected_feature_options = ["OPT_1"]
    context = RuleContext(
        configuration=base_config, catalogue=empty_catalogue,
        trigger_type=RuleTriggerType.ON_SELECTION,
        correlation_id="c1", execution_timestamp="ts"
    )
    evaluator.resolve(context)
    assert "COMP_A" in base_config.resolved_components
    
    # Reset
    base_config.resolved_components = []
    
    # Test case 2: OPT_1 AND OPT_3 -> False
    base_config.selected_feature_options = ["OPT_1", "OPT_3"]
    context = RuleContext(
        configuration=base_config, catalogue=empty_catalogue,
        trigger_type=RuleTriggerType.ON_SELECTION,
        correlation_id="c2", execution_timestamp="ts"
    )
    evaluator.resolve(context)
    assert "COMP_A" not in base_config.resolved_components

def test_rule_idempotency(empty_catalogue, base_config):
    rule = Rule(
        id="R_IDEMP", name="Idempotency",
        trigger_type=RuleTriggerType.ON_SELECTION, priority=100,
        condition="has_option('OPT_1')",
        action=RuleAction.ADD_COMPONENT,
        action_payload={"component_id": "COMP_B"}
    )
    registry = RuleRegistry(empty_catalogue, MockRuleRepository([rule]))
    registry.validator.validate_rules = lambda r: r
    registry.load_and_validate()
    evaluator = RuleEvaluator(empty_catalogue, registry, ActionRegistry())
    
    base_config.selected_feature_options = ["OPT_1"]
    
    # Run twice
    c1 = RuleContext(
        configuration=base_config, catalogue=empty_catalogue, 
        trigger_type=RuleTriggerType.ON_SELECTION,
        correlation_id="c1", execution_timestamp="ts"
    )
    evaluator.resolve(c1)
    
    c2 = RuleContext(
        configuration=base_config, catalogue=empty_catalogue,
        trigger_type=RuleTriggerType.ON_SELECTION,
        correlation_id="c2", execution_timestamp="ts"
    )
    evaluator.resolve(c2)
    
    # COMP_B should be present exactly once
    assert base_config.resolved_components.count("COMP_B") == 1
    
    # rule_results should have 2 entries for this rule (one for each run)
    assert len(base_config.rule_results) == 2

def test_error_isolation(empty_catalogue, base_config):
    # R1 has a missing component in payload (ActionRegistry doesn't validate payload, but action execution might if we override it, or we can just pass an invalid action type that raises an exception)
    r1 = Rule(
        id="R1_BAD", name="Bad Rule",
        trigger_type=RuleTriggerType.ON_SELECTION, priority=100,
        condition="not has_option('NON_EXISTENT')",
        action=RuleAction.ADD_COMPONENT,
        action_payload={"component_id": "COMP_MISSING"}
    )
    r2 = Rule(
        id="R2_GOOD", name="Good Rule",
        trigger_type=RuleTriggerType.ON_SELECTION, priority=50,
        condition="not has_option('NON_EXISTENT')",
        action=RuleAction.ADD_COMPONENT,
        action_payload={"component_id": "COMP_C"}
    )
    
    registry = RuleRegistry(empty_catalogue, MockRuleRepository([r1, r2]))
    registry.validator.validate_rules = lambda r: r
    registry.load_and_validate()
    
    action_reg = ActionRegistry()
    
    # Mock ADD_COMPONENT to match ActionHandler interface
    class SafeMockAddComponent:
        def validate_payload(self, payload):
            pass
            
        def execute(self, context, action_payload):
            comp_id = action_payload.get("component_id")
            if comp_id == "COMP_MISSING":
                raise ValueError("Intentional crash")
            if comp_id not in context.configuration.resolved_components:
                context.configuration.resolved_components.append(comp_id)
            from app.rules.action_handlers import ActionResult
            return ActionResult(success=True, message="Mock Added")
                
    action_reg.register(RuleAction.ADD_COMPONENT, SafeMockAddComponent())
    
    evaluator = RuleEvaluator(empty_catalogue, registry, action_reg)
    
    c1 = RuleContext(
        configuration=base_config, catalogue=empty_catalogue,
        trigger_type=RuleTriggerType.ON_SELECTION,
        correlation_id="c1", execution_timestamp="ts"
    )
    report = evaluator.resolve(c1)
    
    # R1 failed, R2 succeeded
    assert "R1_BAD" in report.failed_rules
    assert "R2_GOOD" in report.executed_rules
    assert "COMP_C" in base_config.resolved_components
