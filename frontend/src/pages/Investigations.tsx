import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { formatCurrency, getInvestigations } from "../api";
import type { InvestigationSummary } from "../types";

export default function Investigations() {
  const [investigations, setInvestigations] = useState<InvestigationSummary[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getInvestigations()
      .then(setInvestigations)
      .catch(() => setError("Unable to load investigations."));
  }, []);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Investigations</h1>
          <p className="muted">Evidence-backed leakage analysis across the contract-to-cash chain.</p>
        </div>
      </header>

      {error ? <p className="error-text">{error}</p> : null}

      <div className="card">
        {investigations.length === 0 ? (
          <p className="muted">No investigations yet. Open a contract and run an investigation.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Investigation</th>
                <th>Contract</th>
                <th>Customer</th>
                <th>Leakage</th>
                <th>Findings</th>
                <th>LLM</th>
              </tr>
            </thead>
            <tbody>
              {investigations.map((item) => (
                <tr key={item.id}>
                  <td>
                    <Link to={`/investigations/${item.id}`}>{item.id.slice(0, 8)}</Link>
                  </td>
                  <td>{item.contract_id}</td>
                  <td>{item.customer_name}</td>
                  <td className="impact">{formatCurrency(item.total_leakage)}</td>
                  <td>{item.finding_count}</td>
                  <td>{item.llm_enhanced ? "Yes" : "Rules"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
