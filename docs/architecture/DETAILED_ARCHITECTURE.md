# AgriGuardian AI – Detailed Software Architecture

## 1. System Overview
The **AgriGuardian AI** platform is an end‑to‑end intelligent farming solution that connects IoT edge devices, a FastAPI backend, an XGBoost/SHAP AI engine, a PostgreSQL database, and a React‑Vite frontend. It provides real‑time sensor ingestion, explainable AI recommendations, and a premium SaaS‑like dashboard for farmers.

---

## 2. High‑Level Module Dependency Graph
```
[IoT Edge] --> (HTTP POST) --> [FastAPI Backend]
[FastAPI Backend] --> PostgreSQL
[FastAPI Backend] --> AI Engine (XGBoost + SHAP)
[FastAPI Backend] --> External APIs (Weather, Market, Govt Schemes)
[AI Engine] --> PostgreSQL (store recommendations, history)
[FastAPI Backend] --> React Frontend (REST/GraphQL JSON)
[React Frontend] --> FastAPI Backend (Axios)
[DevOps] --> Docker Compose (frontend, backend, db)
```
*All arrows denote request/response or data flow.*

---

## 3. Request Flow (External Client → Platform)
1. **Browser** loads the React SPA (`http://localhost:5173`).
2. On login, the SPA sends `POST /api/v1/auth/login` with credentials.
3. Backend validates, returns a **JWT**.
4. SPA stores JWT (HttpOnly cookie or localStorage) and attaches `Authorization: Bearer <token>` to subsequent API calls.
5. Dashboard page polls `GET /api/v1/dashboard/{farm_id}` every 30 s.
6. The response payload contains:
   - hero recommendation
   - live sensor snapshot
   - weather forecast
   - market prices
   - government schemes
   - analytics chart data
   - recommendation history
7. UI components render data; loading skeletons shown while awaiting.
8. User actions (acknowledge recommendation, view details) trigger further POST/PUT endpoints.

---

## 4. Backend Flow (FastAPI)
### 4.1 Layered Clean Architecture
```
backend/
│   app/
│   ├─ api/          # FastAPI routers (auth, sensor, dashboard, recommendations)
│   ├─ core/         # Domain models, business rules, AI engine wrapper
│   ├─ services/     # Use‑case services (IngestionService, RecommendationService)
│   ├─ repositories/ # Data‑access layer (SQLAlchemy/SQLModel) for each entity
│   ├─ utils/        # Helper utilities (security, pagination, logging)
│   └─ models/       # Pydantic schemas (request/response) and ORM models
```
### 4.2 Dependency Injection
* FastAPI’s `Depends` injects services/repositories into routers.
* DB session provided per‑request via a context‑manager.
* AI engine injected as a singleton; lazy‑loaded on first call.

### 4.3 Asynchronous Endpoints
* Sensor ingestion (`POST /api/v1/sensor`) is `async` to handle high‑frequency data.
* Background tasks (`FastAPI.background`) enqueue jobs to a worker (Celery/RQ – future).

---

## 5. Frontend Flow (React‑Vite)
```
src/
│   components/          # Reusable UI pieces (cards, charts, layout)
│   pages/               # Route‑level pages (Dashboard, Settings, …)
│   services/            # Axios API wrappers
│   context/             # AuthContext, GlobalState
│   hooks/               # Custom hooks (useDashboard, useSensors)
│   App.jsx + router    # React‑Router v6 mapping URLs to pages
```
* **Auth flow** – `AuthContext` stores JWT, auto‑refreshes on expiry.
* **Data fetching** – `useDashboard` hook calls the dashboard endpoint, returns `data`, `loading`, `error`.
* **Skeleton UI** – while `loading` displays `<Skeleton/>` components (Tailwind).
* **State management** – lightweight `useContext` + `useReducer`; no Redux needed for current scope.
* **Animations** – Tailwind’s `transition`, `animate‑pulse`, and CSS keyframes.

---

