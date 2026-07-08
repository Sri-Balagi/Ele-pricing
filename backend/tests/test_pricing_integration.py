import pytest
from decimal import Decimal

from app.models.domain import (
    Component, Configuration, ConfigurationStatus, FeatureOption,
    ProductCatalogue, Rule, RuleAction, RuleContext, RuleTriggerType,
    CatalogMetadata, Dependency, DependencyType, DependencyResolutionContext,
    DependencyResolutionReport, PricingCatalogue, TaxConfiguration, PricingRecord
)
from app.rules.evaluator import RuleEvaluator
from app.rules.registry import RuleRegistry
from app.rules.action_handlers import ActionRegistry
from app.dependency_engine.resolver import DependencyResolver
from app.pricing_engine.engine import PricingEngine
from app.pricing_engine.context import PricingContext
from app.pricing_engine.registry import PricingRegistry
from app.pricing_engine.validator import PricingValidator

class MockRepository:
    def __init__(self, data):
        self._data = data
    def get_all(self):
        return self._data
    def exists(self, id: str):
        return True
    def get_by_id(self, id: str):
        return None

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
            PricingRecord(entity_id="COMP_FINAL", entity_type="COMPONENT", price=Decimal("300")),
        ]
    )
    
    return ProductCatalogue(
        metadata=CatalogMetadata(
            catalogue_version="2.0", schema_version="1.0",
            created_date="2026-07-08T00:00:00Z",
            last_updated="2026-07-08T00:00:00Z",
            prototype_version="1.0",
        ),
        categories=[], feature_groups=[], features=[],
        components=[
            Component(id="COMP_M2", category="Cabin", name="M2 Added Component", unit="pcs"),
            Component(id="COMP_M3", category="Cabin", name="M3 Added Component", unit="pcs"),
            Component(id="COMP_FINAL", category="Cabin", name="Final Dependent", unit="pcs"),
        ],
        feature_options=[
            FeatureOption(id="OPT_USER", feature_id="F1", display_name="User Selected", internal_value="Y"),
        ],
        mappings=[],
        dependencies=[
            Dependency(id="D1", source_id="COMP_M2", target_id="COMP_M3", dependency_type=DependencyType.REQUIRES),
            Dependency(id="D2", source_id="COMP_M3", target_id="COMP_FINAL", dependency_type=DependencyType.REQUIRES),
        ],
        pricing=pricing_cat
    )

@pytest.fixture
def base_config():
    return Configuration(
        configuration_id="INT-FULL-CFG",
        selected_category="CAT_A",
        status=ConfigurationStatus.DRAFT,
        selected_feature_options=["OPT_USER"],
        resolved_components=[],
    )

def test_full_pipeline_m2_m3_m4(integrated_catalogue, base_config):
    # --- Setup Rules ---
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
    
    # --- Setup Dependency ---
    dep_repo = MockRepository(integrated_catalogue.dependencies)
    dependency_resolver = DependencyResolver(integrated_catalogue, repository=dep_repo)
    
    # --- Setup Pricing ---
    price_repo = MockRepository(integrated_catalogue.pricing)
    pricing_registry = PricingRegistry(price_repo, PricingValidator())
    pricing_engine = PricingEngine()
    
    # --- EXECUTE PIPELINE ---
    
    # 1. Rules (M2)
    rule_ctx = RuleContext(
        configuration=base_config, catalogue=integrated_catalogue,
        trigger_type=RuleTriggerType.ON_SELECTION,
        correlation_id="corr-m2", execution_timestamp="ts"
    )
    rule_evaluator.resolve(rule_ctx)
    base_config.status = ConfigurationStatus.VALIDATED  # Simulate rule engine pass
    
    # 2. Dependencies (M3)
    dep_report = DependencyResolutionReport(configuration_id=base_config.configuration_id)
    dep_ctx = DependencyResolutionContext(
        configuration=base_config, catalogue=integrated_catalogue, report=dep_report,
        correlation_id="corr-m3", execution_timestamp="ts"
    )
    dependency_resolver.resolve(dep_ctx)
    
    # Simulate BOM Generation (M4a / pre-pricing)
    from app.models.domain import BillOfMaterials, BOMItem
    base_config.bill_of_materials = BillOfMaterials(
        items=[BOMItem(component_id=comp, quantity=1) for comp in base_config.resolved_components]
    )
    
    # Pre-pricing asserts
    assert "COMP_M2" in base_config.resolved_components
    assert "COMP_M3" in base_config.resolved_components
    assert "COMP_FINAL" in base_config.resolved_components
    assert len(base_config.bill_of_materials.items) == 3
    
    # 3. Pricing (M4)
    price_ctx = PricingContext(
        configuration=base_config, catalogue=integrated_catalogue,
        pricing_registry=pricing_registry, correlation_id="corr-m4", execution_timestamp="ts"
    )
    pricing_report = pricing_engine.resolve(price_ctx)
    
    # --- Post-Pricing Asserts ---
    assert len(pricing_report.errors) == 0
    assert base_config.status == ConfigurationStatus.PRICED
    
    summary = base_config.pricing_summary
    assert summary.currency == "EUR"
    assert summary.category_cost == Decimal("5000")
    assert summary.feature_cost == Decimal("500")
    # Components: 100 + 200 + 300 = 600
    assert summary.component_cost == Decimal("600")
    
    # Subtotal = 5000 + 500 + 600 = 6100
    assert summary.subtotal_before_tax == Decimal("6100")
    
    # Tax: 20% of 6100 = 1220
    assert summary.tax_amount == Decimal("1220")
    
    # Total = 6100 + 1220 = 7320
    assert summary.total_after_tax == Decimal("7320")
    
    # Check BOM Unit Costs populated
    for item in base_config.bill_of_materials.items:
        assert item.unit_cost is not None
        assert item.pricing_record_id == item.component_id
