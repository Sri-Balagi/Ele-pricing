# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- **Monitoring**: Abstracted monitoring service ready for Sentry/OpenTelemetry integration.

### Changed
- Refactored `client.ts` to unwrap `APISuccessEnvelope` globally.
- Updated all API typings to directly map from backend `openapi.json`.

### Fixed
- Fixed typescript strict mode issues across frontend components.
- Fixed TS deprecation warnings by updating `tsconfig.app.json`.
- Enforced zero business logic on the frontend by stripping any calculation code.
