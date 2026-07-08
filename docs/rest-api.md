# REST API Architecture

This document describes the design and contracts of the REST API layer built on top of the frozen Elevator Configuration Engine.

## Architectural Boundaries

The REST layer acts strictly as a transport boundary. It contains **zero business logic**. 
- DTOs map to/from internal `Configuration` models.
- Controllers invoke `ConfigurationPipeline.execute()`.
- Endpoints return standard success/error envelopes.

## Endpoint Catalogue

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness probe |
| `GET` | `/health/ready` | Readiness probe (waits for startup) |
| `GET` | `/health/details` | Engine and pipeline diagnostics |
| `GET` | `/api/v1/system/pipeline` | Detailed pipeline execution state |
| `POST` | `/api/v1/configurations` | Start a new configuration session |
| `GET` | `/api/v1/configurations` | List configurations (paginated) |
| `GET` | `/api/v1/configurations/{id}` | Read configuration state |
| `PUT` | `/api/v1/configurations/{id}` | Update feature selections |
| `POST` | `/api/v1/configurations/{id}/validate`| Trigger Rule/Dependency/Pricing pipeline |
| `GET` | `/api/v1/configurations/{id}/pricing` | Return existing pricing summary |
| `GET` | `/api/v1/configurations/{id}/validation`| Return read-only validation status |
| `DELETE`| `/api/v1/configurations/{id}` | Discard configuration |

## Standard Envelopes

Every successful request uses the `APISuccessEnvelope`:
```json
{
  "success": true,
  "data": { ... payload ... },
  "correlation_id": "PIPE-UUID-...",
  "timestamp": "2026-07-08T00:00:00Z"
}
```

Every failed request uses the `APIErrorEnvelope`:
```json
{
  "success": false,
  "error_code": "PIPELINE_001",
  "message": "Validation failed",
  "correlation_id": "PIPE-UUID-...",
  "timestamp": "2026-07-08T00:00:00Z",
  "details": { ... }
}
```

## Error Matrix

| Error Code | HTTP | Description |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Bad request payload |
| `NOT_FOUND` | 404 | Missing resource |
| `STORE_LIMIT_EXCEEDED` | 503 | Server capacity reached, no eviction targets |
| `RULE_001` | 400 | Business rule violation |
| `DEP_001` | 400 | Dependency constraint violation |
| `PRICE_001` | 400 | Pricing calculation error |
| `PIPELINE_001` | 400 | Execution aborted gracefully by pipeline |

## Correlation ID Lifecycle

1. `RequestLoggingMiddleware` intercepts the request.
2. Checks for `X-Correlation-ID` header; if absent, generates `PIPE-{uuid}`.
3. Injects ID into `request.state.correlation_id`.
4. Endpoint extracts and maps it to `PipelineExecutionReport` or success envelope.
5. Handled by global exception handlers if a fault occurs.
6. Emitted in standard JSON log format.
