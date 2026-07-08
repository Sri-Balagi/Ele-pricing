# Data Dictionary

This document provides a canonical reference for the core domain models and data sources (JSON files) in the Elevator Configuration & Pricing Engine.

## Domain Entities

- **ProductCatalogue**: The single source of truth for all engineering, sales, and pricing data for a specific product version.
- **Configuration**: Represents a user's active session building an elevator. It tracks user selections and acts as an aggregator for engine results.
- **ConfigurationMutation**: An audit record capturing what was changed (`entity_id`), how it changed (`mutation_type`), why (`reason`), and by whom (`source_engine`).

---

## Catalogue Data Sources (JSON)

The backend `DataLoader` ingests the following JSON files to build the `ProductCatalogue`.

### 1. catalog_metadata.json
- **Purpose**: Defines versioning and lifecycle metadata for the catalogue itself.
- **Primary Fields**: `catalogue_version`, `schema_version`, `created_date`, `last_updated`.
- **Relationships**: N/A (Root file).
- **Example**:
  ```json
  {
    "catalogue_version": "1.0.0",
    "schema_version": "1.0",
    "created_date": "2026-07-08T00:00:00Z",
    "last_updated": "2026-07-08T00:00:00Z",
    "prototype_version": "1.0"
  }
  ```

### 2. categories.json
- **Purpose**: Defines high-level product breakdown (e.g., Structural, Mechanical, Electrical, Cabin).
- **Primary Fields**: `id`, `name`, `description`.
- **Relationships**: Features and Components belong to a Category.
- **Example**:
  ```json
  [
    { "id": "CAT_CABIN", "name": "Cabin", "description": "Elevator cabin options." }
  ]
  ```

### 3. feature_groups.json
- **Purpose**: Groups related UI features together logically.
- **Primary Fields**: `id`, `category_id`, `name`, `is_mandatory`.
- **Relationships**: Belongs to a Category (`category_id`). Contains Features.
- **Example**:
  ```json
  [
    { "id": "FG_DIM", "category_id": "CAT_CABIN", "name": "Dimensions", "is_mandatory": true }
  ]
  ```

### 4. features.json
- **Purpose**: Defines an individual configurable attribute (e.g., "Load Capacity").
- **Primary Fields**: `id`, `group_id`, `name`, `ui_type` (dropdown, numeric), `validation_rules`.
- **Relationships**: Belongs to a Feature Group (`group_id`). Contains Feature Options.
- **Example**:
  ```json
  [
    { "id": "F_CAPACITY", "group_id": "FG_DIM", "name": "Capacity (kg)", "ui_type": "dropdown" }
  ]
  ```

### 5. feature_options.json
- **Purpose**: Defines the selectable values for a specific feature.
- **Primary Fields**: `id`, `feature_id`, `display_name`, `internal_value`, `is_default`.
- **Relationships**: Belongs to a Feature (`feature_id`). Used in Rule conditions.
- **Example**:
  ```json
  [
    { "id": "OPT_1000KG", "feature_id": "F_CAPACITY", "display_name": "1000 kg", "internal_value": "1000", "is_default": true }
  ]
  ```

### 6. components.json
- **Purpose**: Defines physical engineering parts and logic modules (the actual Bill of Materials).
- **Primary Fields**: `id`, `category`, `name`, `unit`.
- **Relationships**: Added by Rules. Tied together via Dependencies.
- **Example**:
  ```json
  [
    { "id": "COMP_MOTOR_10KW", "category": "Mechanical", "name": "10kW Traction Motor", "unit": "pcs" }
  ]
  ```

### 7. feature_mappings.json
- **Purpose**: (Legacy / Direct mapping) Defines a 1:1 mapping between an option and a component without complex logic. Often superseded by Rules.
- **Primary Fields**: `option_id`, `component_id`, `quantity`.
- **Relationships**: Links FeatureOption (`option_id`) to Component (`component_id`).
- **Example**:
  ```json
  [
    { "option_id": "OPT_1000KG", "component_id": "COMP_CABIN_FRAME_L", "quantity": 1 }
  ]
  ```

### 8. rules.json
- **Purpose**: Defines conditional logic that translates feature selections into actions (e.g. adding a component).
- **Primary Fields**: `id`, `name`, `trigger_type`, `priority`, `condition`, `action`, `action_payload`.
- **Relationships**: References Feature Options (in `condition`) and Components (in `action_payload`).
- **Example**:
  ```json
  [
    {
      "id": "RULE_MOTOR_SIZE",
      "name": "Select motor based on capacity",
      "trigger_type": "ON_SELECTION",
      "priority": 100,
      "condition": "has_option('OPT_1000KG')",
      "action": "ADD_COMPONENT",
      "action_payload": { "component_id": "COMP_MOTOR_10KW" }
    }
  ]
  ```

### 9. dependencies.json
- **Purpose**: Defines structural graph-based requirements between components.
- **Primary Fields**: `id`, `source_id`, `target_id`, `dependency_type` (e.g., REQUIRES, INCOMPATIBLE).
- **Relationships**: Links Component (`source_id`) to Component (`target_id`).
- **Example**:
  ```json
  [
    { "id": "DEP_MOTOR_CBL", "source_id": "COMP_MOTOR_10KW", "target_id": "COMP_HEAVY_CABLE", "dependency_type": "REQUIRES" }
  ]
  ```

### 10. pricing.json
- **Purpose**: Defines cost, markups, and final prices for components and options (Milestone 4).
- **Primary Fields**: `entity_id`, `entity_type` (COMPONENT, OPTION), `base_cost`, `markup_percentage`, `price`.
- **Relationships**: Links to either a Component or FeatureOption (`entity_id`).
- **Example**:
  ```json
  [
    { "entity_id": "COMP_MOTOR_10KW", "entity_type": "COMPONENT", "base_cost": 5000.0, "markup_percentage": 20.0, "price": 6000.0 }
  ]
  ```
