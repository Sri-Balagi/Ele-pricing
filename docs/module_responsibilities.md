# Module Responsibilities

## The Golden Rule

> Every module has **one job**. If you cannot state what a module does in one sentence, split it.

---

## `app/core/`

| File | Owns | Must NOT |
|------|------|---------|
| `config.py` | Reading + caching all configuration from `.env` | Contain business logic or data access |
| `constants.py` | All enums and string constants | Import from any other app module |
| `exceptions.py` | Custom exception classes with error codes | Handle exceptions (that's `app/__init__.py`) |
| `logging_config.py` | Logger initialization via `dictConfig` | Be called more than once |
| `startup.py` | Startup validation and lifespan hooks | Contain API or service logic |

## `app/schemas/`

| File | Owns |
|------|------|
| `base.py` | `SuccessResponse`, `ErrorResponse` |
| `health.py` | `HealthResponse`, `DataFilesStatus` |
| *(milestone)* `components.py` | `ComponentResponse`, `ComponentListResponse` |

Schemas are **API contracts only**. They may not contain business logic.

## `app/models/`

Internal domain entities. These are **never** returned directly from API routes.
A service maps a model to a schema before returning it to the API layer.

## `app/repositories/`

| File | Owns |
|------|------|
| `base.py` | `BaseRepository[T]` abstract interface |
| `json_repository.py` | File-backed implementation of `BaseRepository` |

Repositories may **only** access data. No business logic, no rule evaluation.

## `app/utils/`

| File | Owns |
|------|------|
| `data_loader.py` | File I/O, JSON parsing, in-memory cache |

DataLoader is injected into repositories. It does not know about domain models.

## `app/services/`

Services orchestrate. They:
- Call repositories to fetch data.
- Call engines (rule, dependency, pricing) to transform data.
- Return domain models (not raw dicts, not API schemas).
- Never import from `app/api/`.

## `app/api/v1/`

Routes are **thin**:
1. Parse and validate the request using schemas.
2. Call one service method.
3. Map the result to a response schema.
4. Return the schema.

No `if` statements containing business logic. No direct repository calls.

## `app/middleware/`

Cross-cutting concerns only: logging, tracing, auth headers.

## `app/rules/`, `app/pricing/`, `app/dependency_engine/`, `app/config_engine/`

Domain algorithm packages. Implemented in later milestones.
They receive data from services and return results. They never touch the API layer.
