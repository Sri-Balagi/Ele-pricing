from app.models.domain import ProductCatalogue
from app.services.bom_generator import BOMGenerator


def test_bom_generator_basic(sample_configuration):
    catalogue = ProductCatalogue(
        metadata={
            "catalogue_version": "1.0",
            "schema_version": "1.0",
            "created_date": "2026",
            "last_updated": "2026",
            "prototype_version": "1.0",
            "supported_schema_versions": ["1.0"],
        },
        categories=[],
        feature_groups=[],
        features=[],
        components=[],
        feature_options=[],
        mappings=[],
        dependencies=[],
        pricing={
            "catalogue_version": "1.0",
            "currency": "USD",
            "tax_configuration": {"enabled": False, "rate": 0.0},
            "pricing_records": [],
        },
    )
    bom_gen = BOMGenerator(catalogue)

    sample_configuration.resolved_components = ["C-MOT-100", "C-CAB-BAS"]
    sample_configuration.selected_feature_options = ["OPT-MOT-100", "OPT-CAB-BAS"]

    bom = bom_gen.generate(sample_configuration)

    assert bom is not None
    assert len(bom.items) == 2
    assert bom.total_components >= 2

    # Pricing info must NOT be populated by BOM Generator
    for item in bom.items:
        assert item.unit_cost is None
        assert item.pricing_record_id is None
