from app.database import get_connection

TREND_POINTS = 10


def fetch_pos_status():
    conn = get_connection()
    try:
        # Disable strict SQL mode for this session to bypass zero date issues
        with conn.cursor() as cur:
            cur.execute("SET sql_mode = ''")

            # 1. Fetch all-time totals per POS directly using SQL SUM and JSON_UNQUOTE/JSON_EXTRACT
            totals_query = """
                SELECT b.sale_lot, 
                       SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(l.payment, '$."เครดิต"')) AS DOUBLE)) AS credit,
                       SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(l.payment, '$."โอน"')) AS DOUBLE)) AS transfer,
                       SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(l.payment, '$."เงินสด"')) AS DOUBLE)) AS cash
                FROM prod_out_bill_list l
                JOIN prod_out_bill b ON b.bill_no = l.bill_no
                WHERE b.sale_lot IS NOT NULL AND b.sale_lot <> ''
                GROUP BY b.sale_lot
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

        # 3. For each of POS 1 to 4, fetch the latest 10 transactions to build trends
        pos_list = ["1", "2", "3", "4"]
        results = []

        for lot in pos_list:
            trend_query = """
                SELECT l.amount
                FROM prod_out_bill b
                JOIN prod_out_bill_list l ON b.bill_no = l.bill_no
                WHERE b.sale_lot = %s
                ORDER BY l.id DESC
                LIMIT 10
            """
            with conn.cursor() as cur:
                cur.execute(trend_query, (lot,))
                lot_rows = cur.fetchall()

            last_sale_total = lot_rows[0]["amount"] if lot_rows else 0.0
            trend = [r["amount"] for r in lot_rows]
            trend.reverse()  # oldest to newest for UI sparkline

            totals = totals_by_lot.get(lot, {"credit": 0.0, "transfer": 0.0, "cash": 0.0})

            results.append({
                "sale_lot": lot,
                "last_sale_total": last_sale_total,
                "credit": totals["credit"] or 0.0,
                "transfer": totals["transfer"] or 0.0,
                "cash": totals["cash"] or 0.0,
                "trend": trend,
                "is_live": lot == live_lot,
            })

        results.sort(key=lambda x: x["sale_lot"])
        return results

    finally:
        conn.close()
