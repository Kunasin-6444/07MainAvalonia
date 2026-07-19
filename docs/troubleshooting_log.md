# Nakhon Parts Dashboard — Bug & Error Log

A running record of every issue encountered, its root cause, and how it was fixed.

---

## Bug 1 — Broken `venv` launcher (wrong Python path)

### Symptom
```
Fatal error in launcher: Unable to create process using
'"D:\SideProject\04FastAPIPhase1\fastapi_app\fastapi_app\venv\Scripts\python.exe"'
The system cannot find the file specified.
```
Running `uvicorn app.main:app --reload` failed immediately.

### Root Cause
The `venv/` folder was carried over from a previous project located at
`D:\SideProject\04FastAPIPhase1\...`. Virtual environments embed an absolute path
to the Python interpreter inside `pyvenv.cfg` and the launcher executables.
Moving or copying a `venv/` to a new directory breaks all launchers.

### Fix
Delete and recreate the venv from scratch:
```powershell
# From D:\SideProject\07MainAvalonia\fastapi_app\fastapi_app
Remove-Item -Recurse -Force venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Bug 2 — API cards very slow to load (full table scan on every request)

### Symptom
Both /pos/status and /pos/latest-transactions endpoints took several seconds
to respond. Delay grew worse as the database grew.

### Root Cause
JOIN_SQL in queries.py joins prod_out_bill -> prod_out_bill_list on bill_no
and filters on sale_lot, but none of these columns had indexes.
Every API call triggered a full table scan on both tables.

### Fix — Part A: Create MySQL indexes (run once)
```sql
CREATE INDEX idx_pob_bill_no  ON prod_out_bill (bill_no);
CREATE INDEX idx_pob_sale_lot ON prod_out_bill (sale_lot);
CREATE INDEX idx_pobl_bill_no ON prod_out_bill_list (bill_no);
```
> Note: prod_out_bill_list.id is a PRIMARY KEY and is already indexed automatically.

### Fix — Part B: Remove double query in fetch_transactions()
The old code ran PAYMENT_ONLY_SQL as a second full join query just for the donut chart.
This was eliminated. fetch_transactions() now reuses all_rows to compute payment_summary
in Python, cutting DB round-trips from 2 to 1.

---

## Bug 3 — MySQL session timeout

### Symptom
After the app was idle, the next API call failed with MySQL "connection lost" or
"session timed out" error.

### Root Cause
database.py opened a brand-new TCP connection on every API call with no pooling.
MySQL's wait_timeout closes long-idle connections. The app also paid the full
TCP + auth handshake cost on every request.

### Fix
Replaced raw pymysql.connect() with DBUtils.PooledDB:
- mincached=2: keep 2 warm connections at all times
- ping=1: re-ping before handing out a connection, detects stale sessions and reconnects automatically

Added DBUtils==3.1.0 to requirements.txt.

---

## Bug 4 — CREATE INDEX IF NOT EXISTS syntax error

### Symptom
ERROR 1064 (42000): You have an error in your SQL syntax near
'IF NOT EXISTS idx_pob_bill_no ON prod_out_bill (bill_no)'

### Root Cause
CREATE INDEX IF NOT EXISTS was added in MySQL 8.0.29.
Older MySQL versions do not support IF NOT EXISTS for CREATE INDEX.

### Fix
Remove IF NOT EXISTS — plain CREATE INDEX works on all MySQL versions:
```sql
CREATE INDEX idx_pob_bill_no  ON prod_out_bill (bill_no);
CREATE INDEX idx_pob_sale_lot ON prod_out_bill (sale_lot);
CREATE INDEX idx_pobl_bill_no ON prod_out_bill_list (bill_no);
```
If run twice, MySQL returns 'Duplicate key name' — harmless, index already exists.

---

## Bug 5 — X | Y type union syntax crashes on Python < 3.10

### Symptom
FastAPI/uvicorn fails to start with TypeError on import of database.py on Python 3.8/3.9.

### Root Cause
_pool: PooledDB | None = None
The X | Y union shorthand was introduced in Python 3.10 (PEP 604).
Using it as a runtime annotation raises TypeError on older interpreters.

### Fix
Use Optional[X] from typing, which works on Python 3.8+:
```python
from typing import Optional
_pool: Optional[PooledDB] = None
```

---

## Bug 6 — HttpClient no timeout (UI freezes for 100 seconds)

### Symptom
When the FastAPI server was slow or unreachable, the Avalonia dashboard froze
with 'Loading...' and did not show an error for up to 100 seconds.

### Root Cause
HttpClient default timeout is 100 seconds. ApiClient was constructed without
setting Timeout, so the UI waited the full 100s.

### Fix (Services/ApiClient.cs)
```csharp
_http = new HttpClient
{
    BaseAddress = new Uri(BaseUrl),
    Timeout = TimeSpan.FromSeconds(10)
};
```

---

*Last updated: 2026-07-16*


---

## Bug 7 — 404 Not Found from Avalonia (HttpClient BaseAddress + leading-slash bug)

### Symptom
The Avalonia dashboard shows 404 / error even though the FastAPI server is running
and both endpoints return 200 when called directly from a browser or curl.

### Root Cause
A well-known .NET `HttpClient` gotcha:

| BaseAddress | Relative path | Resolved URL |
|---|---|---|
| `http://127.0.0.1:8000` (no trailing slash) | `/pos/status` (leading slash) | `http://127.0.0.1/pos/status` ← **port 8000 dropped!** |
| `http://127.0.0.1:8000/` (trailing slash) | `pos/status` (no leading slash) | `http://127.0.0.1:8000/pos/status` ✅ |

