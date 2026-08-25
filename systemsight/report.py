"""Self-contained observability report generation."""
from __future__ import annotations
from html import escape
from typing import Iterable, Mapping, Any

def sparkline_svg(values: Iterable[float], width: int = 180, height: int = 42) -> str:
    series = [float(v) for v in values]
    if not series: return ""
    low, high = min(series), max(series); span = high - low or 1.0; step = width / max(1, len(series) - 1)
    points = " ".join(f"{i*step:.1f},{height - ((v-low)/span)*(height-4)-2:.1f}" for i, v in enumerate(series))
    return f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="metric trend"><polyline fill="none" stroke="#38bdf8" stroke-width="2.5" points="{points}"/></svg>'
def build_report(snapshot: Mapping[str, Any], series: Mapping[str, Iterable[float]] | None = None, alerts: Iterable[Mapping[str, Any]] = ()) -> str:
    host = escape(str(snapshot.get("host") or snapshot.get("hostname") or "host")); series = series or {}; cards = []
    for label, path in (("CPU", "cpu.percent"), ("Memory", "memory.percent"), ("Disk", "disk.percent")):
        value: Any = snapshot
        for part in path.split("."): value = value.get(part) if isinstance(value, Mapping) else None
        display = "n/a" if value is None else f"{float(value):.1f}%"; cards.append(f'<article class="card"><span>{label}</span><b>{display}</b>{sparkline_svg(series.get(path, []))}</article>')
    alert_html = "".join(f'<li><b>{escape(str(a.get("severity", "warning"))).upper()}</b> {escape(str(a.get("message", "")))}</li>' for a in alerts) or '<li class="muted">No active alerts</li>'
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SystemSight · {host}</title><style>body{{margin:0;background:#020617;color:#e2e8f0;font:14px/1.5 Inter,system-ui,sans-serif}}main{{max-width:980px;margin:auto;padding:48px 24px}}header{{padding:30px;border:1px solid #1e293b;border-radius:22px;background:linear-gradient(135deg,#0f172a,#082f49)}}.eyebrow{{color:#38bdf8;text-transform:uppercase;letter-spacing:.16em;font-size:11px}}h1{{margin:6px 0 0;font-size:34px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:20px 0}}.card,.panel{{border:1px solid #1e293b;background:#0f172a;border-radius:18px;padding:20px}}.card span,.muted{{color:#94a3b8}}.card b{{display:block;font-size:30px;margin:4px 0 8px}}svg{{width:100%;height:42px}}ul{{padding-left:20px}}</style></head><body><main><header><div class="eyebrow">SystemSight observability report</div><h1>{host}</h1></header><section class="grid">{''.join(cards)}</section><section class="panel"><h2>Active alerts</h2><ul>{alert_html}</ul></section></main></body></html>'''
