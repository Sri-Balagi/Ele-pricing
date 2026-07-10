from app.core.exceptions import PricingException
from app.models.domain import PricingCatalogue


class PricingValidationError(PricingException):
    def __init__(self, message: str):
        super().__init__(message=message)


class PricingValidator:
    """
    Validates the structured pricing.json representation.
    Fails fast on duplicates or malformed records.
    """

    def validate(self, catalogue: PricingCatalogue) -> list[str]:
        """
        Validate pricing records. Returns a list of warnings if any,
        raises PricingValidationError for hard failures.
        """
        seen_ids = set()
        warnings = []

        if not catalogue.tax_configuration:
            raise PricingValidationError("Tax configuration is missing.")

        for record in catalogue.pricing_records:
            if not record.entity_id:
                raise PricingValidationError("Pricing record missing entity_id.")

            if record.entity_id in seen_ids:
                raise PricingValidationError(
                    f"Duplicate pricing record for entity: {record.entity_id}"
                )
            seen_ids.add(record.entity_id)

            if record.price < 0:
                raise PricingValidationError(
                    f"Negative price not allowed for {record.entity_id}."
                )

        return warnings
