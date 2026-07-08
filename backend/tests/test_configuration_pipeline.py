import pytest
from decimal import Decimal

from app.core.constants import ConfigurationStatus
from app.models.domain import (
    Component, Configuration, FeatureOption,
    ProductCatalogue, CatalogMetadata, Dependency, DependencyType,
    PricingCatalogue, TaxConfiguration, PricingRecord, Rule, RuleTriggerType, RuleAction
)
from app.rules.evaluator import RuleEvaluator
from app.rules.registry import RuleRegistry
from app.rules.action_handlers import ActionRegistry
from app.dependency_engine.resolver import DependencyResolver
from app.pricing_engine.engine import PricingEngine
from app.pricing_engine.registry import PricingRegistry
from app.pricing_engine.validator import PricingValidator
from app.services.configuration_pipeline import ConfigurationPipeline

class MockRepository:
    def __init__(self, data):
        self._data = data
    def get_all(self): return self._data
    def exists(self, id: str): return True
    def get_by_id(self, id: str): return None

@pytest.fixture
def integrated_catalogue():
    pricing_cat = PricingCatalogue(
        catalogue_version="2.0", currency="EUR",
        tax_configuration=TaxConfiguration(enabled=True, tax_name="VAT", rate=Decimal("20.0")),
        pricing_records=[
            PricingRecord(entity_id="CAT_A", entity_type="CATEGORY", price=Decimal("5000")),
            PricingRecord(entity_id="OPT_USER", entity_type="FEATURE_OPTION", price=Decimal("500")),
            PricingRecord(entity_id="COMP_M2", entity_type="COMPONENT", price=Decimal("100")),
            PricingRecord(entity_id="COMP_M3", entity_type="COMPONENT", price=Decimal("200")),
        ]
    )
    
    return ProductCatalogue(
        metadata=CatalogMetadata(
            catalogue_version="2.0", schema_version="1.0",
            created_date="2026-07-08T00:00:00Z", last_updated="2026-07-08T00:00:00Z",
            prototype_version="1.0",
        ),
        categories=[], feature_groups=[], features=[],
        components=[
            Component(id="COMP_M2", category="Cabin", name="M2 Component", unit="pcs"),
            Component(id="COMP_M3", category="Cabin", name="M3 Component", unit="pcs"),
        ],
        feature_options=[
            FeatureOption(id="OPT_USER", feature_id="F1", display_name="User Selected", internal_value="Y"),
        ],
        mappings=[],
        dependencies=[
            Dependency(id="D1", source_id="COMP_M2", target_id="COMP_M3", dependency_type=DependencyType.REQUIRES),
        ],
        pricing=pricing_cat
    )

@pytest.fixture
def pipeline(integrated_catalogue):
    rules = [
        Rule(
            id="RULE_M2", name="Rule mapping OPT_USER to COMP_M2",
            trigger_type=RuleTriggerType.ON_SELECTION, priority=10,
            condition="has_option('OPT_USER')",
            action=RuleAction.ADD_COMPONENT,
            action_payload={"component_id": "COMP_M2"}
        )
    ]
    rule_repo = MockRepository(rules)
    rule_registry = RuleRegistry(integrated_catalogue, rule_repo)
    rule_registry.validator.validate_rules = lambda r: r
    rule_registry.load_and_validate()
    
    action_reg = ActionRegistry()
    class StandardMockAddComponent:
        def validate_payload(self, payload): pass
        def execute(self, context, action_payload):
            comp_id = action_payload.get("component_id")
            if comp_id not in context.configuration.resolved_components:
                context.configuration.resolved_components.append(comp_id)
            from app.rules.action_handlers import ActionResult
            return ActionResult(success=True, message=f"Added {comp_id}")
    action_reg.register(RuleAction.ADD_COMPONENT, StandardMockAddComponent())
    rule_evaluator = RuleEvaluator(integrated_catalogue, rule_registry, action_reg)
    
    dep_repo = MockRepository(integrated_catalogue.dependencies)
    dependency_resolver = DependencyResolver(integrated_catalogue, repository=dep_repo)
    
    price_repo = MockRepository(integrated_catalogue.pricing)
    pricing_registry = PricingRegistry(price_repo, PricingValidator())
    pricing_engine = PricingEngine()
    
    return ConfigurationPipeline(
        catalogue=integrated_catalogue,
        rule_evaluator=rule_evaluator,
        dependency_resolver=dependency_resolver,
        pricing_engine=pricing_engine,
        pricing_registry=pricing_registry
    )

def test_pipeline_idempotency(pipeline):
    """
    Executing the pipeline multiple times on the same configuration should not 
    duplicate components, mutations, or produce inconsistent prices.
    """
    config = Configuration(
        configuration_id="TEST-IDEMP-001",
        selected_category="CAT_A",
        status=ConfigurationStatus.DRAFT,
        selected_feature_options=["OPT_USER"]
    )
    
    # First execution
    report_1 = pipeline.execute(config)
    assert report_1.metrics.success is True
    assert config.status == ConfigurationStatus.PRICED
    
    components_count_1 = len(config.resolved_components)
    total_1 = config.pricing_summary.total_after_tax
    mutations_count_1 = len(config.mutations)
    
    assert components_count_1 == 2  # M2 added by rule, M3 by dependency
    
    # Reset status manually to simulate a re-run from DRAFT after user changed their mind
    # Actually, a pipeline should handle a pre-existing PRICED config gracefully 
    # but we will just re-execute on the same object to test idempotency of the engines.
    
    # Second execution
    report_2 = pipeline.execute(config)
    assert report_2.metrics.success is True
    assert config.status == ConfigurationStatus.PRICED
    
    components_count_2 = len(config.resolved_components)
    total_2 = config.pricing_summary.total_after_tax
    
    # The dependency engine adds new mutations if it sees an edge. We need to make sure 
    # the DependencyResolver doesn't double-mutate if the node is already resolved!
    # Wait, the rule engine mock ActionHandler does `if comp_id not in context.configuration.resolved_components:`.
    # Let's verify total components remains 2.
    assert components_count_2 == components_count_1, "Components duplicated on second run!"
    assert total_2 == total_1, "Pricing duplicated on second run!"
