<div align="center">

# 🌿 AgriGuardian AI

### One Intelligent Decision Platform for Every Farmer

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)
[![ESP32](https://img.shields.io/badge/IoT-ESP32-E7352C.svg)](https://espressif.com)

*AI + IoT powered precision farming platform built for the modern Indian farmer*

[Documentation](docs/) • [Architecture](docs/architecture/) • [API Reference](docs/api/) • [Hardware Guide](docs/hardware/)

</div>

## Current local MVP startup

The active development database is `backend/agri_guardian.db`; do not use the
empty root-level database file. Apply forward migrations before starting the
backend:

```powershell
cd backend
alembic upgrade head
uvicorn src.api.main:app --reload --port 8000
```

In a second terminal:

```powershell
cd frontend
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

With Docker installed, `docker compose up --build` starts the frontend,
FastAPI backend, SQLite-mounted application data, and local Mosquitto broker.
MQTT broker and physical ESP32 verification remain required before field use.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [System Architecture](#-system-architecture)
3. [Complete Folder Structure](#-complete-folder-structure)
4. [Tech Stack](#-tech-stack)
5. [Installation & Setup](#-installation--setup)
6. [Development Flow](#-development-flow)
7. [Module Roadmap](#-module-roadmap)
8. [Future Expansion](#-future-expansion)
9. [GitHub Workflow](#-github-workflow)
10. [Coding Standards](#-coding-standards)
11. [Contributing](#-contributing)
12. [License](#-license)

---

## 🌾 Project Overview

AgriGuardian AI is a **full-stack, AI-powered precision agriculture platform** that transforms raw sensor data and external signals into actionable farming decisions delivered directly to the farmer's dashboard.

### Core Problem

Indian farmers face three critical bottlenecks:
- **Information overload** — weather, market prices, government schemes, and disaster alerts are fragmented across dozens of sources.
- **Decision uncertainty** — when to irrigate, when to sell, which crop to plant, all require expert knowledge most farmers lack.
- **Reactive farming** — farmers react to problems (pest attacks, crop failure, price crashes) instead of preventing them.

### Solution

AgriGuardian AI creates a **closed-loop intelligence system**:

```
IoT Sensors → Real-time Data → AI Decision Engine → Explainable Recommendations → Farmer Dashboard
       ↑                                                                                    ↓
 Smart Relay ← Automated Irrigation ←─────────────────────────────────── User Approval
```

### Key Features (v1.0)

| Feature | Description |
|---|---|
| 🌱 **Crop Advisory** | AI-personalized crop recommendations based on soil + weather |
| 💧 **Smart Irrigation** | Automated and manual irrigation triggers via relay control |
| 📈 **Market Intelligence** | Real-time price trends + sell/hold recommendations |
| 🚨 **Disaster Alerts** | Flood, drought, pest warnings from multiple alert APIs |
| 🏛️ **Scheme Finder** | Government scheme matching based on farmer profile |
| 🔍 **Explainable AI** | Every recommendation shows reason + confidence score |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AGRIGUARDIAN AI — SYSTEM ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────────────────────────┘

  ┌───────────────────────────────────────────────────────────────────────────┐
  │  LAYER 1: DATA COLLECTION                                                  │
  │                                                                             │
  │   [ESP32 + Sensors]          [External APIs]          [User Input]         │
  │   ├── Soil Moisture          ├── OpenWeatherMap        ├── Crop Selection   │
  │   ├── Temperature (DHT22)    ├── AgMarket Prices       ├── Farm Profile     │
  │   ├── Humidity (DHT22)       ├── Govt Schemes API      └── Location         │
  │   ├── Rain Sensor            └── Disaster Alert API                         │
  │   └── Water Level                                                            │
  └───────────────────────────────────────────────────────────────────────────┘
                │ MQTT over WiFi                   │ REST / WebSocket
                ▼                                  ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │  LAYER 2: BACKEND (FastAPI)                                                │
  │                                                                             │
  │   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                  │
  │   │  IoT Service  │   │ Data Ingestion│   │ External API  │                  │
  │   │  (MQTT Sub)   │   │  Pipeline    │   │  Aggregator   │                  │
  │   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘                  │
  │          └──────────────────┼──────────────────┘                           │
  │                             ▼                                               │
  │   ┌─────────────────────────────────────────────────────────┐              │
  │   │              AI Decision Engine                          │              │
  │   │   ┌────────────┐  ┌────────────┐  ┌────────────┐        │              │
  │   │   │Crop Advisor│  │ Irrigation │  │  Market    │        │              │
  │   │   │  (XGBoost) │  │  Planner   │  │  Analyst   │        │              │
  │   │   └────────────┘  └────────────┘  └────────────┘        │              │
  │   │   ┌────────────┐  ┌─────────────────────────────┐        │              │
  │   │   │ Scheme     │  │ Explainability Engine (SHAP) │        │              │
  │   │   │ Matcher    │  └─────────────────────────────┘        │              │
  │   │   └────────────┘                                         │              │
  │   └─────────────────────────────────────────────────────────┘              │
  │                             │                                               │
  │   ┌──────────────────────── ▼─────────────────────────┐                   │
  │   │              PostgreSQL + Redis Cache              │                   │
  │   └────────────────────────────────────────────────────┘                   │
  └───────────────────────────────────────────────────────────────────────────┘
                                  │ REST API + WebSocket
                                  ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │  LAYER 3: FRONTEND (React + Tailwind + Chart.js)                           │
  │                                                                             │
  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
  │   │Sensor    │  │ AI       │  │ Market   │  │ Disaster │  │ Scheme   │  │
  │   │Dashboard │  │ Advisory │  │ Insights │  │ Alerts   │  │ Finder   │  │
  │   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
  └───────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Sensor Reading → MQTT Publish → FastAPI MQTT Subscriber → Validate & Store (PostgreSQL)
                                         ↓
                            Trigger AI Decision Engine
                                         ↓
              [Crop Model + Irrigation Model + Market Model + Scheme Matcher]
                                         ↓
                           Generate Recommendations + SHAP Explanations
                                         ↓
                     Store to DB → Push via WebSocket → Dashboard
```

---

## 📁 Complete Folder Structure

```
AgriGuardian-AI/                          ← Monorepo Root
│
├── .github/                              ← GitHub Automation
│   ├── workflows/                        ← CI/CD GitHub Actions pipelines
│   ├── ISSUE_TEMPLATE/                   ← Bug report & feature request templates
│   └── PULL_REQUEST_TEMPLATE/            ← PR description templates
│
├── hardware/                             ← All IoT Hardware code and docs
│   ├── esp32/
│   │   ├── firmware/                     ← Main Arduino/PlatformIO source (.ino / .cpp)
│   │   ├── config/                       ← WiFi, MQTT, pin config headers
│   │   └── libraries/                    ← Custom local libraries for sensors
│   ├── schematics/                       ← Circuit diagrams (Fritzing / KiCad)
│   ├── pcb/                              ← PCB layout files
│   └── docs/                             ← Hardware setup guide, wiring diagrams
│
├── backend/                              ← FastAPI Python Backend
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/            ← Route handlers (sensors, advisory, market…)
│   │   │       └── middleware/           ← Auth, logging, rate-limit middleware
│   │   ├── core/                         ← Config, security, startup/shutdown events
│   │   ├── services/
│   │   │   ├── weather/                  ← OpenWeatherMap integration
│   │   │   ├── market/                   ← AgMarket price API integration
│   │   │   ├── schemes/                  ← Government scheme API integration
│   │   │   ├── disaster/                 ← Disaster alert API integration
│   │   │   └── iot/                      ← MQTT subscriber & sensor data ingestion
│   │   ├── models/                       ← SQLAlchemy ORM models
│   │   ├── schemas/                      ← Pydantic request/response schemas
│   │   ├── repositories/                 ← Database query abstractions (Repository pattern)
│   │   ├── utils/                        ← Helpers: date, geo, unit conversion
│   │   └── tasks/                        ← Background tasks (Celery / APScheduler)
│   ├── alembic/                          ← Database migration tool
│   │   └── versions/                     ← Migration version scripts
│   ├── tests/
│   │   ├── unit/                         ← Unit tests for services, models, utils
│   │   ├── integration/                  ← API endpoint integration tests
│   │   └── fixtures/                     ← Shared test data & mock factories
│   ├── scripts/                          ← Backend utility scripts (seed DB, test API)
│   ├── requirements.txt                  ← Production Python dependencies
│   ├── requirements-dev.txt              ← Development dependencies (pytest, black…)
│   ├── pyproject.toml                    ← Project metadata, linting config
│   └── Dockerfile                        ← Backend container definition
│
├── frontend/                             ← React + Tailwind + Chart.js Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/                   ← Shared UI: Button, Card, Badge, Modal…
│   │   │   ├── dashboard/                ← Main dashboard layout & widgets
│   │   │   ├── advisory/                 ← AI recommendation display components
│   │   │   ├── sensors/                  ← Sensor gauge & chart components
│   │   │   ├── market/                   ← Market price chart & sell/hold card
│   │   │   ├── alerts/                   ← Disaster alert banner & notification
│   │   │   └── schemes/                  ← Government scheme card & filter
│   │   ├── pages/                        ← Top-level page components (routing targets)
│   │   ├── hooks/                        ← Custom React hooks (useWebSocket, useSensor…)
│   │   ├── context/                      ← React Context providers (Auth, Theme, Farm)
│   │   ├── services/                     ← Axios API service layer (one file per domain)
│   │   ├── store/
│   │   │   └── slices/                   ← Redux Toolkit slices (sensor, advisory…)
│   │   ├── utils/                        ← Frontend helpers: formatters, validators
│   │   ├── assets/
│   │   │   ├── images/                   ← Static images, crop photos
│   │   │   └── icons/                    ← Custom SVG icons
│   │   ├── styles/                       ← Global CSS, Tailwind customization
│   │   └── types/                        ← TypeScript interface/type definitions
│   ├── public/                           ← Static files served as-is
│   ├── tests/
│   │   ├── unit/                         ← Component unit tests (Vitest)
│   │   └── e2e/                          ← End-to-end tests (Playwright)
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── ai/                                   ← AI / ML Engine
│   ├── models/
│   │   ├── crop_advisory/                ← Crop recommendation model (XGBoost)
│   │   ├── irrigation/                   ← Irrigation decision model
│   │   ├── market/                       ← Market sell/hold model
│   │   └── disease_detection/            ← (Future) CNN-based disease detection
│   ├── data/
│   │   ├── raw/                          ← Original unprocessed datasets
│   │   ├── processed/                    ← Cleaned, feature-engineered datasets
│   │   └── external/                     ← Third-party datasets (soil, weather history)
│   ├── notebooks/                        ← Jupyter notebooks for EDA & prototyping
│   ├── pipelines/                        ← Training & inference pipeline scripts
│   ├── evaluation/                       ← Model metrics, confusion matrices, reports
│   ├── explainability/                   ← SHAP explainer scripts and outputs
│   ├── registry/                         ← Saved trained model artifacts (.pkl, .joblib)
│   └── tests/                            ← AI model unit and integration tests
│
├── database/                             ← Database management
│   ├── migrations/                       ← SQL migration scripts (managed by Alembic)
│   ├── seeds/                            ← Initial seed data (crop list, scheme list)
│   ├── schemas/                          ← Entity-relationship diagrams & schema docs
│   ├── backups/                          ← Backup scripts and scheduled dump configs
│   └── queries/                          ← Reusable SQL query templates
│
├── docs/                                 ← All project documentation
│   ├── architecture/                     ← Architecture Decision Records, diagrams
│   ├── api/                              ← OpenAPI/Swagger spec exports
│   ├── hardware/                         ← Wiring diagrams, sensor datasheets
│   ├── deployment/                       ← Deployment runbooks, cloud setup
│   ├── user_guide/                       ← End-user documentation
│   └── adr/                              ← Architecture Decision Records (ADR-001…)
│
├── testing/                              ← Cross-cutting test infrastructure
│   ├── performance/                      ← Load tests (k6, Locust)
│   ├── security/                         ← OWASP ZAP scans, auth tests
│   ├── integration/                      ← Full-stack integration test suite
│   └── mocks/                            ← External API mocks (weather, market, IoT)
│
├── scripts/                              ← Developer & operations scripts
│   ├── setup/                            ← One-command dev environment setup scripts
│   ├── data/                             ← Data download & preprocessing scripts
│   ├── deploy/                           ← Deployment automation scripts
│   └── monitoring/                       ← Log tailing, health check scripts
│
├── deployment/                           ← Infrastructure as Code
│   ├── docker/                           ← Docker Compose files (dev, prod, test)
│   ├── kubernetes/                       ← K8s manifests (future)
│   ├── nginx/                            ← Nginx reverse proxy configuration
│   ├── terraform/                        ← Cloud infrastructure provisioning
│   └── ci/                               ← CI configuration helpers
│
├── .github/                              ← GitHub-specific files
│   ├── workflows/                        ← CI/CD pipelines (YAML)
│   ├── ISSUE_TEMPLATE/                   ← Issue templates
│   └── PULL_REQUEST_TEMPLATE/            ← PR templates
│
├── .env.example                          ← Environment variable template
├── .gitignore                            ← Git ignore rules
├── docker-compose.yml                    ← Local development stack
├── docker-compose.prod.yml               ← Production stack
├── Makefile                              ← Developer shortcuts (make dev, make test…)
├── README.md                             ← This file
└── CONTRIBUTING.md                       ← Contribution guidelines
```

---

## 🔧 Tech Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 18.x | UI framework |
| Vite | 5.x | Build tool & dev server |
| Tailwind CSS | 3.x | Utility-first styling |
| Chart.js + react-chartjs-2 | 4.x | Data visualization |
| Redux Toolkit | 2.x | Global state management |
| React Router | 6.x | Client-side routing |
| Axios | 1.x | HTTP client |
| Socket.io-client | 4.x | WebSocket real-time data |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Runtime |
| FastAPI | 0.110+ | API framework |
| SQLAlchemy | 2.x | ORM |
| Alembic | 1.x | Database migrations |
| Pydantic | 2.x | Data validation |
| aiomqtt | 1.x | Async MQTT client |
| APScheduler | 3.x | Background task scheduling |
| Celery | 5.x | Async task queue |
| httpx | 0.27+ | Async HTTP client for external APIs |

### Database & Caching
| Technology | Purpose |
|---|---|
| PostgreSQL 16 | Primary relational database |
| Redis 7 | Session cache, pub/sub, task broker |
| TimescaleDB (ext) | Time-series sensor data optimization |

### AI / ML
| Library | Purpose |
|---|---|
| Scikit-learn | Classification, preprocessing pipelines |
| XGBoost | Crop & irrigation gradient boosting models |
| Pandas | Data manipulation & feature engineering |
| NumPy | Numerical computations |
| SHAP | Explainable AI — feature importance |
| Joblib | Model serialization |
| MLflow | (Future) Experiment tracking |

### IoT / Hardware
| Component | Purpose |
|---|---|
| ESP32 | Microcontroller + WiFi + MQTT |
| DHT22 | Temperature & humidity sensor |
| Capacitive Soil Moisture | Soil moisture measurement |
| Rain Sensor | Rainfall detection |
| HC-SR04 / Float Sensor | Water level measurement |
| 4-Channel Relay Module | Irrigation pump control |
| Mosquitto MQTT Broker | Message broker (self-hosted) |

### DevOps
| Tool | Purpose |
|---|---|
| Docker + Docker Compose | Containerization |
| GitHub Actions | CI/CD automation |
| Nginx | Reverse proxy, SSL termination |
| Terraform | Cloud infrastructure provisioning |

---

## ⚙️ Installation & Setup

### Prerequisites

```bash
# Required tools
Node.js >= 20.x
Python >= 3.11
Docker & Docker Compose >= 2.x
Git >= 2.40
Arduino IDE or PlatformIO (for ESP32 firmware)
```

### Quick Start (Docker — Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/AgriGuardian-AI.git
cd AgriGuardian-AI

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys and credentials

# 3. Start the full stack
docker compose up --build

# 4. Access the application
# Frontend:  http://localhost:5173
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
# Swagger:   http://localhost:8000/redoc
```

### Manual Development Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn src.api.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev

# Application available at: http://localhost:5173
```

#### Hardware

```bash
# Open hardware/esp32/firmware/ in Arduino IDE or PlatformIO
# Install required libraries (see hardware/docs/LIBRARIES.md)
# Configure hardware/esp32/config/config.h with your WiFi & MQTT credentials
# Flash to ESP32
```

### Makefile Shortcuts

```bash
make dev          # Start full development stack
make backend      # Start backend only
make frontend     # Start frontend only
make test         # Run all tests
make lint         # Run linters (backend + frontend)
make migrate      # Run database migrations
make seed         # Seed the database
make clean        # Remove all build artifacts
make docs         # Build and serve documentation
```

---

## 🔄 Development Flow

```
Feature Branch → Development → Testing → Code Review → Staging → Production
```

### Day-to-Day Workflow

```bash
# 1. Sync with main branch
git checkout main && git pull origin main

# 2. Create a feature branch
git checkout -b feature/MODULE-NUMBER-short-description
# Example: git checkout -b feature/M2-sensor-api-endpoint

# 3. Develop with tests
# Write code → Write tests → Run tests → Fix → Commit

# 4. Commit with conventional commits
git commit -m "feat(backend): add sensor data ingestion endpoint"
git commit -m "fix(ai): correct soil moisture feature scaling"
git commit -m "docs(hardware): add DHT22 wiring diagram"

# 5. Push and open Pull Request
git push origin feature/M2-sensor-api-endpoint
# Create PR on GitHub → Request review → Merge after approval
```

### Conventional Commit Types

| Type | Usage |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting (no logic change) |
| `refactor` | Code restructuring |
| `test` | Adding or updating tests |
| `chore` | Build scripts, dependencies |
| `ci` | CI/CD pipeline changes |
| `perf` | Performance improvements |
| `iot` | Hardware/firmware changes |

---

## 🗺️ Module Roadmap

| Module | Name | Status |
|---|---|---|
| M1 | Hardware & IoT | 🔲 Planned |
| M2 | Backend Core | 🔲 Planned |
| M3 | Database | 🔲 Planned |
| M4 | AI Engine | 🔲 Planned |
| M5 | Frontend | 🔲 Planned |
| M6 | Integration | 🔲 Planned |
| M7 | Deployment | 🔲 Planned |

> Detailed roadmap: see [ROADMAP.md](ROADMAP.md)

---

## 🚀 Future Expansion

| Feature | Phase | Description |
|---|---|---|
| 🦠 Crop Disease Detection | v1.5 | CNN model on ESP32-CAM images |
| 🛸 Drone Integration | v2.0 | Aerial field monitoring + spraying |
| 🛰️ Satellite Data | v2.0 | NDVI analysis from Sentinel-2 |
| 🛒 Marketplace | v2.5 | Direct farmer-to-buyer platform |
| ⛓️ Blockchain Traceability | v3.0 | Crop provenance on-chain |
| 👥 Farmer Community | v2.0 | Forum, knowledge sharing, expert AMA |
| 📱 Mobile App | v1.5 | React Native companion app |
| 🌐 Multi-language | v1.5 | Hindi, Marathi, Tamil, Telugu support |
| 🔮 Predictive Analytics | v2.0 | 30-day crop yield forecasting |

---

## 🌿 GitHub Workflow

### Branching Strategy (Git Flow)

```
main              ← Production-ready code
├── develop       ← Integration branch
│   ├── feature/M1-esp32-firmware
│   ├── feature/M2-sensor-api
│   ├── feature/M3-database-schema
│   ├── feature/M4-crop-model
│   └── feature/M5-dashboard-ui
├── release/v1.0  ← Release candidate
└── hotfix/xxx    ← Emergency production fixes
```

### Branch Naming

```
feature/M{module_number}-{short-kebab-description}
fix/M{module_number}-{bug-description}
docs/{topic-description}
hotfix/{critical-issue}
release/v{major}.{minor}
```

### PR Guidelines

- Every PR must reference an Issue number
- Minimum 1 reviewer approval required
- All CI checks must pass before merge
- PR description must include: What, Why, How, Testing Done
- No direct commits to `main` or `develop`

### GitHub Actions CI Pipeline

```
On PR to develop/main:
  ├── lint-backend     (flake8, black, mypy)
  ├── lint-frontend    (eslint, prettier)
  ├── test-backend     (pytest with coverage)
  ├── test-frontend    (vitest)
  ├── build-docker     (validate docker images build)
  └── security-scan    (bandit, npm audit)

On merge to main:
  ├── build-and-push   (push images to registry)
  └── deploy-staging   (auto-deploy to staging env)
```

---

## 📐 Coding Standards

### Python (Backend + AI)

```python
# Style: PEP 8 + Black formatter (line length: 88)
# Type hints: Required on all public functions
# Docstrings: Google-style docstrings required
# Linting: flake8 + isort + mypy (strict)

# Example function signature:
async def get_sensor_reading(
    sensor_id: str,
    db: AsyncSession,
) -> SensorReadingSchema:
    """Retrieve the latest sensor reading for a given sensor.

    Args:
        sensor_id: Unique identifier of the sensor device.
        db: Async SQLAlchemy database session.

    Returns:
        SensorReadingSchema with the latest telemetry data.

    Raises:
        SensorNotFoundException: If the sensor ID does not exist.
    """
    ...
```

### TypeScript / React (Frontend)

```typescript
// Style: ESLint + Prettier (Airbnb config)
// TypeScript: Strict mode enabled
// Components: Functional components with TypeScript props interface
// State: Redux Toolkit for global, useState for local

// Example component pattern:
interface SensorCardProps {
  sensorId: string;
  label: string;
  unit: string;
  value: number;
  trend: 'up' | 'down' | 'stable';
}

const SensorCard: React.FC<SensorCardProps> = ({
  sensorId,
  label,
  unit,
  value,
  trend,
}) => {
  // ...
};

export default SensorCard;
```

### C++ (ESP32 Firmware)

```cpp
// Style: Google C++ Style Guide
// All functions must have header comment blocks
// Use #define for pin constants, struct for sensor config
// No blocking delays in main loop (use non-blocking millis())
```

### General Rules

1. **No magic numbers** — use named constants
2. **No commented-out code** in commits
3. **Error handling required** on all async operations
4. **Logging** — use structured logging (JSON format in production)
5. **Security** — never hardcode secrets; always use `.env`
6. **Tests** — minimum 70% coverage required for backend
7. **Docs** — every public function/class must have a docstring

---

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Setting up your development environment
- Code review process
- Issue reporting guidelines
- Pull request standards

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ for India's 120 million farmers

*AgriGuardian AI — Because every harvest matters*

</div>
