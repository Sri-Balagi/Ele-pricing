"""
Product Domain Models.

These Pydantic models represent the complete digital representation of the
elevator product catalogue. They ensure strong typing, validation, and provide
a stable foundation for the configuration, rule, and pricing engines.
"""

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.core.constants import (
    ComponentCategory,
    DependencyType,
    Unit,
    RuleTriggerType,
    RuleSeverity,
    RuleAction,
    ConfigurationStatus,
)


class CatalogMetadata(BaseModel):
    """Tracks versioning, schema compatibility, and update timestamps."""

    catalogue_version: str = Field(
        ..., description="Semantic version of the catalogue data"
    )
    schema_version: str = Field(..., description="Version of the schema format")
    created_date: str = Field(..., description="ISO8601 creation date")
    last_updated: str = Field(..., description="ISO8601 last update date")
    prototype_version: str = Field(..., description="Target prototype version")
    supported_schema_versions: list[str] = Field(
        default_factory=list, description="List of supported schemas"
    )
    migration_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Metadata for migrations"
    )


class ElevatorCategory(BaseModel):
    """Defines the high-level product lines (e.g., Type A, Type B, Type C)."""

    id: str = Field(..., description="Unique identifier (e.g., CAT-A)")
    name: str = Field(..., description="Display name of the category")
    description: str = Field(..., description="Detailed description")
    active: bool = Field(default=True, description="Whether this category is orderable")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary frontend/business metadata"
    )


class FeatureGroup(BaseModel):
    """Logically organizes features for UI and maintainability."""

    id: str = Field(..., description="Unique identifier (e.g., GRP-CABIN)")
    name: str = Field(..., description="Display name of the group")
    description: str = Field(..., description="Detailed description")
    display_order: int = Field(default=0, description="Sorting order for UI")
    active: bool = Field(default=True, description="Whether this group is visible")


class Feature(BaseModel):
    """A configurable property of an elevator (e.g., Capacity, Door Type)."""

    id: str = Field(..., description="Unique identifier (e.g., FEAT-CAP)")
    name: str = Field(..., description="Display name of the feature")
    description: str = Field(..., description="Detailed description")
    category_id: str = Field(..., description="Foreign key to ElevatorCategory")
    group_id: str = Field(..., description="Foreign key to FeatureGroup")
    required: bool = Field(default=True, description="Must the user select an option?")
    configurable: bool = Field(default=True, description="Can the user change this?")
    active: bool = Field(default=True, description="Available for selection")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary metadata"
    )


class FeatureOption(BaseModel):
    """A specific, selectable value for a Feature (e.g., '1000kg' for Capacity)."""

    id: str = Field(..., description="Unique identifier (e.g., OPT-CAP-1000)")
    feature_id: str = Field(..., description="Foreign key to Feature")
    display_name: str = Field(..., description="User-facing display value")
    internal_value: Any = Field(..., description="Internal engineering/logic value")
    description: str = Field(default="", description="Detailed description")
    active: bool = Field(default=True, description="Available for selection")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary metadata"
    )


class Component(BaseModel):
    """A physical engineering part required to build the elevator."""

    id: str = Field(..., description="Unique identifier (e.g., COMP-MOT-01)")
    name: str = Field(..., description="Display name of the component")
    description: str = Field(default="", description="Detailed description")
    category: ComponentCategory = Field(
        ..., description="Standardized engineering category"
    )
    manufacturer: str = Field(default="Generic", description="Supplier or manufacturer")
    unit: Unit = Field(..., description="Unit of measure")
    specifications: dict[str, Any] = Field(
        default_factory=dict, description="Physical/electrical properties"
    )
    active: bool = Field(default=True, description="Available for BOM inclusion")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary metadata"
    )


class FeatureComponentMapping(BaseModel):
    """Bridges commercial choices (Feature Options) with engineering reality (Components)."""

    id: str = Field(..., description="Unique identifier (e.g., MAP-CAP1000-MOT)")
    feature_option_id: str = Field(..., description="Foreign key to FeatureOption")
    component_id: str = Field(..., description="Foreign key to Component")
    quantity: int = Field(default=1, description="Number of components added")
    action: str = Field(default="ADD", description="Action: ADD, REMOVE, REPLACE")
    active: bool = Field(default=True, description="Whether this mapping is active")


class Dependency(BaseModel):
    """Represents an engineering relationship or constraint between entities."""

    id: str = Field(..., description="Unique identifier (e.g., DEP-MOT-CTRL)")
    source_id: str = Field(
        ..., description="Source entity ID (FeatureOption or Component)"
    )
    target_id: str = Field(
        ..., description="Target entity ID (FeatureOption or Component)"
    )
    dependency_type: DependencyType = Field(
        ..., description="Nature of the relationship"
    )
    description: str = Field(default="", description="Human-readable explanation")
    priority: int = Field(default=100, description="Execution priority for rule engine")
    condition_expression: str | None = Field(
        default=None, description="Future evaluation expression"
    )


