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
    QuoteStatus,
    ExportFormat,
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


class TaxConfiguration(BaseModel):
    """Configuration for global tax calculation."""
    enabled: bool = Field(default=True, description="Whether tax calculation is active")
    tax_name: str = Field(default="VAT", description="Description of the tax (e.g. 'VAT')")
    rate: Decimal = Field(..., description="Tax rate percentage (e.g. 18.0 for 18%)")


class PricingRecord(BaseModel):
    """A data-driven record defining the base cost and markup for an entity."""
    entity_id: str = Field(..., description="The ID of the Category, Component, or FeatureOption")
    entity_type: str = Field(..., description="CATEGORY, COMPONENT, or FEATURE_OPTION")
    base_cost: Decimal = Field(default=Decimal("0.00"), description="Raw manufacturing or procurement cost")
    markup_percentage: Decimal = Field(default=Decimal("0.00"), description="Profit markup percentage")
    price: Decimal = Field(..., description="Final price (base_cost + markup)")


class PricingCatalogue(BaseModel):
    """The collection of all pricing data for the product catalogue."""
    catalogue_version: str = Field(..., description="Version of the pricing catalogue")
    currency: str = Field(default="EUR", description="Base currency code")
    tax_configuration: TaxConfiguration
    pricing_records: list[PricingRecord] = Field(default_factory=list)


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
    pricing: PricingCatalogue | None = Field(default=None, description="Pricing data if loaded")


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


from enum import Enum

class BOMOrigin(str, Enum):
    FEATURE = "FEATURE"
    DEPENDENCY = "DEPENDENCY"
    RULE = "RULE"
    MANUAL = "MANUAL"

class BOMItem(BaseModel):
    """A line item in the generated Bill of Materials."""

    component_id: str = Field(..., description="The physical component ID")
    component_name: str | None = Field(default=None, description="The human-readable name of the component")
    quantity: int = Field(default=1, description="Quantity required")
    source_feature_option_id: str | None = Field(default=None, description="The feature choice that triggered this")
    reason: str = Field(default="", description="Explanation of why this is included")
    origin_type: BOMOrigin = Field(default=BOMOrigin.FEATURE, description="Origin of this BOM item")
    unit_cost: Decimal | None = Field(default=None, description="Price per unit (populated by Pricing Engine)")
    pricing_record_id: str | None = Field(default=None, description="The pricing record that provided the unit_cost")



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

    currency: str = Field(default="EUR", description="Currency code (e.g. EUR, USD)")
    currency_symbol: str = Field(default="€", description="Currency symbol")
    exchange_rate: Decimal | None = Field(default=None, description="Exchange rate if applicable")

    category_cost: Decimal = Field(default=Decimal("0.00"), description="Base category price")
    component_cost: Decimal = Field(default=Decimal("0.00"), description="Sum of physical component costs")
    feature_cost: Decimal = Field(default=Decimal("0.00"), description="Sum of feature option upcharges")
    floor_coverage_cost: Decimal = Field(default=Decimal("0.00"), description="Additional cost for floor coverage")
    
    # Backward compatible aliases / existing names
    base_price: Decimal = Field(default=Decimal("0.00"), description="Alias for category_cost")
    component_costs: Decimal = Field(default=Decimal("0.00"), description="Alias for component_cost")
    feature_costs: Decimal = Field(default=Decimal("0.00"), description="Alias for feature_cost")
    
    subtotal_before_tax: Decimal = Field(default=Decimal("0.00"), description="Total before tax is applied")
    adjustments: list[PriceAdjustment] = Field(default_factory=list, description="Discounts and markups")
    tax_amount: Decimal = Field(default=Decimal("0.00"), description="Calculated taxes based on tax configuration")
    total_after_tax: Decimal = Field(default=Decimal("0.00"), description="Final total price to quote")
    
    # Backward compatible aliases
    taxes: Decimal = Field(default=Decimal("0.00"), description="Alias for tax_amount")
    total: Decimal = Field(default=Decimal("0.00"), description="Alias for total_after_tax")


