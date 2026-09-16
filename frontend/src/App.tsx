import { useEffect, useState } from "react";

type Contract = {
  contract_id: string;
  contract_value: number;
};

type Finding = {
  category: string;
  severity: string;
  description: string;
  financial_impact: number;
  evidence: string[];
};

type Investigation = {
  id: string;
  contract_id: string;
  status: string;
  total_leakage: number;
  findings: Finding[];
  recommendation: string;
};

export default function App() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [selectedContract, setSelectedContract] = useState("");
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/contracts")
      .then((response) => response.json())
      .then((data: Contract[]) => {
        setContracts(data);
        if (data.length > 0) {
          setSelectedContract(data[0].contract_id);
        }
      })
      .catch(() => setError("Unable to load contracts from the API."));
  }, []);

  async function runInvestigation() {
    setLoading(true);
    setError("");
    setInvestigation(null);

    try {
      const response = await fetch("/api/investigations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contract_id: selectedContract }),
      });

      if (!response.ok) {
        throw new Error("Investigation request failed.");
      }

      const data = (await response.json()) as Investigation;
      setInvestigation(data);
    } catch {
      setError("Investigation failed. Confirm the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>RevenueTrace AI</h1>
      <p className="muted">
        Contract-to-Cash investigation dashboard for detecting revenue leakage.
      </p>

      <div className="card">
        <label htmlFor="contract-select">Contract</label>
        <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.75rem" }}>
          <select
            id="contract-select"
            value={selectedContract}
            onChange={(event) => setSelectedContract(event.target.value)}
            style={{ flex: 1, padding: "0.65rem", borderRadius: "8px" }}
          >
            {contracts.map((contract) => (
              <option key={contract.contract_id} value={contract.contract_id}>
                {contract.contract_id} (${contract.contract_value.toLocaleString()})
              </option>
            ))}
          </select>
          <button onClick={runInvestigation} disabled={loading || !selectedContract}>
            {loading ? "Investigating..." : "Run Investigation"}
          </button>
        </div>
      </div>

      {error && <p className="impact">{error}</p>}

      {investigation && (
        <div className="card">
          <h2>Investigation {investigation.id.slice(0, 8)}</h2>
          <p>
            Total estimated leakage:{" "}
            <span className="impact">${investigation.total_leakage.toLocaleString()}</span>
          </p>
          <p>{investigation.recommendation}</p>

          {investigation.findings.map((finding) => (
            <div key={`${finding.category}-${finding.description}`} style={{ marginTop: "1rem" }}>
              <strong>{finding.category.toUpperCase()} ({finding.severity})</strong>
              <p>{finding.description}</p>
              <ul>
                {finding.evidence.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
