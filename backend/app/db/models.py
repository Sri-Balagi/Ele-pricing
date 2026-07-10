"""ORM models for persistent configuration storage."""

from sqlalchemy import Column, Float, Integer, String, Text

from app.db.database import Base


class ConfigurationRecord(Base):
    __tablename__ = "configurations"

    # Immutable internal PK — used for sequential display IDs
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Business key
    configuration_id = Column(String, unique=True, nullable=False, index=True)

    # Customer-visible fields (indexed for search)
    project_name = Column(String, nullable=False, default="", index=True)
    status = Column(String, nullable=False, default="CONFIGURED", index=True)
    selected_category = Column(String, nullable=False, default="")

    # Pricing summary (null until priced)
    pricing_total = Column(Float, nullable=True)

    # Full serialised Configuration domain object
    data = Column(Text, nullable=False)

    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)
