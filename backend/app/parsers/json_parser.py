from __future__ import annotations

import json

from ..models import ContractRecord


def parse_contracts_json(content: bytes) -> list[ContractRecord]:
    payload = json.loads(content.decode("utf-8"))
    contracts = payload["contracts"] if isinstance(payload, dict) else payload
    if not isinstance(contracts, list):
        raise ValueError("JSON must contain a contracts array.")

    return [ContractRecord(**item, source="upload") for item in contracts]
