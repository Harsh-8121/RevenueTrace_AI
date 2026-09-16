import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { formatCurrency, getContract, runInvestigation } from "../api";
import type { Contract } from "../types";

export default function ContractDetail() {
  const { contractId } = useParams();
  const navigate = useNavigate();
  const [contract, setContract] = useState<Contract | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!contractId) return;
    getContract(contractId)
      .then(setContract)
      .catch(() => setError("Contract not found."));
  }, [contractId]);

  async function investigate() {
    if (!contractId) return;
    setLoading(true);
    setError("");
    try {
      const investigation = await runInvestigation(contractId);
      navigate(`/investigations/${investigation.id}`);
    } catch {
      setError("Investigation failed.");
    } finally {
      setLoading(false);
    }
  }

  if (!contract) {
    return <p className="muted">{error || "Loading contract..."}</p>;
  }

  const orderTotal = contract.orders.reduce((sum, item) => sum + item.amount, 0);
  const deliveredTotal = contract.deliveries.reduce((sum, item) => sum + item.amount, 0);
  const invoicedTotal = contract.invoices.reduce((sum, item) => sum + item.amount, 0);
  const paidTotal = contract.payments.reduce((sum, item) => sum + item.amount, 0);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">
            <Link to="/contracts">Contracts</Link> / {contract.contract_id}
          </p>
          <h1>{contract.customer_name}</h1>
          <p className="muted">{contract.terms}</p>
        </div>
        <button className="button" onClick={investigate} disabled={loading}>
          {loading ? "Investigating..." : "Run Investigation"}
        </button>
      </header>

      {error ? <p className="error-text">{error}</p> : null}

      <section className="grid chain-grid">
        <div className="chain-step">
          <span>Contract</span>
          <strong>{formatCurrency(contract.contract_value)}</strong>
        </div>
        <div className="chain-step">
          <span>Orders</span>
          <strong>{formatCurrency(orderTotal)}</strong>
        </div>
        <div className="chain-step">
          <span>Deliveries</span>
          <strong>{formatCurrency(deliveredTotal)}</strong>
        </div>
        <div className="chain-step">
          <span>Invoices</span>
          <strong>{formatCurrency(invoicedTotal)}</strong>
        </div>
        <div className="chain-step">
          <span>Payments</span>
          <strong>{formatCurrency(paidTotal)}</strong>
        </div>
      </section>

      <section className="grid two-column">
        <RecordTable title="Orders" rows={contract.orders.map((item) => [item.order_id, item.order_date, formatCurrency(item.amount)])} />
        <RecordTable title="Deliveries" rows={contract.deliveries.map((item) => [item.delivery_id, item.delivery_date, formatCurrency(item.amount)])} />
        <RecordTable title="Invoices" rows={contract.invoices.map((item) => [item.invoice_id, item.invoice_date, formatCurrency(item.amount)])} />
        <RecordTable title="Payments" rows={contract.payments.map((item) => [item.payment_id, item.payment_date, formatCurrency(item.amount)])} />
      </section>
    </div>
  );
}

function RecordTable({ title, rows }: { title: string; rows: string[][] }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      {rows.length === 0 ? (
        <p className="muted">No records.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Date</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row[0]}>
                <td>{row[0]}</td>
                <td>{row[1]}</td>
                <td>{row[2]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
