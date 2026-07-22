import json
from app.core.database import get_connection

def fetch_pos_status():
    conn = get_connection()
    try:
        # Disable strict SQL mode for this session to bypass zero date issues
        with conn.cursor() as cur:
            cur.execute("SET sql_mode = ''")

            # 1. Fetch all-time totals per POS directly using SQL SUM and JSON_UNQUOTE/JSON_EXTRACT
            totals_query = """
                SELECT br.sale_lot, 
                       SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(l.payment, '$."เครดิต"')) AS DOUBLE)) AS credit,
                       SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(l.payment, '$."โอน"')) AS DOUBLE)) AS transfer,
                       SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(l.payment, '$."เงินสด"')) AS DOUBLE)) AS cash
                FROM prod_out_bill_list l
                JOIN (SELECT bill_no, MAX(sale_lot) sale_lot
                      FROM prod_out_bill 
                      WHERE sale_lot IS NOT NULL AND sale_lot <> ''
                      GROUP BY bill_no) br ON br.bill_no = l.bill_no
                GROUP BY br.sale_lot
            """
            cur.execute(totals_query)
            totals_rows = cur.fetchall()

        totals_by_lot = {r["sale_lot"]: r for r in totals_rows}

        # 2. Identify the single "live" POS (the one with the latest transaction list_id globally)
        live_lot = None
        live_query = """
            SELECT b.sale_lot
            FROM prod_out_bill b
            JOIN prod_out_bill_list l ON b.bill_no = l.bill_no
            WHERE b.sale_lot IS NOT NULL AND b.sale_lot <> ''
            ORDER BY l.id DESC
            LIMIT 1
        """
        with conn.cursor() as cur:
            cur.execute(live_query)
            live_row = cur.fetchone()
            if live_row:
                live_lot = live_row["sale_lot"]

        # 3. For each of POS 1 to 4, fetch the latest sale total
        pos_list = ["1", "2", "3", "4"]
        results = []

        for lot in pos_list:
            last_sale_query = """
                SELECT l.amount
                FROM prod_out_bill b
                JOIN prod_out_bill_list l ON b.bill_no = l.bill_no
                WHERE b.sale_lot = %s
                ORDER BY l.id DESC
                LIMIT 1
            """
            with conn.cursor() as cur:
                cur.execute(last_sale_query, (lot,))
                row = cur.fetchone()

            last_sale_total = row["amount"] if row else 0.0
            totals = totals_by_lot.get(lot, {"credit": 0.0, "transfer": 0.0, "cash": 0.0})

            results.append({
                "sale_lot": lot,
                "last_sale_total": last_sale_total,
                "credit": totals["credit"] or 0.0,
                "transfer": totals["transfer"] or 0.0,
                "cash": totals["cash"] or 0.0,
                "is_live": lot == live_lot,
            })

        results.sort(key=lambda x: x["sale_lot"])
        return results

    finally:
        conn.close()


def _parse_payment_dict(payment_json_str_or_dict) -> list:
    """Parse payment data (which can be a parsed dict or raw JSON string) to return non-zero payment types."""
    if not payment_json_str_or_dict:
        return []
    data = payment_json_str_or_dict if isinstance(payment_json_str_or_dict, dict) else json.loads(payment_json_str_or_dict)
    methods = []
    if float(data.get("เครดิต", 0) or 0) > 0:
        methods.append("credit")
    if float(data.get("โอน", 0) or 0) > 0:
        methods.append("transfer")
    if float(data.get("เงินสด", 0) or 0) > 0:
        methods.append("cash")
    return methods


def fetch_transactions():
    conn = get_connection()
    try:
        # Disable strict SQL mode for this session to bypass zero date issues
        with conn.cursor() as cur:
            cur.execute("SET sql_mode = ''")

            # 1. Fetch latest 1 transaction for each POS (4 rows total)
            pos_list = ["1", "2", "3", "4"]
            feed = []
            for lot in pos_list:
                q = """
                    SELECT b.sale_lot, 
                           COALESCE(s.prod_name, b.prod_id) AS prod_name, 
                           l.amount, 
                           l.payment, 
                           l.upd_date, 
                           l.id AS list_id
                    FROM prod_out_bill b
                    JOIN prod_out_bill_list l ON b.bill_no = l.bill_no
                    LEFT JOIN prod_stock s ON s.prod_id = b.prod_id
                    WHERE b.sale_lot = %s
                    ORDER BY l.id DESC
                    LIMIT 1
                """
                cur.execute(q, (lot,))
                row = cur.fetchone()
                if row:
                    feed.append(row)

            # Sort the combined transaction feed DESC by global list_id (newest first)
            feed.sort(key=lambda x: x["list_id"], reverse=True)

            transactions = []
            for idx, r in enumerate(feed):
                transactions.append({
                    "date": str(r["upd_date"]),
                    "sale_lot": r["sale_lot"],
                    "prod_name": r["prod_name"],
                    "amount": r["amount"],
                    "payment_type": _parse_payment_dict(r["payment"]),
                    "is_live": (idx == 0),
                })

            # 2. Fetch all-time payment counts and sums directly in SQL for the donut chart
            donut_query = """
                SELECT 
                    SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(payment, '$."เครดิต"')) AS DOUBLE) > 0) AS credit_count,
                    SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(payment, '$."โอน"')) AS DOUBLE) > 0) AS transfer_count,
                    SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(payment, '$."เงินสด"')) AS DOUBLE) > 0) AS cash_count,
                    SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(payment, '$."เครดิต"')) AS DOUBLE)) AS credit_total,
                    SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(payment, '$."โอน"')) AS DOUBLE)) AS transfer_total,
                    SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(payment, '$."เงินสด"')) AS DOUBLE)) AS cash_total
                FROM prod_out_bill_list
            """
            cur.execute(donut_query)
            donut = cur.fetchone()

        # Format and structure the payment summary response
        credit_count = int(donut["credit_count"] or 0)
        transfer_count = int(donut["transfer_count"] or 0)
        cash_count = int(donut["cash_count"] or 0)
        credit_total = float(donut["credit_total"] or 0.0)
        transfer_total = float(donut["transfer_total"] or 0.0)
        cash_total = float(donut["cash_total"] or 0.0)

        total_bills = credit_count + transfer_count + cash_count or 1

        def pct(val):
            return round(val / total_bills * 100, 1)

        payment_summary = {
            "credit": {"bill_count": credit_count, "percent": pct(credit_count), "total_amount": credit_total},
            "transfer": {"bill_count": transfer_count, "percent": pct(transfer_count), "total_amount": transfer_total},
            "cash": {"bill_count": cash_count, "percent": pct(cash_count), "total_amount": cash_total},
        }

        return {"transactions": transactions, "payment_summary": payment_summary}

    finally:
        conn.close()


def fetch_dashboard():
    """Combined dashboard logic. Combines optimized POS status queries and Latest Transaction queries."""
    pos_cards = fetch_pos_status()
    tx_data = fetch_transactions()
    return {
        "pos_cards": pos_cards,
        "transactions": tx_data["transactions"],
        "payment_summary": tx_data["payment_summary"],
    }
