from typing import List
from pydantic import BaseModel


class PosStatus(BaseModel):
    sale_lot: str
    last_sale_total: float
    credit: float
    transfer: float
    cash: float
    is_live: bool


class Transaction(BaseModel):
    date: str
    sale_lot: str
    prod_name: str
    amount: float
    payment_type: List[str]
    is_live: bool = False


class PaymentStat(BaseModel):
    bill_count: int
    percent: float
    total_amount: float


class PaymentSummary(BaseModel):
    credit: PaymentStat
    transfer: PaymentStat
    cash: PaymentStat


class TransactionsResponse(BaseModel):
    transactions: List[Transaction]
    payment_summary: PaymentSummary


class DashboardResponse(BaseModel):
    """Single combined response — replaces two separate API calls."""
    pos_cards: List[PosStatus]
    transactions: List[Transaction]
    payment_summary: PaymentSummary
