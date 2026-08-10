# Backend — AgriGuardian AI FastAPI Service

## Overview

The backend is a **FastAPI** application providing:
- REST API for all data domains
- WebSocket for real-time dashboard updates
- MQTT subscriber for IoT sensor data ingestion
- AI Decision Engine integration
- External API aggregation (weather, market, schemes, disaster)

## Folder Structure

```
backend/
├── app/
│   ├── main.py              ← Application factory
│   ├── api/v1/              ← All API routes
│   ├── core/                ← Config, security, database
│   ├── services/            ← Business logic, external APIs
│   ├── models/              ← SQLAlchemy ORM models
│   ├── schemas/             ← Pydantic validation schemas
│   ├── repositories/        ← Database query layer
│   ├── utils/               ← Helper functions
│   └── tasks/               ← Background scheduled tasks
├── alembic/                 ← Database migrations
├── tests/                   ← Unit + integration tests
├── scripts/                 ← Utility scripts
└── Dockerfile
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
uvicorn src.api.main:app --reload
```

## API Documentation

After starting the server, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Environment Variables

See [../.env.example](../.env.example) for all required variables.

## Testing

```bash
pytest tests/ --cov=app --cov-report=html
```
