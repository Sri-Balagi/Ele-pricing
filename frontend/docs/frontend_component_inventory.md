# Frontend Component Inventory

This document lists the reusable components located within the `src/components/` directory.

## 1. `DataTable` (`src/components/DataTable.tsx`)
- **Purpose**: Generic tabular data renderer.
- **Props**:
  - `data: T[]` - Array of generic data objects.
  - `columns: ColumnDef<T>[]` - Definition array dictating headers, alignment, and cell renderers.
  - `emptyTitle?: string` - Title to display when `data` is empty.
  - `emptyDescription?: string` - Description for the empty state.
- **Dependencies**: Shadcn `Table` primitives, `EmptyState` component.
- **Reuse Locations**: `BOM.tsx`, `Validation.tsx`.

## 2. `EmptyState` (`src/components/EmptyState.tsx`)
- **Purpose**: Visual placeholder for empty lists or uninitialized states.
- **Props**:
  - `title: string` - Primary heading.
  - `description?: string` - Secondary detail text.
  - `icon?: React.ReactNode` - Custom Lucide icon (Defaults to `<Inbox>`).
  - `action?: React.ReactNode` - Optional CTA button/element.
- **Dependencies**: Lucide React.
- **Reuse Locations**: `Wizard.tsx`, `DataTable.tsx`.

## 3. `ErrorBoundary` (`src/components/ErrorBoundary.tsx`)
- **Purpose**: Global exception catcher to prevent React tree unmounts.
- **Props**:
  - `children?: ReactNode` - Wrapped components.
  - `fallback?: ReactNode` - Optional custom fallback UI.
- **Dependencies**: React Class Component APIs.
- **Reuse Locations**: `App.tsx` (wraps the main Router).

## 4. `Skeletons` (`src/components/Skeletons.tsx`)
- **Purpose**: Loading placeholders matching specific layout structures.
- **Exports**:
  - `TableSkeleton(rows?: number)`: Simulates a data table.
  - `CardSkeleton()`: Simulates a generic Card.
  - `WizardSkeleton()`: Simulates the Wizard view.
- **Dependencies**: Shadcn `Skeleton`, `Card`.
- **Reuse Locations**: `Dashboard.tsx`, `Pricing.tsx`, `BOM.tsx`, `App.tsx` (Suspense fallbacks).

## 5. Shadcn UI Primitives (`src/components/ui/*`)
- **Purpose**: Base design system building blocks.
- **Key Components**: `Button`, `Input`, `Card`, `Badge`, `Dialog`, `Select`, `Table`, `Sonner` (Toasts).
- **Dependencies**: Radix UI Primitives, TailwindCSS, `clsx`, `tailwind-merge`.
- **Reuse Locations**: Universally used across all Pages and Layouts.
