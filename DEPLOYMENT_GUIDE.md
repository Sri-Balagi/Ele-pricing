# Deployment Guide

This guide outlines the steps for deploying Version 1.0.0 of the Elevator Configuration & Pricing Engine to a production environment.

## 1. Prerequisites
- Docker Engine & Docker Compose installed on the host machine.
- Minimum 2GB RAM / 2 vCPUs recommended for combined workloads.
- Open Port 80 for HTTP traffic (or Port 443 with a reverse proxy).

## 2. Environment Configuration
Create a `.env` file in the root directory (do not commit this file to version control).
```env
# Backend Settings
ENVIRONMENT=production
LOG_LEVEL=info

# Example future integrations
# DATABASE_URL=postgresql://user:pass@host:5432/db
# SENTRY_DSN=...
```

## 3. Launching the Platform (Docker Compose)
The provided `docker-compose.yml` orchestrates both the Python FastAPI backend and the NGINX React frontend.

```bash
# Build the production images
docker compose build

# Start the platform in detached mode
docker compose up -d
```

## 4. Verification
1. **Frontend Status**: Navigate to `http://<your-server-ip>/`. The Dashboard should load and the System Status bar at the bottom should show "Healthy" (Green).
2. **Backend API**: Navigate to `http://<your-server-ip>:8000/api/v1/health`. It should return a JSON object confirming `status: healthy`.
3. **Logs**: Check logs for any startup errors.
```bash
docker compose logs -f
```

## 5. Scaling (Future)
The backend is completely stateless (currently using file-system / mock DBs). To scale the API horizontally behind a load balancer, modify the docker-compose settings to include `replicas: 3` and map it through a reverse proxy like Traefik or an AWS ALB.
