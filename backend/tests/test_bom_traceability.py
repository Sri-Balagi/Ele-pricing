import pytest
from app.services.bom_generator import BOMGenerator
from app.models.domain import Configuration, BOMOrigin, ConfigurationMutation

from app.models.domain import ProductCatalogue

def test_bom_traceability(sample_configuration):
    catalogue = ProductCatalogue(metadata={"catalogue_version": "1.0", "schema_version": "1.0", "created_date": "2026", "last_updated": "2026", "prototype_version": "1.0", "supported_schema_versions": ["1.0"]}, categories=[], feature_groups=[], features=[], components=[], feature_options=[], mappings=[{"id": "M-1", "feature_option_id": "OPT-MOT-100", "component_id": "C-MOT-100", "quantity": 1, "active": True}], dependencies=[], pricing={"catalogue_version": "1.0", "currency": "USD", "tax_configuration": {"enabled": False, "rate": 0.0}, "pricing_records": []})
    bom_gen = BOMGenerator(catalogue)
    
    # Suppose we have three components added by different engines
    sample_configuration.resolved_components = ["C-MOT-100", "C-DEP-1", "C-RUL-1", "C-MAN-1"]
    sample_configuration.selected_feature_options = ["OPT-MOT-100"]
    
    sample_configuration.mutations = [
        ConfigurationMutation(timestamp="2026-07-08T00:00:00Z", source_engine="DEPENDENCY_ENGINE", entity_id="C-DEP-1", mutation_type="ADDED"),
        ConfigurationMutation(timestamp="2026-07-08T00:00:00Z", source_engine="RULE_ENGINE", entity_id="C-RUL-1", mutation_type="ADDED"),
        ConfigurationMutation(timestamp="2026-07-08T00:00:00Z", source_engine="MANUAL", entity_id="C-MAN-1", mutation_type="ADDED")
    ]
    
    bom = bom_gen.generate(sample_configuration)
    
    items = {item.component_id: item for item in bom.items}
    
    assert items["C-MOT-100"].origin_type == BOMOrigin.FEATURE
    assert items["C-DEP-1"].origin_type == BOMOrigin.DEPENDENCY
    assert items["C-RUL-1"].origin_type == BOMOrigin.RULE
    assert items["C-MAN-1"].origin_type == BOMOrigin.MANUAL
    
    # Reason checks
    assert items["C-MOT-100"].reason == "Feature Mapping"
    assert items["C-DEP-1"].reason == "Dependency Resolution"
    assert items["C-RUL-1"].reason == "Rule Engine"
    assert items["C-MAN-1"].reason == "Manual Override"
