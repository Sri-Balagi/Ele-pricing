# Testing Strategy

This document outlines the testing strategy for the Elevator Configuration & Pricing Engine.

## Testing Layers

### 1. Unit Tests
Found in `tests/test_domain.py`, `tests/test_validator.py`, etc.
Focus on individual models and validation routines (e.g. `pydantic` validation logic).

### 2. Engine Isolation Tests
Found in `tests/test_rule_engine_extended.py` and `tests/test_dependency_engine.py`.
Tests the core resolution loops of each engine using isolated configurations and mocked context.

### 3. Cross-Engine Integration Tests
Found in `tests/test_integration_m2_m3.py`.
Validates the handoff between engines (e.g., Rule Engine outputs -> Dependency Engine inputs). Ensures the Configuration acts as a reliable state accumulator.

### 4. Adversarial Tests
Found in `tests/test_adversarial.py`.
Injects corrupted topologies (e.g., circular dependencies) and validates that the system degrades gracefully with clear errors, rather than crashing.

### 5. Snapshot Tests
Found in `tests/test_snapshots.py`.
Guarantees backward compatibility of domain models. Asserts that API-facing outputs conform exactly to a structural contract.

### 6. Benchmark Tests
Found in `tests/test_benchmarks.py`.
Performance-only tests designed to observe resolution times at high data volumes (e.g. 1000 rules, 1000 graph nodes). These are strictly observable metrics and do not fail CI.

## Regression Policy

To maintain architectural stability and prevent regressions, the following test suites **MUST** be run based on the scope of the code changes:

- **Changes to Domain Models (`app/models/domain.py`)**:
  - Run Unit Tests (`tests/test_domain.py`).
  - Run Snapshot Tests (`tests/test_snapshots.py`) to guarantee backwards compatibility.

- **Changes to a Specific Engine (`app/rules/`, `app/dependency_engine/`)**:
  - Run Engine Isolation Tests (`tests/test_rule_engine_extended.py` or `tests/test_dependency_engine.py`).
  - Run Adversarial Tests (`tests/test_adversarial.py`) to verify resilience against edge cases.
  - Run Cross-Engine Integration Tests (`tests/test_integration_m2_m3.py`) to ensure the hand-off contract is preserved.

- **Changes to Repository Layer or DataLoader (`app/utils/data_loader.py`)**:
  - Run Unit Tests (`tests/test_startup.py`).
  - Run Cache Validation Tests (`tests/test_caching.py`).

- **Changes to the API / Web Layer (Milestone 5+)**:
  - Run Cross-Engine Integration Tests to ensure the complete pipeline resolves end-to-end.
  - Run Snapshot Tests.
  
For any pull request or deployment, **the entire test suite** (Phase 10: Final Regression Testing) must pass locally and in CI.
