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
<img width="1536" height="1024" alt="WhatsApp Image 2026-08-11 at 7 10 45 PM" src="https://github.com/user-attachments/assets/bbd235cc-f39e-4a24-bf6f-ad0426102167" />

~~~
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

# Install depende
