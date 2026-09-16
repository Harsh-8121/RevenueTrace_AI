from __future__ import annotations

import uuid
from typing import Any

from .models import Finding, Investigation


SAMPLE_RECORDS: dict[str, dict[str, Any]] = {
    "CTR-1001": {
        "contract_value": 250000.0,
        "order_total": 250000.0,
        "delivered_value": 245000.0,
        "invoiced_amount": 240000.0,
        "paid_amount": 235000.0,
        "terms": "Net 30, 2% early payment discount within 10 days",
    }
}


def run_investigation(contract_id: str) -> Investigation:
    record = SAMPLE_RECORDS.get(contract_id)
    if record is None:
        raise ValueError(f"Unknown contract id: {contract_id}")

    findings: list[Finding] = []
    delivery_gap = record["order_total"] - record["delivered_value"]
    if delivery_gap > 0:
        findings.append(
            Finding(
                category="delivery",
                severity="medium",
                description=(
                    f"Delivered value is ${record['delivered_value']:,.0f}, "
                    f"which is ${delivery_gap:,.0f} below the order total."
                ),
                financial_impact=delivery_gap,
                evidence=[
                    f"Order total: ${record['order_total']:,.0f}",
                    f"Delivered value: ${record['delivered_value']:,.0f}",
                ],
            )
        )

    invoice_gap = record["delivered_value"] - record["invoiced_amount"]
    if invoice_gap > 0:
        findings.append(
            Finding(
                category="billing",
                severity="high",
                description=(
                    f"Invoiced amount is ${record['invoiced_amount']:,.0f}, "
                    f"under-billing delivered goods by ${invoice_gap:,.0f}."
                ),
                financial_impact=invoice_gap,
                evidence=[
                    f"Delivered value: ${record['delivered_value']:,.0f}",
                    f"Invoiced amount: ${record['invoiced_amount']:,.0f}",
                ],
            )
        )

    payment_gap = record["invoiced_amount"] - record["paid_amount"]
    if payment_gap > 0:
        findings.append(
            Finding(
                category="collections",
                severity="medium",
                description=(
                    f"Customer paid ${record['paid_amount']:,.0f} against "
                    f"${record['invoiced_amount']:,.0f} invoiced."
                ),
                financial_impact=payment_gap,
                evidence=[
                    f"Invoiced amount: ${record['invoiced_amount']:,.0f}",
                    f"Paid amount: ${record['paid_amount']:,.0f}",
                    f"Payment terms: {record['terms']}",
                ],
            )
        )

    total_leakage = sum(finding.financial_impact for finding in findings)
    recommendation = (
        "Issue a catch-up invoice for under-billed delivery and open a "
        "collections task for the outstanding payment."
        if findings
        else "No revenue leakage detected for this contract."
    )

    return Investigation(
        id=str(uuid.uuid4()),
        contract_id=contract_id,
        status="completed",
        total_leakage=total_leakage,
        findings=findings,
        recommendation=recommendation,
    )