When the base URL has no trailing slash and the relative path starts with `/`,
.NET treats the path as absolute from the root and silently drops the base path
(including the port number). The request lands on port 80 instead of 8000 → 404.

### Fix (Services/ApiClient.cs)
```csharp
// WRONG — no trailing slash on BaseAddress
private const string BaseUrl = "http://127.0.0.1:8000";
var result = await _http.GetFromJsonAsync<...>("/pos/status");   // leading /

// CORRECT — trailing slash + no leading slash on relative paths
private const string BaseUrl = "http://127.0.0.1:8000/";
var result = await _http.GetFromJsonAsync<...>("pos/status");    // no leading /
```

### Rule to remember
> `BaseAddress` must end with `/`.
> Relative paths passed to `GetAsync` / `GetFromJsonAsync` must NOT start with `/`.


---

## Bug 8 - dotnet build fails with MSB1003 (wrong working directory)

### Symptom
```
MSBUILD : error MSB1003: Specify a project or solution file.
The current working directory does not contain a project or solution file.
```
Running `dotnet build` from `d:\SideProject\07MainAvalonia\avalonia_app` failed.

### Root Cause
The `.csproj` file lives one level deeper at:
`d:\SideProject\07MainAvalonia\avalonia_app\avalonia_app\`
Running `dotnet build` from the outer `avalonia_app\` wrapper folder finds no project file.

### Fix
Always run dotnet commands from the inner project directory that contains the `.csproj`:
```powershell
cd D:\SideProject\07MainAvalonia\avalonia_app\avalonia_app
dotnet build
dotnet run
```

*Last updated: 2026-07-16*


---

## Bug 9 - Section 2 empty / cards slow due to sequential API calls and timer pileup

### Symptom
- POS cards (Section 1) loaded slowly
- Section 2 (Live Transaction Feed + Donut chart) never displayed
- Status bar showed: `Error: TaskCanceledException - The request was canceled due to the configured HttpClient.Timeout of 60 seconds elapsing`

### Root Cause
Three compounding issues:
1. GetPosStatusAsync() and GetLatestTransactionsAsync() were called SEQUENTIALLY (17s + 28s = 45s total)
2. The refresh timer fired every 10s, stacking new LoadDataAsync() calls on top of the still-running one
3. Concurrent DB connections through the pool all ran slow full-table-scan queries simultaneously, pushing total time past 60s

### Fix (ViewModels/MainWindowViewModel.cs)
1. Parallelized both API calls with Task.WhenAll - reduces total wait from 45s to max(17s,28s) = ~28s
2. Added _isLoading volatile bool guard - skips new load if one is already in progress
3. Increased timer interval from 10s to 60s to prevent pileup during slow queries
4. Long-term fix: run CREATE INDEX on prod_out_bill and prod_out_bill_list (queries drop to under 1s)

*Last updated: 2026-07-16*
