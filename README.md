# RevenueTrace AI

RevenueTrace AI is an AI-powered Contract-to-Cash investigation platform that detects revenue leakage by tracing discrepancies across contracts, orders, deliveries, invoices, and payments.

## Features

- Contract-to-cash dashboard with portfolio metrics
- Multi-contract investigation engine across order, delivery, billing, and collections gaps
- Investigation history with evidence-backed findings and recommendations
- Data import via JSON, CSV, or PDF upload
- Optional LLM-enhanced executive summaries when `OPENAI_API_KEY` is configured

## Project structure

- `backend/` — FastAPI application, investigation engine, parsers, and seed data
- `frontend/` — React dashboard
- `api/index.py` — Vercel serverless entrypoint
- `scripts/install.sh` — local dependency installation

## Local development

```bash
bash scripts/install.sh
python3 -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
npm --prefix frontend run dev
```

Open http://localhost:5173

## Deploy to Vercel

1. Import the GitHub repository in Vercel.
2. Keep **Root Directory** as the repository root (`./`).
3. Redeploy from the latest `main` branch.

Optional environment variable:

- `OPENAI_API_KEY` — enables LLM-enhanced investigation summaries

## Data input formats

### JSON

Upload a file with a `contracts` array matching the structure in `backend/data/seed_contracts.json`.

### CSV

Required columns: `record_type`, `contract_id`, `customer_name`, `amount`

Supported `record_type` values: `contract`, `order`, `delivery`, `invoice`, `payment`

See `backend/data/sample_upload.csv` for an example.

### PDF

Upload a contract PDF. The parser extracts contract ID, customer, amounts, and payment terms heuristically.

## API

| Endpoint | Description |
| --- | --- |
| `GET /api/health` | Health check |
| `GET /api/dashboard` | Portfolio metrics |
| `GET /api/contracts` | List contracts |
| `GET /api/contracts/{id}` | Contract detail |
| `POST /api/investigations` | Run investigation |
| `GET /api/investigations` | List investigations |
| `GET /api/investigations/{id}` | Investigation detail |
| `POST /api/uploads` | Import JSON, CSV, or PDF |
