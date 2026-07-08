"""
Centralized exception hierarchy for the Elevator Configuration Engine.

Design principles:
  - Every application exception inherits from ElevatorBaseException.
  - Each domain owns a subtree (Data, Configuration, Rule, Dependency, Pricing).
  - Exceptions carry both a human message and a machine-readable error_code.
  - http_status on each class tells the global exception handler which HTTP
    status code to use, without scattering that knowledge across routes.
  - FastAPI exception handlers (registered in app/__init__.py) map these to
    structured ErrorResponse payloads — raw Python exceptions never reach clients.
"""


class ElevatorBaseException(Exception):
    """Root exception for all application-specific errors."""

    error_code: str = "ELEVATOR_ERROR"
    http_status: int = 500

    def __init__(self, message: str, details: object = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"error_code={self.error_code!r}, "
            f"message={self.message!r})"
        )


# ── Data Exceptions ───────────────────────────────────────────────────────────
class DataException(ElevatorBaseException):
    """Base for all data-access errors."""

    error_code = "DATA_ERROR"
    http_status = 500


class DataFileNotFoundException(DataException):
    """A required JSON data file is missing from DATA_DIR."""

    error_code = "DATA_FILE_NOT_FOUND"
    http_status = 500


class DataLoadException(DataException):
    """A data file exists but cannot be read (I/O error, permissions, etc.)."""

    error_code = "DATA_LOAD_FAILED"
    http_status = 500


class DataFormatException(DataException):
    """A data file exists but contains malformed JSON."""

    error_code = "DATA_FORMAT_INVALID"
    http_status = 500


# ── Configuration Exceptions ──────────────────────────────────────────────────
class ConfigurationException(ElevatorBaseException):
    """Base for elevator configuration errors."""

    error_code = "CONFIGURATION_ERROR"
    http_status = 400


class InvalidComponentException(ConfigurationException):
    """A referenced component ID does not exist in the component catalogue."""

    error_code = "INVALID_COMPONENT"
    http_status = 422


class IncompatibleFeaturesException(ConfigurationException):
    """Two or more selected features cannot coexist in a valid configuration."""

    error_code = "INCOMPATIBLE_FEATURES"
    http_status = 422


# ── Rule Engine Exceptions ────────────────────────────────────────────────────
class RuleEngineException(ElevatorBaseException):
    """Base for rule-engine errors."""

    error_code = "RULE_ENGINE_ERROR"
    http_status = 500


class RuleLoadException(RuleEngineException):
    """Rules could not be loaded from the data source."""

    error_code = "RULE_LOAD_FAILED"
    http_status = 500


class RuleEvaluationException(RuleEngineException):
    """A rule produced an error during evaluation."""

    error_code = "RULE_EVALUATION_FAILED"
    http_status = 422


# ── Dependency Exceptions ─────────────────────────────────────────────────────
class DependencyException(ElevatorBaseException):
    """Base for component-dependency resolution errors."""

    error_code = "DEPENDENCY_ERROR"
    http_status = 422


class CircularDependencyException(DependencyException):
    """A circular dependency chain was detected between components."""

    error_code = "CIRCULAR_DEPENDENCY"
    http_status = 422


class MissingDependencyException(DependencyException):
    """A required dependency component is absent from the configuration."""

    error_code = "MISSING_DEPENDENCY"
    http_status = 422


# ── Validation Exceptions ─────────────────────────────────────────────────────
class ValidationException(ElevatorBaseException):
    """Base for input-validation errors."""

    error_code = "VALIDATION_ERROR"
    http_status = 422


class SchemaValidationException(ValidationException):
    """A request or data payload does not conform to its expected schema."""

    error_code = "SCHEMA_VALIDATION_FAILED"
    http_status = 422


# ── Pricing Exceptions ────────────────────────────────────────────────────────
class PricingException(ElevatorBaseException):
    """Base for pricing-calculation errors."""

    error_code = "PRICING_ERROR"
    http_status = 500


class PricingComponentNotFoundException(PricingException):
    """No price entry exists for the requested component."""

    error_code = "PRICING_COMPONENT_NOT_FOUND"
    http_status = 404


class PricingCalculationException(PricingException):
    """An error occurred during price calculation."""

    error_code = "PRICING_CALCULATION_FAILED"
    http_status = 500


# ── Pipeline Exceptions ───────────────────────────────────────────────────────
class PipelineError(ElevatorBaseException):
    """Base for pipeline orchestration errors."""

    error_code = "PIPELINE_ERROR"
    http_status = 500


class StartupValidationError(PipelineError):
    """One or more engines failed startup validation."""

    error_code = "STARTUP_VALIDATION_FAILED"
    http_status = 500


class PipelineExecutionError(PipelineError):
    """An unrecoverable error occurred during pipeline execution."""

    error_code = "PIPELINE_EXECUTION_FAILED"
    http_status = 500
