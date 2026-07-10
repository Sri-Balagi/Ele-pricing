import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta

from app.models.domain import Configuration, QuoteMetadata, QuoteStatus


class BaseQuoteNumberGenerator(ABC):
    """Strategy interface for generating quote numbers."""

    @abstractmethod
    def generate(self, configuration: Configuration) -> str:
        pass


class DefaultQuoteNumberGenerator(BaseQuoteNumberGenerator):
    """Default implementation for quote numbers (e.g., QT-YYYYMMDD-UUID)."""

    def generate(self, configuration: Configuration) -> str:
        date_part = datetime.now(UTC).strftime("%Y%m%d")
        short_uuid = uuid.uuid4().hex[:6].upper()
        return f"QT-{date_part}-{short_uuid}"


import hashlib


class QuoteGenerator:
    """
    Service responsible for managing the Quote lifecycle.
    Executes after the Pricing Engine.
    """

    def __init__(self, number_generator: BaseQuoteNumberGenerator = None):
        self.number_generator = number_generator or DefaultQuoteNumberGenerator()

    def generate(self, configuration: Configuration) -> None:
        """
        Attaches or updates QuoteMetadata on the finalized configuration.
        Revision Policy: Increments ONLY when pipeline re-runs (feature/engineering/pricing changes).
        """
        now_str = datetime.now(UTC).isoformat()
        valid_until_str = (datetime.now(UTC) + timedelta(days=30)).isoformat()

        if configuration.quote_metadata is None:
            # First time generating a quote
            quote_number = self.number_generator.generate(configuration)
            configuration.quote_metadata = QuoteMetadata(
                quote_number=quote_number,
                quote_version=1,
                valid_until=valid_until_str,
                status=QuoteStatus.DRAFT,
            )
        else:
            # Re-running the pipeline means something changed (pricing, features, dependencies)
            # Therefore, we increment the revision.
            # We preserve the original quote number and status (unless it was APPROVED, we might need to reset it,
            # but for now we just increment version).
            configuration.quote_metadata.quote_version += 1
            configuration.quote_metadata.valid_until = valid_until_str
            # Status remains unchanged unless we want to reset APPROVED to DRAFT on modifications.
            if configuration.quote_metadata.status == QuoteStatus.APPROVED:
                configuration.quote_metadata.status = QuoteStatus.DRAFT

        # Generate fingerprint (deterministic)
        configuration.quote_metadata.quote_hash = self._generate_fingerprint(
            configuration
        )

    def _generate_fingerprint(self, configuration: Configuration) -> str:
        """Generates a deterministic SHA-256 fingerprint of the quote components."""
        components = [
            f"config_id:{configuration.configuration_id}",
            f"status:{configuration.status.value}",
            f"quote_number:{configuration.quote_metadata.quote_number}",
            f"quote_version:{configuration.quote_metadata.quote_version}",
        ]
        if configuration.pricing_summary:
            components.append(
                f"total:{float(configuration.pricing_summary.total_after_tax)}"
            )
        if configuration.bill_of_materials:
            components.append(
                f"bom_size:{configuration.bill_of_materials.total_components}"
            )

        raw_string = "|".join(components)
        return hashlib.sha256(raw_string.encode("utf-8")).hexdigest()
