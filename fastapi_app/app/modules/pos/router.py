from typing import List
from fastapi import APIRouter, HTTPException

from app.modules.pos.schema import PosStatus, TransactionsResponse, DashboardResponse
from app.modules.pos.service import fetch_pos_status, fetch_transactions, fetch_dashboard

router = APIRouter(prefix="/pos", tags=["POS"])


@router.get("/status", response_model=List[PosStatus])
def pos_status():
    """Fetch status summary and trend lines for all POS units."""
    try:
        return fetch_pos_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest-transactions", response_model=TransactionsResponse)
def pos_transactions():
    """Fetch recent transaction feed and overall payment method breakdown."""
    try:
        return fetch_transactions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", response_model=DashboardResponse)
def pos_dashboard():
    """Combined endpoint — returns all dashboard data in a single optimized query round-trip."""
    try:
        return fetch_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
