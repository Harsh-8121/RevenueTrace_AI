import uvicorn
import os
import sys

def main():
    print("=" * 70)
    print(" CONTRACT-TO-CASH AI INVESTIGATOR ")
    print(" Trace every rupee from contract to cash. Find what fell through the cracks. ")
    print("=" * 70)
    print("\n[+] Initializing Multi-Agent Financial Investigation Core...")
    print("    - Contract Agent: Online (Rule Extraction Engine)")
    print("    - Reconciliation Agent: Online (Deterministic Python Math)")
    print("    - Investigation Agent: Online (5-Whys Root Cause Analyzer)")
    print("    - Action & Report Agent: Online (Notice & Audit Generator)")
    print("\n[+] Enterprise Scenarios Loaded:")
    print("    1. Apex Global Technologies (Enterprise SaaS - 1,000 Unbilled Seats)")
    print("    2. Titan Heavy Industries (Equipment - Unbilled DC-8821 & Rogue Discount)")
    print("    3. Zenith Health Systems (Healthcare - Unenforced Minimum Commitment)")
    print("\n[+] Launching local forensic web server...")
    print("    -> Web Dashboard:      http://127.0.0.1:8000")
    print("    -> OpenAPI Docs:       http://127.0.0.1:8000/docs")
    print("    -> Portfolio Summary:  http://127.0.0.1:8000/api/portfolio-summary")
    print("=" * 70)
    
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
