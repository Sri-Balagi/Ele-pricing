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

    REQUIRE = "REQUIRE"           # Force-add a component
    EXCLUDE = "EXCLUDE"           # Prevent a component from being selected
    SET_DEFAULT = "SET_DEFAULT"   # Apply a default value
    WARN = "WARN"                 # Emit a warning but allow the configuration
    BLOCK = "BLOCK"               # Hard-stop the configuration


# ── Component Lifecycle ───────────────────────────────────────────────────────
class ComponentStatus(StrEnum):
    ACTIVE = "active"               # Available for selection
    DEPRECATED = "deprecated"       # Available but flagged for removal
    DISCONTINUED = "discontinued"   # No longer orderable


# ── Dependency Relationship Types ─────────────────────────────────────────────
class DependencyType(StrEnum):
    REQUIRES = "REQUIRES"    # Component A requires Component B
    EXCLUDES = "EXCLUDES"    # Component A excludes Component B
    REPLACES = "REPLACES"    # Component A replaces Component B


# ── HTTP / Tracing ────────────────────────────────────────────────────────────
REQUEST_ID_HEADER: str = "X-Request-ID"
API_V1_TAG: str = "v1"

# ── Logging Format ────────────────────────────────────────────────────────────
LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
