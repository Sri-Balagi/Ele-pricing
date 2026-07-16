from app.models.domain import (
    Configuration,
    ConfigurationMutation,
    ConfigurationStatus,
    DependencyResolutionMetrics,
    DependencyResolutionReport,
    ExecutionReport,
    RuleMetrics,
)


def test_configuration_snapshot():
    config = Configuration(
        configuration_id="CFG-100",
        customer_reference="CRM-555",
        status=ConfigurationStatus.DRAFT,
        selected_feature_options=["OPT_1"],
        resolved_components=["COMP_A"],
        mutations=[
            ConfigurationMutation(
                source_engine="DEPENDENCY_ENGINE",
                entity_id="COMP_A",
                mutation_type="ADDED",
                reason="Required by OPT_1",
                timestamp="2026-07-08T00:00:00Z",
            )
        ],
    )

    # Dump to dict (which is equivalent to JSON in API)
    data = config.model_dump(mode="json")

    assert data["configuration_id"] == "CFG-100"
    assert data["customer_reference"] == "CRM-555"
    assert data["status"] == "DRAFT"
    assert data["selected_feature_options"] == ["OPT_1"]
    assert data["resolved_components"] == ["COMP_A"]

    # Ensure keys are present for backward compatibility
    expected_keys = {
        "configuration_id",
        "project_name",
        "customer_name",
        "customer_reference",
        "created_at",
        "expires_at",
        "selected_category",
        "selected_feature_options",
        "resolved_components",
        "validation_results",
        "rule_results",
        "mutations",
        "bill_of_materials",
        "pricing_summary",
        "quote_metadata",
        "status",
    }
    assert set(data.keys()) == expected_keys


def test_dependency_report_snapshot():
    report = DependencyResolutionReport(
        configuration_id="CFG-100",
        metrics=DependencyResolutionMetrics(
            total_nodes=10, active_nodes=5, execution_time_ms=1.5
        ),
    )
    data = report.model_dump(mode="json")

    expected_keys = {
        "configuration_id",
        "metrics",
        "components_added",
        "options_added",
        "conflicts",
        "warnings",
        "cycles_detected",
        "execution_order",
        "summary",
    }
    assert set(data.keys()) == expected_keys
    assert data["metrics"]["total_nodes"] == 10


def test_rule_report_snapshot():
    report = ExecutionReport(
        configuration_id="CFG-100",
        trigger="ON_SELECTION",
        metrics=RuleMetrics(rules_loaded=5, rules_executed=2),
        summary="Test summary",
    )
    data = report.model_dump(mode="json")

    expected_keys = {
        "configuration_id",
        "trigger",
        "executed_rules",
        "skipped_rules",
        "failed_rules",
        "execution_time_ms",
        "summary",
        "metrics",
    }
    assert set(data.keys()) == expected_keys
    assert data["metrics"]["rules_loaded"] == 5
