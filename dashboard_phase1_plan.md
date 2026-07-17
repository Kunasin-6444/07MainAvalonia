# แผงควบคุมกลาง - นครอะไหล่ (Central Dashboard) — Phase 1 Plan

## Scope (Phase 1)
1. **สถานะเครื่อง POS ทั้งหมด** (4 POS cards)
2. **รายการธุรกรรมล่าสุด** + donut chart (payment breakdown)
3. ~~การคืนสินค้าล่าสุด~~ — **skipped**, no source table yet
4. ~~สถานะการส่งสินค้า~~ — not in scope

## Data mapping

### 1. POS Status Cards
- **POS number** ← `prod_out_bill.sale_lot` (test data: values "1"–"4", 1 row per POS min)
- **Last Sale Total** ← latest `prod_out_bill_list.amount` for that POS (join via `bill_no`, order by `upd_date`/`id` desc)
- **บช:เครดิต / โอนเงิน / เงินสด** ← sum of `payment` JSON values per POS, using actual keys confirmed via `SET NAMES utf8mb4;`:
  - `"เครดิต"` = credit, `"โอน"` = transfer, `"เงินสด"` = cash
  - (query by key name directly, not positional order)
  - **Scope confirmed: all-time totals** (not limited to today or last N) — large numbers with full test data are expected
- **Trend sparkline** ← sales graph (ยอดขาย) over time for that POS — last N `amount` values in time order
- **Live badge** ← most recently updated POS (max `upd_date`/id across all 4)

### 2. Live Transaction Feed + Donut
- **Feed = latest 1 transaction per POS** (4 rows total, one per `sale_lot`), sorted with most recent first
- **เวลา** ← `upd_date` (date only for now; will switch to real timestamp later)
- **POS** ← `sale_lot`
- **รายการสินค้าที่ขาย** ← `prod_id` (name substitution later when product table arrives)
- **ยอดเงิน** ← `amount`
- **รูปแบบการชำระเงิน** ← derived from `payment` JSON (which key is non-zero)
- **Donut chart** ← **count of bills** per payment method (เครดิต/โอนเงิน/เงินสด), segments as %; hover tooltip shows % + actual total amount (บาท) for that method
  - A bill with multiple non-zero payment keys counts toward **each** applicable method (not mutually exclusive)
  - **Scope confirmed: all-time** (aggregates every bill, not just the feed rows)

### "Live" definition
The POS card/badge marked live = the `sale_lot` whose most recent transaction (`list_id`) is the most recent across **all** POS — i.e. same POS that appears first in the transaction feed.

### Join key
`prod_out_bill.bill_no` = `prod_out_bill_list.bill_no`

## Open items (later phases)
- Real datetime field for transaction time
- Returns table schema
- Product name table (replace `prod_id`)
- Delivery status table

## Infra
- 2 tables run locally via Docker MySQL on developer laptop
- FastAPI connects via env vars (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`) — see `.env.example`

## Next steps
1. You add test `sale_lot` values (1–4) to some `prod_out_bill` rows ✅ done
2. FastAPI scaffold for `/pos/status` and `/pos/latest-transactions` ✅ done — see `fastapi_app/`
3. Avalonia MVVM scaffold ✅ done — see `avalonia_app/` (HttpClient + LiveCharts2, .NET 8)
4. Run `dotnet restore` + `dotnet run` in `avalonia_app/`, verify UI renders against live API
5. Iterate on styling / layout to match reference image more closely
