# Setup Instructions

## Prerequisites

| Tool | Minimum Version | Check |
|------|----------------|-------|
| Python | 3.12 | `python --version` |
| Node.js | 18.x | `node --version` |
| npm | 9.x | `npm --version` |
| Git | Any | `git --version` |

---

## Backend Setup

### 1. Clone and navigate
```powershell
git clone <repo-url>
cd Ele-pricing
```

### 2. Create virtual environment
```powershell
cd backend
python -m venv .venv
```

### 3. Activate virtual environment
```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

### 4. Install dependencies
```powershell
pip install -r requirements.txt
```

### 5. Configure environment
```powershell
# Copy the example file
copy .env.example .env
# Edit .env if needed (defaults work for local development)
```

### 6. Start the development server
```powershell
# From the backend/ directory with venv active
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### 7. Run the test suite
```powershell
# From the backend/ directory with venv active
pytest tests/ -v
```

---

## Frontend Setup

### 1. Navigate to frontend
```powershell
cd Ele-pricing/frontend
```

### 2. Install dependencies
```powershell
npm install
```

### 3. Start the dev server
```powershell
npm run dev
```

The frontend will be available at: http://localhost:5173

---

## Code Quality

### Run linter
```powershell
cd backend
ruff check .
```

### Run formatter check
```powershell
black --check .
```

### Auto-fix lint + format
```powershell
ruff check . --fix
black .
```

### Install pre-commit hooks (optional but recommended)
```powershell
# From repo root
pip install pre-commit
pre-commit install
```

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_VERSION` | `0.1.0` | Application version string |
| `ENVIRONMENT` | `development` | Runtime environment |
| `DEBUG` | `True` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Minimum log level |
| `LOG_DIR` | `logs` | Log file directory |
| `LOG_MAX_BYTES` | `10485760` | Max log file size (10 MB) |
| `LOG_BACKUP_COUNT` | `5` | Number of rotated log files |
| `API_V1_PREFIX` | `/api/v1` | API version 1 URL prefix |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins |
| `DATA_DIR` | `app/data` | JSON data files directory |

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'app'`
Ensure you are running commands from the `backend/` directory with the venv activated.

### `RuntimeError: Startup validation failed`
One or more JSON data files in `app/data/` are missing or malformed.
Check that all five files exist: `components.json`, `features.json`, `dependencies.json`, `rules.json`, `pricing.json`.

### `uvicorn: command not found`
The virtual environment is not activated. Run `.venv\Scripts\Activate.ps1` first.

### Tests failing with `DataFileNotFoundException`
The test fixtures create their own temporary data directory.
If tests fail, check `tests/conftest.py` — the `tmp_data_dir` fixture must create all 5 files.
