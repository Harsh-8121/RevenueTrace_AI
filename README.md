# RevenueTrace AI

RevenueTrace AI is an AI-powered Contract-to-Cash investigation platform that detects revenue leakage by tracing discrepancies across contracts, orders, deliveries, invoices, and payments. It uses LLMs to understand business rules, investigate anomalies, identify root causes, quantify financial impact, and generate evidence-backed recommendations.

## Project structure

- `backend/` — FastAPI service for contracts and investigations
- `frontend/` — React dashboard for running investigations and viewing findings
- `scripts/install.sh` — installs Python and Node dependencies

## Prerequisites

- Python 3.12+
- Node.js 22+

## Setup

```bash
bash scripts/install.sh
```

## Run locally

Start the API:

```bash
python3 -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Start the web app:

```bash
npm --prefix frontend run dev
```

Open http://localhost:5173 and run an investigation against the sample contract `CTR-1001`.

## API

| Endpoint | Description |
| --- | --- |
| `GET /api/health` | Health check |
| `GET /api/contracts` | List available contracts |
| `POST /api/investigations` | Run an investigation for a contract |
| `GET /api/investigations` | List investigations from the current session |
| `GET /api/investigations/{id}` | Fetch a single investigation |