class QuoteMetadata(BaseModel):
    """Metadata surrounding the generated quotation for this configuration."""

    quote_number: str = Field(..., description="Unique generated quote identifier")
    quote_version: int = Field(default=1, description="Quote version number")
    valid_until: str = Field(..., description="ISO8601 expiry timestamp for this quote")
    approved_at: str | None = Field(default=None, description="ISO8601 approval timestamp")
    status: QuoteStatus = Field(default=QuoteStatus.DRAFT, description="Independent quote lifecycle state")
    quote_hash: str | None = Field(default=None, description="Deterministic fingerprint of the quote components")


class ConfigurationMutation(BaseModel):
    """Tracks atomic changes made to the configuration by engines."""

    timestamp: str = Field(..., description="ISO8601 timestamp of the mutation")
    source_engine: str = Field(..., description="Engine that caused this mutation (e.g., RULE_ENGINE, DEPENDENCY_ENGINE)")
    entity_id: str = Field(..., description="ID of the entity affected")
    mutation_type: str = Field(..., description="ADDED, REMOVED")
    reason: str = Field(default="", description="Reason for the mutation")


class Configuration(BaseModel):
    """The core aggregate root representing a customer's specific elevator configuration."""

    configuration_id: str = Field(..., description="Unique ID for this configuration session")
    project_name: str | None = Field(default=None, description="Customer-given project name (e.g. 'My Apartment')")
    customer_reference: str | None = Field(default=None, description="Optional CRM/ERP reference ID")
    created_at: str | None = Field(default=None, description="ISO8601 creation timestamp")
    expires_at: str | None = Field(default=None, description="ISO8601 quote expiry timestamp")
    selected_category: str | None = Field(default=None, description="The chosen ElevatorCategory ID")
    selected_feature_options: list[str] = Field(default_factory=list, description="IDs of selected FeatureOptions")
    resolved_components: list[str] = Field(default_factory=list, description="IDs of explicitly resolved Components")
    validation_results: ValidationResult | None = Field(default=None, description="Results of the last validation run")
    rule_results: list[RuleResult] = Field(default_factory=list, description="Audit log of applied rules")
    mutations: list[ConfigurationMutation] = Field(default_factory=list, description="Audit log of all state mutations")
    bill_of_materials: BillOfMaterials | None = Field(default=None, description="The generated BOM")
    pricing_summary: PricingSummary | None = Field(default=None, description="The calculated pricing")
    quote_metadata: QuoteMetadata | None = Field(default=None, description="Metadata for the generated quote")
    status: ConfigurationStatus = Field(default=ConfigurationStatus.DRAFT, description="Current lifecycle state")


class RuleContext(BaseModel):
    """The runtime state passed to rule conditions and actions."""

    configuration: Configuration
    catalogue: ProductCatalogue
    current_rule: Rule | None = None
    trigger_type: RuleTriggerType
    execution_timestamp: str = Field(..., description="ISO8601 timestamp of execution")
    correlation_id: str = Field(..., description="Trace ID for this execution run")
    execution_depth: int = Field(default=0, description="Nesting level of rule execution")
    execution_history: list[str] = Field(default_factory=list, description="IDs of rules executed so far in this run")


class ActionResult(BaseModel):
    """The structured result returned by an ActionHandler."""

    success: bool
    message: str | None = None
    affected_entities: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    configuration_changes: dict[str, Any] = Field(default_factory=dict)


class RuleMetrics(BaseModel):
    """Runtime metrics for a single evaluation pass."""

    rules_loaded: int = 0
    rules_executed: int = 0
    rules_skipped: int = 0
    rules_failed: int = 0
    total_execution_time_ms: float = 0.0


