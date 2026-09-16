from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class OrderRecord(BaseModel):
    order_id: str
    amount: float = Field(ge=0)
    order_date: str


class DeliveryRecord(BaseModel):
    delivery_id: str
    amount: float = Field(ge=0)
    delivery_date: str
    order_id: str | None = None


class InvoiceRecord(BaseModel):
    invoice_id: str
    amount: float = Field(ge=0)
    invoice_date: str
    due_date: str


class PaymentRecord(BaseModel):
    payment_id: str
    amount: float = Field(ge=0)
    payment_date: str
    invoice_id: str | None = None


class ContractRecord(BaseModel):
    contract_id: str
    customer_name: str
    contract_value: float = Field(ge=0)
    terms: str
    effective_date: str
    orders: list[OrderRecord]
    deliveries: list[DeliveryRecord]
    invoices: list[InvoiceRecord]
    payments: list[PaymentRecord]
    source: Literal["seed", "upload"] = "seed"


class Finding(BaseModel):
    category: Literal["contract", "order", "delivery", "billing", "collections", "terms", "duplicate"]
    severity: Literal["low", "medium", "high", "critical"]
    description: str
    financial_impact: float = Field(ge=0)
    evidence: list[str]
    root_cause: str | None = None


class InvestigationRequest(BaseModel):
    contract_id: str
    use_llm: bool = True


class InvestigationSummary(BaseModel):
    id: str
    contract_id: str
    customer_name: str
    status: str
    total_leakage: float
    finding_count: int
    created_at: str
    llm_enhanced: bool


class Investigation(BaseModel):
    id: str
    contract_id: str
    customer_name: str
    status: str
    total_leakage: float
    findings: list[Finding]
    recommendation: str
    executive_summary: str
    chain_summary: dict[str, float]
    llm_enhanced: bool
    created_at: str


class DashboardStats(BaseModel):
    contract_count: int
    total_contract_value: float
    contracts_with_leakage: int
    total_identified_leakage: float
    investigation_count: int
    uploaded_contract_count: int


class UploadResult(BaseModel):
    message: str
    contracts_imported: int
    contract_ids: list[str]
