from __future__ import annotations

from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .investigation import run_investigation
from .models import (
    ContractRecord,
    DashboardStats,
    Investigation,
    InvestigationRequest,
    InvestigationSummary,
    UploadResult,
)
from .parsers import parse_contract_pdf, parse_contracts_csv, parse_contracts_json
from .repository import (
    get_contract,
    get_investigation,
    list_contracts,
    list_investigations,
    uploaded_contract_count,
    upsert_contract,
)

app = FastAPI(title="RevenueTrace AI API", version="1.0.0")
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "revenuetrace-ai"}


@router.get("/dashboard", response_model=DashboardStats)
def dashboard() -> DashboardStats:
    contracts = list_contracts()
    investigations = list_investigations()
    leakage_contracts = {
        item["contract_id"]
        for item in investigations
        if item.get("total_leakage", 0) > 0
    }

    return DashboardStats(
        contract_count=len(contracts),
        total_contract_value=sum(contract.contract_value for contract in contracts),
        contracts_with_leakage=len(leakage_contracts),
        total_identified_leakage=sum(item.get("total_leakage", 0) for item in investigations),
        investigation_count=len(investigations),
        uploaded_contract_count=uploaded_contract_count(),
    )


@router.get("/contracts", response_model=list[ContractRecord])
def get_contracts() -> list[ContractRecord]:
    return list_contracts()


@router.get("/contracts/{contract_id}", response_model=ContractRecord)
def get_contract_by_id(contract_id: str) -> ContractRecord:
    contract = get_contract(contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.get("/investigations", response_model=list[InvestigationSummary])
def get_investigations() -> list[InvestigationSummary]:
    summaries: list[InvestigationSummary] = []
    for item in list_investigations():
        summaries.append(
            InvestigationSummary(
                id=item["id"],
                contract_id=item["contract_id"],
                customer_name=item["customer_name"],
                status=item["status"],
                total_leakage=item["total_leakage"],
                finding_count=len(item.get("findings", [])),
                created_at=item["created_at"],
                llm_enhanced=item.get("llm_enhanced", False),
            )
        )
    return sorted(summaries, key=lambda item: item.created_at, reverse=True)


@router.post("/investigations", response_model=Investigation)
def create_investigation(request: InvestigationRequest) -> Investigation:
    try:
        return run_investigation(request.contract_id, use_llm=request.use_llm)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/investigations/{investigation_id}", response_model=Investigation)
def get_investigation_by_id(investigation_id: str) -> Investigation:
    investigation = get_investigation(investigation_id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return Investigation(**investigation)


@router.post("/uploads", response_model=UploadResult)
async def upload_contract_data(file: UploadFile = File(...)) -> UploadResult:
    content = await file.read()
    filename = file.filename or "upload"
    lower_name = filename.lower()

    try:
        if lower_name.endswith(".json"):
            contracts = parse_contracts_json(content)
        elif lower_name.endswith(".csv"):
            contracts = parse_contracts_csv(content)
        elif lower_name.endswith(".pdf"):
            contracts = [parse_contract_pdf(content, filename)]
        else:
            raise HTTPException(
                status_code=400,
                detail="Supported formats: .json, .csv, .pdf",
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    for contract in contracts:
        upsert_contract(contract)

    return UploadResult(
        message="Contracts imported successfully.",
        contracts_imported=len(contracts),
        contract_ids=[contract.contract_id for contract in contracts],
    )


app.include_router(router, prefix="/api")
app.include_router(router)
