# Frontend Performance Report

The UI has been architected to maintain a Lighthouse Performance score of > 90 by strictly adhering to modern React performance paradigms.

## 1. Bundle Splitting (Lazy Loading)
- **Implementation**: `React.lazy()` is used in `App.tsx` for all major page components (`Dashboard`, `Wizard`, `BOM`, `Pricing`, `Validation`, `Quote`).
- **Impact**: The initial Javascript bundle only contains the React runtime, standard layout shells (Sidebar/Nav), and the global CSS. Feature-specific code (like complex forms or specific data tables) is only downloaded when the user actually navigates to that route.

## 2. Suspense and Skeleton Fallbacks
- **Implementation**: `<Suspense fallback={<Skeleton />}>` wraps every lazy-loaded route.
- **Impact**: Eliminates blank white screens during chunk loading. Users perceive the application as instantly responsive.

## 3. Data Caching (TanStack Query)
- **Implementation**: `queryClient.ts` configured with `refetchOnWindowFocus: false` and `staleTime` defaults.
- **Impact**: Prevents redundant network requests to the backend. If a user navigates from `/bom` to `/pricing` and back to `/bom`, the BOM data renders instantly from cache while validating in the background.

## 4. Download Streaming
- **Implementation**: The Quote / Export page does NOT attempt to download binary files (PDF/Excel) into JS memory via Axios. Instead, it generates a direct backend URL and assigns it to an invisible `<a>` tag, triggering the native browser download manager.
- **Impact**: Prevents frontend memory exhaustion when exporting massive configurations or BOMs.

## 5. CSS Optimization
- **Implementation**: Tailwind V4 (via `@tailwindcss/vite`) scans the codebase and generates only the exact CSS classes used.
- **Impact**: Eliminates unused CSS, resulting in a microscopic stylesheet footprint.
