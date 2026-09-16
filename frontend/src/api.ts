import type { Contract, DashboardStats, Investigation, InvestigationSummary } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function getDashboard(): Promise<DashboardStats> {
  return request("/api/dashboard");
}

export function getContracts(): Promise<Contract[]> {
  return request("/api/contracts");
}

export function getContract(contractId: string): Promise<Contract> {
  return request(`/api/contracts/${contractId}`);
}

export function getInvestigations(): Promise<InvestigationSummary[]> {
  return request("/api/investigations");
}

export function getInvestigation(id: string): Promise<Investigation> {
  return request(`/api/investigations/${id}`);
}

export function runInvestigation(contractId: string, useLlm = true): Promise<Investigation> {
  return request("/api/investigations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contract_id: contractId, use_llm: useLlm }),
  });
}

export async function uploadFile(file: File): Promise<{ contract_ids: string[]; message: string }> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch("/api/uploads", { method: "POST", body: formData });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}
