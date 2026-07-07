# Project Conventions

## Naming Conventions

### Python

| What | Convention | Example |
|------|-----------|---------|
| Modules | `snake_case` | `data_loader.py` |
| Classes | `PascalCase` | `JSONRepository` |
| Functions | `snake_case` | `get_all()` |
| Constants | `UPPER_SNAKE_CASE` | `REQUEST_ID_HEADER` |
| Enums | `PascalCase` class, `UPPER_SNAKE_CASE` values | `HealthStatus.HEALTHY` |
| Private methods | `_snake_case` (single underscore) | `_read()` |
| Type aliases | `PascalCase` | `RecordType = dict[str, Any]` |

### File Naming

| What | Convention |
|------|-----------|
| Endpoint files | noun, singular or plural based on resource | `health.py`, `components.py` |
| Service files | `{noun}_service.py` | `configuration_service.py` |
| Repository files | `{noun}_repository.py` | `json_repository.py` |
| Test files | `test_{module_name}.py` | `test_data_loader.py` |

## Coding Standards

### Type Hints
All functions must have complete type hints. No `-> None` omissions. No bare `Any` without a comment explaining why.

```python
# ✅ Correct
def get_by_id(self, record_id: str) -> dict[str, Any] | None:
    ...

# ❌ Wrong
def get_by_id(self, record_id):
    ...
```

### Docstrings
Every class and every public method has a docstring.
Use Google-style for multi-parameter functions.

```python
def load(self, filename: str) -> list | dict:
    """
    Return parsed JSON content for filename.

    Args:
        filename: Base filename (e.g. "components.json").

    Returns:
        Parsed JSON as a list or dict.

    Raises:
        DataFileNotFoundException: File does not exist.
    """
```

### Exception Handling
Never catch bare `Exception` without re-raising or logging with context.
Always raise domain exceptions — never bubble raw `OSError` or `json.JSONDecodeError`.

```python
# ✅ Correct
try:
    data = json.loads(content)
except json.JSONDecodeError as exc:
    raise DataFormatException(message="...", details={...}) from exc

# ❌ Wrong
try:
    data = json.loads(content)
except Exception:
    pass
```

### No Magic Strings
All string constants must come from `app/core/constants.py`.

```python
# ✅ Correct
from app.core.constants import REQUEST_ID_HEADER
response.headers[REQUEST_ID_HEADER] = request_id

# ❌ Wrong
response.headers["X-Request-ID"] = request_id
```

### Configuration Access
Never call `os.getenv()`. Use `get_settings()` or `Depends(get_settings)`.

```python
# ✅ Correct (FastAPI DI)
async def my_route(settings: Settings = Depends(get_settings)):
    path = settings.DATA_DIR

# ✅ Correct (outside FastAPI)
settings = get_settings()
path = settings.DATA_DIR

# ❌ Wrong
path = os.getenv("DATA_DIR", "app/data")
```

## Git Conventions

### Branch Naming
```
feature/milestone-1-component-catalogue
bugfix/health-endpoint-uptime-calculation
docs/add-request-flow-diagram
```

### Commit Messages
```
feat(components): add ComponentRepository with get_by_type filter
fix(startup): handle missing pricing.json with clear error message
test(data_loader): add edge case for empty JSON array
docs(architecture): add rule engine flow diagram
refactor(health): extract _check_data_files into separate function
```

## Testing Conventions

- One test class per concept being tested.
- Test method names start with `test_` and describe the scenario in plain English.
- Use `pytest.raises` with `exc_info` to inspect exception details.
- Never test private methods directly — test through the public interface.
- Session-scoped fixtures for the expensive test client; `tmp_path` for file isolation.
