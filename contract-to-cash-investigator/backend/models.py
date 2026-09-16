from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DiscrepancyType(str, Enum):
    UNBILLED_DELIVERY = 'UNBILLED_DELIVERY'
    PRICING_MISMATCH = 'PRICING_MISMATCH'
    ROGUE_DISCOUNT = 'ROGUE_DISCOUNT'
    UNCOLLECTED_COMMITMENT = 'UNCOLLECTED_COMMITMENT'
    PAYMENT_SHORTFALL = 'PAYMENT_SHORTFALL'
    OVERDUE_INTEREST = 'OVERDUE_INTEREST'
    UNFULFILLED_ORDER = 'UNFULFILLED_ORDER'

class Severity(str, Enum):
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'

class Stage(str, Enum):
    CONTRACT = 'CONTRACT'
    ORDER = 'ORDER'
    DELIVERY = 'DELIVERY'
    INVOICE = 'INVOICE'
    PAYMENT = 'PAYMENT'

class ContractRule(BaseModel):
    rule_id: str
    rule_type: str # pricing, commitment, discount, payment_terms, penalty
    sku: Optional[str] = None
    description: str
    unit_price: Optional[float] = None
    min_commitment: Optional[int] = None
    discount_pct: Optional[float] = None
    grace_days: Optional[int] = 30
    penalty_rate_annual_pct: Optional[float] = None
    clause_reference: str
    clause_text: str

class Contract(BaseModel):
    contract_id: str
    customer_id: str
    customer_name: str
    start_date: str
    end_date: str
    currency: str = 'INR'
    annual_committed_value: float
    rules: List[ContractRule] = []
    raw_text: str

class Order(BaseModel):
    order_id: str
    customer_id: str
    order_date: str
    sku: str
    quantity: int
    contracted_price: float
    order_price: float
    total_amount: float
    po_reference: str
    status: str = 'FULFILLED'

class Delivery(BaseModel):
    delivery_id: str
    order_id: str
    customer_id: str
    delivery_date: str
    sku: str
    delivered_quantity: int
    challan_number: str
    warehouse_ref: str
    status: str = 'DELIVERED'

class Invoice(BaseModel):
    invoice_id: str
    delivery_id: Optional[str] = None
    order_id: str
    customer_id: str
    invoice_date: str
    due_date: str
    sku: str
    billed_quantity: int
    unit_price: float
    applied_discount_pct: float = 0.0
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    total_amount: float
    status: str = 'ISSUED'

class Payment(BaseModel):
    payment_id: str
    invoice_id: str
    customer_id: str
    payment_date: str
    amount_due: float
    amount_paid: float
    shortfall_amount: float = 0.0
    payment_mode: str = 'NEFT/RTGS'
    bank_reference: str
    status: str = 'SETTLED' # SETTLED, PARTIAL, UNPAID

class EvidenceItem(BaseModel):
    source_type: str # Contract Clause, Purchase Order, Delivery Challan, Invoice, Bank Advice
    document_id: str
    key_fields: Dict[str, Any]
    snippet: str
    is_violation: bool = False

class WhyStep(BaseModel):
    level: int
    question: str
    answer: str
    evidence_source: str
    detail: str

class Discrepancy(BaseModel):
    discrepancy_id: str
    customer_id: str
    stage: str # e.g. 'DELIVERY -> INVOICE'
    discrepancy_type: DiscrepancyType
    title: str
    financial_impact: float
    currency: str = 'INR'
    severity: Severity
    summary: str
    affected_count: int = 1
    sample_records: Dict[str, Any] = {}
    relevant_clause: Optional[str] = None

class InvestigationResult(BaseModel):
    investigation_id: str
    discrepancy_id: str
    customer_name: str
    financial_impact: float
    currency: str = 'INR'
    root_cause_category: str
    root_cause_explanation: str
    five_whys: List[WhyStep]
    evidence_trail: List[EvidenceItem]
    systemic_scope: str # isolated vs systemic
    affected_transaction_count: int
    total_systemic_exposure: float
    contract_clause_citation: str
    recommended_actions: List[str]
    confidence_score: float = 0.96

class RecoveryNotice(BaseModel):
    notice_id: str
    customer_name: str
    customer_id: str
    date_generated: str
    recipient_role: str
    total_claim_amount: float
    currency: str = 'INR'
    subject: str
    formal_letter_body: str
    itemized_table: List[Dict[str, Any]]
    contract_clauses_cited: List[str]
    internal_erp_directive: str

class TraceStage(BaseModel):
    stage_name: str
    expected_amount: float
    actual_amount: float
    leakage_amount: float
    leakage_reasons: List[str]
    discrepancy_ids: List[str]
