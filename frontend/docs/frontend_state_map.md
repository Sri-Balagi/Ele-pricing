# Frontend State Management Map

State in this frontend is strictly segregated by responsibility to prevent unnecessary renders and maintain clear ownership.

## 1. Server State (TanStack Query)
- **Domain**: All data originating from the Backend API (Configurations, Diagnostics, Quotes, Pricing, BOM).
- **Location**: Cached globally inside the `QueryClient`.
- **Why**: Server data is inherently stale the moment it is fetched. TanStack Query manages caching, invalidation, background refetching (e.g., polling `healthApi` every 30s), and provides uniform `isLoading` / `isError` flags.

## 2. Global UI State (Zustand)
- **Domain**: Long-lived user preferences and layout state.
- **Location**: `src/stores/uiStore.ts`.
- **Properties**: `theme` (Light/Dark/System), `sidebarOpen` (boolean).
- **Why**: Needs to be accessible globally (Layouts, deeply nested components) without prop-drilling, and requires persistence to `localStorage` so user preferences survive page reloads.

## 3. Form State (React Hook Form)
- **Domain**: Intermediate, unsubmitted user input during configuration.
- **Location**: Bound to the `useForm` hook in `Wizard.tsx`.
- **Why**: High-frequency updates (typing in inputs) would cause excessive re-renders if stored in global or standard local state. React Hook Form manages this internally with uncontrolled inputs and provides robust validation integration (Zod).

## 4. Ephemeral UI State (React `useState`)
- **Domain**: Short-lived, component-specific interaction state.
- **Location**: Isolated within specific components (e.g., `Validation.tsx`, `Quote.tsx`).
- **Properties**: `activeId` (Search inputs), `isDownloading` (Button loading spinner), `showPostTax` (Pricing toggle).
- **Why**: This state is irrelevant outside the component itself. It resets when the component unmounts and does not need global tracking.
