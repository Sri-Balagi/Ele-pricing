# Elevator Configuration & Pricing Engine

A **Rule-Based CPQ (Configure-Price-Quote) Engine** for industrial elevator manufacturing.

Configures elevators, validates engineering constraints, resolves component dependencies, and calculates dynamic pricing — all driven by data files, not hardcoded logic.

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Git

### Backend

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

→ API: http://127.0.0.1:8000  
→ Swagger: http://127.0.0.1:8000/docs

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

→ UI: http://localhost:5173

### Tests

```powershell
cd backend
uv run pytest tests/ -v
```

---

## Project Structure

```
Ele-pricing/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # HTTP routes (thin — no business logic)
│   │   ├── core/            # Config, constants, exceptions, logging
│   │   ├── schemas/         # API request/response Pydantic models
│   │   ├── models/          # Internal domain entities
│   │   ├── repositories/    # Data-access abstraction (JSON → SQL-swappable)
│   │   ├── services/        # Business logic orchestration
│   │   ├── rules/           # Rule engine
│   │   ├── pricing/         # Pricing engine
│   │   ├── dependency_engine/ # Dependency resolution
│   │   ├── config_engine/   # Configuration assembly
│   │   ├── validators/      # Constraint validation
│   │   ├── middleware/      # Request logging, CORS
│   │   ├── utils/           # DataLoader, helpers
│   │   └── data/            # JSON data files
│   └── tests/               # pytest test suite
├── frontend/                # React + TypeScript + Vite + Tailwind
└── docs/                    # Architecture, conventions, setup
```

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI + Python 3.12 |
| ASGI Server | Uvicorn |
| Validation | Pydantic v2 |
| Settings | pydantic-settings |
| Frontend | React + TypeScript + Vite + Tailwind CSS |
| Data Storage | JSON files (SQL-swappable via Repository pattern) |
| Testing | pytest |
| Linting | Ruff + Black |

---

## Elevator Types

| Type | Description |
|------|-------------|
| **Type A** | Standard elevators — fixed feature set |
| **Type B** | Configurable — mixed fixed and customizable features |
| **Type C** | Specialized — strict engineering constraints |
| **Type D** | Highly Customizable — Ultimate luxury and smart features |

---

To run the full platform using Docker:

```bash
docker compose up -d
```

- The UI will be available at `http://localhost:80`
- The API will be available at `http://localhost:8000`

## Milestones Overview

| Milestone | Feature |
|-----------|---------|
| **Setup** ✅ | Project structure, FastAPI, tests, tooling |
| **M1** ✅ | Product Domain Modeling & Component Catalogue (9 entities, referential integrity) |
| **M2** ✅ | Rule engine (10 engineering rules) |
| **M3** ✅ | Dependency resolution engine |
| **M4** ✅ | Dynamic pricing engine |
| **M5** ✅ | Full configuration API |
| **M6** ✅ | Configuration export & BOM |
| **M7** ✅ | Frontend UI (Configurator Wizard) |
| **M8** ✅ | Realistic Data & Validation Mappings |
| **M9** ✅ | Final Polish & Production Readiness |

---

## Documentation

- [Architecture](docs/architecture.md)
- [Module Responsibilities](docs/module_responsibilities.md)
- [Request Flow](docs/request_flow.md)
- [Conventions](docs/conventions.md)
- [Setup Instructions](docs/setup_instructions.md)

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Application health check |
| `POST` | `/api/v1/configurations` | Create a new configuration |
| `GET` | `/api/v1/configurations/{id}` | Retrieve a configuration |
| `PUT` | `/api/v1/configurations/{id}` | Update feature selections |
| `POST` | `/api/v1/configurations/{id}/validate` | Validate and generate BOM |
| `GET` | `/api/v1/configurations/{id}/export/{format}` | Export configuration (PDF, Excel, JSON) |
| `GET` | `/api/v1/catalogue/categories` | Retrieve available elevator categories |
| `GET` | `/docs` | Interactive Swagger API UI |
| `GET` | `/redoc` | Interactive ReDoc API UI |

---

## Design Principles

- **Data-driven** — all business data in JSON files, zero hardcoded logic
- **Repository pattern** — swap JSON for SQL without touching services
- **Fail-fast startup** — validates all data files before accepting requests
- **Consistent API responses** — every endpoint returns `SuccessResponse` or `ErrorResponse`
- **Custom exception hierarchy** — typed exceptions with HTTP status codes
