# Phase 1 Requirements — นครอะไหล่ Central Dashboard

> **Auto-maintained** by the `update_requirements` skill. Updated as features are built, bugs are fixed, or scope changes.

---

## Section 1 — สถานะเครื่อง POS ทั้งหมด (POS Status Cards)

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 1.1 | Show 4 POS cards (POS 1–4) | ✅ Done | `sale_lot` 1–4 from `prod_out_bill` |
| 1.2 | Last Sale Total per POS | ✅ Done | Latest `amount` from `prod_out_bill_list` |
| 1.3 | All-time credit / transfer / cash totals per POS | ✅ Done | Summed from `payment` JSON keys: `"เครดิต"`, `"โอน"`, `"เงินสด"` |
| 1.4 | Trend sparkline (last 10 sales) | ✅ Done | `TREND_POINTS = 10`, oldest→newest order |
| 1.5 | Live badge on most-recently-updated POS | ✅ Done | Max `list_id` across all POS = live |
| 1.6 | Cards sorted by POS number | ✅ Done | `result.sort(key=lambda x: x["sale_lot"])` |

**API endpoint:** `GET /pos/status` → `List[PosStatus]`

---

## Section 2 — รายการธุรกรรมล่าสุด (Live Transaction Feed) + Donut Chart

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 2.1 | Show latest 1 transaction per POS (4 rows total) | ✅ API done | Data returned by `/pos/dashboard` |
| 2.2 | Columns: เวลา, POS, รายการสินค้าที่ขาย, ยอดเงิน, รูปแบบการชำระเงิน | ✅ API done | `upd_date`, `sale_lot`, `prod_id`, `amount`, derived payment |
| 2.3 | Payment type derived from non-zero keys in `payment` JSON | ✅ API done | Returns list: `["cash"]`, `["credit","cash"]`, etc. |
| 2.4 | Section 2 **not rendering** in Avalonia UI | 🔴 Bug | DataGrid / Donut visible in AXAML but not appearing — under investigation |
| 2.5 | Donut chart — bill count per payment method (all-time) | ✅ API done | `_aggregate_payment_summary()` counts each non-zero method |
| 2.6 | Donut tooltip: % + total amount (บาท) per method | ✅ API done | `ToolTipLabelFormatter` set in `BuildDonutSeries()` |
| 2.7 | Donut scope: all-time (not just feed rows) | ✅ Done | Uses full `rows` not just `latest_per_lot` |

**API endpoint:** `GET /pos/dashboard` → `DashboardResponse` (combined Section 1 + 2)

---

## Infrastructure

| Item | Status | Notes |
|------|--------|-------|
| MySQL Docker (local) | ✅ Running | `workshop_db`, tables: `prod_out_bill`, `prod_out_bill_list` |
| FastAPI + uvicorn | ✅ Running | Port 8000, `uvicorn app.main:app --reload` |
| DBUtils connection pool | ✅ Done | `mincached=2`, `ping=1` — no more session timeouts |
| `cryptography` package | ✅ Fixed | Required for MySQL 8+ `caching_sha2_password` auth |
| DB indexes | ⚠️ Manual step | Run once: `CREATE INDEX idx_pob_bill_no`, `idx_pob_sale_lot`, `idx_pobl_bill_no` |
| Avalonia app (.NET 8) | ✅ Building | `dotnet run` from `avalonia_app/avalonia_app/` |
| Single `/pos/dashboard` endpoint | ✅ Done | Replaces two parallel queries — eliminates MySQL I/O contention |

---

## Known Bugs

| # | Bug | Status | Fix Applied |
|---|-----|--------|-------------|
| B1 | Broken venv launcher (wrong Python path) | ✅ Fixed | Delete + recreate venv |
| B2 | Slow API (full table scan on every request) | ✅ Fixed | Add DB indexes + removed double query |
| B3 | MySQL session timeout | ✅ Fixed | DBUtils PooledDB with `ping=1` |
| B4 | `CREATE INDEX IF NOT EXISTS` syntax error | ✅ Fixed | Remove `IF NOT EXISTS` |
| B5 | `X | Y` union syntax crashes Python < 3.10 | ✅ Fixed | Use `Optional[X]` from `typing` |
| B6 | HttpClient no timeout (UI freezes 100 s) | ✅ Fixed | `Timeout = TimeSpan.FromSeconds(15)` |
| B7 | 404 from Avalonia (BaseAddress + leading-slash) | ✅ Fixed | Trailing `/` on BaseUrl, no leading `/` on paths |
| B8 | dotnet build MSB1003 (wrong working directory) | ✅ Fixed | Run from inner `.csproj` directory |
| B9 | Section 2 empty / timer pileup | ✅ Fixed | Single `/pos/dashboard`, `_isLoading` guard |
| B10 | `cryptography` missing (MySQL 8 auth failure) | ✅ Fixed | `pip install cryptography==49.0.0` |
| B11 | CommunityToolkit.Mvvm dual source-generator (SDK 10) | ✅ Fixed | Replaced source generators with manual `INotifyPropertyChanged` |
| B12 | Section 2 (Transaction Feed) not rendering in UI | ✅ Fixed | `Grid` had no `Height` — collapsed to 0 in StackPanel; fixed with `Height="260"` |


---

## Open Items (Later Phases)

- [ ] Real datetime field for transaction time (currently `upd_date` is date-only)
- [ ] Product name lookup table (replace `prod_id` with product name)
- [ ] Returns table schema (skipped — no source table yet)
- [ ] Delivery status table (out of scope for Phase 1)

---

*Last updated: 2026-07-17*
