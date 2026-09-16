from __future__ import annotations

import io
import re

from pypdf import PdfReader

from ..models import ContractRecord, InvoiceRecord, OrderRecord


def _extract_amounts(text: str) -> list[float]:
    matches = re.findall(r"\$?\s?([\d,]+\.\d{2})", text)
    return [float(value.replace(",", "")) for value in matches]


def parse_contract_pdf(content: bytes, filename: str) -> ContractRecord:
    reader = PdfReader(io.BytesIO(content))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    normalized = re.sub(r"\s+", " ", text)

    contract_id_match = re.search(r"(CTR-[A-Z0-9-]+)", normalized, re.IGNORECASE)
    contract_id = contract_id_match.group(1).upper() if contract_id_match else (
        f"CTR-UP-{filename.split('.')[0][:12].upper()}"
    )

    customer_match = re.search(
        r"(?:Customer|Client|Buyer)\s*:\s*([A-Za-z0-9 &.,'-]{3,80})",
        normalized,
        re.IGNORECASE,
    )
    customer_name = customer_match.group(1).strip() if customer_match else "Uploaded Contract"

    amounts = _extract_amounts(normalized)
    contract_value = max(amounts) if amounts else 0.0
    order_amount = amounts[0] if amounts else contract_value
    invoice_amount = amounts[1] if len(amounts) > 1 else contract_value
    payment_amount = amounts[2] if len(amounts) > 2 else invoice_amount

    terms_match = re.search(
        r"(Net\s*\d+|payment terms?:?\s*[^.]{5,80})",
        normalized,
        re.IGNORECASE,
    )
    terms = terms_match.group(1).strip() if terms_match else "Net 30"

    return ContractRecord(
        contract_id=contract_id,
        customer_name=customer_name,
        contract_value=contract_value,
        terms=terms,
        effective_date="2025-01-01",
        orders=[
            OrderRecord(
                order_id=f"SO-{contract_id}",
                amount=order_amount,
                order_date="2025-01-15",
            )
        ],
        deliveries=[],
        invoices=[
            InvoiceRecord(
                invoice_id=f"INV-{contract_id}",
                amount=invoice_amount,
                invoice_date="2025-02-01",
                due_date="2025-03-01",
            )
        ],
        payments=[],
        source="upload",
    )
