# Frontend Bundle Analysis Report

This report summarizes the output of the Vite/Rollup compilation process for the Elevator Configurator Frontend. 
Generated via `rollup-plugin-visualizer`.

## Overall Statistics
- **Total Initial JS Bundle Size (index.js)**: ~292 KB (uncompressed) / ~91 KB (gzipped)
- **CSS Bundle Size**: ~57 KB (uncompressed) / ~10 KB (gzipped)
- **Total App Size (excluding fonts/assets)**: ~412 KB (gzipped)

## Largest Chunks
1. `index-NUq2Q_g3.js` (292 KB)
   - Contains React, ReactDOM, TanStack Query, Zustand, Axios, and React Router.
   - *Optimization Opportunity*: Moving TanStack Query or Axios into a separate vendor chunk.
2. `Wizard-Y2x-bSow.js` (94 KB)
   - Contains React Hook Form and Zod.
   - *Status*: Appropriately chunked and lazy-loaded only when the user navigates to `/wizard`.
3. `card-Txd8N8km.js` (92 KB)
   - Contains shared Radix primitives and Shadcn components.

## Duplicate Libraries
- **Zero duplicates detected**. The `npm ci` process resolved all peer dependencies correctly without installing conflicting versions of React or Lucide.

## Tree Shaking Summary
Vite (via Rollup) successfully stripped unused Lucide icons. Instead of bundling all 1,000+ icons (which would be > 2 MB), the build only includes the specific imports (e.g., `Settings`, `AlertCircle`, `Inbox`), drastically reducing the final bundle weight. 

## Conclusion
The frontend bundle is highly optimized. The initial load payload (91 KB JS + 10 KB CSS) is well within the acceptable bounds for a highly interactive Web App.
