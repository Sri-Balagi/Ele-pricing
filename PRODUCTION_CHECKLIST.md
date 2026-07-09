# Production Readiness Checklist

Before signing off on the production deployment, verify the following checks have been completed.

## 1. Application Security
- [ ] No secrets or API keys are hardcoded in the frontend or backend repositories.
- [ ] Docker images are built using minimal base images (`alpine`, `slim`).
- [ ] Cross-Origin Resource Sharing (CORS) is configured strictly in FastAPI for the production domain.

## 2. Monitoring & Logging
- [ ] Backend is outputting structured JSON logs suitable for ingestion by Datadog / ELK.
- [ ] Frontend monitoring service (`monitoring.ts`) is configured to capture uncaught exceptions.
- [ ] Health endpoints (`/api/v1/health`) are being actively polled by an external uptime service (e.g., Pingdom, BetterStack).

## 3. Performance
- [ ] NGINX is serving the frontend static files with correct GZIP/Brotli compression and `Cache-Control` headers.
- [ ] The Vite build report confirms the initial JS bundle is under 150KB gzipped.
- [ ] Backend API endpoints respond within the performance budget (<200ms p95).

## 4. CI/CD Pipeline
- [ ] GitHub actions are enforcing OpenAPI drift protection successfully.
- [ ] Playwright E2E tests are passing on the `main` branch.
- [ ] Vitest component/hook tests are passing with acceptable coverage.

## 5. Operations
- [ ] Deployment guide has been successfully executed in a staging environment.
- [ ] Rollback procedures are documented.
