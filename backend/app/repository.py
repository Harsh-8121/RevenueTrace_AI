from __future__ import annotations

import json
from pathlib import Path

from .models import ContractRecord

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "seed_contracts.json"

_contracts: dict[str, ContractRecord] = {}
_investigations: dict[str, dict] = {}
_loaded = False


def _load_seed() -> None:
    global _loaded
    if _loaded:
        return

    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    for item in payload["contracts"]:
        contract = ContractRecord(**item, source="seed")
        _contracts[contract.contract_id] = contract
    _loaded = True


def list_contracts() -> list[ContractRecord]:
    _load_seed()
    return sorted(_contracts.values(), key=lambda c: c.contract_id)


def get_contract(contract_id: str) -> ContractRecord | None:
    _load_seed()
    return _contracts.get(contract_id)


def upsert_contract(contract: ContractRecord) -> ContractRecord:
    _load_seed()
    _contracts[contract.contract_id] = contract
    return contract


def save_investigation(investigation: dict) -> dict:
    _investigations[investigation["id"]] = investigation
    return investigation


def list_investigations() -> list[dict]:
    return list(_investigations.values())


def get_investigation(investigation_id: str) -> dict | None:
    return _investigations.get(investigation_id)


def uploaded_contract_count() -> int:
    _load_seed()
    return sum(1 for contract in _contracts.values() if contract.source == "upload")
