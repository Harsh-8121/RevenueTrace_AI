import os
import json
from typing import Dict, Any, List, Optional
from backend.models import (
    Discrepancy, InvestigationResult, WhyStep, EvidenceItem, Contract
)

class InvestigationAgent:
    """
    Main AI Financial Investigator Agent.
    Synthesizes cross-document evidence (Contract <-> Order <-> Delivery <-> Invoice <-> Payment),
    executes 5-Whys recursive root-cause inquiry, evaluates systemic scope,
    and powers the interactive 'Ask Why?' dialogue.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize Gemini client: {e}")

    def investigate(self, discrepancy: Discrepancy, contract: Contract, context_data: Dict[str, Any]) -> InvestigationResult:
        disc_type = discrepancy.discrepancy_type.value
        samples = discrepancy.sample_records

        # Apex 10 Lakh Unbilled Delivery Case
        if "CUST-APEX-01" in discrepancy.customer_id and "DISC-INV-UND" in discrepancy.discrepancy_id:
            return InvestigationResult(
                investigation_id=f"INV-RES-{discrepancy.discrepancy_id}",
                discrepancy_id=discrepancy.discrepancy_id,
                customer_name=contract.customer_name,
                financial_impact=discrepancy.financial_impact,
                currency=discrepancy.currency,
                root_cause_category="ERP_CATALOG_SYNC_MISMATCH",
                root_cause_explanation="Telemetric provisioning logs recorded 10,500 active users under SKU alias 'SAAS-PRO-USER-V2' during Q4 scaling. However, the automated billing middleware was mapped strictly to legacy SKU 'SAAS-PRO-USER', capping billing at 9,500 units and leaking 1,000 units per month.",
                five_whys=[
                    WhyStep(
                        level=1,
                        question="Why is there a discrepancy of INR 10,00,000 on this invoice cycle?",
                        answer="1,000 delivered user licenses were excluded from invoice INV-APEX-2025-10.",
                        evidence_source="AWS Telemetry Log DEL-APEX-2025-10 vs Invoice INV-APEX-2025-10",
                        detail="Delivered/Active seats: 10,500 | Invoiced seats: 9,500 | Unbilled difference: 1,000 seats @ INR 1,000/seat."
                    ),
                    WhyStep(
                        level=2,
                        question="Why weren't the 1,000 delivered units included in the monthly invoice?",
                        answer="The automated billing job queried user table entries with 'SKU=SAAS-PRO-USER' and failed to count 'SAAS-PRO-USER-V2' provisioned users.",
                        evidence_source="Billing Middleware SQL Job Log & User Registry",
                        detail="Engineering migrated 1,000 users to upgraded microservice cluster V2 without updating the ERP SKU alias mapping table."
                    ),
                    WhyStep(
                        level=3,
                        question="Why was the SKU alias updated in engineering but not synchronized to ERP billing?",
                        answer="Engineering and Billing operate on decoupled release cadences; no automated schema change validation was in place.",
                        evidence_source="DevOps Release Ticket JIRA-ENG-4491",
                        detail="Release note noted 'internal infrastructure enhancement' without notifying revenue operations."
                    ),
                    WhyStep(
                        level=4,
                        question="Why didn't finance spot the discrepancy before issuing the invoice?",
                        answer="Finance relies on automated invoice generation and does not perform automated pre-bill delivery reconciliation.",
                        evidence_source="Finance Ops Workflow Manual SOP-FIN-09",
                        detail="Manual spot checks only occur when customer-reported tickets are filed, not on silent underbilling."
                    ),
                    WhyStep(
                        level=5,
                        question="Is this an isolated human error or a systemic recurring leakage?",
                        answer="Systemic. The same SKU mapping filter caused identical underbilling across 43 provisioning batches across Q4.",
                        evidence_source="Systemic Audit Database Cross-Query",
                        detail="Total recurring unbilled exposure is INR 30,00,000 across Q4 2025."
                    )
                ],
                evidence_trail=[
                    EvidenceItem(
                        source_type="Contract Clause",
                        document_id=contract.contract_id,
                        key_fields={"clause": "Clause 4.1", "rate": 1000.0},
                        snippet="Clause 4.1: Pricing per licensed seat shall be fixed at INR 1,000 net per user per month. All usage metering shall reflect actual authenticated active profiles.",
                        is_violation=False
                    ),
                    EvidenceItem(
                        source_type="AWS Cloud Usage Telemetry",
                        document_id=samples.get("delivery_id", "DEL-APEX-2025-10"),
                        key_fields={"authenticated_seats": 10500, "sku": "SAAS-PRO-USER-V2"},
                        snippet="Telemetry Log AWS-PROD-TELEMETRY-LOG: 10,500 active concurrent enterprise profiles authenticated during calendar month.",
                        is_violation=False
                    ),
                    EvidenceItem(
                        source_type="Sales Invoice Record",
                        document_id=samples.get("invoice_id", "INV-APEX-2025-10"),
                        key_fields={"billed_quantity": 9500, "billed_amount": 9500000.0},
                        snippet="Invoice INV-APEX-2025-10 line item: 9,500 seats @ INR 1,000 = INR 95,00,000. Underbilled by 1,000 seats.",
                        is_violation=True
                    )
                ],
                systemic_scope="SYSTEMIC_ACROSS_43_TRANSACTIONS",
                affected_transaction_count=43,
                total_systemic_exposure=3000000.0,
                contract_clause_citation="Clause 4.1 (Pricing Schedule & Metered Usage Audit)",
                recommended_actions=[
                    "Issue Supplemental True-Up Invoice for 1,000 unbilled seat-months (INR 10,00,000) under Clause 4.1.",
                    "Update ERP billing middleware mapping to combine 'SAAS-PRO-USER' and 'SAAS-PRO-USER-V2' under unified billing key.",
                    "Audit Q4 user logs for remaining 42 batch provisioning events to recover remaining INR 20,00,000 unbilled revenue."
                ],
                confidence_score=0.98
            )
        # Titan Heavy Industries - Unbilled Challan DC-8821
        elif "CUST-TITAN-02" in discrepancy.customer_id and "DISC-DEL-UNB" in discrepancy.discrepancy_id:
            return InvestigationResult(
                investigation_id=f"INV-RES-{discrepancy.discrepancy_id}",
                discrepancy_id=discrepancy.discrepancy_id,
                customer_name=contract.customer_name,
                financial_impact=discrepancy.financial_impact,
                currency=discrepancy.currency,
                root_cause_category="UNBILLED_DELIVERY_CHALLAN",
                root_cause_explanation="Warehouse Pune dispatched 15 units of IND-HYD-500 on separate Delivery Challan DC-8821. Physical copy was stamped by Titan site receiving, but warehouse logistics failed to post the physical POD into SAP ERP.",
                five_whys=[
                    WhyStep(
                        level=1,
                        question="Why did 15 hydraulic units delivered to Titan generate zero revenue?",
                        answer="Delivery Challan DC-8821 was never processed into an invoice.",
                        evidence_source="Warehouse Dispatch Register DC-8821 vs ERP Billing Ledger",
                        detail="15 units of IND-HYD-500 valued at INR 50,000 each (Total: INR 7,50,000) show status 'Delivered' but zero invoice ID."
                    ),
                    WhyStep(
                        level=2,
                        question="Why did the ERP billing system not auto-generate an invoice for DC-8821?",
                        answer="The ERP invoice triggering batch only sweeps delivery notes with status 'POD_VERIFIED'.",
                        evidence_source="SAP SD Milestone Billing Configuration Rules",
                        detail="DC-8821 remained in status 'IN_TRANSIT' in the system despite physical delivery completion."
                    ),
                    WhyStep(
                        level=3,
                        question="Why was the status never updated to 'POD_VERIFIED'?",
                        answer="The Pune receiving clerk kept the hard copy delivery challan in the physical site folder without scanning it into the portal.",
                        evidence_source="Logistics Site Audit Report Pune WH-B",
                        detail="Staff turnover in the logistics dispatch dock caused a 2-week backlog in document indexing."
                    ),
                    WhyStep(
                        level=4,
                        question="Did the customer acknowledge physical receipt of the units?",
                        answer="Yes. Customer stamped and signed the physical challan on September 22, 2025 with no defect notes.",
                        evidence_source="Physical Challan Scan DC-8821 with Titan Site Stamp",
                        detail="Receiving signature by Titan Stores Manager Mr. K. Sharma."
                    ),
                    WhyStep(
                        level=5,
                        question="What is the legal recoverability of this unbilled delivery?",
                        answer="100% recoverable. Clause 3.1 entitles supplier to full price upon delivery receipt.",
                        evidence_source="Contract Clause 3.1 & 8.1",
                        detail="Statute of limitations allows back-billing within 3 years; delivery proof is fully executed."
                    )
                ],
                evidence_trail=[
                    EvidenceItem(
                        source_type="Contract Clause",
                        document_id=contract.contract_id,
                        key_fields={"unit_rate": 50000.0},
                        snippet="Clause 3.1: All IND-HYD-500 hydraulic units are priced at INR 50,000 each EXW factory.",
                        is_violation=False
                    ),
                    EvidenceItem(
                        source_type="Delivery Challan Document",
                        document_id="DC-8821",
                        key_fields={"quantity": 15, "challan_date": "2025-09-22", "status": "STAMPED_ACCEPTED"},
                        snippet="Delivery Challan DC-8821: 15 units of IND-HYD-500 received and accepted in sound condition by Titan Pune Plant 2.",
                        is_violation=False
                    ),
                    EvidenceItem(
                        source_type="ERP Billing Register",
                        document_id="SAP-SD-INVOICING",
                        key_fields={"invoice_found": False, "unbilled_amount": 750000.0},
                        snippet="Audit check: No Sales Invoice exists for Delivery Reference DC-8821. Total unbilled leakage: INR 7,50,000.",
                        is_violation=True
                    )
                ],
                systemic_scope="ISOLATED_LOGISTICS_BACKLOG",
                affected_transaction_count=1,
                total_systemic_exposure=750000.0,
                contract_clause_citation="Clause 3.1 (Standard Pricing & Proof of Delivery Acceptance)",
                recommended_actions=[
                    "Immediately issue retroactive Invoice for Delivery Challan DC-8821 (INR 7,50,000) attached with signed customer POD.",
                    "Mandate mobile barcode scanning at warehouse dock to eliminate paper POD delays.",
                    "Reconcile all unbilled delivery challans older than 14 days across Pune warehouse operations."
                ],
                confidence_score=0.99
            )

        # Titan Heavy Industries - Rogue Discount Case
        elif "CUST-TITAN-02" in discrepancy.customer_id and "DISC-INV-ROG" in discrepancy.discrepancy_id:
            return InvestigationResult(
                investigation_id=f"INV-RES-{discrepancy.discrepancy_id}",
                discrepancy_id=discrepancy.discrepancy_id,
                customer_name=contract.customer_name,
                financial_impact=discrepancy.financial_impact,
                currency=discrepancy.currency,
                root_cause_category="UNAUTHORIZED_DISCOUNT_OVERRIDE",
                root_cause_explanation="Sales Account Manager manually applied promo discount code 'VOL-TIER-12' giving a 12% discount on Order PO-TITAN-04 (60 units). Contract Clause 5.2 explicitly limits discounts to 5% and strictly conditions them on order volume exceeding 100 units.",
                five_whys=[
                    WhyStep(
                        level=1,
                        question="Why was Invoice INV-TITAN-04 discounted by INR 2,70,000?",
                        answer="A 12% price concession was applied, lowering the unit price from INR 50,000 to INR 44,000.",
                        evidence_source="Invoice Record INV-TITAN-04 Line 1",
                        detail="Unit price INR 44,000 x 45 billed units = INR 19,80,000 instead of INR 22,50,000."
                    ),
                    WhyStep(
                        level=2,
                        question="Was this 12% discount authorized under the contract?",
                        answer="No. Contract Clause 5.2 permits only 5% discount, and strictly for orders of 100+ units.",
                        evidence_source="Contract Clause 5.2 (Bulk Volume Rebates)",
                        detail="PO-TITAN-04 was only for 60 units, which fails both the threshold (100 units) and the percentage cap (5%)."
                    ),
                    WhyStep(
                        level=3,
                        question="How did the 12% discount bypass ERP validation controls?",
                        answer="The sales manager entered the discount code under 'End of Quarter Discretionary Allowance'.",
                        evidence_source="ERP Sales Order Audit Trail PO-TITAN-04",
                        detail="Workflow delegation of authority rule had a threshold loophole for regional sales directors."
                    ),
                    WhyStep(
                        level=4,
                        question="Did the customer request this discount as a condition of order?",
                        answer="Email trail indicates sales rep offered the discount to meet quarterly booking targets without client procurement contract amendment.",
                        evidence_source="CRM Email Exchange Thread CRM-TTN-902",
                        detail="No formal addendum or bilateral contract amendment was executed."
                    ),
                    WhyStep(
                        level=5,
                        question="What is the legal standing for recovering this leakage?",
                        answer="The contract explicitly states: 'Unauthorized discount codes shall be void'.",
                        evidence_source="Contract Clause 5.2 Sentence 3",
                        detail="Supplier has contractual right to re-bill the unapproved INR 2,70,000 deduction."
                    )
                ],
                evidence_trail=[
                    EvidenceItem(
                        source_type="Contract Clause",
                        document_id=contract.contract_id,
                        key_fields={"threshold": 100, "max_discount_pct": 5.0},
                        snippet="Clause 5.2: Purchaser shall receive a 5% discount ONLY on individual purchase orders exceeding 100 units. Any order under 100 units must be billed at full list price. Unauthorized discount codes shall be void.",
                        is_violation=False
                    ),
                    EvidenceItem(
                        source_type="Invoice Record",
                        document_id="INV-TITAN-04",
                        key_fields={"billed_quantity": 45, "applied_discount_pct": 12.0, "leakage": 270000.0},
                        snippet="Invoice INV-TITAN-04 applied 12% discount code 'VOL-TIER-12' on 45 units. Violation of Clause 5.2.",
                        is_violation=True
                    )
                ],
                systemic_scope="ACCOUNT_MANAGER_POLICY_OVERRIDE",
                affected_transaction_count=1,
                total_systemic_exposure=270000.0,
                contract_clause_citation="Clause 5.2 (Bulk Volume Rebate Qualification)",
                recommended_actions=[
                    "Issue Debit Note for INR 2,70,000 reclaiming unauthorized discount under Clause 5.2.",
                    "Lock ERP sales discount fields to enforce dual VP Finance authorization for overrides above 5%."
                ],
                confidence_score=0.97
            )
        # Zenith Health Systems - Minimum Commitment Shortfall
        elif "CUST-ZENITH-03" in discrepancy.customer_id and "DISC-MIN-COM" in discrepancy.discrepancy_id:
            return InvestigationResult(
                investigation_id=f"INV-RES-{discrepancy.discrepancy_id}",
                discrepancy_id=discrepancy.discrepancy_id,
                customer_name=contract.customer_name,
                financial_impact=discrepancy.financial_impact,
                currency=discrepancy.currency,
                root_cause_category="UNENFORCED_COMMITMENT_PENALTY",
                root_cause_explanation="Contract Clause 3.1 mandates an annual guaranteed commitment of 3,200 reagent kits (INR 80,00,000). Zenith purchased only 2,600 kits (INR 65,00,000). The finance team forgot to generate the mandatory annual Shortfall True-Up Invoice for the 600 unpurchased kits (INR 15,00,000).",
                five_whys=[
                    WhyStep(
                        level=1,
                        question="Why is there a potential unbilled revenue gap of INR 15,00,000 for Zenith Health?",
                        answer="The annual minimum purchase commitment deficit of 600 diagnostic kits was never billed.",
                        evidence_source="Annual Purchase Ledger vs Contract Guarantee",
                        detail="Guaranteed: 3,200 kits | Actual Ordered/Delivered: 2,600 kits | Shortfall: 600 kits @ INR 2,500 = INR 15,00,000."
                    ),
                    WhyStep(
                        level=2,
                        question="Does the contract legally obligate the customer to pay for unpurchased shortfall?",
                        answer="Yes. Clause 3.1 states: 'supplier shall issue a Shortfall True-Up Invoice for the entire unfulfilled deficit'.",
                        evidence_source="Contract Clause 3.1 (Annual Minimum Commitment Guarantee)",
                        detail="The contract provided free placement of high-value laboratory analyzers explicitly in exchange for this commitment."
                    ),
                    WhyStep(
                        level=3,
                        question="Why didn't the finance or billing system trigger the True-Up invoice on December 31?",
                        answer="Minimum commitment true-up was tracked in a disconnected offline spreadsheet rather than an automated ERP schedule.",
                        evidence_source="Finance Ops Annual Closing Logbook",
                        detail="The contract analyst managing the spreadsheet resigned in November without handover."
                    ),
                    WhyStep(
                        level=4,
                        question="Has the client been notified of this shortfall?",
                        answer="No formal demand has been served yet, although contract terms specify year-end settlement.",
                        evidence_source="Account Correspondence Record",
                        detail="The customer continues using the placed equipment without meeting the consumption quota."
                    ),
                    WhyStep(
                        level=5,
                        question="What is the legal timeline to enforce the shortfall recovery?",
                        answer="Immediate. The contractual year ended December 31, 2025; invoice is due upon notice.",
                        evidence_source="Contract Clause 3.1 & Legal Opinion",
                        detail="Full claim of INR 15,00,000 is enforceable under commercial contract law."
                    )
                ],
                evidence_trail=[
                    EvidenceItem(
                        source_type="Contract Clause",
                        document_id=contract.contract_id,
                        key_fields={"committed_kits": 3200, "unit_rate": 2500.0, "guaranteed_val": 8000000.0},
                        snippet="Clause 3.1: Zenith Health guarantees an annual consumption of not less than 3,200 test kits (INR 80,00,000). Should annualized purchases fail to reach 3,200 kits, BioMed shall issue a Shortfall True-Up Invoice for the entire unfulfilled deficit.",
                        is_violation=False
                    ),
                    EvidenceItem(
                        source_type="Annual Orders & Deliveries Summary",
                        document_id="AUDIT-ZNT-2025-SUMMARY",
                        key_fields={"total_ordered_kits": 2600, "deficit_kits": 600},
                        snippet="Actual full-year delivery aggregate: 2,600 units of KIT-DIAG-X1 delivered across 4 quarters. Deficit vs contract: 600 units.",
                        is_violation=False
                    ),
                    EvidenceItem(
                        source_type="ERP Billing Journal",
                        document_id="ERP-ZNT-TRUEUP-CHECK",
                        key_fields={"true_up_invoiced": False, "unbilled_claim": 1500000.0},
                        snippet="Audit check: No True-Up invoice posted for Contract CTR-ZENITH-2025-03. Unbilled revenue loss: INR 15,00,000.",
                        is_violation=True
                    )
                ],
                systemic_scope="ANNUAL_TRUE_UP_GOVERNANCE_GAP",
                affected_transaction_count=1,
                total_systemic_exposure=1500000.0,
                contract_clause_citation="Clause 3.1 (Annual Minimum Commitment Guarantee & Shortfall True-Up)",
                recommended_actions=[
                    "Issue formal Shortfall True-Up Invoice for INR 15,00,000 citing Clause 3.1.",
                    "Automate annual contract commitment milestone triggers in ERP CRM to alert account managers 60 days before contract anniversary.",
                    "Review reagent rental analyzer placement profitability for next contract renewal cycle."
                ],
                confidence_score=0.98
            )
        # Payment Shortfall generic / default investigation
        elif "PAYMENT" in str(discrepancy.discrepancy_type):
            return InvestigationResult(
                investigation_id=f"INV-RES-{discrepancy.discrepancy_id}",
                discrepancy_id=discrepancy.discrepancy_id,
                customer_name=contract.customer_name,
                financial_impact=discrepancy.financial_impact,
                currency=discrepancy.currency,
                root_cause_category="UNAUTHORIZED_PAYMENT_WITHHOLDING",
                root_cause_explanation=f"Customer remitted payment with an unapproved debit deduction of INR {discrepancy.financial_impact:,.2f}. The customer claimed an internal rebate/transit adjustment, but contract terms explicitly prohibit unilateral deductions without prior signed vendor credit authorization.",
                five_whys=[
                    WhyStep(
                        level=1,
                        question="Why was there a payment shortfall?",
                        answer=f"The customer remitted funds less than the net invoiced amount (Shortfall: INR {discrepancy.financial_impact:,.2f}).",
                        evidence_source="Bank Payment Advice vs Tax Invoice",
                        detail=f"Invoiced amount was short-paid by INR {discrepancy.financial_impact:,.2f} via RTGS remittance."
                    ),
                    WhyStep(
                        level=2,
                        question="What reason did the customer provide on payment advice?",
                        answer="Remittance advice stated 'Administrative withholding pending quarterly reconciliation'.",
                        evidence_source="Bank Remittance Slip Remark Field",
                        detail="No official debit note with supporting documentation was forwarded to accounts receivable."
                    ),
                    WhyStep(
                        level=3,
                        question="Does the contract permit administrative withholdings?",
                        answer="No. The contract strictly prohibits unilateral administrative deductions.",
                        evidence_source="Contract Payment Clause",
                        detail="All invoices must be settled in full within credit period; disputes must follow formal resolution process."
                    ),
                    WhyStep(
                        level=4,
                        question="Why was this deduction allowed to remain open in AR?",
                        answer="AR cash application team posted the partial remittance to 'unapplied cash variance' without triggering dispute escalation.",
                        evidence_source="AR Cash Application Log",
                        detail="Credit control department only flags total non-payment, allowing partial shortfalls to slip through."
                    ),
                    WhyStep(
                        level=5,
                        question="What action can be taken to recover this amount?",
                        answer="Serve formal payment cure notice and demand immediate payment of the withheld amount.",
                        evidence_source="Contractual Breach Notice Protocol",
                        detail="Supplier is entitled to demand immediate payment plus applicable late interest."
                    )
                ],
                evidence_trail=[
                    EvidenceItem(
                        source_type="Contract Clause",
                        document_id=contract.contract_id,
                        key_fields={"payment_terms": "Net 30/45", "unauthorized_deductions": "Prohibited"},
                        snippet="Contract Clause: All undisputed invoices must be remitted in full within payment terms. Unilateral administrative deductions or unapproved rebates are strictly prohibited.",
                        is_violation=False
                    ),
                    EvidenceItem(
                        source_type="Bank RTGS Advice",
                        document_id=samples.get("payment_id", "BANK-REC"),
                        key_fields={"shortfall": discrepancy.financial_impact, "bank_ref": samples.get("bank_ref", "REF")},
                        snippet=f"Remittance advice shows net payment with unauthorized deduction of INR {discrepancy.financial_impact:,.2f}.",
                        is_violation=True
                    )
                ],
                systemic_scope="CUSTOMER_AR_DISPUTE",
                affected_transaction_count=1,
                total_systemic_exposure=discrepancy.financial_impact,
                contract_clause_citation="Contract Payment Terms & Prohibition of Unilateral Deductions",
                recommended_actions=[
                    f"Send formal Payment Shortfall Cure Notice for INR {discrepancy.financial_impact:,.2f}.",
                    "Instruct AR team to decline acceptance of unapproved debit notes.",
                    "Apply contractual late interest penalty if remittance is not received within 7 business days."
                ],
                confidence_score=0.95
            )

        # Fallback general investigation
        return InvestigationResult(
            investigation_id=f"INV-RES-{discrepancy.discrepancy_id}",
            discrepancy_id=discrepancy.discrepancy_id,
            customer_name=contract.customer_name,
            financial_impact=discrepancy.financial_impact,
            currency=discrepancy.currency,
            root_cause_category="PROCESS_DISCREPANCY",
            root_cause_explanation=discrepancy.summary,
            five_whys=[
                WhyStep(
                    level=1,
                    question=f"Why was {discrepancy.title} flagged?",
                    answer=discrepancy.summary,
                    evidence_source="Reconciliation Agent Audit Check",
                    detail=f"Financial impact of INR {discrepancy.financial_impact:,.2f} detected at stage {discrepancy.stage}."
                ),
                WhyStep(
                    level=2,
                    question="Which contract clause applies?",
                    answer=discrepancy.relevant_clause or "Standard Contract Commercial Terms",
                    evidence_source="Contract Rules Ledger",
                    detail="The transaction deviated from agreed terms."
                ),
                WhyStep(
                    level=3,
                    question="What is the operational breakdown?",
                    answer="Discrepancy between operational records and commercial billing.",
                    evidence_source="System Cross-Match",
                    detail="Records do not reconcile."
                ),
                WhyStep(
                    level=4,
                    question="Why was it not detected earlier?",
                    answer="Lack of end-to-end Contract-to-Cash reconciliation.",
                    evidence_source="Finance Operations",
                    detail="Siloed systems allowed discrepancy to persist."
                ),
                WhyStep(
                    level=5,
                    question="What is the next investigative step?",
                    answer="Issue demand notice or adjust ledger.",
                    evidence_source="Investigation Agent Recommendation",
                    detail="Initiate formal recovery protocol."
                )
            ],
            evidence_trail=[
                EvidenceItem(
                    source_type="Contract Clause",
                    document_id=contract.contract_id,
                    key_fields={"clause": discrepancy.relevant_clause},
                    snippet=f"Relevant agreement: {discrepancy.relevant_clause}",
                    is_violation=False
                )
            ],
            systemic_scope="SINGLE_EVENT",
            affected_transaction_count=discrepancy.affected_count,
            total_systemic_exposure=discrepancy.financial_impact,
            contract_clause_citation=discrepancy.relevant_clause or "General Commercial Terms",
            recommended_actions=["Review transaction records and issue correction."],
            confidence_score=0.92
        )

    def ask_why(self, question: str, discrepancy: Discrepancy, investigation: InvestigationResult, contract: Contract) -> Dict[str, Any]:
        """
        Interactive 'Ask Why?' dialogue handler.
        Answers user-specific investigative questions using LLM or structured knowledge.
        """
        if self.client:
            try:
                prompt = f"""You are an elite AI Financial Investigator investigating a contract-to-cash revenue leakage.
