# Configuration Lifecycle & Pipeline

This document describes the distinction between the **Business Lifecycle** of a `Configuration` (its state) and the **Processing Pipeline** (the sequence of engines that process it).

## Business Lifecycle

The lifecycle represents the formal state of a configuration from the perspective of the business and the user.

1. **DRAFT**
   - The user starts a new configuration or modifies an existing one.
   - User inputs selections (e.g., Load Capacity, Speed).
   - Only `selected_feature_options` are updated directly by the user/UI.

2. **VALIDATED**
   - The configuration has successfully passed through the engineering rules and dependency engines without unresolvable conflicts.
   - All necessary components are resolved.

3. **PRICING** / **PRICED** (Milestone 4)
   - The configuration has been fully priced. `pricing_summary` is populated.
   
4. **APPROVED**
   - The user or a sales representative has formally approved the configuration and pricing.

5. **EXPORTED**
   - The finalized configuration has been exported to external systems (e.g., ERP, Manufacturing) alongside its complete Bill of Materials (BOM).

## Processing Pipeline

The processing pipeline represents the sequence of backend engines that orchestrate the state transitions and resolve the configuration.

1. **Rule Engine** (Milestone 2)
   - Analyzes `selected_feature_options`.
   - Executes rules in the DSL (e.g., `has_option('HIGH_SPEED')`).
   - Appends components to `resolved_components` and logs `mutations`.

2. **Dependency Engine** (Milestone 3)
   - Analyzes `resolved_components` from the Rule Engine.
   - Traverses the Product Catalogue Dependency Graph.
   - Discovers and appends implicit engineering requirements. Records cycles/conflicts if any.

3. **Pricing Engine** (Milestone 4)
   - Evaluates the final `resolved_components` and `selected_feature_options`.
   - Calculates base costs, markups, and totals.

4. **Validation Engine** 
   - Performs a final holistic check against strict business and structural rules.

5. **BOM Generation Engine**
   - Flattens `resolved_components` into a structured, manufacturable Bill of Materials.

6. **Export Service**
   - Serializes the configuration for downstream manufacturing or ERP systems.
