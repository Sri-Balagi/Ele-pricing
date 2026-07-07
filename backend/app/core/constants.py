"""
Application-wide constants and enumerations.

Rules:
  - No magic strings anywhere else in the codebase.
  - Add new constants here; never inline them.
  - Use Enum for closed sets of values (type-safe, IDE-completable).
  - Use plain module-level constants for single values that don't need enumeration.
"""

from enum import StrEnum

# ── Application Metadata ──────────────────────────────────────────────────────
APP_NAME: str = "Elevator Configuration Engine"
APP_VERSION: str = "0.1.0"


# ── Elevator Categories ───────────────────────────────────────────────────────
class ElevatorType(StrEnum):
    """The three supported elevator categories for this prototype."""

    TYPE_A = "TYPE_A"  # Standard — fixed feature set
    TYPE_B = "TYPE_B"  # Configurable — mixed fixed + customizable features
    TYPE_C = "TYPE_C"  # Specialized — strict engineering constraints


# ── JSON Data File Names ──────────────────────────────────────────────────────
class DataFile(StrEnum):
    """Base filenames for all JSON data files, relative to DATA_DIR."""

    COMPONENTS = "components.json"
    FEATURES = "features.json"
    DEPENDENCIES = "dependencies.json"
    RULES = "rules.json"
    PRICING = "pricing.json"
    CATEGORIES = "categories.json"
    CATALOG_METADATA = "catalog_metadata.json"
    FEATURE_MAPPINGS = "feature_mappings.json"
    FEATURE_GROUPS = "feature_groups.json"
    FEATURE_OPTIONS = "feature_options.json"


# ── Runtime Environments ──────────────────────────────────────────────────────
class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


# ── Application Health ────────────────────────────────────────────────────────
class HealthStatus(StrEnum):
    HEALTHY = "healthy"       # All systems nominal
    DEGRADED = "degraded"     # Running but with partial data issues
    UNHEALTHY = "unhealthy"   # Critical failure, cannot serve requests


# ── Rule Engine ───────────────────────────────────────────────────────────────
class RuleAction(StrEnum):
    """Actions a rule can trigger during configuration evaluation."""
    ADD_COMPONENT = "ADD_COMPONENT"
    REMOVE_COMPONENT = "REMOVE_COMPONENT"
    REQUIRE_OPTION = "REQUIRE_OPTION"
    EXCLUDE_OPTION = "EXCLUDE_OPTION"
    SET_PRICE_MULTIPLIER = "SET_PRICE_MULTIPLIER"
    ABORT_VALIDATION = "ABORT_VALIDATION"


class RuleTriggerType(StrEnum):
    ON_SELECTION = "ON_SELECTION"
    ON_CHANGE = "ON_CHANGE"
    ON_VALIDATION = "ON_VALIDATION"
    ON_PRICING = "ON_PRICING"
    ON_EXPORT = "ON_EXPORT"


class RuleSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ConfigurationStatus(StrEnum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    PRICED = "PRICED"
    APPROVED = "APPROVED"
    EXPORTED = "EXPORTED"


# ── Component Lifecycle ───────────────────────────────────────────────────────
class ComponentStatus(StrEnum):
    ACTIVE = "active"               # Available for selection
    DEPRECATED = "deprecated"       # Available but flagged for removal
    DISCONTINUED = "discontinued"   # No longer orderable


class DependencyType(StrEnum):
    REQUIRES = "REQUIRES"
    EXCLUDES = "EXCLUDES"
    RECOMMENDS = "RECOMMENDS"
    DETERMINES = "DETERMINES"


class DependencyCategory(StrEnum):
    MECHANICAL = "MECHANICAL"
    ELECTRICAL = "ELECTRICAL"
    STRUCTURAL = "STRUCTURAL"
    SAFETY = "SAFETY"
    BUSINESS = "BUSINESS"

# ── Engineering Standardization ───────────────────────────────────────────────
class ComponentCategory(StrEnum):
    STRUCTURAL = "Structural"
    MECHANICAL = "Mechanical"
    ELECTRICAL = "Electrical"
    CONTROL = "Control"
    SAFETY = "Safety"
    CABIN = "Cabin"
    DOOR = "Door"

class Unit(StrEnum):
    PCS = "pcs"
    MM = "mm"
    KG = "kg"
    KW = "kW"
    M_S = "m/s"


# ── HTTP / Tracing ────────────────────────────────────────────────────────────
REQUEST_ID_HEADER: str = "X-Request-ID"
API_V1_TAG: str = "v1"

# ── Logging Format ────────────────────────────────────────────────────────────
LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
