import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from backend.models import (
    Contract, ContractRule, Order, Delivery, Invoice, Payment,
    Discrepancy, InvestigationResult, RecoveryNotice
)
from backend.data_generator import get_scenarios_data
from backend.agents.contract_agent import ContractAgent
from backend.agents.reconciliation_agent import ReconciliationAgent
from backend.agents.investigation_agent import InvestigationAgent
from backend.agents.action_agent import ActionAgent

app = FastAPI(
    title="Contract-to-Cash AI Investigator API",
    description="AI-powered platform to trace revenue leakage across Contract -> Order -> Delivery -> Invoice -> Payment",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCENARIOS_DATA = get_scenarios_data()
API_KEY_STATE = {"gemini_api_key": os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")}

contract_agent = ContractAgent(api_key=API_KEY_STATE["gemini_api_key"])
reconciliation_agent = ReconciliationAgent()
investigation_agent = InvestigationAgent(api_key=API_KEY_STATE["gemini_api_key"])
action_agent = ActionAgent()

class ParseContractRequest(BaseModel):
    text: str
    customer_name: Optional[str] = "Client Enterprise"
    currency: Optional[str] = "INR"

class AskWhyRequest(BaseModel):
    customer_id: str
    discrepancy_id: str
    question: str

class InvestigateRequest(BaseModel):
    customer_id: str
    discrepancy_id: str

class ApiKeyRequest(BaseModel):
    api_key: str

class RecoveryNoticeRequest(BaseModel):
    customer_id: str
    discrepancy_id: str

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "gemini_configured": bool(API_KEY_STATE["gemini_api_key"]),
        "scenarios_available": list(SCENARIOS_DATA.keys())
    }

@app.get("/api/scenarios")
def list_scenarios():
    output = []
    for cid, s in SCENARIOS_DATA.items():
        output.append({
            "customer_id": cid,
            "customer_name": s["customer_name"],
            "industry": s["industry"],
            "contract_id": s["contract"].contract_id,
            "committed_value": s["contract"].annual_committed_value,
            "currency": s["contract"].currency
        })
    return output

@app.get("/api/scenarios/{customer_id}")
def get_scenario_details(customer_id: str):
    if customer_id not in SCENARIOS_DATA:
        raise HTTPException(status_code=404, detail="Scenario not found")
    s = SCENARIOS_DATA[customer_id]
    return {
        "customer_id": s["customer_id"],
        "customer_name": s["customer_name"],
        "industry": s["industry"],
        "contract": s["contract"],
        "orders": s["orders"],
        "deliveries": s["deliveries"],
        "invoices": s["invoices"],
        "payments": s["payments"]
    }

@app.get("/api/reconciliation/{customer_id}")
def reconcile_scenario(customer_id: str):
    if customer_id not in SCENARIOS_DATA:
        raise HTTPException(status_code=404, detail="Scenario not found")
    s = SCENARIOS_DATA[customer_id]
    result = reconciliation_agent.reconcile_customer(
        contract=s["contract"],
        orders=s["orders"],
        deliveries=s["deliveries"],
        invoices=s["invoices"],
        payments=s["payments"]
    )
    return result

@app.get("/api/portfolio-summary")
def get_portfolio_summary():
    all_results = []
    for cid, s in SCENARIOS_DATA.items():
        res = reconciliation_agent.reconcile_customer(
            contract=s["contract"],
            orders=s["orders"],
            deliveries=s["deliveries"],
            invoices=s["invoices"],
            payments=s["payments"]
        )
        all_results.append(res)

    total_contracted = sum(r["metrics"]["contracted_value"] for r in all_results)
    total_ordered = sum(r["metrics"]["ordered_value"] for r in all_results)
    total_delivered = sum(r["metrics"]["delivered_value"] for r in all_results)
    total_invoiced = sum(r["metrics"]["invoiced_value"] for r in all_results)
    total_collected = sum(r["metrics"]["collected_value"] for r in all_results)
    total_leakage = sum(r["metrics"]["total_leakage_detected"] for r in all_results)
    total_recoverable = sum(r["metrics"]["recoverable_potential"] for r in all_results)
    discrepancy_count = sum(r["metrics"]["discrepancy_count"] for r in all_results)

    return {
        "total_contracted": total_contracted,
        "total_ordered": total_ordered,
        "total_delivered": total_delivered,
        "total_invoiced": total_invoiced,
        "total_collected": total_collected,
        "total_leakage": total_leakage,
        "total_recoverable": total_recoverable,
        "discrepancy_count": discrepancy_count,
        "account_count": len(all_results),
        "accounts": [
            {
                "customer_id": r["customer_id"],
                "customer_name": r["customer_name"],
                "leakage": r["metrics"]["total_leakage_detected"],
                "collected": r["metrics"]["collected_value"],
                "top_discrepancy": r["discrepancies"][0].title if r["discrepancies"] else "None"
            }
            for r in all_results
        ]
    }

@app.post("/api/investigate")
def investigate_discrepancy(req: InvestigateRequest):
    if req.customer_id not in SCENARIOS_DATA:
        raise HTTPException(status_code=404, detail="Customer scenario not found")
    s = SCENARIOS_DATA[req.customer_id]
    rec_result = reconciliation_agent.reconcile_customer(
        contract=s["contract"],
        orders=s["orders"],
        deliveries=s["deliveries"],
        invoices=s["invoices"],
        payments=s["payments"]
    )
    target_disc = next((d for d in rec_result["discrepancies"] if d.discrepancy_id == req.discrepancy_id), None)
    if not target_disc:
        raise HTTPException(status_code=404, detail="Discrepancy ID not found")

    investigation = investigation_agent.investigate(
        discrepancy=target_disc,
        contract=s["contract"],
        context_data=s
    )
    return investigation

@app.post("/api/ask-why")
def ask_why_endpoint(req: AskWhyRequest):
    if req.customer_id not in SCENARIOS_DATA:
        raise HTTPException(status_code=404, detail="Customer scenario not found")
    s = SCENARIOS_DATA[req.customer_id]
    rec_result = reconciliation_agent.reconcile_customer(
        contract=s["contract"],
        orders=s["orders"],
        deliveries=s["deliveries"],
        invoices=s["invoices"],
        payments=s["payments"]
    )
    target_disc = next((d for d in rec_result["discrepancies"] if d.discrepancy_id == req.discrepancy_id), None)
    if not target_disc:
        raise HTTPException(status_code=404, detail="Discrepancy ID not found")

    investigation = investigation_agent.investigate(
        discrepancy=target_disc,
        contract=s["contract"],
        context_data=s
    )
    qa_result = investigation_agent.ask_why(
        question=req.question,
        discrepancy=target_disc,
        investigation=investigation,
        contract=s["contract"]
    )
    return qa_result

@app.post("/api/contracts/parse")
def parse_contract_endpoint(req: ParseContractRequest):
    rules = contract_agent.parse_contract_text(
        text=req.text,
        customer_name=req.customer_name or "Client Enterprise",
        currency=req.currency or "INR"
    )
    return {
        "rules_extracted": len(rules),
        "rules": rules
    }

@app.post("/api/actions/generate-notice")
def generate_notice_endpoint(req: RecoveryNoticeRequest):
    if req.customer_id not in SCENARIOS_DATA:
        raise HTTPException(status_code=404, detail="Customer scenario not found")
    s = SCENARIOS_DATA[req.customer_id]
    rec_result = reconciliation_agent.reconcile_customer(
        contract=s["contract"],
        orders=s["orders"],
        deliveries=s["deliveries"],
        invoices=s["invoices"],
        payments=s["payments"]
    )
    target_disc = next((d for d in rec_result["discrepancies"] if d.discrepancy_id == req.discrepancy_id), None)
    if not target_disc:
        raise HTTPException(status_code=404, detail="Discrepancy ID not found")

    investigation = investigation_agent.investigate(
        discrepancy=target_disc,
        contract=s["contract"],
        context_data=s
    )
    notice = action_agent.generate_recovery_notice(
        discrepancy=target_disc,
        investigation=investigation,
        contract=s["contract"]
    )
    return notice

@app.get("/api/actions/audit-report")
def get_audit_report():
    all_results = []
    for cid, s in SCENARIOS_DATA.items():
        res = reconciliation_agent.reconcile_customer(
            contract=s["contract"],
            orders=s["orders"],
            deliveries=s["deliveries"],
            invoices=s["invoices"],
            payments=s["payments"]
        )
        all_results.append(res)
    report_md = action_agent.generate_audit_report(all_results)
    return {"markdown": report_md}

@app.post("/api/settings/api-key")
def update_api_key(req: ApiKeyRequest):
    API_KEY_STATE["gemini_api_key"] = req.api_key.strip()
    global contract_agent, investigation_agent
    contract_agent = ContractAgent(api_key=req.api_key.strip())
    investigation_agent = InvestigationAgent(api_key=req.api_key.strip())
    return {"status": "updated", "configured": bool(req.api_key.strip())}

# Serve frontend single page app
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    def serve_frontend():
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>Frontend index.html not found</h1>"
