from pydantic import BaseModel, Field


class Finding(BaseModel):
    category: str
    severity: str
    description: str
    financial_impact: float = Field(ge=0)
    evidence: list[str]


class InvestigationRequest(BaseModel):
    contract_id: str


class Investigation(BaseModel):
    id: str
    contract_id: str
    status: str
    total_leakage: float
    findings: list[Finding]
    recommendation: str
