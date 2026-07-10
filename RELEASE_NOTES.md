# Release Notes - Version 1.0.0

**Release Date**: 2026-07-08

We are thrilled to announce the official **Version 1.0.0** release of the Elevator Configuration & Pricing Engine.

This release represents the culmination of Milestones 1 through 9, establishing a rock-solid, mathematically sound backend paired with a blazingly fast, accessible frontend, completely tuned for production.

## Major Highlights
1. **Frozen Backend Architecture**: The backend acts as the single source of truth for all complex business logic, pricing, dependency resolution, and rule evaluation.
2. **"Dumb" UI Paradigm**: The React 19 frontend contains zero business logic, ensuring that physical part rules and pricing cannot drift between the server and the browser.
3. **Enterprise Exporting**: Users can seamlessly export their configurations to JSON, PDF, and Excel.
4. **Production Hardened**: This release includes Dockerization, Playwright E2E suites, strict performance budgets, automated OpenAPI drift protection, `uv`-based high speed dependency resolution, and 100% stable CI/CD deployment pipelines.

## Known Limitations
- The product catalog is currently mocked in-memory/static files. Connecting to a real PIM (Product Information Management) system is scheduled for a future release.
- PDF generation blocks synchronously; massive configurations (10,000+ parts) may require an asynchronous web-hook approach in the future.
