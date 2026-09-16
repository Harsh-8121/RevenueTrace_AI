import unittest
from backend.data_generator import get_scenarios_data
from backend.agents.reconciliation_agent import ReconciliationAgent

class TestReconciliationAgent(unittest.TestCase):
    def setUp(self):
        self.scenarios = get_scenarios_data()
        self.agent = ReconciliationAgent()

    def test_apex_reconciliation(self):
        data = self.scenarios["CUST-APEX-01"]
        result = self.agent.reconcile_customer(
            contract=data["contract"],
            orders=data["orders"],
            deliveries=data["deliveries"],
            invoices=data["invoices"],
            payments=data["payments"]
        )
        metrics = result["metrics"]
        # Contracted: 1.20 Cr
        self.assertEqual(metrics["contracted_value"], 12000000.0)
        # Verify discrepancies detected
        disc_types = [d.discrepancy_type.value for d in result["discrepancies"]]
        self.assertIn("UNBILLED_DELIVERY", disc_types)
        self.assertIn("PAYMENT_SHORTFALL", disc_types)

        # Check total leakage is positive
        self.assertGreater(metrics["total_leakage_detected"], 0)
        print("Apex Test Passed. Total Leakage:", metrics["total_leakage_detected"])

    def test_titan_reconciliation(self):
        data = self.scenarios["CUST-TITAN-02"]
        result = self.agent.reconcile_customer(
            contract=data["contract"],
            orders=data["orders"],
            deliveries=data["deliveries"],
            invoices=data["invoices"],
            payments=data["payments"]
        )
        disc_types = [d.discrepancy_type.value for d in result["discrepancies"]]
        self.assertIn("UNBILLED_DELIVERY", disc_types)
        self.assertIn("ROGUE_DISCOUNT", disc_types)
        self.assertIn("PAYMENT_SHORTFALL", disc_types)
        print("Titan Test Passed. Total Leakage:", result["metrics"]["total_leakage_detected"])

    def test_zenith_reconciliation(self):
        data = self.scenarios["CUST-ZENITH-03"]
        result = self.agent.reconcile_customer(
            contract=data["contract"],
            orders=data["orders"],
            deliveries=data["deliveries"],
            invoices=data["invoices"],
            payments=data["payments"]
        )
        disc_types = [d.discrepancy_type.value for d in result["discrepancies"]]
        self.assertIn("UNCOLLECTED_COMMITMENT", disc_types)
        print("Zenith Test Passed. Total Leakage:", result["metrics"]["total_leakage_detected"])

if __name__ == "__main__":
    unittest.main()
