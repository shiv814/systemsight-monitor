from systemsight.incident import build_incidents
from systemsight.report import build_report, sparkline_svg

def test_incident_timeline_and_html_report():
    incidents=build_incidents([{"timestamp":"2026-01-01T00:00:00+00:00","kind":"opened","key":"cpu","severity":"warning"},{"timestamp":"2026-01-01T00:01:00+00:00","kind":"escalated","key":"cpu","severity":"critical"},{"timestamp":"2026-01-01T00:02:00+00:00","kind":"recovered","key":"cpu","severity":"critical"}]); assert incidents[0].peak_severity=="critical"; assert incidents[0].duration_seconds==120; assert "polyline" in sparkline_svg([1,2,3]); html=build_report({"host":"<demo>","cpu":{"percent":10}},{"cpu.percent":[1,2,3]}); assert "&lt;demo&gt;" in html