class ProductCatalogue(BaseModel):
    """The aggregate root containing the entire domain catalogue."""

    metadata: CatalogMetadata
    categories: list[ElevatorCategory]
    feature_groups: list[FeatureGroup]
    features: list[Feature]
    feature_options: list[FeatureOption]
    components: list[Component]
    mappings: list[FeatureComponentMapping]
    dependencies: list[Dependency]


class Rule(BaseModel):
    """A business or engineering rule evaluated during configuration."""

    id: str = Field(..., description="Unique identifier (e.g., RULE-SPD-BUF)")
    name: str = Field(..., description="Short descriptive name")
    description: str = Field(default="", description="Detailed explanation")
    priority: int = Field(default=100, description="Execution priority (lower runs first)")
    enabled: bool = Field(default=True, description="Whether the rule is active")
    trigger_type: RuleTriggerType = Field(..., description="When this rule should evaluate")
    condition: str = Field(..., description="Condition expression (e.g., JSONLogic)")
    action: RuleAction = Field(..., description="Action to take if condition is met")
    action_payload: dict[str, Any] = Field(default_factory=dict, description="Data for the action")
    severity: RuleSeverity = Field(default=RuleSeverity.WARNING, description="Severity if action fails or warns")
    stop_processing: bool = Field(default=False, description="Halt further rules if triggered")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")


class RuleResult(BaseModel):
    """The outcome of evaluating a single rule."""

    rule_id: str = Field(..., description="The ID of the rule evaluated")
    triggered: bool = Field(..., description="Whether the rule condition was met")
    action_taken: str | None = Field(default=None, description="The action that was executed")
    message: str | None = Field(default=None, description="Human readable message from execution")


class ValidationMessage(BaseModel):
    """A single validation error, warning, or info message."""

    severity: RuleSeverity = Field(..., description="Severity of the message")
    code: str = Field(..., description="Standardized error/warning code")
    message: str = Field(..., description="Human readable explanation")
    source_entity_id: str | None = Field(default=None, description="Entity causing the validation message")


class ValidationResult(BaseModel):
    """The complete result of a validation pass."""

    is_valid: bool = Field(..., description="True if no ERROR or CRITICAL messages exist")
    errors: list[ValidationMessage] = Field(default_factory=list)
    warnings: list[ValidationMessage] = Field(default_factory=list)
    info: list[ValidationMessage] = Field(default_factory=list)


class BOMItem(BaseModel):
    """A line item in the generated Bill of Materials."""

    component_id: str = Field(..., description="The physical component ID")
    quantity: int = Field(default=1, description="Quantity required")
    source_feature_option_id: str | None = Field(default=None, description="The feature choice that triggered this")
    reason: str = Field(default="", description="Explanation of why this is included")


class BillOfMaterials(BaseModel):
    """The complete list of components required to build the configuration."""

    items: list[BOMItem] = Field(default_factory=list)
    total_components: int = Field(default=0, description="Total count of components")


class PriceAdjustment(BaseModel):
    """A modification to the final price (discount, markup, surcharge)."""

    name: str = Field(..., description="Name of the adjustment (e.g., 'Summer Discount')")
    amount: Decimal = Field(..., description="The adjustment value")
    is_percentage: bool = Field(default=False, description="True if amount is a percentage")
    reason: str = Field(default="", description="Explanation for the adjustment")


class PricingSummary(BaseModel):
    """The structured cost breakdown of a configuration."""

    base_price: Decimal = Field(default=Decimal("0.00"), description="Base category price")
    component_costs: Decimal = Field(default=Decimal("0.00"), description="Sum of physical component costs")
    feature_costs: Decimal = Field(default=Decimal("0.00"), description="Sum of feature option upcharges")
    adjustments: list[PriceAdjustment] = Field(default_factory=list, description="Discounts and markups")
    taxes: Decimal = Field(default=Decimal("0.00"), description="Calculated taxes")
    total: Decimal = Field(default=Decimal("0.00"), description="Final total price to quote")


class Configuration(BaseModel):
    """The core aggregate root representing a customer's specific elevator configuration."""

    configuration_id: str = Field(..., description="Unique ID for this configuration session")
    selected_category: str | None = Field(default=None, description="The chosen ElevatorCategory ID")
    selected_feature_options: list[str] = Field(default_factory=list, description="IDs of selected FeatureOptions")
    resolved_components: list[str] = Field(default_factory=list, description="IDs of explicitly resolved Components")
    validation_results: ValidationResult | None = Field(default=None, description="Results of the last validation run")
    rule_results: list[RuleResult] = Field(default_factory=list, description="Audit log of applied rules")
    bill_of_materials: BillOfMaterials | None = Field(default=None, description="The generated BOM")
    pricing_summary: PricingSummary | None = Field(default=None, description="The calculated pricing")
    status: ConfigurationStatus = Field(default=ConfigurationStatus.DRAFT, description="Current lifecycle state")
