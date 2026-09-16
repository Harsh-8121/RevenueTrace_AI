import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { formatCurrency, getInvestigation } from "../api";
import type { Investigation } from "../types";

export default function InvestigationDetail() {
  const { investigationId } = useParams();
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!investigationId) return;
    getInvestigation(investigationId)
      .then(setInvestigation)
      .catch(() => setError("Investigation not found."));
  }, [investigationId]);

  if (!investigation) {
    return <p className="muted">{error || "Loading investigation..."}</p>;
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">
            <Link to="/investigations">Investigations</Link> / {investigation.id.slice(0, 8)}
          </p>
          <h1>{investigation.customer_name}</h1>
          <p className="muted">
            Contract {investigation.contract_id} · {investigation.llm_enhanced ? "LLM-enhanced" : "Rules-based"} analysis
          </p>
        </div>
      </header>

      <section className="grid stats-grid">
        <div className="stat-card">
          <span className="stat-label">Estimated Leakage</span>
          <strong className="stat-value impact">{formatCurrency(investigation.total_leakage)}</strong>
        </div>
        <div className="stat-card">
          <span className="stat-label">Findings</span>
          <strong className="stat-value">{investigation.findings.length}</strong>
        </div>
        <div className="stat-card">
          <span className="stat-label">Invoiced</span>
          <strong className="stat-value">{formatCurrency(investigation.chain_summary.invoiced_total)}</strong>
        </div>
        <div className="stat-card">
          <span className="stat-label">Paid</span>
          <strong className="stat-value">{formatCurrency(investigation.chain_summary.paid_total)}</strong>
        </div>
      </section>

      <section className="grid two-column">
        <div className="card">
          <h2>Executive Summary</h2>
          <p>{investigation.executive_summary}</p>
          <h3>Recommendation</h3>
          <p>{investigation.recommendation}</p>
        </div>

        <div className="card">
          <h2>Contract-to-Cash Chain</h2>
          <ul className="chain-list">
            {Object.entries(investigation.chain_summary).map(([key, value]) => (
              <li key={key}>
                <span>{key.replaceAll("_", " ")}</span>
                <strong>{formatCurrency(value)}</strong>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="card">
        <h2>Findings</h2>
        {investigation.findings.length === 0 ? (
          <p className="muted">No leakage findings detected.</p>
        ) : (
          <div className="finding-list">
            {investigation.findings.map((finding) => (
              <article key={`${finding.category}-${finding.description}`} className="finding-card">
                <div className="finding-header">
                  <strong>{finding.category.toUpperCase()}</strong>
                  <span className={`pill ${finding.severity}`}>{finding.severity}</span>
                  <span className="impact">{formatCurrency(finding.financial_impact)}</span>
                </div>
                <p>{finding.description}</p>
                {finding.root_cause ? <p className="muted">Root cause: {finding.root_cause}</p> : null}
                <ul>
                  {finding.evidence.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
