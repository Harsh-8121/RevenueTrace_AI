from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from ..models import ContractRecord, Investigation


def enhance_investigation(
    investigation: Investigation, contract: ContractRecord
) -> Investigation:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return investigation

    prompt = {
        "contract": contract.model_dump(),
        "investigation": {
            "total_leakage": investigation.total_leakage,
            "findings": [finding.model_dump() for finding in investigation.findings],
            "chain_summary": investigation.chain_summary,
        },
        "instructions": (
            "Return JSON with keys executive_summary and recommendation. "
            "Explain root causes and prioritized remediation for finance leadership."
        ),
    }

    body = json.dumps(
        {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a contract-to-cash revenue assurance analyst. "
                        "Be concise, evidence-backed, and quantify impact."
                    ),
                },
                {"role": "user", "content": json.dumps(prompt)},
            ],
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        content = payload["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        investigation.executive_summary = parsed.get(
            "executive_summary", investigation.executive_summary
        )
        investigation.recommendation = parsed.get(
            "recommendation", investigation.recommendation
        )
        investigation.llm_enhanced = True
    except (urllib.error.URLError, KeyError, json.JSONDecodeError, TimeoutError):
        pass

    return investigation
