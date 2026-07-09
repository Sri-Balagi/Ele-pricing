# Frontend API Contract Mapping

This table illustrates the direct relationship between Backend REST Endpoints and the Frontend UI. It proves that all data requirements are satisfied by the Version 1.0.0 API.

| Backend Endpoint | Frontend API Wrapper | React Query Hook (Type) | UI Page | Displayed Components |
| :--- | :--- | :--- | :--- | :--- |
| `GET /health` | `healthApi.getLiveness` | `useQuery(["liveness"])` | `AppLayout` | `StatusBar` (Color indicator) |
| `GET /system/pipeline` | `systemApi.getPipelineDiagnostics` | `useQuery(["systemPipeline"])` | `Dashboard` | `Card` (Uptime, Execution counts) |
| `POST /configurations` | `configurationApi.create` | `useMutation()` | `Wizard` | `Button` (Submit form) |
| `PUT /configurations/{id}` | `configurationApi.update` | `useMutation()` | `Wizard` | `Button` (Update form) |
| `GET /configurations/{id}` | `configurationApi.get` | `useQuery(["bom", id])` | `BOM` | `DataTable` (BOM Items) |
| `GET /configurations/{id}/pricing`| `configurationApi.getPricing` | `useQuery(["pricing", id])` | `Pricing` | `Card`, `Switch` (Pre/Post tax) |
| `GET /configurations/{id}/validation` | `configurationApi.getValidation` | `useQuery(["validation", id])`| `Validation` | `DataTable` (Violations) |
| `GET /configurations/{id}/quote`| `quoteApi.getQuoteInfo` | `useQuery(["quote", id])` | `Quote` | `Card` (Metadata) |
| `GET /configurations/{id}/export/{format}` | `exportApi.getExportUrl` | Native Browser DL (`<a>`) | `Quote` | `Button` (JSON/PDF/Excel) |