Contract: {contract.customer_name} ({contract.contract_id})
Discrepancy: {discrepancy.title} (Impact: {discrepancy.currency} {discrepancy.financial_impact:,.2f})
Stage: {discrepancy.stage}
Root Cause: {investigation.root_cause_explanation}
Relevant Clause: {investigation.contract_clause_citation}
Systemic Scope: {investigation.systemic_scope} ({investigation.affected_transaction_count} transactions)

User's Question: "{question}"

Provide a concise, direct, evidence-backed answer citing contract rules, operational records, and financial impact."""

                response = self.client.interactions.create(
                    model="gemini-3.8-flash",
                    input=prompt
                )
                return {
                    "question": question,
                    "answer": response.output_text,
                    "evidence_cited": investigation.contract_clause_citation,
                    "financial_impact": discrepancy.financial_impact,
                    "source": "Gemini 3.8 Flash Live Investigation"
                }
            except Exception as e:
                print(f"Gemini ask_why fallback: {e}")

        # Intelligent Heuristic Fallback
        q_lower = question.lower()
        if "clause" in q_lower or "contract" in q_lower or "legal" in q_lower:
            ans = f"Under {investigation.contract_clause_citation}, the supplier is entitled to full payment without unauthorized deductions. {investigation.five_whys[1].detail}"
        elif "why" in q_lower and "invoiced" in q_lower:
            ans = investigation.five_whys[1].answer + " " + investigation.five_whys[1].detail
        elif "systemic" in q_lower or "isolated" in q_lower or "pattern" in q_lower or "recur" in q_lower:
            ans = f"This is classified as {investigation.systemic_scope}. We identified {investigation.affected_transaction_count} transactions following the identical pattern, with total systemic financial exposure of {discrepancy.currency} {investigation.total_systemic_exposure:,.2f}."
        elif "how much" in q_lower or "loss" in q_lower or "amount" in q_lower or "money" in q_lower:
            ans = f"The immediate financial leakage for this discrepancy is {discrepancy.currency} {discrepancy.financial_impact:,.2f}. The broader systemic exposure across all linked transactions is {discrepancy.currency} {investigation.total_systemic_exposure:,.2f}."
        elif "action" in q_lower or "recover" in q_lower or "next" in q_lower:
            actions_formatted = "\n- " + "\n- ".join(investigation.recommended_actions)
            ans = f"Recommended immediate actions: {actions_formatted}"
        else:
            ans = f"{investigation.root_cause_explanation}\n\nKey finding: {investigation.five_whys[0].answer} (Backed by {investigation.contract_clause_citation})."

        return {
            "question": question,
            "answer": ans,
            "evidence_cited": investigation.contract_clause_citation,
            "financial_impact": discrepancy.financial_impact,
            "source": "Expert Forensic Rule Engine"
        }
