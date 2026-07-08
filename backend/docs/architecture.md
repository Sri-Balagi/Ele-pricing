# Architecture Overview

This document outlines the high-level architecture of the Elevator Configuration & Pricing Engine.

## Configuration Pipeline

The following sequence diagram illustrates the processing pipeline of a `Configuration` as it flows through the backend engines.

```mermaid
sequenceDiagram
    participant UI as User Interface
    participant CE as Configuration Engine
    participant RE as Rule Engine
    participant DE as Dependency Engine
    participant PE as Pricing Engine
    participant DB as Product Catalogue

    UI->>CE: Submit User Selections (DRAFT)
    CE->>RE: resolve(ConfigurationContext)
    RE->>DB: Fetch Rules (has_option)
    RE-->>CE: Output: Executed Rules & Added Components
    
    CE->>DE: resolve(DependencyContext)
    DE->>DB: Fetch Dependency Graph
    DE-->>CE: Output: Resolved BOM Components & Cycles/Warnings
    
    CE->>PE: resolve(PricingContext) [Milestone 4]
    PE->>DB: Fetch Pricing Data
    PE-->>CE: Output: Pricing Summary & Totals
    
    CE-->>UI: Return Configuration (VALIDATED/PRICED)
```

## Architectural Tenets
1. **Engine Isolation**: Each engine operates independently, accepting a strict `Context` object and returning a `Report`.
2. **Immutable Catalogue**: The `ProductCatalogue` is read-only during execution. Updates to the catalogue trigger version bumps and cache invalidations.
3. **State Accumulation**: The `Configuration` acts as an event-sourced accumulator, maintaining a history of `mutations` caused by the pipeline.
