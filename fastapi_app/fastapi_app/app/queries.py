import json
from collections import defaultdict
from app.database import get_connection

TREND_POINTS = 10

# Actual JSON keys confirmed from DB (utf8mb4)
KEY_CREDIT = "เครดิต"
KEY_TRANSFER = "โอน"
KEY_CASH = "เงินสด"


def _parse_payment(payment_raw) -> dict:
    """payment column may already be a dict (pymysql json) or a JSON string."""
    data = payment_raw if isinstance(payment_raw, dict) else json.loads(payment_raw)
    return {
        "credit": float(data.get(KEY_CREDIT, 0) or 0),
        "transfer": float(data.get(KEY_TRANSFER, 0) or 0),
        "cash": float(data.get(KEY_CASH, 0) or 0),
    }


# Single query that fetches everything both endpoints need.
# IMPORTANT: create these indexes in MySQL once for a massive speed-up:
#   CREATE INDEX idx_pob_sale_lot  ON prod_out_bill(sale_lot);
#   CREATE INDEX idx_pob_bill_no   ON prod_out_bill(bill_no);
#   CREATE INDEX idx_pobl_bill_no  ON prod_out_bill_list(bill_no);
#   CREATE INDEX idx_pobl_id       ON prod_out_bill_list(id);
JOIN_SQL = """
    SELECT b.sale_lot, b.prod_id, l.id AS list_id, l.bill_no,
    l.amount, l.payment, l.upd_date
    FROM prod_out_bill b
    JOIN prod_out_bill_list l ON b.bill_no = l.bill_no
    WHERE b.sale_lot IS NOT NULL AND b.sale_lot <> ''
    ORDER BY l.id DESC"""


def _aggregate_payment_summary(payment_rows):
    credit_count = transfer_count = cash_count = 0
    credit_amt = transfer_amt = cash_amt = 0.0

    for r in payment_rows:
        pay = _parse_payment(r["payment"])
        if pay["credit"] > 0:
            credit_count += 1
            credit_amt += pay["credit"]
        if pay["transfer"] > 0:
            transfer_count += 1
            transfer_amt += pay["transfer"]
        if pay["cash"] > 0:
            cash_count += 1
            cash_amt += pay["cash"]

    total_bills = credit_count + transfer_count + cash_count or 1  # avoid /0

    def pct(count):
        return round(count / total_bills * 100, 1)

    return {
        "credit": {"bill_count": credit_count, "percent": pct(credit_count), "total_amount": credit_amt},
        "transfer": {"bill_count": transfer_count, "percent": pct(transfer_count), "total_amount": transfer_amt},
        "cash": {"bill_count": cash_count, "percent": pct(cash_count), "total_amount": cash_amt},
    }


def fetch_pos_status():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(JOIN_SQL)
            rows = cur.fetchall()

        by_lot = defaultdict(list)
        for r in rows:
            by_lot[r["sale_lot"]].append(r)

        # POS with the globally most recent list_id is "live"
        live_lot = rows[0]["sale_lot"] if rows else None

        result = []
        for lot, lot_rows in by_lot.items():
            # lot_rows already ordered DESC by list_id (newest first)
            last_row = lot_rows[0]
            credit = transfer = cash = 0.0
            for r in lot_rows:
                pay = _parse_payment(r["payment"])
                credit += pay["credit"]
                transfer += pay["transfer"]
                cash += pay["cash"]

            trend = [r["amount"] for r in lot_rows[:TREND_POINTS]]
            trend.reverse()  # oldest -> newest for the sparkline

            result.append({
                "sale_lot": lot,
                "last_sale_total": last_row["amount"],
                "credit": credit,
                "transfer": transfer,
                "cash": cash,
                "trend": trend,
                "is_live": lot == live_lot,
            })

        result.sort(key=lambda x: x["sale_lot"])
        return result
    finally:
        conn.close()


def fetch_transactions():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Single query — all_rows has everything we need for both the
            # transaction list AND the all-time payment summary.
            # The old code ran PAYMENT_ONLY_SQL as a second full-table scan;
            # we now reuse all_rows to compute the same aggregation in Python.
            cur.execute(JOIN_SQL)
            all_rows = cur.fetchall()

        # Latest 1 row per sale_lot (all_rows already ordered DESC by list_id)
        seen_lots = set()
        latest_per_lot = []
        for r in all_rows:
            if r["sale_lot"] not in seen_lots:
                seen_lots.add(r["sale_lot"])
                latest_per_lot.append(r)

        transactions = []
        for r in latest_per_lot:
            pay = _parse_payment(r["payment"])
            methods = []
            if pay["credit"] > 0:
                methods.append("credit")
            if pay["transfer"] > 0:
                methods.append("transfer")
            if pay["cash"] > 0:
                methods.append("cash")

            transactions.append({
                "date": str(r["upd_date"]),
                "sale_lot": r["sale_lot"],
                "prod_id": r["prod_id"],
                "amount": r["amount"],
                "payment_type": methods,
            })

        # Reuse all_rows for the donut — avoids a second full-table scan
        payment_summary = _aggregate_payment_summary(all_rows)

        return {"transactions": transactions, "payment_summary": payment_summary}
    finally:
        conn.close()


def fetch_dashboard():
    """Single DB round-trip that returns everything the dashboard needs.

    Previously the client called /pos/status and /pos/latest-transactions in
    parallel, forcing MySQL to run two heavy JOIN scans simultaneously and
    causing I/O contention that pushed each query past the timeout.
    This function runs JOIN_SQL exactly once and derives all data in Python.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(JOIN_SQL)
            rows = cur.fetchall()   # all rows, newest list_id first

        # ── 1. POS Status Cards ──────────────────────────────────────────────
        by_lot = defaultdict(list)
        for r in rows:
            by_lot[r["sale_lot"]].append(r)

        live_lot = rows[0]["sale_lot"] if rows else None

        pos_cards = []
        for lot, lot_rows in by_lot.items():
            last_row = lot_rows[0]
            credit = transfer = cash = 0.0
            for r in lot_rows:
                pay = _parse_payment(r["payment"])
                credit   += pay["credit"]
                transfer += pay["transfer"]
                cash     += pay["cash"]

            trend = [r["amount"] for r in lot_rows[:TREND_POINTS]]
            trend.reverse()

            pos_cards.append({
                "sale_lot": lot,
                "last_sale_total": last_row["amount"],
                "credit": credit,
                "transfer": transfer,
                "cash": cash,
                "trend": trend,
                "is_live": lot == live_lot,
            })

        pos_cards.sort(key=lambda x: x["sale_lot"])

        # ── 2. Latest Transaction Feed ───────────────────────────────────────
        seen_lots: set = set()
        transactions = []
        for r in rows:
            if r["sale_lot"] in seen_lots:
                continue
            seen_lots.add(r["sale_lot"])
            pay = _parse_payment(r["payment"])
            methods = [m for m, v in [("credit", pay["credit"]),
                                       ("transfer", pay["transfer"]),
                                       ("cash", pay["cash"])] if v > 0]
            transactions.append({
                "date": str(r["upd_date"]),
                "sale_lot": r["sale_lot"],
                "prod_id": r["prod_id"],
                "amount": r["amount"],
                "payment_type": methods,
            })

        # ── 3. Donut (all-time payment summary) ──────────────────────────────
        payment_summary = _aggregate_payment_summary(rows)

        return {
            "pos_cards": pos_cards,
            "transactions": transactions,
            "payment_summary": payment_summary,
        }
    finally:
        conn.close()

