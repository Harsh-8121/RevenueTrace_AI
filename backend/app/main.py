from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .investigation_engine import SAMPLE_RECORDS, run_investigation
from .models import Investigation, InvestigationRequest

app = FastAPI(title="RevenueTrace AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_investigations: dict[str, Investigation] = {}


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/contracts")
def list_contracts() -> list[dict[str, str | float]]:
    return [
        {
            "contract_id": contract_id,
            "contract_value": record["contract_value"],
        }
        for contract_id, record in SAMPLE_RECORDS.items()
    ]


@app.get("/api/investigations")
def list_investigations() -> list[Investigation]:
    return list(_investigations.values())


@app.post("/api/investigations", response_model=Investigation)
def create_investigation(request: InvestigationRequest) -> Investigation:
    try:
        investigation = run_investigation(request.contract_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    _investigations[investigation.id] = investigation
    return investigation


@app.get("/api/investigations/{investigation_id}", response_model=Investigation)
def get_investigation(investigation_id: str) -> Investigation:
    investigation = _investigations.get(investigation_id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return investigation
