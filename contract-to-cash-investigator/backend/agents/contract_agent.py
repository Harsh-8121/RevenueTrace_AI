import os
import re
import json
from typing import List, Dict, Any, Optional
from backend.models import Contract, ContractRule

class ContractAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize Gemini client: {e}")

    def parse_contract_text(self, text: str, customer_name: str = "Client Enterprise", currency: str = "INR") -> List[ContractRule]:
        if self.client:
            try:
                prompt = f"""You are an elite Contract Intelligence AI Agent for financial auditing.
Extract all business, pricing, discount, commitment, and payment rules from the following contract text.
For each rule, identify:
- rule_type: one of ["pricing", "commitment", "discount", "payment_terms", "penalty"]
- sku: product/service code if mentioned
- description: concise rule description
- unit_price: numeric unit rate if applicable
- min_commitment: minimum required units/volume if applicable
- discount_pct: percentage discount if applicable
- grace_days: payment credit term in days (default 30)
- penalty_rate_annual_pct: annual penalty interest rate if applicable
- clause_reference: clause title or number (e.g. Clause 4.1)
- clause_text: verbatim text snippet of the clause

Contract Text:
\"\"\"
{text}
\"\"\"

Return ONLY a valid JSON array of objects matching this schema."""

                response = self.client.interactions.create(
                    model="gemini-3.8-flash",
                    input=prompt
                )
                output = response.output_text
                # clean possible markdown formatting
                clean_json = re.sub(r"^```json\s*", "", output.strip(), flags=re.MULTILINE)
                clean_json = re.sub(r"^```\s*", "", clean_json, flags=re.MULTILINE)
                parsed = json.loads(clean_json)
                rules = []
                for idx, r in enumerate(parsed, 1):
                    rules.append(ContractRule(
                        rule_id=f"RULE-AI-{idx:02d}",
                        rule_type=r.get("rule_type", "pricing"),
                        sku=r.get("sku"),
                        description=r.get("description", "Contract Rule"),
                        unit_price=float(r["unit_price"]) if r.get("unit_price") is not None else None,
                        min_commitment=int(r["min_commitment"]) if r.get("min_commitment") is not None else None,
                        discount_pct=float(r["discount_pct"]) if r.get("discount_pct") is not None else None,
                        grace_days=int(r.get("grace_days", 30)),
                        penalty_rate_annual_pct=float(r["penalty_rate_annual_pct"]) if r.get("penalty_rate_annual_pct") is not None else None,
                        clause_reference=r.get("clause_reference", "General Clause"),
                        clause_text=r.get("clause_text", "")
                    ))
                if rules:
                    return rules
            except Exception as ex:
                print(f"Gemini rule extraction fallback: {ex}")

        # Deterministic Heuristic Rule Extraction Fallback
        rules = []
        rule_counter = 1

        # Pricing detection
        price_matches = re.findall(r"(?:price|rate|priced\s+at)\s+(?:is\s+)?(?:fixed\s+at\s+)?(?:INR|Rs\.?|₹|\$)\s*([\d,]+)", text, re.IGNORECASE)
        sku_match = re.search(r"\b([A-Z]{3,}-[A-Z0-9-]+)\b", text)
        sku_val = sku_match.group(1) if sku_match else "STANDARD-PRODUCT"

        if price_matches:
            unit_rate = float(price_matches[0].replace(",", ""))
            clause_match = re.search(r"(Clause\s*[\d\.]+[^\n:]*[:\n][^\n]+)", text, re.IGNORECASE)
            clause_ref = clause_match.group(1).split(":")[0].strip() if clause_match else "Clause 1.0 (Pricing)"
            clause_snippet = clause_match.group(1).strip() if clause_match else f"Standard pricing set at INR {unit_rate:,.2f}"
            rules.append(ContractRule(
                rule_id=f"RULE-HEUR-{rule_counter:02d}",
                rule_type="pricing",
                sku=sku_val,
                description=f"Standard unit price for {sku_val}",
                unit_price=unit_rate,
                clause_reference=clause_ref,
                clause_text=clause_snippet
            ))
            rule_counter += 1

        # Minimum commitment detection
        commit_match = re.search(r"(?:commitment|minimum|guarantees)\s+of\s+(?:not\s+less\s+than\s+)?([\d,]+)\s+(?:active\s+)?(?:units|licenses|kits|users)", text, re.IGNORECASE)
        if commit_match:
            min_val = int(commit_match.group(1).replace(",", ""))
            clause_match = re.search(r"(Clause\s*[\d\.]+[^\n:]*(?:commitment|volume)[^\n:]*[:\n][^\n]+)", text, re.IGNORECASE)
            clause_ref = clause_match.group(1).split(":")[0].strip() if clause_match else "Clause 2.0 (Volume Commitment)"
            clause_snippet = clause_match.group(1).strip() if clause_match else f"Client commits to minimum volume of {min_val:,} units."
            rules.append(ContractRule(
                rule_id=f"RULE-HEUR-{rule_counter:02d}",
                rule_type="commitment",
                sku=sku_val,
                description=f"Minimum Volume Commitment ({min_val:,} units)",
                min_commitment=min_val,
                clause_reference=clause_ref,
                clause_text=clause_snippet
            ))
            rule_counter += 1

        # Discount detection
        disc_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*discount", text, re.IGNORECASE)
        if disc_match:
            disc_pct = float(disc_match.group(1))
            rules.append(ContractRule(
                rule_id=f"RULE-HEUR-{rule_counter:02d}",
                rule_type="discount",
                sku=sku_val,
                description=f"Conditional volume discount of {disc_pct}%",
                discount_pct=disc_pct,
                clause_reference="Clause 5.0 (Volume Discount)",
                clause_text=f"Volume discount of {disc_pct}% conditional on qualifying order size."
            ))
            rule_counter += 1

        # Payment terms & grace days
        term_match = re.search(r"within\s+(\d+)\s*(?:calendar\s+)?days", text, re.IGNORECASE)
        grace_days = int(term_match.group(1)) if term_match else 30
        rules.append(ContractRule(
            rule_id=f"RULE-HEUR-{rule_counter:02d}",
            rule_type="payment_terms",
            description=f"Net {grace_days} Day Credit Terms",
            grace_days=grace_days,
            clause_reference="Clause 7.0 (Payment Terms)",
            clause_text=f"Invoices must be settled in full within {grace_days} calendar days of issuance."
        ))

        return rules
