# Central Project Plan & Milestones Checklist

This file contains the current checklist of features, fixes, and milestones. Future agents should refer to this document to understand the next steps.

---

## 📋 Milestone Checklist

### Phase 1 — Central Dashboard Core Layout & Rendering
- [x] Create 4 POS Cards displaying:
  - POS Number
  - Last Sale Total
  - All-time totals grouped by method (บช:เครดิต, โอนเงิน, เงินสด)
  - Trend sparkline (last 10 transactions)
  - Live badge indicator
- [x] Create Live Transaction Feed DataGrid (เวลา, POS, รายการสินค้าที่ขาย, ยอดเงิน, รูปแบบการชำระเงิน)
- [x] Create Donut Chart summarizing count of bills per payment method
- [x] Fix DataGrid layout height collapse issues (resolved Section 2 empty/invisible bug)
- [x] Fix performance bottlenecks (added database indexes, unified APIs to single `/pos/dashboard` endpoint, and added loading guard to prevent timer pileup)
- [x] Fix Thai language rendering (Tofu/squares) in Donut Chart legends & tooltips using global Tahoma typeface configuration in SkiaSharp

---

## 🛠️ Known Bugs & Status

| ID | Description | Status | Reference |
|---|---|---|---|
| B1-B11 | Various environment, database connection, performance, and API route bugs | ✅ Fixed | See [troubleshooting_log.md](file:///d:/SideProject/07MainAvalonia/troubleshooting_log.md) |
| B12 | Section 2 (Transaction Feed) not rendering in UI | ✅ Fixed | See [troubleshooting_log.md](file:///d:/SideProject/07MainAvalonia/troubleshooting_log.md) |
| B13 | Donut chart rendering Thai characters as tofu boxes | ✅ Fixed | Resolved via global `SKTypeface` config in `App.axaml.cs` |

---

## 🚀 Phase 2 Planned Tasks (Next Steps)

- [ ] **Transaction Time Field**: Implement a real datetime field for transaction times (currently `upd_date` only stores dates).
- [ ] **Product Name Lookup**: Implement a product name lookup table to replace raw `prod_id` strings with actual product names.
- [ ] **Returns Table Integration**: Define the database schema and endpoints for recent returns once the source table is available.
- [ ] **Delivery Status Tracking**: Add delivery status tracking and map the corresponding database table when available.

---

## ⚠️ Important Rules for Agents
- **MD File Modification Rule**: Every time you need to create or modify a `.md` file in this workspace, **you must ask the user for explicit permission first**. Do not automatically edit files without checking.

*Last updated: 2026-07-18*
