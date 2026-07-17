"""FastAPI web dashboard for browsing scan history and launching scans.

Requires the ``[web]`` extra: ``pip install "aliens-eye[web]"``
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

try:
    from fastapi import FastAPI, HTTPException, Query, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn
except ImportError:
    FastAPI = None  # type: ignore

from alians_eye.core.history import HistoryDB

app = FastAPI(title="Alien's Eye", version="2.2.2") if FastAPI else None  # type: ignore


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Alien's Eye Dashboard</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          background: #0a0a1a; color: #e0e0e0; }}
  header {{ background: linear-gradient(135deg, #0d0d24, #1a0a2e);
            padding: 24px 32px; border-bottom: 1px solid #2a2a5a; }}
  header h1 {{ color: #00ff88; font-size: 1.5rem; }}
  header span {{ color: #888; font-size: 0.9rem; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 24px 32px; }}
  .stats {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
  .stat-card {{ background: #111133; border: 1px solid #2a2a5a; border-radius: 8px;
                padding: 16px 24px; flex: 1; min-width: 140px; }}
  .stat-card .value {{ font-size: 2rem; font-weight: bold; color: #00ff88; }}
  .stat-card .label {{ font-size: 0.85rem; color: #888; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; background: #111133;
           border-radius: 8px; overflow: hidden; }}
  th {{ background: #1a1a3a; color: #00ccff; padding: 12px 16px; text-align: left;
        font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; }}
  td {{ padding: 12px 16px; border-top: 1px solid #1a1a3a; font-size: 0.9rem; }}
  tr:hover {{ background: #1a1a3a; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px;
             font-size: 0.75rem; font-weight: 600; }}
  .badge.found {{ background: #00ff8833; color: #00ff88; }}
  .badge.level {{ background: #6600ff33; color: #9966ff; }}
  a {{ color: #00ccff; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .empty {{ text-align: center; padding: 48px; color: #666; }}
  .time {{ color: #666; font-size: 0.8rem; }}
  .scan-btn {{ display: inline-block; margin-top: 16px; padding: 10px 24px;
               background: linear-gradient(135deg, #00ff88, #00ccff);
               color: #000; border: none; border-radius: 6px; font-weight: 600;
               cursor: pointer; text-decoration: none; }}
  .scan-btn:hover {{ opacity: 0.9; }}
</style>
</head>
<body>
<header>
  <h1>👁️ Alien's Eye <span>Dashboard</span></h1>
</header>
<div class="container">
  {{content}}
</div>
</body>
</html>"""


def _render_page(title: str, body: str) -> str:
    return HTML_TEMPLATE.replace("{{content}}", f"<h2>{title}</h2>\n{body}", 1)


def _time_ago(ts: float) -> str:
    delta = time.time() - ts
    if delta < 60:
        return "just now"
    if delta < 3600:
        return f"{int(delta // 60)}m ago"
    if delta < 86400:
        return f"{int(delta // 3600)}h ago"
    return f"{int(delta // 86400)}d ago"


def _scan_history_page() -> str:
    db = HistoryDB()
    scans = db.recent_scans(50)
    total = len(scans)
    found_total = sum(s["total_found"] for s in scans)

    stats = f"""<div class="stats">
  <div class="stat-card"><div class="value">{total}</div><div class="label">Total Scans</div></div>
  <div class="stat-card"><div class="value">{found_total}</div><div class="label">Profiles Found</div></div>
</div>"""

    if not scans:
        return _render_page("Scan History", f"""{stats}<div class="empty">No scans yet. Run <code>alians_eye username</code> to start.</div>""")

    rows = "".join(
        f"""<tr>
          <td><a href="/scan/{s['id']}">{s['username']}</a></td>
          <td><span class="badge level">{s['scan_level']}</span></td>
          <td><span class="badge found">{s['total_found']} found</span></td>
          <td>{s['total_scanned']} sites</td>
          <td class="time">{_time_ago(s['timestamp'])}</td>
        </tr>"""
        for s in scans
    )

    table = f"""<table>
      <thead><tr><th>Username</th><th>Level</th><th>Results</th><th>Scanned</th><th>When</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>"""

    return _render_page("Scan History", stats + table)


def _scan_detail_page(scan_id: int) -> str:
    db = HistoryDB()
    scan = db.get_scan(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")

    username = scan["username"]
    results = json.loads(scan["results_json"]) if scan["results_json"] else {}
    total_found = scan["total_found"]

    body = f"""<div class="stats">
  <div class="stat-card"><div class="value">{username}</div><div class="label">Username</div></div>
  <div class="stat-card"><div class="value">{scan['scan_level']}</div><div class="label">Level</div></div>
  <div class="stat-card"><div class="value">{total_found}</div><div class="label">Found</div></div>
  <div class="stat-card"><div class="value">{scan['total_scanned']}</div><div class="label">Sites</div></div>
  <div class="stat-card"><div class="value">{_time_ago(scan['timestamp'])}</div><div class="label">Scanned</div></div>
</div>"""

    variations = list(results.keys())
    if not variations:
        body += '<div class="empty">No variation data in this scan.</div>'
    else:
        rows = "".join(
            f"<tr><td>{v}</td><td><span class=\"badge found\">{len(results[v])} results</span></td></tr>"
            for v in variations
        )
        body += f"""<table><thead><tr><th>Variation</th><th>Results</th></tr></thead><tbody>{rows}</tbody></table>"""

    return _render_page(f"Scan: @{username}", body)


def _run_scan_page(username: str) -> str:
    return _render_page(f"Scanning @{username}",
        '<div class="empty">Scan launched in background. <a href="/">Back to dashboard</a></div>')


# --- Routes ---

@app.on_event("startup")
async def startup() -> None:
    HistoryDB()


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return _scan_history_page()


@app.get("/scan/{scan_id}", response_class=HTMLResponse)
async def scan_detail(scan_id: int) -> str:
    return _scan_detail_page(scan_id)


@app.get("/api/scans", response_class=JSONResponse)
async def api_scans(limit: int = Query(20, le=100)) -> list[dict[str, Any]]:
    return HistoryDB().recent_scans(limit)


@app.get("/api/scans/{scan_id}", response_class=JSONResponse)
async def api_scan_detail(scan_id: int) -> dict[str, Any]:
    scan = HistoryDB().get_scan(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


def run_web(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Launch the web dashboard."""
    if FastAPI is None:
        print("Web dashboard requires FastAPI and uvicorn.")
        print("Install with: pip install \"aliens-eye[web]\"")
        return
    uvicorn.run(app, host=host, port=port, log_level="info")
