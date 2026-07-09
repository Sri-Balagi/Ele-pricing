# Frontend Module Reference

This document explains every significant folder in the `src/` directory.

## `api/`
- **Purpose**: Encapsulates all network interactions and backend communication.
- **Key Files**: `client.ts`, `configuration.ts`, `health.ts`
- **Responsibilities**: Normalizing API responses, unwrapping success envelopes, extracting correlation IDs, and exposing typed async functions.
- **Interactions**: Called exclusively by TanStack Query hooks or direct mutation handlers in pages.
- **Future Extensions**: Adding authentication interceptors (e.g., JWT injection) and WebSocket clients.

## `components/`
- **Purpose**: Houses highly reusable presentation components.
- **Key Files**: `DataTable.tsx`, `EmptyState.tsx`, `ErrorBoundary.tsx`, `ui/*`
- **Responsibilities**: Providing accessible, styled blocks (Buttons, Inputs, Tables) with zero knowledge of backend data structures.
- **Interactions**: Imported globally across all pages and layouts.
- **Future Extensions**: Complex specialized data tables, interactive visualizations for dependency graphs.

## `layouts/`
- **Purpose**: Defines the shell and structural framing of the application.
- **Key Files**: `AppLayout.tsx`
- **Responsibilities**: Rendering the Top Navigation, Sidebar, Status Bar, and managing the `<Outlet />` for child pages.
- **Interactions**: Wraps the Router's main content area. Fetches health metrics for the StatusBar.
- **Future Extensions**: Role-based layout changes, dynamic sidebar navigation based on backend feature flags.

## `pages/`
- **Purpose**: The high-level features and route destinations.
- **Key Files**: `Wizard.tsx`, `Dashboard.tsx`, `BOM.tsx`, `Pricing.tsx`
- **Responsibilities**: Orchestrating data fetching (via API + Query), orchestrating forms, and assembling components into a complete feature view.
- **Interactions**: Registered in `App.tsx` routes. Consumes `api/` and `components/`.
- **Future Extensions**: Additional visualization pages (e.g., Rule Dependency Visualizer).

## `stores/`
- **Purpose**: Global UI client state management.
- **Key Files**: `uiStore.ts`
- **Responsibilities**: Managing non-server state like sidebar visibility and theme preferences.
- **Interactions**: Read/Updated by layout components and user preference menus.
- **Future Extensions**: User session stores, localized user preference overrides.

## `theme/`
- **Purpose**: Centralized design tokens for consistent theming.
- **Key Files**: `colors.ts`, `typography.ts`, `spacing.ts`
- **Responsibilities**: Providing JavaScript-accessible token values if needed for charts or programmatic styling.
- **Interactions**: Referenced by Tailwind configuration and specialized charting components.
- **Future Extensions**: Multi-brand theme definitions.

## `types/`
- **Purpose**: Strictly typed models representing the backend contract.
- **Key Files**: `api.ts`
- **Responsibilities**: Providing the single source of truth for data structures.
- **Interactions**: Imported globally across `api/` and `pages/`.
- **Future Extensions**: Automatically regenerated on every backend OpenAPI schema change via CI/CD.

## `test/`
- **Purpose**: Testing infrastructure and mock servers.
- **Key Files**: `setup.ts`, `mocks/handlers.ts`, `mocks/server.ts`
- **Responsibilities**: Bootstrapping testing environments and defining mock backend responses.
- **Interactions**: Consumed by Vitest during `npm run test`.
- **Future Extensions**: Expanding mock scenarios for edge cases and failure modes.
