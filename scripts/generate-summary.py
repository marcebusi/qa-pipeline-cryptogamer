"""
Genera un resumen HTML de todos los resultados de tests.
Busca archivos junit.xml en subdirectorios y los consolida.

Uso:
  python scripts/generate-summary.py --reports-dir all-reports --output summary.html
"""
import argparse
import os
import xml.etree.ElementTree as ET
from datetime import datetime

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>QA Pipeline Summary — cryptogamer</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           background: #0f172a; color: #e2e8f0; margin: 0; padding: 2rem; }}
    h1 {{ color: #6366f1; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0; }}
    .card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; text-align: center; }}
    .card .num {{ font-size: 2.5rem; font-weight: 700; }}
    .card .label {{ color: #94a3b8; margin-top: .5rem; }}
    .passed {{ color: #22c55e; }}
    .failed {{ color: #ef4444; }}
    .skipped {{ color: #f59e0b; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 2rem; }}
    th {{ background: #1e293b; padding: .75rem 1rem; text-align: left; }}
    td {{ padding: .75rem 1rem; border-bottom: 1px solid #1e293b; }}
    .badge {{ display: inline-block; padding: .2rem .6rem; border-radius: 9999px; font-size: .8rem; }}
    .badge-pass {{ background: #166534; color: #86efac; }}
    .badge-fail {{ background: #7f1d1d; color: #fca5a5; }}
    .timestamp {{ color: #64748b; font-size: .85rem; margin-top: 3rem; }}
  </style>
</head>
<body>
  <h1>🎮 QA Pipeline Summary — cryptogamer-ecommerce</h1>
  <div class="grid">
    <div class="card"><div class="num">{total_suites}</div><div class="label">Suites</div></div>
    <div class="card"><div class="num passed">{total_passed}</div><div class="label">✅ Passed</div></div>
    <div class="card"><div class="num failed">{total_failed}</div><div class="label">❌ Failed</div></div>
    <div class="card"><div class="num">{total_tests}</div><div class="label">Total tests</div></div>
  </div>
  <table>
    <thead><tr><th>Suite</th><th>Tests</th><th>Passed</th><th>Failed</th><th>Tiempo</th><th>Estado</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <p class="timestamp">Generado: {timestamp}</p>
</body>
</html>"""

ROW_TEMPLATE = """
    <tr>
      <td><strong>{name}</strong></td>
      <td>{tests}</td>
      <td class="passed">{passed}</td>
      <td class="failed">{failed}</td>
      <td>{time:.1f}s</td>
      <td><span class="badge {badge_class}">{status}</span></td>
    </tr>"""


def parse_junit(path):
    tree = ET.parse(path)
    root = tree.getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        return None
    tests = int(suite.get("tests", 0))
    failures = int(suite.get("failures", 0)) + int(suite.get("errors", 0))
    time = float(suite.get("time", 0))
    return {"tests": tests, "failed": failures, "passed": tests - failures, "time": time}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", default="all-reports")
    parser.add_argument("--output", default="summary.html")
    args = parser.parse_args()

    suites = []
    for root, _, files in os.walk(args.reports_dir):
        for f in files:
            if f.endswith(".xml"):
                path = os.path.join(root, f)
                data = parse_junit(path)
                if data:
                    name = os.path.basename(os.path.dirname(path)) or f
                    suites.append({"name": name, **data})

    if not suites:
        print("No se encontraron archivos JUnit XML en", args.reports_dir)
        return

    rows = ""
    for s in suites:
        ok = s["failed"] == 0
        rows += ROW_TEMPLATE.format(
            name=s["name"],
            tests=s["tests"],
            passed=s["passed"],
            failed=s["failed"],
            time=s["time"],
            badge_class="badge-pass" if ok else "badge-fail",
            status="PASS" if ok else "FAIL",
        )

    total_tests = sum(s["tests"] for s in suites)
    total_passed = sum(s["passed"] for s in suites)
    total_failed = sum(s["failed"] for s in suites)

    html = HTML_TEMPLATE.format(
        total_suites=len(suites),
        total_passed=total_passed,
        total_failed=total_failed,
        total_tests=total_tests,
        rows=rows,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Reporte generado: {args.output}")
    print(f"   {total_tests} tests — {total_passed} passed, {total_failed} failed")


if __name__ == "__main__":
    main()
