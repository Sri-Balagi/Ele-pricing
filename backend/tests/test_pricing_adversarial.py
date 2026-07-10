from decimal import Decimal

import pytest

from app.models.domain import (
    BillOfMaterials,
    BOMItem,
    CatalogMetadata,
    Configuration,
    ConfigurationStatus,
    PricingCatalogue,
    PricingRecord,
    ProductCatalogue,
    TaxConfiguration,
)
from app.pricing_engine.context import PricingContext
from app.pricing_engine.engine import PricingEngine
from app.pricing_engine.registry import PricingRegistry
from app.pricing_engine.repository import PricingRepository
from app.pricing_engine.validator import PricingValidationError, PricingValidator


class MockRepo(PricingRepository):
    def __init__(self, data):
        self._data = data

    def get_all(self):
        return self._data

    def exists(self, entity_id: str) -> bool:
        return True

    def get_by_id(self, entity_id: str):
        return None


def test_missing_tax_configuration_fails_fast():
    catalogue = PricingCatalogue.model_construct(
        catalogue_version="1.0",
        currency="USD",
        tax_configuration=None,  # type: ignore
        pricing_records=[],
    )
    validator = PricingValidator()
    with pytest.raises(PricingValidationError) as exc:
        validator.validate(catalogue)
    assert "Tax configuration is missing" in str(exc.value)


def test_duplicate_pricing_records_fail_fast():
    catalogue = PricingCatalogue(
        catalogue_version="1.0",
        currency="USD",
        tax_configuration=TaxConfiguration(
            enabled=True, tax_name="VAT", rate=Decimal("10.0")
        ),
        pricing_records=[
            PricingRecord(
                entity_id="COMP_1", entity_type="COMPONENT", price=Decimal("100")
            ),
            PricingRecord(
                entity_id="COMP_1", entity_type="COMPONENT", price=Decimal("150")
            ),
        ],
    )
    validator = PricingValidator()
    with pytest.raises(PricingValidationError) as exc:
        validator.validate(catalogue)
    assert "Duplicate pricing record" in str(exc.value)


def test_negative_price_fails_fast():
    catalogue = PricingCatalogue(
        catalogue_version="1.0",
        currency="USD",
        tax_configuration=TaxConfiguration(
            enabled=True, tax_name="VAT", rate=Decimal("10.0")
        ),
        pricing_records=[
            PricingRecord(
                entity_id="COMP_1", entity_type="COMPONENT", price=Decimal("-10.0")
            ),
        ],
    )
    validator = PricingValidator()
    with pytest.raises(PricingValidationError) as exc:
        validator.validate(catalogue)
    assert "Negative price not allowed" in str(exc.value)


def test_bom_unit_cost_sum_equals_component_cost():
    # Setup catalogue
    pricing_cat = PricingCatalogue(
        catalogue_version="1.0",
        currency="USD",
        tax_configuration=TaxConfiguration(
            enabled=True, tax_name="VAT", rate=Decimal("10.0")
        ),
        pricing_records=[
            PricingRecord(
                entity_id="CAT_A", entity_type="CATEGORY", price=Decimal("1000")
            ),
            PricingRecord(
                entity_id="COMP_1", entity_type="COMPONENT", price=Decimal("100.55")
            ),
            PricingRecord(
                entity_id="COMP_2", entity_type="COMPONENT", price=Decimal("200.45")
            ),
        ],
    )
    product_cat = ProductCatalogue(
        metadata=CatalogMetadata(
            catalogue_version="1.0",
            schema_version="1.0",
            created_date="2026-07-08T00:00:00Z",
            last_updated="2026-07-08T00:00:00Z",
            prototype_version="1.0",
        ),
        categories=[],
        feature_groups=[],
        features=[],
        feature_options=[],
        components=[],
        mappings=[],
        dependencies=[],
        pricing=pricing_cat,
    )

    registry = PricingRegistry(MockRepo(product_cat.pricing), PricingValidator())
    registry.load_and_validate()

    config = Configuration(
        configuration_id="CFG-BOM-1",
        selected_category="CAT_A",
        resolved_components=["COMP_1", "COMP_2"],
        status=ConfigurationStatus.VALIDATED,
        bill_of_materials=BillOfMaterials(
            items=[
                BOMItem(component_id="COMP_1", quantity=1),
                BOMItem(component_id="COMP_2", quantity=1),
            ]
        ),
    )
    context = PricingContext(
        configuration=config,
        catalogue=product_cat,
        pricing_registry=registry,
        correlation_id="test-bom-1",
        execution_timestamp="2026-07-08T12:00:00Z",
    )

    engine = PricingEngine()
    engine.resolve(context)

    # Assert BOM cost sum equals the component cost calculated by the engine
    sum_bom = sum(
        item.unit_cost
        for item in config.bill_of_materials.items
        if item.unit_cost is not None
    )
    assert sum_bom == config.pricing_summary.component_cost
    assert sum_bom == Decimal("301.00")
