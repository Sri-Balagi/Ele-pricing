import pytest
from datetime import datetime, timezone
from app.core.constants import RuleAction, RuleTriggerType, RuleSeverity, ConfigurationStatus
from app.models.domain import (
    Configuration, Rule, ProductCatalogue, CatalogMetadata, 
    RuleContext, ExecutionReport
)
from app.rules.dsl import ConditionParser, ConditionEvaluator
from app.rules.action_handlers import ActionRegistry
from app.rules.registry import RuleRegistry
from app.rules.evaluator import RuleEvaluator


@pytest.fixture
def mock_catalogue():
    return ProductCatalogue(
        metadata=CatalogMetadata(
            catalogue_version="1.0",
            schema_version="1.0",
            created_date="2026-07-07T00:00:00Z",
            last_updated="2026-07-07T00:00:00Z",
            prototype_version="1.0",
        ),
        categories=[],
        feature_groups=[],
        features=[],
        feature_options=[],
        components=[],
        mappings=[],
        dependencies=[]
    )

@pytest.fixture
def mock_config():
    return Configuration(
        configuration_id="test-config-123",
        selected_category="CAT-A",
        selected_feature_options=[],
        resolved_components=[],
        rule_results=[],
        status=ConfigurationStatus.DRAFT
    )


def test_condition_parser_and_evaluator(mock_config, mock_catalogue):
    parser = ConditionParser()
    evaluator = ConditionEvaluator()
    
    context = RuleContext(
        configuration=mock_config,
        catalogue=mock_catalogue,
        current_rule=Rule(
            id="R1", name="R1", trigger_type=RuleTriggerType.ON_SELECTION,
            condition="True", action=RuleAction.ADD_COMPONENT
        ),
        trigger_type=RuleTriggerType.ON_SELECTION,
        execution_timestamp=datetime.now(timezone.utc).isoformat(),
        correlation_id="123",
    )
    
    mock_config.selected_feature_options = ["OPT-A"]
    mock_config.resolved_components = ["COMP-1"]
    
    # Test has_option
    ast_node = parser.parse("has_option('OPT-A')")
    assert evaluator.evaluate(ast_node, context) is True
    
    ast_node = parser.parse("has_option('OPT-B')")
    assert evaluator.evaluate(ast_node, context) is False
    
    # Test has_component
    ast_node = parser.parse("has_component('COMP-1')")
    assert evaluator.evaluate(ast_node, context) is True
    
    # Test AND / NOT
    ast_node = parser.parse("has_option('OPT-A') and not has_component('COMP-2')")
    assert evaluator.evaluate(ast_node, context) is True


class MockRepository:
    def __init__(self, rules):
        self.rules = rules
    def get_all(self):
        return self.rules


def test_rule_evaluator_integration(mock_config, mock_catalogue):
    # Setup mock rules (skip validator for simple test or bypass it)
    r1 = Rule(
        id="RULE-1",
        name="Test Rule 1",
        trigger_type=RuleTriggerType.ON_SELECTION,
        condition="has_option('OPT-A')",
        action=RuleAction.ADD_COMPONENT,
        action_payload={"component_id": "COMP-X"},
        priority=10
    )
    r2 = Rule(
        id="RULE-2",
        name="Test Rule 2",
        trigger_type=RuleTriggerType.ON_SELECTION,
        condition="has_component('COMP-X')",
        action=RuleAction.REQUIRE_OPTION,
        action_payload={"option_id": "OPT-B"},
        priority=20
    )
    
    mock_repo = MockRepository([r1, r2])
    
    # We patch validator since it checks catalogue FKs
    registry = RuleRegistry(catalogue=mock_catalogue, repository=mock_repo)
    # Bypass validation for testing
    registry.validator.validate_rules = lambda rules: rules 
    registry.load_and_validate()
    
    action_reg = ActionRegistry()
    evaluator = RuleEvaluator(catalogue=mock_catalogue, rule_registry=registry, action_registry=action_reg)
    
    mock_config.selected_feature_options = ["OPT-A"]
    
    context = RuleContext(
        configuration=mock_config,
        catalogue=mock_catalogue,
        trigger_type=RuleTriggerType.ON_SELECTION,
        execution_timestamp="2026-01-01T00:00:00Z",
        correlation_id="test-corr"
    )
    
    report = evaluator.resolve(context)
    
    assert report.metrics.rules_loaded == 2
    assert report.metrics.rules_executed == 2
    
    assert "COMP-X" in mock_config.resolved_components
    assert "OPT-B" in mock_config.selected_feature_options
    
    assert len(mock_config.rule_results) == 2
    assert mock_config.rule_results[0].rule_id == "RULE-1"
    assert mock_config.rule_results[0].triggered is True
    assert mock_config.rule_results[1].rule_id == "RULE-2"
    assert mock_config.rule_results[1].triggered is True
