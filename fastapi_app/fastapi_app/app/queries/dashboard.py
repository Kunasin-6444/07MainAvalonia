from app.queries.pos import fetch_pos_status
from app.queries.transactions import fetch_transactions


def fetch_dashboard():
    """Combined dashboard logic. Combines optimized POS status queries and Latest Transaction queries."""
    pos_cards = fetch_pos_status()
    tx_data = fetch_transactions()
    return {
        "pos_cards": pos_cards,
        "transactions": tx_data["transactions"],
        "payment_summary": tx_data["payment_summary"],
    }
