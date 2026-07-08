import pytest
import time
from decimal import Decimal

from app.models.domain import (
    Configuration, ConfigurationStatus, ProductCatalogue, CatalogMetadata, 
    PricingCatalogue, PricingRecord, TaxConfiguration, BillOfMaterials, BOMItem
)
from app.pricing_engine.context import PricingContext
from app.pricing_engine.registry import PricingRegistry
from app.pricing_engine.engine import PricingEngine
from app.pricing_engine.validator import PricingValidator
from app.pricing_engine.repository import PricingRepository

class MockRepo(PricingRepository):
    def __init__(self, data):
        self._data = data
    def get_all(self):
        return self._data
    def exists(self, entity_id: str) -> bool:
        return True
    def get_by_id(self, entity_id: str):
        return None


def run_benchmark_for_n_components(n: int):
    # Setup catalogue with 1 category and N components
    pricing_records = [PricingRecord(entity_id="CAT_A", entity_type="CATEGORY", price=Decimal("1000"))]
    resolved_components = []
    bom_items = []
    for i in range(n):
        comp_id = f"COMP_{i}"
        pricing_records.append(PricingRecord(entity_id=comp_id, entity_type="COMPONENT", price=Decimal("10.00")))
        resolved_components.append(comp_id)
        bom_items.append(BOMItem(component_id=comp_id, quantity=1))
        
    pricing_cat = PricingCatalogue(
        catalogue_version="1.0",
        currency="USD",
        tax_configuration=TaxConfiguration(enabled=True, tax_name="VAT", rate=Decimal("10.0")),
        pricing_records=pricing_records
    )
    product_cat = ProductCatalogue(
        metadata=CatalogMetadata(
            catalogue_version="1.0", schema_version="1.0",
            created_date="2026-07-08T00:00:00Z",
            last_updated="2026-07-08T00:00:00Z",
            prototype_version="1.0",
        ),
        categories=[], feature_groups=[], features=[], feature_options=[],
        components=[], mappings=[], dependencies=[],
        pricing=pricing_cat
    )
    
    registry = PricingRegistry(MockRepo(product_cat.pricing), PricingValidator())
    registry.load_and_validate()
    
    config = Configuration(
        configuration_id=f"CFG-BENCH-{n}",
        selected_category="CAT_A",
        resolved_components=resolved_components,
        status=ConfigurationStatus.VALIDATED,
        bill_of_materials=BillOfMaterials(items=bom_items)
    )
    context = PricingContext(
        configuration=config,
        catalogue=product_cat,
        pricing_registry=registry,
        correlation_id=f"bench-{n}",
        execution_timestamp="2026-07-08T12:00:00Z"
    )
    
    engine = PricingEngine()
    
    t0 = time.perf_counter()
    report = engine.resolve(context)
    t1 = time.perf_counter()
    
    assert len(report.errors) == 0
    return (t1 - t0) * 1000  # Return ms

def test_benchmark_100_components():
    ms = run_benchmark_for_n_components(100)
    print(f"\\n100 components priced in {ms:.2f} ms")

def test_benchmark_500_components():
    ms = run_benchmark_for_n_components(500)
    print(f"\\n500 components priced in {ms:.2f} ms")

def test_benchmark_1000_components():
    ms = run_benchmark_for_n_components(1000)
    print(f"\\n1000 components priced in {ms:.2f} ms")
