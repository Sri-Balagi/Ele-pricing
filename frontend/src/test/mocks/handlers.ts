import { http, HttpResponse } from "msw";

export const handlers = [
  // Health
  http.get("/api/v1/health", () => {
    return HttpResponse.json({
      status: "healthy",
      version: "1.0.0",
      environment: "test",
      uptime_seconds: 1000,
      data_initialized: true,
      pipeline_ready: true,
    });
  }),
  
  // Dashboard Metrics
  http.get("/api/v1/system/pipeline", () => {
    return HttpResponse.json({
      registered_engines: ["rule", "dependency"],
      catalogue_version: "v1",
      schema_version: "v1",
      startup_timestamp: "2026-07-08",
      ready: true,
      startup_metrics: {
        application_startup_duration_ms: 100,
        repository_initialization_ms: 20,
        registry_initialization_ms: 10,
        pipeline_initialization_ms: 70
      },
      runtime_metrics: {
        uptime_seconds: 5000,
        total_requests_processed: 42,
        pipeline_executions: 12
      }
    });
  }),
  
  // Configuration Create
  http.post("/api/v1/configurations", async () => {
    return HttpResponse.json({
      success: true,
      data: {
        configuration_id: "CFG-TEST-123",
        status: "DRAFT",
        selected_category: "TEST_CAT",
        selected_feature_options: []
      },
      timestamp: new Date().toISOString()
    }, { status: 201 });
  })
];
