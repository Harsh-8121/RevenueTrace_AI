import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { formatCurrency, getContracts, getDashboard, getInvestigations } from "../api";
import StatCard from "../components/StatCard";
import type { Contract, DashboardStats, InvestigationSummary } from "../types";

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [investigations, setInvestigations] = useState<InvestigationSummary[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getDashboard(), getContracts(), getInvestigations()])
      .then(([dashboard, contractList, investigationList]) => {
        setStats(dashboard);
        setContracts(contractList);
        setInvestigations(investigationList.slice(0, 5));
      })
      .catch(() => setError("Unable to load dashboard data."));
  }, []);

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Revenue Assurance Dashboard</h1>
          <p className="muted">
            Trace contract-to-cash leakage across orders, deliveries, invoices, and payments.
          </p>
        </div>
        <Link className="button" to="/upload">Import Data</Link>
      </header>

      {stats && (
        <section className="grid stats-grid">
          <StatCard label="Contracts" value={String(stats.contract_count)} />
          <StatCard label="Portfolio Value" value={formatCurrency(stats.total_contract_value)} />
          <StatCard
            label="Identified Leakage"
            value={formatCurrency(stats.total_identified_leakage)}
            hint={`${stats.contracts_with_leakage} contracts impacted`}
          />
          <StatCard label="Investigations Run" value={String(stats.investigation_count)} />
        </section>
      )}

      <section className="grid two-column">
        <div className="card">
          <div className="card-header">
            <h2>Contracts</h2>
            <Link to="/contracts">View all</Link>
          </div>
          <table>
            <thead>
              <tr>
                <th>Contract</th>
                <th>Customer</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              {contracts.slice(0, 5).map((contract) => (
                <tr key={contract.contract_id}>
                  <td>
                    <Link to={`/contracts/${contract.contract_id}`}>{contract.contract_id}</Link>
                  </td>
                  <td>{contract.customer_name}</td>
                  <td>{formatCurrency(contract.contract_value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <div className="card-header">
            <h2>Recent Investigations</h2>
            <Link to="/investigations">View all</Link>
          </div>
          {investigations.length === 0 ? (
            <p className="muted">No investigations yet. Run one from a contract page.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Contract</th>
                  <th>Leakage</th>
                  <th>Findings</th>
                </tr>
              </thead>
              <tbody>
                {investigations.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <Link to={`/investigations/${item.id}`}>{item.contract_id}</Link>
                    </td>
                    <td className="impact">{formatCurrency(item.total_leakage)}</td>
                    <td>{item.finding_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  );
}
