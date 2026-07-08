import pytest
from app.services.quote_generator import QuoteGenerator

def test_quote_repeatability(sample_configuration):
    generator = QuoteGenerator()
    
    generator.generate(sample_configuration)
    original_number = sample_configuration.quote_metadata.quote_number
    
    # Running it again should increment version but keep the quote number the same
    generator.generate(sample_configuration)
    
    assert sample_configuration.quote_metadata.quote_number == original_number
    assert sample_configuration.quote_metadata.quote_version == 2
