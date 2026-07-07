# Request Flow — Step-by-Step Trace

## Example: GET /api/v1/health

```
Browser / API Client
     │
     │  GET /api/v1/health
     ▼
─────────────────────────────────────────────────
MIDDLEWARE LAYER
─────────────────────────────────────────────────
     │
     ▼  RequestLoggingMiddleware.dispatch()
     │    - Generates unique request_id (UUID)
     │    - Records start_time
     │    - Passes request to next handler
     │
     ▼  CORSMiddleware
     │    - Validates Origin header
     │    - Adds CORS headers to response
     │
─────────────────────────────────────────────────
FASTAPI ROUTING
─────────────────────────────────────────────────
     │
     ▼  FastAPI matches route to health_check()
     │    - Injects Settings via Depends(get_settings)
     │
─────────────────────────────────────────────────
API LAYER  app/api/v1/endpoints/health.py
─────────────────────────────────────────────────
     │
     ▼  health_check(settings)
     │    - Calls _check_data_files(settings)
     │       └── Creates DataLoader(data_dir)
     │           └── Calls validate_all()
     │               └── For each DataFile enum:
     │                   └── DataLoader._read(filename)
     │                       └── Path.exists() check
     │                       └── file.read_text()
     │                       └── json.loads()
     │    - Calculates uptime_seconds
     │    - Determines HealthStatus (healthy/degraded)
     │    - Constructs HealthResponse Pydantic model
     │    - Returns HealthResponse
     │
─────────────────────────────────────────────────
FASTAPI SERIALIZATION
─────────────────────────────────────────────────
     │
     ▼  FastAPI serializes HealthResponse → JSON
     │
─────────────────────────────────────────────────
MIDDLEWARE LAYER (return path)
─────────────────────────────────────────────────
     │
     ▼  RequestLoggingMiddleware (return)
     │    - Adds X-Request-ID header to response
     │    - Logs: "GET /api/v1/health → 200 (5.2 ms) [uuid]"
     │
     ▼  Response returned to client
```

## Example: Future POST /api/v1/configurations (Milestone 5)

```
Browser / API Client
     │
     │  POST /api/v1/configurations
     │  Body: { elevator_type, selected_features, selected_components }
     ▼
─────────────────────────────────────────────────
MIDDLEWARE LAYER (same as above)
─────────────────────────────────────────────────
     │
─────────────────────────────────────────────────
API LAYER  endpoints/configuration.py
─────────────────────────────────────────────────
     │
     ▼  create_configuration(request: ConfigurationRequest)
     │    - Pydantic validates ConfigurationRequest schema
     │    - Calls ConfigurationService.create(request_data)
     │
─────────────────────────────────────────────────
SERVICE LAYER  services/configuration_service.py
─────────────────────────────────────────────────
     │
     ▼  ConfigurationService.create(data)
     │    - Validates component IDs via ComponentRepository
     │    - Sends to RuleEngine.evaluate(components, rules)
     │    - Sends to DependencyEngine.resolve(components, dependencies)
     │    - Sends to PricingEngine.calculate(components, pricing)
     │    - Assembles ConfigurationResult domain model
     │    - Returns ConfigurationResult
     │
─────────────────────────────────────────────────
API LAYER (return)
─────────────────────────────────────────────────
     │
     ▼  Maps ConfigurationResult → ConfigurationResponse schema
     ▼  Returns SuccessResponse(data=configuration_response)
```

## Error Flow

```
Any layer raises ElevatorBaseException (e.g. InvalidComponentException)
     │
     ▼  FastAPI calls elevator_exception_handler()  [app/__init__.py]
     │    - Logs the error with path and details
     │    - Returns JSONResponse(status_code=422, content=ErrorResponse)
     │
     ▼  Client receives:
        {
          "success": false,
          "error_code": "INVALID_COMPONENT",
          "message": "Component 'C999' does not exist.",
          "details": { "requested_id": "C999" }
        }
```