class ExecutionReport(BaseModel):
    """The final summary of a rule evaluation pass."""

    configuration_id: str
    trigger: str
    executed_rules: list[str] = Field(default_factory=list)
    skipped_rules: list[str] = Field(default_factory=list)
    failed_rules: list[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    summary: str
    metrics: RuleMetrics


class DependencyNode(BaseModel):
    """Represents a node (component or option) in the dependency graph."""

    entity_id: str = Field(..., description="ID of the FeatureOption or Component")
    entity_type: str = Field(..., description="Type: 'COMPONENT' or 'OPTION'")
    resolved: bool = Field(default=False, description="Whether this node has been resolved in the current pass")


class DependencyEdge(BaseModel):
    """Represents a directed edge between two DependencyNodes."""

    dependency: Dependency = Field(..., description="The underlying dependency relationship")
    is_active: bool = Field(default=True, description="True if condition_expression evaluated to True")


class DependencyGraph(BaseModel):
    """The in-memory topological graph of engineering dependencies."""

    nodes: dict[str, DependencyNode] = Field(default_factory=dict)
    adjacency_list: dict[str, list[DependencyEdge]] = Field(default_factory=dict)
    reverse_adjacency: dict[str, list[DependencyEdge]] = Field(default_factory=dict)


class DependencyConflict(BaseModel):
    """Structured record of an EXCLUDES violation discovered during resolution."""

    dependency_id: str = Field(..., description="ID of the dependency that caused the conflict")
    source_entity_id: str = Field(..., description="Entity that declared the exclusion")
    target_entity_id: str = Field(..., description="Entity that was excluded but present")
    reason: str = Field(..., description="Human-readable explanation")


class ResolutionStep(BaseModel):
    """A structured record of one resolved dependency action."""

    step_number: int = Field(..., description="Position in execution order")
    entity_id: str = Field(..., description="The target entity affected")
    dependency_id: str = Field(..., description="The dependency that triggered this step")
    action_performed: str = Field(..., description="REQUIRES, EXCLUDES, DETERMINES, or RECOMMENDS")
    mutated: bool = Field(..., description="True if this step changed Configuration state")
    timestamp: str = Field(..., description="ISO8601 timestamp of this step")


class DependencyResolutionMetrics(BaseModel):
    """Extended graph and execution statistics from a dependency resolution pass."""

    total_nodes: int = 0
    total_edges: int = 0
    active_nodes: int = 0
    active_edges: int = 0
    traversed_nodes: int = 0
    skipped_nodes: int = 0
    resolved_nodes: int = 0
    execution_time_ms: float = 0.0


class DependencyResolutionReport(BaseModel):
    """The complete audit trail of a dependency resolution pass, split into logical sections."""

    configuration_id: str

    # Section 1 — Resolution Metrics
    metrics: DependencyResolutionMetrics = Field(default_factory=DependencyResolutionMetrics)

    # Section 2 — Configuration Mutations
    components_added: list[str] = Field(default_factory=list)
    options_added: list[str] = Field(default_factory=list)

    # Section 3 — Conflicts
    conflicts: list[DependencyConflict] = Field(default_factory=list)

    # Section 4 — Warnings
    warnings: list[str] = Field(default_factory=list)
    cycles_detected: list[str] = Field(default_factory=list)

    # Section 5 — Resolution Steps (full ordered execution trail)
    execution_order: list[ResolutionStep] = Field(default_factory=list)

    # Section 6 — Execution Summary
    summary: str = ""


class DependencyResolutionContext(BaseModel):
    """Dedicated runtime context for the Dependency Engine. Never reuses RuleContext."""

    configuration: Configuration
    catalogue: ProductCatalogue
    graph: DependencyGraph | None = Field(default=None, description="Topology graph")
    report: DependencyResolutionReport | None = Field(default=None, description="Execution report")
    correlation_id: str = Field(..., description="Trace ID for this resolution run")
    execution_timestamp: str = Field(..., description="ISO8601 timestamp of the run")
    current_node_id: str | None = Field(default=None, description="Node currently being processed")
    current_edge: DependencyEdge | None = Field(default=None, description="Edge currently being evaluated")


class PricingMetrics(BaseModel):
    """Metrics produced during a pricing engine run."""
    components_priced: int = 0
    features_priced: int = 0
    subtotal: Decimal = Decimal("0.00")
    taxes: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    execution_time_ms: float = 0.0


class PricingStep(BaseModel):
    """An audit trail step for a pricing calculation."""
    step_number: int = Field(..., description="Position in execution order")
    entity_id: str | None = Field(default=None, description="The entity priced (None for subtotal/tax)")
    description: str = Field(..., description="Description of the calculation step")
    amount: Decimal = Field(..., description="The amount added or calculated")
    timestamp: str = Field(..., description="ISO8601 timestamp of this step")


class PricingReport(BaseModel):
    """The final summary of a pricing engine execution pass."""
    configuration_id: str
    metrics: PricingMetrics = Field(default_factory=PricingMetrics)
    pricing_steps: list[PricingStep] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    summary: str = ""


class EngineStartupReport(BaseModel):
    """Structured report returned by each engine during startup validation."""
    engine_name: str
    ready: bool
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0


class PipelineMetrics(BaseModel):
    """Overall pipeline execution metrics."""
    total_execution_time_ms: float = 0.0
    startup_validation_time_ms: float = 0.0
    engines_executed: int = 0
    engines_skipped: int = 0
    success: bool = False


class PipelineExecutionReport(BaseModel):
    """The canonical backend execution artifact."""
    correlation_id: str
    final_configuration_status: ConfigurationStatus
    rule_engine_report: ExecutionReport | None = None
    dependency_engine_report: DependencyResolutionReport | None = None
    pricing_engine_report: PricingReport | None = None
    startup_reports: list[EngineStartupReport] = Field(default_factory=list)
    metrics: PipelineMetrics = Field(default_factory=PipelineMetrics)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class PipelineContext(BaseModel):
    """The unified context passed through the orchestration layer."""
    configuration: Configuration
    correlation_id: str
    execution_timestamp: str
    request_source: str = Field(default="API", description="WEB, API, CLI, TEST")
    report: PipelineExecutionReport


class ExportMetadata(BaseModel):
    """Metadata detailing the physical output of an export operation."""
    generated_at: str = Field(..., description="ISO8601 generation timestamp")
    generated_by: str = Field(default="SYSTEM", description="User or system that generated the export")
    generator_version: str = Field(default="1.0", description="Version of the export generator")
    backend_version: str = Field(default="0.1.0", description="Backend version that generated the export")
    schema_version: str = Field(default="1.0", description="Version of the export schema")
    export_duration_ms: float = Field(default=0.0, description="Generation duration in ms")
    export_format: ExportFormat = Field(..., description="Format of the export")
    checksum: str | None = Field(default=None, description="SHA-256 checksum of the exported file")
    filename: str = Field(..., description="The generated filename")
    mime_type: str = Field(..., description="MIME type of the generated file")
    file_size: int = Field(..., description="File size in bytes")

class ExportManifest(BaseModel):
    """Manifest of exported files in a bundle."""
    configuration_id: str
    quote_number: str | None = None
    exported_files: list[str] = Field(default_factory=list)
    checksums: dict[str, str] = Field(default_factory=dict)
    export_version: str = "1.0"
    schema_version: str = "1.0"
    backend_version: str = "0.1.0"
    generated_timestamp: str


class ExportReport(BaseModel):
    """The final summary of an export execution."""
    export_format: ExportFormat
    filename: str
    mime_type: str
    checksum: str
    file_size: int
    generation_time_ms: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    success: bool = False
    content: bytes | None = Field(default=None, description="The generated export content in memory")


class ExportContext(BaseModel):
    """The runtime context passed to a BaseExporter."""
    configuration: Configuration
    correlation_id: str = Field(..., description="Trace ID for this export run")
    execution_timestamp: str = Field(..., description="ISO8601 timestamp of the run")
    export_format: ExportFormat = Field(..., description="Target export format")
