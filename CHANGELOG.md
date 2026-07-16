# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Type-D Elevator Integration**: Fully populated catalogue data for Type-D elevators (Ultimate Luxury & Smart).
- **Component Pricing (Type-D)**: Implemented highly granular pricing data based on individual component cost prices with explicit margins mapped to 0% for base components.
- **Advanced Constraints**: Added 37 exhaustive dependency constraints (both `EXCLUDES` and `REQUIRES`) for Type-D configuration rules.

### Changed
- **Categories Update**: Rebranded the Type-D category name in the database from "Type D Custom" to "Type D Highly Customizable".
- **Wizard Defaults**: Changed the default number of stops to `2` for Type-B, Type-C, and Type-D, standardizing the baseline floor coverage across the board.
- **Pricing Logic**: Adjusted the floor coverage calculation for all non-Type-A elevators to start accruing additional per-floor cost from `numStops > 2`.
- **PDF Exporter Formatting**: Modified the backend `PDFExporter` to arrange features in a clean, bulleted list instead of a comma-separated paragraph for improved readability in the Configuration Summary.

### Fixed
- **Wizard Compatibility Exhaustiveness**: Fixed an issue where toast notifications for option incompatibilities were silently swallowed if an option was already incompatible due to default selections. The system now thoroughly tracks and displays toasts for all `REQUIRES` and `EXCLUDES` compatibility updates.
- **Number of Stops Input Bug**: Updated `handleStopsChange` to optimistically accept intermediate numerical input (e.g., typing `1`), preventing the input from reverting to blank and allowing users to type double-digit floor counts seamlessly.
- **Requires Logic Rendering**: Enhanced the frontend validation engine in `Wizard.tsx` to automatically select targets of `REQUIRES` constraints and block deselection when a dependent feature is active.

## [1.0.0] - 2026-07-08

### Added
- **Frontend App**: Production-ready React 19 application utilizing Tailwind V4 and Shadcn UI.
- **Backend App**: Version 1.0.0 frozen FastAPI backend handling all logic.
- **Rule Engine**: Validates inputs and resolves conflicts.
- **Dependency Engine**: Excludes and includes dependencies based on selected features.
- **Pricing Engine**: Determines costs with robust margin/tax modifiers.
- **BOM Generator**: Produces physical part manifests.
- **Export Framework**: JSON, Excel, and PDF quote exports.
- **CI/CD**: GitHub actions for drift protection, linting, testing, and Docker builds.
- **Production Catalogs (M8)**: Fully populated and realistic configuration data for Type-B elevators (components, constraints, and dependencies).
- **CI/CD Hardening (M9)**: Switched to `uv` for dependency management. Strict `ruff` and `eslint` enforcement in GitHub Actions.
- **API Synchronization (M9)**: Created tooling to automatically dump and snapshot the OpenAPI schema, syncing it precisely with frontend typing.
- **Monitoring**: Abstracted monitoring service ready for Sentry/OpenTelemetry integration.

### Changed
- Refactored `client.ts` to unwrap `APISuccessEnvelope` globally.
- Updated all API typings to directly map from backend `openapi.json`.

### Fixed
- Fixed typescript strict mode issues across frontend components.
- Fixed TS deprecation warnings by updating `tsconfig.app.json`.
- Enforced zero business logic on the frontend by stripping any calculation code.
