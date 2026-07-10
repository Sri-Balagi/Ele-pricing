import time

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


class MockRuleRepo:
    def __init__(self, data):
        self._data = data

    def get_all(self):
        return self._data


class MockDepRepo:
    def __init__(self, data):
        self._data = data

    def get_all(self):
        return self._data

    def get_outgoing(self, node_id):
        return [d for d in self._data if d.source_id == node_id]


@pytest.fixture
def large_catalogue():
    # 1000 components, 1000 options, 1000 rules, 1000 dependencies
    components = [
        Component(id=f"C_{i}", category="Cabin", name=f"Comp {i}", unit="pcs")
        for i in range(1000)
    ]
    options = [
        FeatureOption(
            id=f"O_{i}", feature_id="F1", display_name=f"Opt {i}", internal_value=str(i)
        )
        for i in range(1000)
    ]

    deps = []

    for i in range(1000):
        # Each dependency: C_i requires C_{i+1} (except last)
        if i < 999:
            deps.append(
                Dependency(
                    id=f"D_{i}",
                    source_id=f"C_{i}",
                    target_id=f"C_{i + 1}",
                    dependency_type=DependencyType.REQUIRES,
                )
            )

    return ProductCatalogue(
        metadata=CatalogMetadata(
            catalogue_version="v_bench",
            schema_version="1.0",
            created_date="2026-07-08T00:00:00Z",
            last_updated="2026-07-08T00:00:00Z",
            prototype_version="1.0",
        ),
        categories=[],
        feature_groups=[],
        features=[],
        components=components,
        feature_options=options,
        mappings=[],
        dependencies=deps,
    )


def test_performance_benchmark(large_catalogue):
    rules = []
    for i in range(1000):
        # Each rule triggers on O_i and adds C_i
        rules.append(
            Rule(
                id=f"R_{i}",
                name=f"Rule {i}",
                trigger_type=RuleTriggerType.ON_SELECTION,
                priority=10,
                condition=f"has_option('O_{i}')",
                action=RuleAction.ADD_COMPONENT,
                action_payload={"component_id": f"C_{i}"},
            )
        )

    """
    Performance-only benchmark. 
    Does not fail CI unless an exception occurs.
    """
    # -- 1. Setup Rule Engine --
    rule_repo = MockRuleRepo(rules)
    rule_reg = RuleRegistry(large_catalogue, rule_repo)
    rule_reg.validator.validate_rules = lambda r: r
    rule_reg.load_and_validate()

    action_reg = ActionRegistry()

    class FastAction:
        def validate_payload(self, p):
            pass

        def execute(self, ctx, payload):
            ctx.configuration.resolved_components.append(payload["component_id"])
            from app.rules.action_handlers import ActionResult

            return ActionResult(success=True)

    action_reg.register(RuleAction.ADD_COMPONENT, FastAction())

    rule_eval = RuleEvaluator(large_catalogue, rule_reg, action_reg)

    # -- 2. Setup Dependency Engine --
    dep_repo = MockDepRepo(large_catalogue.dependencies)
    dep_res = DependencyResolver(large_catalogue, dep_repo)

    # -- 3. Execute Rule Engine (Trigger top 100 options) --
    config = Configuration(
        configuration_id="CFG-BENCH",
        status=ConfigurationStatus.DRAFT,
        selected_feature_options=[f"O_{i}" for i in range(100)],
        resolved_components=[],
    )

    t0 = time.perf_counter()
    r_ctx = RuleContext(
        configuration=config,
        catalogue=large_catalogue,
        correlation_id="b1",
        execution_timestamp="ts",
        trigger_type=RuleTriggerType.ON_SELECTION,
    )
    r_rep = rule_eval.resolve(r_ctx)
    t1 = time.perf_counter()

    rule_time_ms = (t1 - t0) * 1000

    # -- 4. Execute Dependency Engine (traverse from 100 resolved components) --
    d_rep = DependencyResolutionReport(configuration_id=config.configuration_id)
    d_ctx = DependencyResolutionContext(
        configuration=config,
        catalogue=large_catalogue,
        report=d_rep,
        correlation_id="b2",
        execution_timestamp="ts",
    )

    t2 = time.perf_counter()
    d_res_rep = dep_res.resolve(d_ctx)
    t3 = time.perf_counter()

    dep_time_ms = (t3 - t2) * 1000

    # Log times
    print(f"\n[BENCHMARK] Rule Engine (1000 rules, 100 hits): {rule_time_ms:.2f} ms")
    print(
        f"[BENCHMARK] Dependency Engine (1000 nodes, deep traversal): {dep_time_ms:.2f} ms"
    )

    # Simple assert to ensure it actually ran
    assert len(r_rep.executed_rules) == 100
    assert (
        d_res_rep.metrics.resolved_nodes == 1000
    )  # since C_0 -> C_1 ... -> C_999 is a single chain, resolving any triggers the rest