## 6. AI Flow (Decision Engine)
1. **Trigger** – either a scheduled nightly batch or immediate post‑sensor‑ingest background task.
2. **Data aggregation** – recent sensor snapshots, latest weather forecast, market data fetched from the DB or external APIs.
3. **Model inference** – load pre‑trained XGBoost models (`.joblib`) from `ai/registry/`.
4. **Explainability** – SHAP explainer produces feature importance; a templating function turns this into a human‑readable `reason` string.
5. **Recommendation contract**
   ```json
   {
     "decision": "Irrigate 12 L/m²",
     "confidence": 0.92,
     "reason": "Soil moisture 28% (‑17% vs optimal) and no rain forecast",
     "source": "irrigation_model_v1"
   }
   ```
6. **Persistence** – store in `recommendations` table, also push to a notification queue for the frontend.
7. **History** – each acknowledgment creates a `recommendation_history` entry.

---

## 7. Database Flow (PostgreSQL)
* **Schema** – defined in `docs/architecture/ARCHITECTURE.md` (users, farms, sensor_readings, weather, market_prices, recommendations, recommendation_history, government_schemes, device_status, alerts).
* **ORM** – SQLModel (SQLAlchemy 2.x) provides type‑safe models and migrations via Alembic.
* **Transactions** – each API endpoint uses a single DB session; commits only on successful business logic.
* **Read‑replica** – future scaling: read‑heavy dashboard queries can be routed to a read‑replica.
* **Connection pooling** – `asyncpg` pool managed by FastAPI startup event.

---

## 8. API Flow (OpenAPI v3)
* FastAPI auto‑generates OpenAPI spec at `/docs`.
* Major endpoints (excerpt):
  - `POST /api/v1/auth/login` – JWT issuance
  - `POST /api/v1/auth/register`
  - `POST /api/v1/sensor` – ingest payload
  - `GET /api/v1/dashboard/{farm_id}` – full dashboard payload
  - `GET /api/v1/recommendations/{farm_id}` – latest recommendation(s)
  - `POST /api/v1/recommendations/{id}/ack` – acknowledge
  - `GET /api/v1/weather/{farm_id}` – external weather proxy
* All responses conform to Pydantic schemas; error handling via standardized `ErrorResponse` model.

---

## 9. Authentication Flow (JWT + bcrypt)
1. **Registration** – password hashed with `bcrypt` (`argon2` optional) before persisting.
2. **Login** – supplied password verified against stored hash.
3. **Token creation** – `jwt.encode({sub: user.id, exp: now+15m}, SECRET_KEY)`.
4. **Protected routes** – `Depends(get_current_user)` extracts token, validates, injects `User` object.
5. **Refresh** – optional `/auth/refresh` endpoint (future) using long‑lived refresh token stored in HttpOnly cookie.
6. **RBAC** – simple role check (`user.role == "admin"`) for admin‑only routes.

---

## 10. DevOps & Deployment
* **Docker Compose** – orchestrates `frontend`, `backend`, `postgres`, `redis` (future) services.
* **CI/CD** – GitHub Actions lint (`eslint`, `flake8`), test (`pytest`, `jest`), build Docker images, push to registry.
* **Production** – backend runs with **Gunicorn + Uvicorn workers**; frontend served via **nginx** static files.
* **Observability** – Prometheus metrics endpoint (`/metrics`) and Grafana dashboards for latency, error rates.
* **Secrets** – managed via Docker secrets or GitHub‑encrypted variables (JWT secret, DB password).

---

## 11. Open Issues / Clarifications Needed
- Real‑time streaming strategy (MQTT vs HTTP) – do we need it now or later?
- Multi‑tenant isolation (schema per farm vs row‑level security).
- Desired hosting environment (AWS, GCP, Azure, Render, Railway). 
- Any additional external APIs (satellite imagery, soil APIs) to integrate?

---

### Next Steps
1. **Phase 3 – Folder‑Structure Review** – confirm the proposed backend and frontend directories.
2. **Phase 4 – Frontend implementation** – start building reusable UI components as per the premium design guidelines.

*Please review this architecture document and approve or provide feedback before we proceed to the next phase.*
