import pytest
from decimal import Decimal

from app.models.domain import (
    Configuration, ConfigurationStatus, ProductCatalogue, CatalogMetadata, 
    PricingCatalogue, PricingRecord, TaxConfiguration, BillOfMaterials, BOMItem
)
from app.pricing_engine.context import PricingContext
from app.pricing_engine.registry import PricingRegistry
from app.pricing_engine.engine import PricingEngine
from app.pricing_engine.calculator import PricingCalculationError
from app.pricing_engine.repository import PricingRepository
from app.pricing_engine.validator import PricingValidator

class MockRepo(PricingRepository):
    def __init__(self, data):
        self._data = data
    def get_all(self):
        return self._data
    def exists(self, entity_id: str) -> bool:
        return True
    def get_by_id(self, entity_id: str):
        return None

@pytest.fixture
def dummy_pricing_catalogue():
    return PricingCatalogue(
        catalogue_version="1.0",
        currency="USD",
        tax_configuration=TaxConfiguration(enabled=True, tax_name="VAT", rate=Decimal("10.0")),
        pricing_records=[
            PricingRecord(entity_id="CAT_A", entity_type="CATEGORY", base_cost=Decimal("1000.00"), markup_percentage=Decimal("0.0"), price=Decimal("1000.00")),
            PricingRecord(entity_id="OPT_1", entity_type="FEATURE_OPTION", base_cost=Decimal("50.00"), markup_percentage=Decimal("10.0"), price=Decimal("55.00")),
            PricingRecord(entity_id="COMP_1", entity_type="COMPONENT", base_cost=Decimal("200.00"), markup_percentage=Decimal("0.0"), price=Decimal("200.00")),
        ]
    )

@pytest.fixture
def dummy_product_catalogue(dummy_pricing_catalogue):
    return ProductCatalogue(
        metadata=CatalogMetadata(
            catalogue_version="1.0", schema_version="1.0",
            created_date="2026-07-08T00:00:00Z",
            last_updated="2026-07-08T00:00:00Z",
            prototype_version="1.0",
        ),
        categories=[], feature_groups=[], features=[], feature_options=[],
        components=[], mappings=[], dependencies=[],
        pricing=dummy_pricing_catalogue
    )

def test_pricing_engine_success(dummy_product_catalogue):
    registry = PricingRegistry(MockRepo(dummy_product_catalogue.pricing), PricingValidator())
    registry.load_and_validate()
    
    config = Configuration(
        configuration_id="CFG-PRICE-01",
        selected_category="CAT_A",
        selected_feature_options=["OPT_1"],
        resolved_components=["COMP_1"],
        status=ConfigurationStatus.VALIDATED,
        bill_of_materials=BillOfMaterials(items=[
            BOMItem(component_id="COMP_1", quantity=1)
        ])
    )
    
    context = PricingContext(
        configuration=config,
        catalogue=dummy_product_catalogue,
        pricing_registry=registry,
        correlation_id="test-1",
        execution_timestamp="2026-07-08T12:00:00Z"
    )
    
    engine = PricingEngine()
    report = engine.resolve(context)
    
    assert len(report.errors) == 0
    assert config.status == ConfigurationStatus.VALIDATED
    
    summary = config.pricing_summary
    assert summary is not None
    assert summary.currency == "USD"
    
    # 1000 + 55 + 200 = 1255.00
    assert summary.subtotal_before_tax == Decimal("1255.00")
    
    # Tax: 10% of 1255 = 125.50
    assert summary.tax_amount == Decimal("125.50")
    
    # Total: 1255 + 125.50 = 1380.50
    assert summary.total_after_tax == Decimal("1380.50")
    
    # Check aliases
    assert summary.taxes == Decimal("125.50")
    assert summary.total == Decimal("1380.50")
    
    # Check BOM
    assert config.bill_of_materials.items[0].unit_cost == Decimal("200.00")
    assert config.bill_of_materials.items[0].pricing_record_id == "COMP_1"

def test_pricing_engine_missing_price(dummy_product_catalogue):
    registry = PricingRegistry(MockRepo(dummy_product_catalogue.pricing), PricingValidator())
    registry.load_and_validate()
    
    config = Configuration(
        configuration_id="CFG-PRICE-02",
        selected_category="CAT_A",
        selected_feature_options=["OPT_MISSING"],
        resolved_components=["COMP_1"],
        status=ConfigurationStatus.VALIDATED
    )
    
    context = PricingContext(
        configuration=config,
        catalogue=dummy_product_catalogue,
        pricing_registry=registry,
        correlation_id="test-2",
        execution_timestamp="2026-07-08T12:00:00Z"
    )
    
    engine = PricingEngine()
    report = engine.resolve(context)
    
    assert len(report.errors) == 1
    assert "Missing pricing record for feature option: OPT_MISSING" in report.errors[0]
    
    # Ensure status was not transitioned
    assert config.status == ConfigurationStatus.VALIDATED
    assert config.pricing_summary is None

def test_tax_calculation_precision(dummy_product_catalogue):
    # Tax: 10% on 1000.55 = 100.055 -> 100.06 (ROUND_HALF_UP)
    dummy_product_catalogue.pricing.pricing_records[0].price = Decimal("1000.55")
    dummy_product_catalogue.pricing.pricing_records[1].price = Decimal("0.00")
    dummy_product_catalogue.pricing.pricing_records[2].price = Decimal("0.00")
    
    registry = PricingRegistry(MockRepo(dummy_product_catalogue.pricing), PricingValidator())
    registry.load_and_validate()
    
    config = Configuration(
        configuration_id="CFG-PRICE-03",
        selected_category="CAT_A",
        status=ConfigurationStatus.VALIDATED
    )
    
    context = PricingContext(
        configuration=config,
        catalogue=dummy_product_catalogue,
        pricing_registry=registry,
        correlation_id="test-3",
        execution_timestamp="2026-07-08T12:00:00Z"
    )
    
    engine = PricingEngine()
    engine.resolve(context)
    
    assert config.pricing_summary.subtotal_before_tax == Decimal("1000.55")
    assert config.pricing_summary.tax_amount == Decimal("100.06")
    assert config.pricing_summary.total_after_tax == Decimal("1100.61")
