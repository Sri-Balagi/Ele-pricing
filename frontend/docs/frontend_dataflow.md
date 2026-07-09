# Frontend Dataflow Diagrams

This document illustrates the standardized flow of data through the frontend application architecture.

## Primary Configuration Dataflow

This represents the path of user input triggering a backend state change and re-rendering the UI.

```text
[User Action] (Clicks "Update Configuration" in Wizard)
      ↓
[React Hook Form] (Validates input against Zod schema)
      ↓
[TanStack Mutation] (Calls configurationApi.update)
      ↓
[Axios Client] (Constructs HTTP PUT request)
      ↓
[Backend API] (Receives request at /api/v1/configurations/{id})
      ↓
[Configuration Pipeline] (Rule Engine -> Dependency Engine -> Pricing -> BOM)
      ↓
[Response] (Returns APISuccessEnvelope with updated config)
      ↓
[Axios Interceptor] (Unwraps data, attaches x-correlation-id)
      ↓
[TanStack Cache] (Invalidates stale data, caches new response)
      ↓
[React Components] (Triggered to re-render with fresh data)
      ↓
[Rendered UI] (User sees updated Quote / BOM / Pricing)
```

## Theme Preference Dataflow

```text
[User Action] (Toggles Dark Mode)
      ↓
[Zustand Store] (Updates `theme` state in uiStore)
      ↓
[Zustand Persist Middleware] (Writes to localStorage 'ui-storage')
      ↓
[React Layout] (Applies 'dark' class to <html> tag)
      ↓
[TailwindCSS / Shadcn] (CSS Variables swap to Dark Mode palettes)
```

## Routing Dataflow

```text
[User Action] (Clicks "Validation" in Sidebar)
      ↓
[React Router] (Intercepts navigation event)
      ↓
[Suspense] (Displays WizardSkeleton fallback while chunk loads)
      ↓
[React.lazy] (Fetches Validation.tsx JS chunk)
      ↓
[Page Mounts] (Triggers TanStack useQuery for validation data)
      ↓
[UI Renders] (Data table populates with violations)
```

## Download / Export Dataflow

```text
[User Action] (Clicks "Export as PDF" in Quote Page)
      ↓
[React Component] (Invokes handleDownload('pdf'))
      ↓
[Export API Module] (Generates direct backend URL via exportApi.getExportUrl)
      ↓
[DOM Manipulation] (Creates invisible <a> tag with href, triggers click)
      ↓
[Browser Native] (Issues GET request directly to backend)
      ↓
[Backend] (Streams PDF File)
      ↓
[User OS] (Downloads file via standard browser download manager)
```
