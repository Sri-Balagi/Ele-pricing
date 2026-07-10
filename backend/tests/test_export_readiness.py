import pytest
from app.models.domain import (
    Configuration, 
    ConfigurationStatus,
    QuoteMetadata,
    QuoteStatus,
    ExportContext,
    ExportFormat,
    ExportMetadata
)
from app.services.configuration_pipeline import ConfigurationPipeline

def test_configuration_serialization_roundtrip():
    config = Configuration(
        configuration_id="CFG-123",
        status=ConfigurationStatus.PRICED,
        selected_category="TYPE_A",
        selected_feature_options=["OPT-1"]
    )
    # Serialize
    dumped = config.model_dump(mode='json')
    # Deserialize
    restored = Configuration.model_validate(dumped)
    
    assert config == restored
    assert config.configuration_id == restored.configuration_id
    assert config.status == restored.status

def test_exporter_readiness():
    config = Configuration(
        configuration_id="CFG-123",
        status=ConfigurationStatus.PRICED,
        quote_metadata=QuoteMetadata(
            quote_number="QT-100",
            valid_until="2026-12-31T00:00:00Z",
            status=QuoteStatus.DRAFT
        )
    )
    # We pretend pipeline priced it, so let's attach mock PricingSummary and BOM
    from app.models.domain import PricingSummary, BillOfMaterials
    config.pricing_summary = PricingSummary(
        currency="EUR", base_price=1000, subtotal_before_tax=1000, tax_amount=200, total_after_tax=1200,
        taxes=200, total=1200
    )
    config.bill_of_materials = BillOfMaterials(total_components=0, items=[])
    
    # Export Metadata isn't strictly on the config, it's on ExportReport, but let's just serialize config
    dumped = config.model_dump(mode='json')
    
    assert "pricing_summary" in dumped
    assert "bill_of_materials" in dumped
    assert "quote_metadata" in dumped
    assert dumped["quote_metadata"]["quote_number"] == "QT-100"

def test_configuration_immutability():
    config = Configuration(
        configuration_id="CFG-123",
        status=ConfigurationStatus.PRICED
    )
    context = ExportContext(
        configuration=config,
        correlation_id="PIPE-111",
        execution_timestamp="2026-01-01T00:00:00Z",
        export_format=ExportFormat.JSON
    )
    
    # Asserting that context construction did not mutate the config
    assert context.configuration.status == ConfigurationStatus.PRICED
    assert context.configuration.configuration_id == "CFG-123"

def test_pipeline_repeatability(client):
    pipeline = client.app.state.pipeline
    
    config_1 = Configuration(configuration_id="CFG-1", selected_category="TYPE_B")
    report_1 = pipeline.execute(config_1)
    
    config_2 = Configuration(configuration_id="CFG-1", selected_category="TYPE_B")
    report_2 = pipeline.execute(config_2)
    
    # Output should be identical
    assert report_1.final_configuration_status == report_2.final_configuration_status
    if config_1.pricing_summary:
        assert config_1.pricing_summary.total_after_tax == config_2.pricing_summary.total_after_tax
    if config_1.bill_of_materials:
        assert config_1.bill_of_materials.total_components == config_2.bill_of_materials.total_components

def test_response_headers_are_present(client):
    response = client.get("/api/v1/health")
    if response.status_code == 404:
        response = client.get("/health")
    assert response.status_code == 200
    assert "X-Correlation-ID" in response.headers
    assert "X-API-Version" in response.headers
    assert "X-Process-Time" in response.headers
    assert response.headers["X-API-Version"] == "v1"
