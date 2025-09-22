#!/usr/bin/env python3
"""
Minimal MCP servers HTTP facade for NFRGuard.

This service exposes HTTP endpoints that mirror the mock tools defined in
`mcp_integration_example.py`, so agents can call them over the network.

Endpoints (prefix /mcp):
- /mcp/risk/analyze_transaction_risk        POST { transaction_data }
- /mcp/risk/get_risk_score                  POST { transaction_id, amount, metadata? }
- /mcp/banking/check_balance                POST { account_id }
- /mcp/banking/get_transaction_history      POST { account_id, limit? }
- /mcp/compliance/get_compliance_action     POST { risk_score, transaction_amount }

Note: This is a pragmatic HTTP facade to unblock deployment on GKE quickly.
It can be swapped with a true MCP server library without changing the
downstream agents if we maintain the request/response shapes.
"""

from __future__ import annotations

import os
from typing import Any, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="NFRGuard MCP Servers (HTTP Facade)")


# --------------------------
# Request/Response Schemas
# --------------------------


class AnalyzeTransactionRiskRequest(BaseModel):
    transaction_data: Dict[str, Any]


class GetRiskScoreRequest(BaseModel):
    transaction_id: str
    amount: float
    metadata: Dict[str, Any] | None = None


class CheckBalanceRequest(BaseModel):
    account_id: str


class GetTransactionHistoryRequest(BaseModel):
    account_id: str
    limit: int | None = 10


class GetComplianceActionRequest(BaseModel):
    risk_score: float
    transaction_amount: float


# --------------------------
# Handlers (logic mirrored from mocks)
# --------------------------


@app.post("/mcp/risk/analyze_transaction_risk")
def analyze_transaction_risk(req: AnalyzeTransactionRiskRequest):
    tx = req.transaction_data or {}
    risk_factors = []
    if tx.get("amount", 0) > 10000:
        risk_factors.append("high_amount")
    if tx.get("metadata", {}).get("cross_border", False):
        risk_factors.append("cross_border")
    if tx.get("metadata", {}).get("unusual_time", False):
        risk_factors.append("unusual_timing")

    return {
        "risk_factors": risk_factors,
        "analysis": f"Transaction analyzed: {len(risk_factors)} risk factors detected",
        "confidence": 0.95,
    }


@app.post("/mcp/risk/get_risk_score")
def get_risk_score(req: GetRiskScoreRequest):
    score = 0.0
    if req.amount > 10000:
        score += 0.4
    meta = req.metadata or {}
    if meta.get("cross_border", False):
        score += 0.3
    if meta.get("unusual_time", False):
        score += 0.2
    if meta.get("new_merchant", False):
        score += 0.1
    score = min(score, 1.0)
    return {
        "transaction_id": req.transaction_id,
        "risk_score": score,
        "risk_level": "high" if score > 0.7 else ("medium" if score > 0.3 else "low"),
    }


@app.post("/mcp/banking/check_balance")
def check_balance(req: CheckBalanceRequest):
    return {
        "status": "success",
        "account_id": req.account_id,
        "balance": "1,250.50",
        "currency": "USD",
        "last_updated": "2025-01-14T21:46:00Z",
    }


@app.post("/mcp/banking/get_transaction_history")
def get_transaction_history(req: GetTransactionHistoryRequest):
    transactions = [
        {
            "transaction_id": "txn_001",
            "amount": "100.00",
            "type": "debit",
            "description": "Purchase at Store ABC",
            "timestamp": "2025-01-14T10:30:00Z",
        },
        {
            "transaction_id": "txn_002",
            "amount": "500.00",
            "type": "credit",
            "description": "Salary deposit",
            "timestamp": "2025-01-13T09:00:00Z",
        },
    ]
    limit = req.limit or 10
    return {
        "status": "success",
        "account_id": req.account_id,
        "transactions": transactions[:limit],
        "total_count": len(transactions),
    }


@app.post("/mcp/compliance/get_compliance_action")
def get_compliance_action(req: GetComplianceActionRequest):
    if req.risk_score > 0.8 or req.transaction_amount > 10000:
        action = "hold_and_report"
    elif req.risk_score > 0.5:
        action = "monitor_closely"
    else:
        action = "monitor"
    return {
        "action": action,
        "reason": f"Risk score: {req.risk_score}, Amount: {req.transaction_amount}",
        "rule": "AUSTRAC_threshold",
    }


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


def get_uvicorn_kwargs():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8081")))
    return {"host": host, "port": port}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", **get_uvicorn_kwargs())









