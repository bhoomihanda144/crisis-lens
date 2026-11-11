# CrisisLens Backend Service

Trust-Aware Emergency Intelligence System - Backend, Database & Integration Layer.

## Role Responsibility
**Member 2: Backend, Database and Integration Lead**
- FastAPI REST API architecture and endpoints
- Supabase PostgreSQL schema, migrations, and database connection pooling
- Integration between Frontend, AI Engine, and Data Services

---

## Architecture & Directory Structure

```
backend/
│
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # FastAPI application entrypoint
│   ├── core/                 # App configuration, security, constants
│   ├── database/             # Supabase & PostgreSQL client / session
│   ├── models/               # Database ORM models (SQLAlchemy / Supabase)
│   ├── schemas/              # Pydantic validation schemas (request/response)
│   ├── routers/              # API route controllers (endpoints)
│   ├── services/             # Core business logic and external integrations
│   └── utils/                # Helper functions, logger, formatters
│
├── tests/                    # Unit and integration test suites
│   └── __init__.py
│
├── .env.example              # Template for environment variables
├── .gitignore                # Git ignore rules for Python & venv
├── requirements.txt          # Python dependencies
└── README.md                 # Backend documentation
```

---

## Environment Setup Instructions (Windows PowerShell)

### 1. Prerequisites
- **Python**: Python 3.11+ (verified compatible: Python 3.14.10)
- **PowerShell**: Windows PowerShell
- **Git**: Configured for `feature/backend` branch

### 2. Navigate to Backend Directory
```powershell
cd backend
```

### 3. Virtual Environment
The virtual environment is created in `backend/venv`.

To activate the virtual environment in Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

> **Note**: If PowerShell shows an `ExecutionPolicy` restriction, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

To verify activation:
```powershell
python --version
pip --version
```

### 4. Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Fill in your Supabase database credentials and API keys in `.env`.

### 5. Running the API Server (Development)
```powershell
uvicorn app.main:app --reload --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive API Docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API Docs (ReDoc): `http://localhost:8000/redoc`
