from backend.models import (
    Contract, ContractRule, Order, Delivery, Invoice, Payment,
    Discrepancy, DiscrepancyType, Severity
)
from typing import Dict, Any, List

def get_scenarios_data() -> Dict[str, Dict[str, Any]]:
    # Scenario 1: Apex Global Technologies
    apex_contract = Contract(
        contract_id="CTR-APEX-2025-01",
        customer_id="CUST-APEX-01",
        customer_name="Apex Global Technologies",
        start_date="2025-01-01",
        end_date="2025-12-31",
        currency="INR",
        annual_committed_value=12000000.0,
        rules=[
            ContractRule(
                rule_id="RULE-APEX-P1",
                rule_type="pricing",
                sku="SAAS-PRO-USER",
                description="Enterprise Pro License monthly subscription price",
                unit_price=1000.0,
                clause_reference="Clause 4.1 (Pricing Schedule)",
                clause_text="Pricing per licensed seat shall be fixed at INR 1,000 net per user per calendar month, billed in arrears."
            ),
            ContractRule(
                rule_id="RULE-APEX-C1",
                rule_type="commitment",
                sku="SAAS-PRO-USER",
                description="Minimum Annual User Commitment",
                min_commitment=10000,
                clause_reference="Clause 4.2 (Volume Commitment)",
                clause_text="Client commits to maintaining a minimum aggregate commitment of 10,000 active monthly licenses."
            ),
            ContractRule(
                rule_id="RULE-APEX-T1",
                rule_type="payment_terms",
                description="Net 30 Payment Terms",
                grace_days=30,
                clause_reference="Clause 7.3 (Payment Terms & Deductions)",
                clause_text="All undisputed invoices must be remitted in full within 30 calendar days. Unilateral administrative deductions are strictly prohibited."
            )
        ],
        raw_text="""MASTER SERVICES & SOFTWARE LICENSE AGREEMENT
Party A: CloudScale Enterprise Solutions Ltd.
Party B: Apex Global Technologies Pvt. Ltd.
Effective Date: January 1, 2025. Expiration: December 31, 2025.

Clause 4.1 (Pricing Schedule):
The contracted unit price for SAAS-PRO-USER enterprise cloud licenses is fixed at INR 1,000 per user per month. All usage metering shall reflect actual authenticated active profiles.

Clause 4.2 (Volume Commitment):
Client guarantees an annual commitment of not less than 10,000 monthly active users (120,000 total annual user-months), representing a minimum committed contract value of INR 1,20,00,000.

Clause 7.3 (Payment Terms & Deductions):
Payment shall be made within 30 days of invoice generation. No deductions or withholdings for administrative processing or promotional rebates shall be permitted without prior written authorization signed by CloudScale VP Finance."""
    )

    apex_orders = []
    order_quantities = [9500, 9500, 9600, 9600, 9700, 9700, 9800, 9800, 9800, 10000, 10000, 10000]
    for idx, qty in enumerate(order_quantities, 1):
        apex_orders.append(Order(
            order_id=f"PO-APEX-2025-{idx:02d}",
            customer_id="CUST-APEX-01",
            order_date=f"2025-{idx:02d}-01",
            sku="SAAS-PRO-USER",
            quantity=qty,
            contracted_price=1000.0,
            order_price=1000.0,
            total_amount=qty * 1000.0,
            po_reference=f"PO-APX-{202500 + idx}"
        ))

    apex_deliveries = []
    for idx, o in enumerate(apex_orders, 1):
        deliv_qty = o.quantity if idx < 10 else 10500
        apex_deliveries.append(Delivery(
            delivery_id=f"DEL-APEX-2025-{idx:02d}",
            order_id=o.order_id,
            customer_id="CUST-APEX-01",
            delivery_date=f"2025-{idx:02d}-28",
            sku="SAAS-PRO-USER" if idx < 10 else "SAAS-PRO-USER-V2",
            delivered_quantity=deliv_qty,
            challan_number=f"CHL-APX-{5500 + idx}",
            warehouse_ref="AWS-PROD-TELEMETRY-LOG"
        ))

    apex_invoices = []
    for idx, d in enumerate(apex_deliveries, 1):
        billed_qty = d.delivered_quantity if idx < 10 else 9500
        apex_invoices.append(Invoice(
            invoice_id=f"INV-APEX-2025-{idx:02d}",
            delivery_id=d.delivery_id,
            order_id=d.order_id,
            customer_id="CUST-APEX-01",
            invoice_date=f"2025-{idx:02d}-30",
            due_date=f"2025-{min(idx+1, 12):02d}-28",
            sku="SAAS-PRO-USER",
            billed_quantity=billed_qty,
            unit_price=1000.0,
            total_amount=billed_qty * 1000.0
        ))

    apex_payments = []
    for idx, inv in enumerate(apex_invoices, 1):
        if idx == 10:
            apex_payments.append(Payment(
                payment_id=f"PAY-APEX-2025-{idx:02d}",
                invoice_id=inv.invoice_id,
                customer_id="CUST-APEX-01",
                payment_date="2025-11-20",
                amount_due=inv.total_amount,
                amount_paid=inv.total_amount - 700000.0,
                shortfall_amount=700000.0,
                bank_reference="HDFC-RTGS-8912431-SHORT",
                status="PARTIAL"
            ))
        else:
            apex_payments.append(Payment(
                payment_id=f"PAY-APEX-2025-{idx:02d}",
                invoice_id=inv.invoice_id,
                customer_id="CUST-APEX-01",
                payment_date=f"2025-{idx:02d}-25",
                amount_due=inv.total_amount,
                amount_paid=inv.total_amount,
                shortfall_amount=0.0,
                bank_reference=f"HDFC-RTGS-{770000 + idx}",
                status="SETTLED"
            ))

    # Scenario 2: Titan Heavy Industries
    titan_contract = Contract(
        contract_id="CTR-TITAN-2025-02",
        customer_id="CUST-TITAN-02",
        customer_name="Titan Heavy Industries",
        start_date="2025-01-01",
        end_date="2025-12-31",
        currency="INR",
        annual_committed_value=9000000.0,
        rules=[
            ContractRule(
                rule_id="RULE-TITAN-P1",
                rule_type="pricing",
                sku="IND-HYD-500",
                description="Industrial Heavy Hydraulic Pump 500HP",
                unit_price=50000.0,
                clause_reference="Clause 3.1 (Standard Pricing)",
                clause_text="Industrial Hydraulic Pump 500HP shall be invoiced at the contractual rate of INR 50,000 per unit EXW factory."
            ),
            ContractRule(
                rule_id="RULE-TITAN-D1",
                rule_type="discount",
                sku="IND-HYD-500",
                description="Tiered Bulk Volume Discount Rule",
                discount_pct=5.0,
                clause_reference="Clause 5.2 (Bulk Volume Rebates)",
                clause_text="A volume discount of 5.0% shall apply strictly to single purchase orders specifying 100 or more units. No discounts apply to orders below 100 units."
            ),
            ContractRule(
                rule_id="RULE-TITAN-T1",
                rule_type="payment_terms",
                description="Net 45 Credit Terms",
                grace_days=45,
                clause_reference="Clause 8.1 (Payment Terms & Claims)",
                clause_text="Payment due within 45 days. Transit claims must be registered within 48 hours accompanied by certified warehouse damage inspection."
            )
        ],
        raw_text="""HEAVY INDUSTRIAL SUPPLY AGREEMENT
Party A: Vulcan Heavy Machinery Ltd.
Party B: Titan Heavy Industries Ltd.
Effective Date: January 1, 2025.

Clause 3.1 (Standard Pricing):
All IND-HYD-500 hydraulic units are priced at INR 50,000 each.

Clause 5.2 (Bulk Volume Rebates):
Purchaser shall receive a 5% discount ONLY on individual purchase orders exceeding 100 units. Any order under 100 units must be billed at full list price of INR 50,000 per unit. Unauthorized discount codes shall be void.

Clause 8.1 (Payment Terms & Claims):
Payment within 45 days. Short-payments on basis of defect or transit loss must be supported by official joint surveyor report; unilateral withholding of funds is a contractual breach."""
    )

    titan_orders = [
        Order(order_id="PO-TITAN-01", customer_id="CUST-TITAN-02", order_date="2025-02-10", sku="IND-HYD-500", quantity=40, contracted_price=50000.0, order_price=50000.0, total_amount=2000000.0, po_reference="PO-TTN-801"),
        Order(order_id="PO-TITAN-02", customer_id="CUST-TITAN-02", order_date="2025-04-15", sku="IND-HYD-500", quantity=30, contracted_price=50000.0, order_price=50000.0, total_amount=1500000.0, po_reference="PO-TTN-802"),
        Order(order_id="PO-TITAN-03", customer_id="CUST-TITAN-02", order_date="2025-06-20", sku="IND-HYD-500", quantity=50, contracted_price=50000.0, order_price=50000.0, total_amount=2500000.0, po_reference="PO-TTN-803"),
        Order(order_id="PO-TITAN-04", customer_id="CUST-TITAN-02", order_date="2025-09-05", sku="IND-HYD-500", quantity=60, contracted_price=50000.0, order_price=44000.0, total_amount=2640000.0, po_reference="PO-TTN-804")
    ]

    titan_deliveries = [
        Delivery(delivery_id="DEL-TITAN-01", order_id="PO-TITAN-01", customer_id="CUST-TITAN-02", delivery_date="2025-02-25", sku="IND-HYD-500", delivered_quantity=40, challan_number="CHL-TTN-101", warehouse_ref="WH-PUNE-A"),
        Delivery(delivery_id="DEL-TITAN-02", order_id="PO-TITAN-02", customer_id="CUST-TITAN-02", delivery_date="2025-04-28", sku="IND-HYD-500", delivered_quantity=30, challan_number="CHL-TTN-102", warehouse_ref="WH-PUNE-A"),
        Delivery(delivery_id="DEL-TITAN-03", order_id="PO-TITAN-03", customer_id="CUST-TITAN-02", delivery_date="2025-06-30", sku="IND-HYD-500", delivered_quantity=50, challan_number="CHL-TTN-103", warehouse_ref="WH-PUNE-A"),
        Delivery(delivery_id="DEL-TITAN-04", order_id="PO-TITAN-04", customer_id="CUST-TITAN-02", delivery_date="2025-09-18", sku="IND-HYD-500", delivered_quantity=45, challan_number="CHL-TTN-104", warehouse_ref="WH-PUNE-B"),
        Delivery(delivery_id="DEL-TITAN-05", order_id="PO-TITAN-04", customer_id="CUST-TITAN-02", delivery_date="2025-09-22", sku="IND-HYD-500", delivered_quantity=15, challan_number="DC-8821", warehouse_ref="WH-PUNE-B")
    ]

    titan_invoices = [
        Invoice(invoice_id="INV-TITAN-01", delivery_id="DEL-TITAN-01", order_id="PO-TITAN-01", customer_id="CUST-TITAN-02", invoice_date="2025-03-01", due_date="2025-04-15", sku="IND-HYD-500", billed_quantity=40, unit_price=50000.0, total_amount=2000000.0),
        Invoice(invoice_id="INV-TITAN-02", delivery_id="DEL-TITAN-02", order_id="PO-TITAN-02", customer_id="CUST-TITAN-02", invoice_date="2025-05-02", due_date="2025-06-15", sku="IND-HYD-500", billed_quantity=30, unit_price=50000.0, total_amount=1500000.0),
        Invoice(invoice_id="INV-TITAN-03", delivery_id="DEL-TITAN-03", order_id="PO-TITAN-03", customer_id="CUST-TITAN-02", invoice_date="2025-07-05", due_date="2025-08-20", sku="IND-HYD-500", billed_quantity=50, unit_price=50000.0, total_amount=2500000.0),
        Invoice(invoice_id="INV-TITAN-04", delivery_id="DEL-TITAN-04", order_id="PO-TITAN-04", customer_id="CUST-TITAN-02", invoice_date="2025-09-25", due_date="2025-11-10", sku="IND-HYD-500", billed_quantity=45, unit_price=44000.0, applied_discount_pct=12.0, discount_amount=270000.0, total_amount=1980000.0)
    ]

    titan_payments = [
        Payment(payment_id="PAY-TITAN-01", invoice_id="INV-TITAN-01", customer_id="CUST-TITAN-02", payment_date="2025-04-10", amount_due=2000000.0, amount_paid=2000000.0, bank_reference="SBI-NEFT-991201", status="SETTLED"),
        Payment(payment_id="PAY-TITAN-02", invoice_id="INV-TITAN-02", customer_id="CUST-TITAN-02", payment_date="2025-06-12", amount_due=1500000.0, amount_paid=1500000.0, bank_reference="SBI-NEFT-991202", status="SETTLED"),
        Payment(payment_id="PAY-TITAN-03", invoice_id="INV-TITAN-03", customer_id="CUST-TITAN-02", payment_date="2025-08-18", amount_due=2500000.0, amount_paid=2500000.0, bank_reference="SBI-NEFT-991203", status="SETTLED"),
        Payment(payment_id="PAY-TITAN-04", invoice_id="INV-TITAN-04", customer_id="CUST-TITAN-02", payment_date="2025-11-15", amount_due=1980000.0, amount_paid=1480000.0, shortfall_amount=500000.0, bank_reference="SBI-NEFT-991204-SHORT", status="PARTIAL")
    ]

    # Scenario 3: Zenith Health Systems
    zenith_contract = Contract(
        contract_id="CTR-ZENITH-2025-03",
        customer_id="CUST-ZENITH-03",
        customer_name="Zenith Health Systems",
        start_date="2025-01-01",
        end_date="2025-12-31",
        currency="INR",
        annual_committed_value=8000000.0,
        rules=[
            ContractRule(
                rule_id="RULE-ZENITH-P1",
                rule_type="pricing",
                sku="KIT-DIAG-X1",
                description="Automated Pathology Diagnostic Reagent Kit",
                unit_price=2500.0,
                clause_reference="Clause 2.1 (Reagent Pricing)",
                clause_text="Each diagnostic test kit shall be priced at INR 2,500."
            ),
            ContractRule(
                rule_id="RULE-ZENITH-C1",
                rule_type="commitment",
                sku="KIT-DIAG-X1",
                description="Minimum Annual Commitment Shortfall Clause",
                min_commitment=3200,
                clause_reference="Clause 3.1 (Annual Minimum Commitment Guarantee)",
                clause_text="Client covenants to purchase a minimum of 3,200 kits (INR 80,00,000 value) per calendar year. If actual purchases fall below 3,200 kits, supplier shall invoice the full deficit at contracted rate of INR 2,500/kit as Shortfall Liquidated Recovery on December 31."
            ),
            ContractRule(
                rule_id="RULE-ZENITH-PEN1",
                rule_type="penalty",
                description="Delayed Payment Interest Penalty",
                penalty_rate_annual_pct=18.0,
                grace_days=45,
                clause_reference="Clause 8.4 (Late Payment Interest)",
                clause_text="Invoices unpaid after 45 days shall accrue default interest at eighteen percent (18.0%) per annum, calculated daily."
            )
        ],
        raw_text="""HEALTHCARE REAGENT & ANALYZER SERVICE CONTRACT
Party A: BioMed Diagnostics India Pvt Ltd
Party B: Zenith Health Systems Hospital Network
Duration: Jan 1, 2025 to Dec 31, 2025

Clause 2.1 (Reagent Pricing):
Unit price for KIT-DIAG-X1 is INR 2,500 per unit.

Clause 3.1 (Annual Minimum Commitment Guarantee):
In consideration of zero upfront equipment placement fee, Zenith Health guarantees an annual consumption of not less than 3,200 test kits (INR 80,00,000). Should annualized purchases fail to reach 3,200 kits, BioMed shall issue a Shortfall True-Up Invoice for the entire unfulfilled deficit.

Clause 8.4 (Late Payment Interest):
Zenith shall pay invoices within 45 days. Late payments beyond 45 days shall automatically incur 18% p.a. interest penalty till settled in full."""
    )

    zenith_orders = [
        Order(order_id="PO-ZENITH-01", customer_id="CUST-ZENITH-03", order_date="2025-01-20", sku="KIT-DIAG-X1", quantity=700, contracted_price=2500.0, order_price=2500.0, total_amount=1750000.0, po_reference="PO-ZNT-11"),
        Order(order_id="PO-ZENITH-02", customer_id="CUST-ZENITH-03", order_date="2025-04-18", sku="KIT-DIAG-X1", quantity=600, contracted_price=2500.0, order_price=2500.0, total_amount=1500000.0, po_reference="PO-ZNT-12"),
        Order(order_id="PO-ZENITH-03", customer_id="CUST-ZENITH-03", order_date="2025-07-22", sku="KIT-DIAG-X1", quantity=700, contracted_price=2500.0, order_price=2500.0, total_amount=1750000.0, po_reference="PO-ZNT-13"),
        Order(order_id="PO-ZENITH-04", customer_id="CUST-ZENITH-03", order_date="2025-10-15", sku="KIT-DIAG-X1", quantity=600, contracted_price=2500.0, order_price=2500.0, total_amount=1500000.0, po_reference="PO-ZNT-14")
    ]

    zenith_deliveries = [
        Delivery(delivery_id="DEL-ZENITH-01", order_id="PO-ZENITH-01", customer_id="CUST-ZENITH-03", delivery_date="2025-01-28", sku="KIT-DIAG-X1", delivered_quantity=700, challan_number="CHL-ZNT-501", warehouse_ref="MED-COLDCHAIN-1"),
        Delivery(delivery_id="DEL-ZENITH-02", order_id="PO-ZENITH-02", customer_id="CUST-ZENITH-03", delivery_date="2025-04-26", sku="KIT-DIAG-X1", delivered_quantity=600, challan_number="CHL-ZNT-502", warehouse_ref="MED-COLDCHAIN-1"),
        Delivery(delivery_id="DEL-ZENITH-03", order_id="PO-ZENITH-03", customer_id="CUST-ZENITH-03", delivery_date="2025-07-30", sku="KIT-DIAG-X1", delivered_quantity=700, challan_number="CHL-ZNT-503", warehouse_ref="MED-COLDCHAIN-1"),
        Delivery(delivery_id="DEL-ZENITH-04", order_id="PO-ZENITH-04", customer_id="CUST-ZENITH-03", delivery_date="2025-10-22", sku="KIT-DIAG-X1", delivered_quantity=600, challan_number="CHL-ZNT-504", warehouse_ref="MED-COLDCHAIN-1")
    ]

    zenith_invoices = [
        Invoice(invoice_id="INV-ZENITH-01", delivery_id="DEL-ZENITH-01", order_id="PO-ZENITH-01", customer_id="CUST-ZENITH-03", invoice_date="2025-02-01", due_date="2025-03-18", sku="KIT-DIAG-X1", billed_quantity=700, unit_price=2500.0, total_amount=1750000.0),
        Invoice(invoice_id="INV-ZENITH-02", delivery_id="DEL-ZENITH-02", order_id="PO-ZENITH-02", customer_id="CUST-ZENITH-03", invoice_date="2025-05-01", due_date="2025-06-15", sku="KIT-DIAG-X1", billed_quantity=600, unit_price=2500.0, total_amount=1500000.0),
        Invoice(invoice_id="INV-ZENITH-03", delivery_id="DEL-ZENITH-03", order_id="PO-ZENITH-03", customer_id="CUST-ZENITH-03", invoice_date="2025-08-01", due_date="2025-09-15", sku="KIT-DIAG-X1", billed_quantity=700, unit_price=2500.0, total_amount=1750000.0),
        Invoice(invoice_id="INV-ZENITH-04", delivery_id="DEL-ZENITH-04", order_id="PO-ZENITH-04", customer_id="CUST-ZENITH-03", invoice_date="2025-11-01", due_date="2025-12-16", sku="KIT-DIAG-X1", billed_quantity=600, unit_price=2500.0, total_amount=1500000.0)
    ]

    zenith_payments = [
        Payment(payment_id="PAY-ZENITH-01", invoice_id="INV-ZENITH-01", customer_id="CUST-ZENITH-03", payment_date="2025-03-10", amount_due=1750000.0, amount_paid=1750000.0, bank_reference="ICICI-CMS-1001", status="SETTLED"),
        Payment(payment_id="PAY-ZENITH-02", invoice_id="INV-ZENITH-02", customer_id="CUST-ZENITH-03", payment_date="2025-06-10", amount_due=1500000.0, amount_paid=1500000.0, bank_reference="ICICI-CMS-1002", status="SETTLED"),
        Payment(payment_id="PAY-ZENITH-03", invoice_id="INV-ZENITH-03", customer_id="CUST-ZENITH-03", payment_date="2025-12-20", amount_due=1750000.0, amount_paid=1750000.0, shortfall_amount=0.0, bank_reference="ICICI-CMS-1003-LATE", status="SETTLED"),
        Payment(payment_id="PAY-ZENITH-04", invoice_id="INV-ZENITH-04", customer_id="CUST-ZENITH-03", payment_date="2026-01-10", amount_due=1500000.0, amount_paid=1500000.0, bank_reference="ICICI-CMS-1004", status="SETTLED")
    ]

    return {
        "CUST-APEX-01": {
            "customer_id": "CUST-APEX-01",
            "customer_name": "Apex Global Technologies",
            "industry": "Enterprise SaaS & Cloud Infrastructure",
            "contract": apex_contract,
            "orders": apex_orders,
            "deliveries": apex_deliveries,
            "invoices": apex_invoices,
            "payments": apex_payments
        },
        "CUST-TITAN-02": {
            "customer_id": "CUST-TITAN-02",
            "customer_name": "Titan Heavy Industries",
            "industry": "Heavy Machinery, Logistics & Industrial Equipment",
            "contract": titan_contract,
            "orders": titan_orders,
            "deliveries": titan_deliveries,
            "invoices": titan_invoices,
            "payments": titan_payments
        },
        "CUST-ZENITH-03": {
            "customer_id": "CUST-ZENITH-03",
            "customer_name": "Zenith Health Systems",
            "industry": "Healthcare & Hospital Diagnostic Networks",
            "contract": zenith_contract,
            "orders": zenith_orders,
            "deliveries": zenith_deliveries,
            "invoices": zenith_invoices,
            "payments": zenith_payments
        }
    }
