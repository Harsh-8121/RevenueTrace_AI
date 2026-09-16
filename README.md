# Contract-to-Cash AI Investigator

> **"Trace every rupee from contract to cash. Find what fell through the cracks."**

Contract-to-Cash AI Investigator is an enterprise-grade AI financial investigation platform that traces the complete journey of revenue across:

$$\text{Contract} \longrightarrow \text{Order} \longrightarrow \text{Delivery/Usage} \longrightarrow \text{Invoice} \longrightarrow \text{Payment}$$

Traditional BI tools merely show that high-level numbers do not balance. This platform acts as an **AI financial forensic investigator** that reconciles operational reality against contractual entitlements, pinpoints root causes, cites exact contractual clauses and operational transactions, calculates financial leakage down to the rupee, and generates formal customer recovery demand notices.

---

## Key Features

### 1. 🔍 Trace My Money (Interactive Journey Waterfall)
- Visual step-by-step handover tracking:
  - **Contracted Revenue** (e.g. ₹1.20 Cr)
  - **Ordered** (e.g. ₹1.16 Cr)
  - **Delivered / Consumed** (e.g. ₹1.15 Cr)
  - **Invoiced** (e.g. ₹1.08 Cr)
  - **Collected** (e.g. ₹1.01 Cr)
- Clear financial leakage indicators at each handover step.
- One-click **"Investigate this Gap"** button to jump directly into the AI root cause analysis.

### 2. 🧠 "Ask Why?" 5-Whys Root Cause Engine
- Deconstructs every discrepancy down to its operational and system failure:
  - **Finding:** ₹10,00,000 potential unbilled revenue.
  - **Why 1:** 1,000 delivered units were omitted from invoices.
  - **Why 2:** The telemetry logs recorded usage under `SAAS-PRO-USER-V2`, but billing middleware queried legacy `SAAS-PRO-USER`.
  - **Why 3:** Engineering upgraded the cluster without updating the ERP catalog mapping table.
  - **Why 4:** Finance relied on automated billing without pre-bill telemetry reconciliation.
  - **Why 5 (Systemic Scope):** Identical discrepancy discovered across 43 automated batch transactions in Q4 (total exposure: ₹30,00,000).
- Interactive conversational interrogation: ask custom questions like *"Which clause entitles us to back-bill?"* and receive authoritative forensic answers.

### 3. 🤖 Multi-Agent Architecture
- **Contract Agent:** Parses master service agreements, extracting structured rules (rates, minimum commitments, tiered volume rebates, payment credit terms, and delay penalties) via Gemini 3.8 Flash or deterministic regex fallback.
- **Reconciliation Agent:** Deterministic Python/Pandas mathematical engine ensuring zero financial hallucinations.
- **Investigation Agent:** Cross-references evidence across contract clauses, purchase orders, delivery challans, tax invoices, and bank remittance advices.
- **Action & Report Agent:** Formulates legally binding customer Recovery Demand Letters and generates comprehensive executive audit reports.

---

## Pre-Loaded Enterprise Scenarios

1. **Apex Global Technologies (Enterprise SaaS & Cloud Infrastructure)**
   - **Contract:** ₹1,000/seat/mo, 10,000 seat annual minimum commitment (₹1.20 Cr).
   - **Leakage:** 10,500 active users delivered, but billing only invoiced 9,500 seats due to ERP SKU alias mismatch (`SAAS-PRO-USER-V2`).
   - **Financial Impact:** ₹10,00,000 unbilled leakage + ₹7,00,000 unauthorized customer payment deduction.

2. **Titan Heavy Industries (Industrial Equipment & Logistics)**
   - **Contract:** ₹50,000/pump, 5% volume rebate strictly for orders > 100 units.
   - **Leakage:** 15 pumps delivered on Challan `DC-8821` completely unbilled (₹7,50,000); unauthorized 12% rogue discount applied on Order 4 (₹2,70,000); short payment of ₹5,00,000.

3. **Zenith Health Systems (Healthcare Diagnostic Networks)**
   - **Contract:** ₹2,500/reagent kit with guaranteed annual commitment of 3,200 kits (₹80,00,000) or shortfall liquidated recovery.
   - **Leakage:** Customer ordered only 2,600 kits (₹65,00,000). Finance failed to trigger the mandatory ₹15,00,000 Minimum Commitment Shortfall True-Up Invoice.

---

## Quickstart Guide

### Prerequisites
- Python 3.10+ (No Node.js or NPM required!)

### Installation & Launch
```bash
# 1. Clone or navigate to the repository
cd contract-to-cash-investigator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the platform
python run_app.py
```

Open your browser at:
- **Web Dashboard:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Technology Stack
- **Backend:** Python 3.11, FastAPI, Uvicorn, Pydantic v2
- **Data & Reconciliation:** Python, Pandas
- **AI Core:** `google-genai` SDK (Gemini 3.8 Flash) with built-in Expert Forensic Fallback
- **Frontend:** Responsive Single-Page Application (HTML5, Tailwind CSS, Alpine.js, Lucide Icons)
