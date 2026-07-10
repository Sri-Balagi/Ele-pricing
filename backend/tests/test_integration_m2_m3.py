import pytest

from app.dependency_engine.resolver import DependencyResolver
from app.models.domain import (
    CatalogMetadata,
    Component,
    Configuration,
    ConfigurationStatus,
    Dependency,
    DependencyResolutionContext,
    DependencyResolutionReport,
    DependencyType,
    FeatureOption,
    ProductCatalogue,
    Rule,
    RuleAction,
    RuleContext,
    RuleTriggerType,
)
from app.rules.action_handlers import ActionRegistry
from app.rules.evaluator import RuleEvaluator
from app.rules.registry import RuleRegistry


class MockRepository:
    def __init__(self, data):
        self._data = data

    def get_all(self):
        return self._data


@pytest.fixture
def integrated_catalogue():
    return ProductCatalogue(
        metadata=CatalogMetadata(
            catalogue_version="2.0",
            schema_version="1.0",
            created_date="2026-07-08T00:00:00Z",
            last_updated="2026-07-08T00:00:00Z",
            prototype_version="1.0",
        ),
        categories=[],
        feature_groups=[],
        features=[],
        components=[
            Component(
                id="COMP_M2", category="Cabin", name="M2 Added Component", unit="pcs"
            ),
            Component(
                id="COMP_M3", category="Cabin", name="M3 Added Component", unit="pcs"
            ),
            Component(
                id="COMP_FINAL", category="Cabin", name="Final Dependent", unit="pcs"
            ),
        ],
        feature_options=[
            FeatureOption(
                id="OPT_USER",
                feature_id="F1",
                display_name="User Selected",
                internal_value="Y",
            ),
        ],
        mappings=[],
        dependencies=[
            # COMP_M2 (added by rule) requires COMP_M3
            Dependency(
                id="D1",
                source_id="COMP_M2",
                target_id="COMP_M3",
                dependency_type=DependencyType.REQUIRES,
            ),
            # COMP_M3 requires COMP_FINAL
            Dependency(
                id="D2",
                source_id="COMP_M3",
                target_id="COMP_FINAL",
                dependency_type=DependencyType.REQUIRES,
            ),
        ],
    )


@pytest.fixture
def base_config():
    return Configuration(
        configuration_id="INT-CFG-1",
        status=ConfigurationStatus.DRAFT,
        selected_feature_options=["OPT_USER"],
        resolved_components=[],
    )


def test_full_pipeline_m2_to_m3(integrated_catalogue, base_config):
    # Rules list
    rules = [
        Rule(
            id="RULE_M2",
            name="Rule mapping OPT_USER to COMP_M2",
            trigger_type=RuleTriggerType.ON_SELECTION,
            priority=10,
            condition="has_option('OPT_USER')",
            action=RuleAction.ADD_COMPONENT,
            action_payload={"component_id": "COMP_M2"},
        )
    ]

    # 1. Setup Rule Engine
    rule_repo = MockRepository(rules)
    rule_registry = RuleRegistry(integrated_catalogue, rule_repo)
    rule_registry.validator.validate_rules = lambda r: r
    rule_registry.load_and_validate()

    # We use standard actions here so we need a real ActionRegistry.
    # We have app.rules.action_handlers.ActionRegistry, but wait! We haven't fully implemented standard actions
    # in milestone 2? We mocked ADD_COMPONENT previously. Wait, let's mock it again just to be safe.
    action_reg = ActionRegistry()

    class StandardMockAddComponent:
        def validate_payload(self, payload):
            pass

        def execute(self, context, action_payload):
            comp_id = action_payload.get("component_id")
            if comp_id not in context.configuration.resolved_components:
                context.configuration.resolved_components.append(comp_id)
            from app.rules.action_handlers import ActionResult

            return ActionResult(success=True, message=f"Added {comp_id}")

    action_reg.register(RuleAction.ADD_COMPONENT, StandardMockAddComponent())

    rule_evaluator = RuleEvaluator(integrated_catalogue, rule_registry, action_reg)

    # 2. Setup Dependency Engine
    dep_repo = MockRepository(integrated_catalogue.dependencies)
    dependency_resolver = DependencyResolver(integrated_catalogue, repository=dep_repo)

    # 3. Execution Phase A: Rule Engine (M2)
    rule_ctx = RuleContext(
        configuration=base_config,
        catalogue=integrated_catalogue,
        trigger_type=RuleTriggerType.ON_SELECTION,
        correlation_id="corr-m2",
        execution_timestamp="ts",
    )
    rule_report = rule_evaluator.resolve(rule_ctx)

    # Rule engine added COMP_M2
    assert "COMP_M2" in base_config.resolved_components
    assert "RULE_M2" in rule_report.executed_rules
    assert "COMP_M3" not in base_config.resolved_components

    # 4. Execution Phase B: Dependency Engine (M3)
    dep_report = DependencyResolutionReport(
        configuration_id=base_config.configuration_id
    )
    dep_ctx = DependencyResolutionContext(
        configuration=base_config,
        catalogue=integrated_catalogue,
        report=dep_report,
        correlation_id="corr-m3",
        execution_timestamp="ts",
    )
    resolution_report = dependency_resolver.resolve(dep_ctx)

    # Dependency engine resolves COMP_M3 and COMP_FINAL automatically based on COMP_M2 being present
    assert "COMP_M3" in base_config.resolved_components
    assert "COMP_FINAL" in base_config.resolved_components
    assert resolution_report.metrics.resolved_nodes == 3  # M2, M3, FINAL

    # The mutation audit log in config should have records for M2 (by rule) and M3, FINAL (by dep engine)
    # Wait, the mock action handler for Rule engine didn't add mutations.
    # But Dependency Engine definitely adds mutations. Let's check Dependency Engine mutations.
    dep_mutations = [
        m for m in base_config.mutations if m.source_engine == "DEPENDENCY_ENGINE"
    ]
    assert len(dep_mutations) == 2
    assert any(m.entity_id == "COMP_M3" for m in dep_mutations)
    assert any(m.entity_id == "COMP_FINAL" for m in dep_mutations)
