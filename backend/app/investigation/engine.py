from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ..models import ContractRecord, Finding, Investigation
from ..repository import get_contract, save_investigation
from .llm import enhance_investigation


def _sum_amounts(items: list, field: str = "amount") -> float:
    return sum(getattr(item, field) for item in items)


def _analyze_contract(contract: ContractRecord) -> list[Finding]:
    findings: list[Finding] = []

    order_total = _sum_amounts(contract.orders)
    delivered_total = _sum_amounts(contract.deliveries)
    invoiced_total = _sum_amounts(contract.invoices)
    paid_total = _sum_amounts(contract.payments)

    if order_total > contract.contract_value:
        gap = order_total - contract.contract_value
        findings.append(
            Finding(
                category="contract",
                severity="high",
                description=(
                    f"Orders total ${order_total:,.0f}, exceeding contract value "
                    f"${contract.contract_value:,.0f}."
                ),
                financial_impact=gap,
                evidence=[
                    f"Contract value: ${contract.contract_value:,.0f}",
                    f"Order total: ${order_total:,.0f}",
                ],
                root_cause="Order volume exceeded contracted ceiling without amendment.",
            )
        )

    if delivered_total < order_total:
        gap = order_total - delivered_total
        findings.append(
            Finding(
                category="delivery",
                severity="medium",
                description=(
                    f"Delivered ${delivered_total:,.0f} against ${order_total:,.0f} ordered."
                ),
                financial_impact=gap,
                evidence=[
                    f"Order total: ${order_total:,.0f}",
                    f"Delivered total: ${delivered_total:,.0f}",
                ],
                root_cause="Partial fulfillment or delivery shortfall before billing.",
            )
        )

    if invoiced_total < delivered_total:
        gap = delivered_total - invoiced_total
        findings.append(
            Finding(
                category="billing",
                severity="high",
                description=(
                    f"Invoiced ${invoiced_total:,.0f} for ${delivered_total:,.0f} delivered."
                ),
                financial_impact=gap,
                evidence=[
                    f"Delivered total: ${delivered_total:,.0f}",
                    f"Invoiced total: ${invoiced_total:,.0f}",
                ],
                root_cause="Under-billing relative to accepted delivery value.",
            )
        )

    if paid_total < invoiced_total:
        gap = invoiced_total - paid_total
        findings.append(
            Finding(
                category="collections",
                severity="medium",
                description=(
                    f"Collected ${paid_total:,.0f} against ${invoiced_total:,.0f} invoiced."
                ),
                financial_impact=gap,
                evidence=[
                    f"Invoiced total: ${invoiced_total:,.0f}",
                    f"Paid total: ${paid_total:,.0f}",
                    f"Payment terms: {contract.terms}",
                ],
                root_cause="Outstanding receivable or delayed customer payment.",
            )
        )

    invoice_ids = [invoice.invoice_id for invoice in contract.invoices]
    if len(invoice_ids) != len(set(invoice_ids)):
        findings.append(
            Finding(
                category="duplicate",
                severity="critical",
                description="Duplicate invoice identifiers detected in the billing chain.",
                financial_impact=0.0,
                evidence=[f"Invoice IDs: {', '.join(invoice_ids)}"],
                root_cause="Duplicate billing reference may indicate a posting error.",
            )
        )

    if len(contract.invoices) > 1 and invoiced_total > delivered_total:
        gap = invoiced_total - delivered_total
        findings.append(
            Finding(
                category="billing",
                severity="high",
                description=(
                    f"Total invoiced ${invoiced_total:,.0f} exceeds delivered "
                    f"${delivered_total:,.0f}."
                ),
                financial_impact=gap,
                evidence=[
                    f"Invoice count: {len(contract.invoices)}",
                    f"Delivered total: ${delivered_total:,.0f}",
                    f"Invoiced total: ${invoiced_total:,.0f}",
                ],
                root_cause="Split or duplicate invoicing may have over-billed the customer.",
            )
        )

    if "retainage" in contract.terms.lower() and contract.payments and not any(
        payment.amount < invoiced_total * 0.15 for payment in contract.payments
    ):
        findings.append(
            Finding(
                category="terms",
                severity="low",
                description="Retainage terms present but no retained payment pattern detected.",
                financial_impact=0.0,
                evidence=[f"Terms: {contract.terms}"],
                root_cause="Retainage release may not have been invoiced or collected.",
            )
        )

    return findings


def run_investigation(contract_id: str, use_llm: bool = True) -> Investigation:
    contract = get_contract(contract_id)
    if contract is None:
        raise ValueError(f"Unknown contract id: {contract_id}")

    findings = _analyze_contract(contract)
    total_leakage = sum(finding.financial_impact for finding in findings)

    chain_summary = {
        "contract_value": contract.contract_value,
        "order_total": _sum_amounts(contract.orders),
        "delivered_total": _sum_amounts(contract.deliveries),
        "invoiced_total": _sum_amounts(contract.invoices),
        "paid_total": _sum_amounts(contract.payments),
    }

    recommendation = (
        "Prioritize billing catch-up for under-invoiced delivery, then open collections "
        "on outstanding receivables and validate contract amendments for order overruns."
        if findings
        else "No material revenue leakage detected across the contract-to-cash chain."
    )

    executive_summary = (
        f"{contract.customer_name} shows ${total_leakage:,.0f} in estimated leakage across "
        f"{len(findings)} finding(s) from contract through payment."
        if findings
        else f"{contract.customer_name} is aligned across order, delivery, invoice, and payment totals."
    )

    investigation = Investigation(
        id=str(uuid.uuid4()),
        contract_id=contract.contract_id,
        customer_name=contract.customer_name,
        status="completed",
        total_leakage=total_leakage,
        findings=findings,
        recommendation=recommendation,
        executive_summary=executive_summary,
        chain_summary=chain_summary,
        llm_enhanced=False,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    if use_llm and findings:
        investigation = enhance_investigation(investigation, contract)

    save_investigation(investigation.model_dump())
    return investigation
