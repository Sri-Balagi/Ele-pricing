# Elevator Configurator - Frontend Application (Milestone 7)

This is the production-grade React 19 frontend application built for the Elevator Configurator.

## Architectural Guarantees

1. **Zero Business Logic**: The frontend contains exactly zero business logic. All pricing calculations, dependency resolutions, validations, rules, and BOM generations occur strictly in the Version 1.0.0 frozen backend.
2. **Single Source of Truth**: The `src/types/api.ts` file is generated strictly from the backend's OpenAPI contract. No manual DTOs are created.
3. **Resilience**: A global React ErrorBoundary prevents runtime crashes from breaking the entire application. API errors are normalized by an Axios interceptor before reaching TanStack Query.
4. **Performance**: All major feature pages (Dashboard, Wizard, BOM, Pricing, Validation, Quote) are lazily loaded (`React.lazy`). Data fetching happens asynchronously with stale-while-revalidate caching.

## Tech Stack

- React 19
- Vite
- TypeScript
- TailwindCSS (V4)
- React Router (v7)
- TanStack Query (v5)
- Zustand (v5)
- React Hook Form + Zod
- Shadcn UI + Radix
- Vitest + Testing Library + MSW

## API Design

The API client (`src/api/client.ts`) handles the unwrapping of the backend's standardized envelope format (`APISuccessEnvelope`). The endpoints are modularized by feature (`configuration.ts`, `health.ts`, `system.ts`, etc.). 

## State Management

- **Server State**: Managed exclusively by `@tanstack/react-query`. Caches data with specific retry policies (GET: 2, POST: 0).
- **Client/UI State**: Managed by `zustand` (`src/stores/uiStore.ts`). Tracks Sidebar, Theme, etc. (Persisted to localStorage).

## How to Run

```bash
# Install dependencies
npm install

# Start Dev Server
npm run dev

# Run Tests
npm run test
```

## Lighthouse Target Scores

The application components are built with Shadcn/Radix which provide robust accessibility (a11y) out of the box. Expected Lighthouse scores when built for production:
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 90
- SEO: > 90
