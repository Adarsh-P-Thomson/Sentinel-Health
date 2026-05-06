# Sentinel Health - Backend API

FastAPI backend for the Sentinel Health patient safety monitoring platform.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- MongoDB 6.0+
- Redis (optional, for caching)

### Installation

```bash
# Navigate to backend directory
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update database credentials in `.env`:
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sentinel_health
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here

MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=sentinel_health
```

### Run Development Server

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏥 Health Check Endpoints

### Basic Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### PostgreSQL Health Check
```bash
curl http://localhost:8000/api/v1/health/postgres
```

### MongoDB Health Check
```bash
curl http://localhost:8000/api/v1/health/mongodb
```

### All Databases Health Check
```bash
curl http://localhost:8000/api/v1/health/databases
```

### Detailed System Health Check
```bash
curl http://localhost:8000/api/v1/health/detailed
```

## 📁 Project Structure

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   └── health.py        # Health check endpoints
│   ├── core/                # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py        # Settings management
│   │   └── database.py      # Database connections
│   ├── models/              # SQLAlchemy & Pydantic models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── .env                     # Environment variables (not in git)
├── .env.example             # Example environment file
├── .gitignore
├── requirements.txt         # Python dependencies
└── README.md
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | Sentinel Health API |
| `ENVIRONMENT` | Environment (development/production) | development |
| `DEBUG` | Debug mode | True |
| `API_PREFIX` | API route prefix | /api/v1 |
| `POSTGRES_HOST` | PostgreSQL host | localhost |
| `POSTGRES_PASSWORD` | PostgreSQL password | postgres123 |
| `MONGODB_HOST` | MongoDB host | localhost |
| `SECRET_KEY` | JWT secret key | (change in production) |

See `.env.example` for complete list.

## 🗄️ Database Setup

### PostgreSQL

```bash
# Create database
psql -U postgres -c "CREATE DATABASE sentinel_health;"

# Apply schema
psql -U postgres -d sentinel_health -f ../DOCS/DB/POSTGRES/schema.sql
```

### MongoDB

```bash
# Apply schema
mongosh < ../DOCS/DB/MONGODB/schema.js
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📦 Dependencies

### Core
- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### Databases
- **SQLAlchemy**: PostgreSQL ORM (async)
- **Motor**: MongoDB async driver
- **Redis**: Caching

### Security
- **python-jose**: JWT tokens
- **passlib**: Password hashing

See `requirements.txt` for complete list.

## 🚢 Production Deployment

### Using Gunicorn + Uvicorn

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Using Docker

```bash
# Build image
docker build -t sentinel-health-api .

# Run container
docker run -p 8000:8000 --env-file .env sentinel-health-api
```

### Environment Variables for Production

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<strong-random-key>
POSTGRES_PASSWORD=<secure-password>
ENABLE_SWAGGER_UI=False
```

## 📊 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Security

- Change `SECRET_KEY` in production
- Use strong database passwords
- Enable SSL for database connections
- Disable Swagger UI in production
- Implement rate limiting
- Use environment-specific configurations

## 📝 Logging

Logs are configured via `LOG_LEVEL` and `LOG_FORMAT` environment variables.

```python
# Available log levels
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR|CRITICAL
```

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run tests
4. Submit pull request

## 📄 License

Proprietary - Sentinel Health Team

---

**Last Updated**: May 6, 2026
