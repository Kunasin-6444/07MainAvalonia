import json
from app.database import get_connection


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
                    SELECT b.sale_lot, b.prod_id, l.amount, l.payment, l.upd_date, l.id AS list_id
                    FROM prod_out_bill b
                    JOIN prod_out_bill_list l ON b.bill_no = l.bill_no
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
            for r in feed:
                transactions.append({
                    "date": str(r["upd_date"]),
                    "sale_lot": r["sale_lot"],
                    "prod_id": r["prod_id"],
                    "amount": r["amount"],
                    "payment_type": _parse_payment_dict(r["payment"]),
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
