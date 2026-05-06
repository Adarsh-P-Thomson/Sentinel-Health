# ⚡ Backend Quick Start

Get the FastAPI backend running in under 3 minutes.

## Prerequisites

- Python 3.10+
- PostgreSQL running on localhost:5432
- MongoDB running on localhost:27017

## Setup Steps

### 1. Navigate to Backend Directory
```bash
cd Backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell)**:
```bash
venv\Scripts\Activate.ps1
```

**Windows (CMD)**:
```bash
venv\Scripts\activate.bat
```

**macOS/Linux**:
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

**Installation time**: ~2-3 minutes

### 5. Configure Environment

The `.env` file is already created with default values. Update PostgreSQL password:

```bash
# Edit .env file
# Change POSTGRES_PASSWORD=postgres123 to your actual password
```

### 6. Start Server
```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 7. Test Health Endpoints

Open your browser or use curl:

**Basic Health**:
```bash
curl http://localhost:8000/api/v1/health
```

**PostgreSQL Health**:
```bash
curl http://localhost:8000/api/v1/health/postgres
```

**MongoDB Health**:
```bash
curl http://localhost:8000/api/v1/health/mongodb
```

**All Databases**:
```bash
curl http://localhost:8000/api/v1/health/databases
```

### 8. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### PostgreSQL Connection Failed

```bash
# Check if PostgreSQL is running
# Windows:
pg_ctl status

# macOS/Linux:
sudo systemctl status postgresql
```

Update `.env` with correct credentials:
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_actual_password
```

### MongoDB Connection Failed

```bash
# Check if MongoDB is running
# Windows:
mongod --version

# macOS/Linux:
sudo systemctl status mongod
```

### Module Not Found Errors

```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Port 8000 Already in Use

```bash
# Run on different port
uvicorn app.main:app --reload --port 8001
```

## Next Steps

1. ✅ Backend is running
2. 🗄️ Set up databases (see `/DOCS/DB/`)
3. 🔧 Configure external APIs (Twitter, OpenAI)
4. 🚀 Start building features

## Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint |
| `/api/v1/health` | GET | Basic health check |
| `/api/v1/health/postgres` | GET | PostgreSQL connectivity |
| `/api/v1/health/mongodb` | GET | MongoDB connectivity |
| `/api/v1/health/databases` | GET | All databases status |
| `/api/v1/health/detailed` | GET | Detailed system info |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc documentation |

---

**Estimated Setup Time**: 3-5 minutes  
**Last Updated**: May 6, 2026
