# Architecture Decision Records (ADRs)

This directory contains the accepted architectural decisions that guide the development of the Elevator Configuration & Pricing Engine.

## ADR Index (Milestones 1–5)

| ADR Number | Title | Status | Date | Related Milestone | Summary |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ADR-001** | Repository Pattern | Accepted | 2026-07 | M1 | Standardized data access via `BaseRepository` abstracting flat JSON files for easy future SQL migration. |
| **ADR-002** | Immutable Product Catalogue | Accepted | 2026-07 | M1 | The core `ProductCatalogue` is loaded once into memory at startup and remains strictly read-only to prevent drift. |
| **ADR-003** | Rule DSL | Accepted | 2026-07 | M2 | Defined a domain-specific language for business rules to evaluate configurations independently of hardcoded logic. |
| **ADR-004** | Registry Pattern | Accepted | 2026-07 | M2, M4 | Adopted registries (e.g., `RuleRegistry`, `PricingRegistry`) to decouple loading and validation from engine execution. |
| **ADR-005** | Version-Based Graph Cache | Accepted | 2026-07 | M3 | The dependency graph is cached via a version hash to optimize structural resolutions while guaranteeing freshness. |
| **ADR-006** | Topological Dependency Resolution | Accepted | 2026-07 | M3 | Engineering dependencies (REQUIRES, EXCLUDES) are resolved via directed graphs and topological sorting to prevent cycles. |
| **ADR-007** | BaseEngine Generic Contract | Accepted | 2026-07 | M3.5 | All engines (`RuleEngine`, `DependencyEngine`, `PricingEngine`) implement a standardized interface utilizing `Context` and `Report`. |
| **ADR-008** | ConfigurationPipeline Sole Orchestrator | Accepted | 2026-07 | M4 | The pipeline exclusively dictates engine execution order and mutates the `Configuration.status` lifecycle. |
| **ADR-009** | Pricing Engine Owns Financial Calculations | Accepted | 2026-07 | M4 | Only the Pricing Engine is allowed to calculate taxes, sub-totals, and BOM unit costs. |
| **ADR-010** | REST Boundary Isolation | Accepted | 2026-07 | M5 | Web routing endpoints contain zero business logic and act strictly as transport layers bridging HTTP to the Pipeline. |
| **ADR-011** | DTO Separation | Accepted | 2026-07 | M5 | API requests and responses are strictly separated from internal domain models (e.g., `APISuccessEnvelope`). |
| **ADR-012** | Exporters as Read-Only Services | Accepted | 2026-07 | M6 (Prep) | Export tools (PDF/Excel) are implemented as formatters, not engines, as they only project read-only configurations. |
| **ADR-013** | Configuration as the Single Mutable Aggregate | Accepted | 2026-07 | M1-M5 | The `Configuration` entity is the sole object that mutates throughout the pipeline process. All other data is static context. |
| **ADR-014** | Correlation ID Ownership | Accepted | 2026-07 | M5 | `ConfigurationPipeline` generates the `PIPE-UUID`, which propagates through all engines and returns in the REST response header `X-Correlation-ID`. |
| **ADR-015** | Architecture Freeze (Milestones 1–5) | Accepted | 2026-07 | M5 | Core framework interfaces (`BaseEngine`, `ConfigurationPipeline`, Models) are permanently frozen against structural redesigns. |
