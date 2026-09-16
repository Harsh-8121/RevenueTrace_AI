from __future__ import annotations

import csv
import io
from collections import defaultdict

from ..models import (
    ContractRecord,
    DeliveryRecord,
    InvoiceRecord,
    OrderRecord,
    PaymentRecord,
)


def parse_contracts_csv(content: bytes) -> list[ContractRecord]:
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    required = {"record_type", "contract_id", "customer_name", "amount"}
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
        raise ValueError(
            "CSV must include columns: record_type, contract_id, customer_name, amount."
        )

    grouped: dict[str, dict] = defaultdict(
        lambda: {
            "orders": [],
            "deliveries": [],
            "invoices": [],
            "payments": [],
            "meta": {},
        }
    )

    for row in reader:
        contract_id = row["contract_id"].strip()
        record_type = row["record_type"].strip().lower()
        amount = float(row["amount"])
        bucket = grouped[contract_id]

        if record_type == "contract":
            bucket["meta"] = {
                "contract_id": contract_id,
                "customer_name": row.get("customer_name", "").strip() or contract_id,
                "contract_value": amount,
                "terms": row.get("terms", "Net 30").strip(),
                "effective_date": row.get("date", row.get("effective_date", "2025-01-01")),
            }
        elif record_type == "order":
            bucket["orders"].append(
                OrderRecord(
                    order_id=row.get("reference_id", f"SO-{contract_id}"),
                    amount=amount,
                    order_date=row.get("date", "2025-01-01"),
                )
            )
        elif record_type == "delivery":
            bucket["deliveries"].append(
                DeliveryRecord(
                    delivery_id=row.get("reference_id", f"DL-{contract_id}"),
                    amount=amount,
                    delivery_date=row.get("date", "2025-01-15"),
                )
            )
        elif record_type == "invoice":
            bucket["invoices"].append(
                InvoiceRecord(
                    invoice_id=row.get("reference_id", f"INV-{contract_id}"),
                    amount=amount,
                    invoice_date=row.get("date", "2025-02-01"),
                    due_date=row.get("due_date", "2025-03-01"),
                )
            )
        elif record_type == "payment":
            bucket["payments"].append(
                PaymentRecord(
                    payment_id=row.get("reference_id", f"PAY-{contract_id}"),
                    amount=amount,
                    payment_date=row.get("date", "2025-03-01"),
                )
            )

    contracts: list[ContractRecord] = []
    for contract_id, bucket in grouped.items():
        meta = bucket["meta"] or {
            "contract_id": contract_id,
            "customer_name": contract_id,
            "contract_value": sum(item.amount for item in bucket["orders"]) or 0.0,
            "terms": "Net 30",
            "effective_date": "2025-01-01",
        }
        contracts.append(
            ContractRecord(
                **meta,
                orders=bucket["orders"],
                deliveries=bucket["deliveries"],
                invoices=bucket["invoices"],
                payments=bucket["payments"],
                source="upload",
            )
        )

    if not contracts:
        raise ValueError("No contract rows found in CSV.")

    return contracts
