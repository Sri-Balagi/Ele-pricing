# Frontend Engineering Handover Report

## Executive Summary
This frontend application provides a modern, scalable, and resilient presentation layer for the Elevator Configuration & Pricing Engine. Designed strictly as a "dumb" UI, it enforces the architectural constraint of **Zero Business Logic**. The backend (Version 1.0.0) remains the single source of truth for all rules, dependencies, and pricing calculations. The frontend focuses entirely on user experience, API consumption, state management, and error handling.

## Technology Stack
- **Framework**: React 19 + Vite (TypeScript)
- **Styling**: TailwindCSS (V4) + Shadcn UI + Radix Primitives
- **Routing**: React Router (v7)
- **Data Fetching (Server State)**: `@tanstack/react-query` + Axios
- **Global UI State**: Zustand (v5)
- **Form Handling**: React Hook Form + Zod
- **Testing**: Vitest + MSW + React Testing Library

## Folder Architecture
```text
src/
├── api/          # API Client & typed endpoint modules
├── assets/       # Static assets
├── components/   # Reusable UI components (Shadcn + custom)
├── layouts/      # Application layout shells (TopNav, Sidebar, StatusBar)
├── lib/          # Utilities and configuration (e.g., queryClient, tailwind merge)
├── pages/        # Lazy-loaded feature views
├── stores/       # Zustand state stores
├── test/         # MSW Handlers and Vitest setup
├── theme/        # Centralized design tokens
└── types/        # Auto-generated OpenAPI TypeScript models
```

## State Ownership
- **Server State**: Owned by TanStack Query. All data fetched from the backend resides in the query cache.
- **Form State**: Owned by React Hook Form. Manages intermediate input before submission.
- **UI State**: Owned by Zustand (e.g., Theme, Sidebar toggle) and persisted to `localStorage`.
- **Local State**: Owned by React `useState` for transient component behaviors (e.g., modal visibility).

## API Layer
The API layer (`src/api`) wraps Axios. The interceptor globally intercepts the backend's `APISuccessEnvelope` and `APIErrorResponse`. It automatically unwraps the `data` payload and attaches the `x-correlation-id` to ensure components only deal with the actual models and standardized error objects.

## Component Hierarchy
- `App` (Router, QueryProvider, Toaster)
  - `ErrorBoundary` (Global crash protection)
    - `AppLayout` (Sidebar, TopNav, StatusBar)
      - `<Outlet />` (Lazy-loaded feature pages)
        - Components (DataTables, Forms, Skeletons)

## Routing
Routing is handled by `react-router-dom` using `<BrowserRouter>`. All primary pages (`Dashboard`, `Wizard`, `Validation`, `BOM`, `Pricing`, `Quote`) are lazy-loaded to reduce the initial bundle size.

## Theme System
Design tokens (Colors, Typography, Spacing, Radius) are centralized in `src/theme/`. Shadcn components consume CSS variables defined in `index.css`. Theme persistence (Light/Dark/System) is managed via `uiStore.ts`.

## Error Handling
1. **API Level**: Axios interceptors normalize all backend errors into a consistent format.
2. **Component Level**: Failed queries render local error states without unmounting the layout.
3. **Global Level**: A React `ErrorBoundary` wraps the router to gracefully catch unhandled runtime exceptions.

## Loading Strategy
- **Initial Load**: Handled by `<Suspense>` fallbacks using highly specific Skeleton components (`TableSkeleton`, `WizardSkeleton`).
- **Data Load**: Handled by TanStack Query's `isLoading` states.

## Empty State Strategy
A centralized `<EmptyState />` component is used across the application when lists (like BOM or Validation) return zero items, ensuring the user always sees a polished interface rather than a blank screen.

## Testing Strategy
- **MSW**: Intercepts HTTP calls at the network level, simulating backend responses for tests.
- **Vitest**: Test runner.
- **RTL**: Component testing.
Tests focus on contract adherence (API unwrapping) and component rendering.

## Build Process
Run `npm run build`. Vite utilizes Rollup to bundle the application. TypeScript performs type-checking (`tsc -b`) prior to the build.

## Performance Optimizations
- Route-level code splitting (`React.lazy`).
- Strict caching and retry policies (GET=2, POST=0) to prevent redundant network calls.
- Memoized layout components.

## Known Limitations
- The backend currently does not provide a paginated category list; the wizard requires manual entry or predefined categories.
- Export streaming downloads directly via browser native mechanisms; large files could hypothetically block if the backend response is delayed.

## Future Improvements
- Implement Playwright for full E2E workflow testing (Create -> Configure -> Price -> Export).
- Add WebSocket support for real-time pipeline execution visualization.
