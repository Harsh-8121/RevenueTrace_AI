export type Contract = {
  contract_id: string;
  customer_name: string;
  contract_value: number;
  terms: string;
  effective_date: string;
  orders: { order_id: string; amount: number; order_date: string }[];
  deliveries: { delivery_id: string; amount: number; delivery_date: string }[];
  invoices: { invoice_id: string; amount: number; invoice_date: string; due_date: string }[];
  payments: { payment_id: string; amount: number; payment_date: string }[];
  source: "seed" | "upload";
};

export type Finding = {
  category: string;
  severity: string;
  description: string;
  financial_impact: number;
  evidence: string[];
  root_cause?: string | null;
};

export type Investigation = {
  id: string;
  contract_id: string;
  customer_name: string;
  status: string;
  total_leakage: number;
  findings: Finding[];
  recommendation: string;
  executive_summary: string;
  chain_summary: Record<string, number>;
  llm_enhanced: boolean;
  created_at: string;
};

export type InvestigationSummary = {
  id: string;
  contract_id: string;
  customer_name: string;
  status: string;
  total_leakage: number;
  finding_count: number;
  created_at: string;
  llm_enhanced: boolean;
};

export type DashboardStats = {
  contract_count: number;
  total_contract_value: number;
  contracts_with_leakage: number;
  total_identified_leakage: number;
  investigation_count: number;
  uploaded_contract_count: number;
};
