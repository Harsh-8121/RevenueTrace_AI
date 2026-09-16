import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestC2CInvestigatorAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(len(data["scenarios_available"]), 3)

    def test_02_list_scenarios(self):
        response = self.client.get("/api/scenarios")
        self.assertEqual(response.status_code, 200)
        scenarios = response.json()
        self.assertEqual(len(scenarios), 3)
        cust_ids = [s["customer_id"] for s in scenarios]
        self.assertIn("CUST-APEX-01", cust_ids)
        self.assertIn("CUST-TITAN-02", cust_ids)
        self.assertIn("CUST-ZENITH-03", cust_ids)

    def test_03_scenario_details(self):
        response = self.client.get("/api/scenarios/CUST-APEX-01")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["customer_id"], "CUST-APEX-01")
        self.assertEqual(len(data["orders"]), 12)
        self.assertEqual(len(data["deliveries"]), 12)
        self.assertEqual(len(data["invoices"]), 12)
        self.assertEqual(len(data["payments"]), 12)

    def test_04_reconciliation(self):
        response = self.client.get("/api/reconciliation/CUST-APEX-01")
        self.assertEqual(response.status_code, 200)
        recon = response.json()
        self.assertIn("metrics", recon)
        self.assertIn("stages", recon)
        self.assertIn("discrepancies", recon)
        self.assertEqual(len(recon["stages"]), 5)
        self.assertGreater(recon["metrics"]["total_leakage_detected"], 0)

    def test_05_portfolio_summary(self):
        response = self.client.get("/api/portfolio-summary")
        self.assertEqual(response.status_code, 200)
        summary = response.json()
        self.assertEqual(summary["account_count"], 3)
        self.assertGreater(summary["total_leakage"], 0)

    def test_06_investigate_and_ask_why(self):
        # 1. Reconcile to get a discrepancy ID
        rec_res = self.client.get("/api/reconciliation/CUST-APEX-01").json()
        discrepancy = rec_res["discrepancies"][0]

        # 2. Run investigation
        inv_res = self.client.post("/api/investigate", json={
            "customer_id": "CUST-APEX-01",
            "discrepancy_id": discrepancy["discrepancy_id"]
        })
        self.assertEqual(inv_res.status_code, 200)
        inv = inv_res.json()
        self.assertIn("five_whys", inv)
        self.assertEqual(len(inv["five_whys"]), 5)
        self.assertIn("evidence_trail", inv)
        self.assertIn("recommended_actions", inv)

        # 3. Test Ask Why
        why_res = self.client.post("/api/ask-why", json={
            "customer_id": "CUST-APEX-01",
            "discrepancy_id": discrepancy["discrepancy_id"],
            "question": "Why wasn't this invoiced?"
        })
        self.assertEqual(why_res.status_code, 200)
        why = why_res.json()
        self.assertIn("answer", why)
        self.assertIn("evidence_cited", why)

    def test_07_generate_notice_and_audit_report(self):
        rec_res = self.client.get("/api/reconciliation/CUST-APEX-01").json()
        discrepancy = rec_res["discrepancies"][0]

        notice_res = self.client.post("/api/actions/generate-notice", json={
            "customer_id": "CUST-APEX-01",
            "discrepancy_id": discrepancy["discrepancy_id"]
        })
        self.assertEqual(notice_res.status_code, 200)
        notice = notice_res.json()
        self.assertIn("formal_letter_body", notice)
        self.assertIn("internal_erp_directive", notice)

        audit_res = self.client.get("/api/actions/audit-report")
        self.assertEqual(audit_res.status_code, 200)
        self.assertIn("markdown", audit_res.json())

    def test_08_frontend_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Contract-to-Cash", response.text)
        self.assertIn("Trace My Money", response.text)

if __name__ == "__main__":
    unittest.main()
