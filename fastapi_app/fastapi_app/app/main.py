from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.schemas import PosStatus, TransactionsResponse, DashboardResponse
from app.queries import fetch_pos_status, fetch_transactions, fetch_dashboard

app = FastAPI(title="Nakhon Parts Dashboard API")

# Allow the Avalonia desktop client (and local testing tools) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root():
    """Redirect root to the interactive API docs."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    """Quick liveness check — does not touch the database."""
    return {"status": "ok"}


@app.get("/pos/status", response_model=List[PosStatus])
def pos_status():
    try:
        return fetch_pos_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pos/latest-transactions", response_model=TransactionsResponse)
def pos_transactions():
    try:
        return fetch_transactions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pos/dashboard", response_model=DashboardResponse)
def pos_dashboard():
    """Combined endpoint — runs JOIN_SQL once and returns all dashboard data.
    Replaces two separate calls to /pos/status + /pos/latest-transactions,
    eliminating MySQL I/O contention from concurrent parallel queries.
    """
    try:
        return fetch_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
