import pytest
from app.services.quote_generator import QuoteGenerator, DefaultQuoteNumberGenerator
from app.models.domain import QuoteStatus

def test_quote_generation_initial(sample_configuration):
    generator = QuoteGenerator()
    assert sample_configuration.quote_metadata is None
    
    generator.generate(sample_configuration)
    
    assert sample_configuration.quote_metadata is not None
    assert sample_configuration.quote_metadata.quote_version == 1
    assert sample_configuration.quote_metadata.status == QuoteStatus.DRAFT
    assert sample_configuration.quote_metadata.quote_number.startswith("QT-")

def test_quote_generation_increment_revision(sample_configuration):
    generator = QuoteGenerator()
    
    # First generation
    generator.generate(sample_configuration)
    assert sample_configuration.quote_metadata.quote_version == 1
    
    # Second generation (simulating pipeline re-run)
    generator.generate(sample_configuration)
    assert sample_configuration.quote_metadata.quote_version == 2
