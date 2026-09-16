import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { formatCurrency, getContracts } from "../api";
import type { Contract } from "../types";

export default function Contracts() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getContracts()
      .then(setContracts)
      .catch(() => setError("Unable to load contracts."));
  }, []);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Contracts</h1>
          <p className="muted">Review contract-to-cash source records and launch investigations.</p>
        </div>
      </header>

      {error ? <p className="error-text">{error}</p> : null}

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Contract</th>
              <th>Customer</th>
              <th>Value</th>
              <th>Terms</th>
              <th>Source</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {contracts.map((contract) => (
              <tr key={contract.contract_id}>
                <td>{contract.contract_id}</td>
                <td>{contract.customer_name}</td>
                <td>{formatCurrency(contract.contract_value)}</td>
                <td>{contract.terms}</td>
                <td>
                  <span className={`pill ${contract.source}`}>{contract.source}</span>
                </td>
                <td>
                  <Link className="button secondary" to={`/contracts/${contract.contract_id}`}>
                    Open
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
