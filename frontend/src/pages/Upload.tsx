import { useState } from "react";
import { Link } from "react-router-dom";
import { uploadFile } from "../api";

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [contractIds, setContractIds] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleUpload() {
    if (!file) return;
    setLoading(true);
    setError("");
    setMessage("");
    setContractIds([]);
    try {
      const result = await uploadFile(file);
      setMessage(result.message);
      setContractIds(result.contract_ids);
    } catch {
      setError("Upload failed. Use JSON, CSV, or PDF input.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Upload Contract Data</h1>
          <p className="muted">
            Import contract-to-cash records from JSON, CSV, or PDF to extend investigations.
          </p>
        </div>
      </header>

      <div className="card upload-card">
        <h2>Supported formats</h2>
        <ul>
          <li><strong>JSON</strong> — full contract objects with orders, deliveries, invoices, and payments</li>
          <li><strong>CSV</strong> — rows with `record_type`, `contract_id`, `customer_name`, `amount`, and optional references</li>
          <li><strong>PDF</strong> — extracts contract ID, customer, amounts, and payment terms heuristically</li>
        </ul>

        <input
          type="file"
          accept=".json,.csv,.pdf"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />

        <button className="button" onClick={handleUpload} disabled={!file || loading}>
          {loading ? "Uploading..." : "Upload and Import"}
        </button>

        {message ? <p className="success-text">{message}</p> : null}
        {error ? <p className="error-text">{error}</p> : null}

        {contractIds.length > 0 ? (
          <div>
            <p>Imported contracts:</p>
            <ul>
              {contractIds.map((contractId) => (
                <li key={contractId}>
                  <Link to={`/contracts/${contractId}`}>{contractId}</Link>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </div>
  );
}
