import subprocess
import csv
import os

SERVICES = ["webapp.service", "database.service"]
LOG_FILE = "/home/ubuntu/restart_history.csv"
OUT_FILE = "/home/ubuntu/dashboard.html"

def is_active(service):
    r = subprocess.run(["systemctl", "is-active", service],
                       capture_output=True, text=True)
    return r.stdout.strip()

def read_history(limit=15):
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, newline="") as f:
        rows = list(csv.DictReader(f))
    return rows[-limit:][::-1]

cards = ""
for s in SERVICES:
    state = is_active(s)
    color = "#1d9e75" if state == "active" else "#e24b4a"
    cards += f'<div class="card"><div class="dot" style="background:{color}"></div><div><div class="svc">{s}</div><div class="state" style="color:{color}">{state}</div></div></div>'

rows = ""
for r in read_history():
    rows += f'<tr><td>{r["timestamp"]}</td><td>{r["service"]}</td><td>{r["action"]}</td><td>{r["detail"]}</td></tr>'

html = f'''<html><head><title>Restart Manager Dashboard</title>
<style>
body {{ font-family: sans-serif; background:#0f1c3f; color:#fff; margin:0; padding:30px; }}
h1 {{ font-weight:500; }}
.cards {{ display:flex; gap:20px; margin:20px 0 40px; }}
.card {{ background:#1a2a54; border-radius:12px; padding:20px 24px; display:flex; align-items:center; gap:16px; min-width:220px; }}
.dot {{ width:16px; height:16px; border-radius:50%; }}
.svc {{ font-size:15px; }} .state {{ font-size:20px; font-weight:500; }}
table {{ width:100%; border-collapse:collapse; background:#1a2a54; border-radius:12px; overflow:hidden; }}
th,td {{ text-align:left; padding:12px 16px; font-size:14px; border-bottom:1px solid #2a3a64; }}
th {{ background:#22335f; }}
</style></head><body>
<h1>Smart Linux Service Restart Manager</h1>
<div class="cards">{cards}</div>
<h2>Recent decisions</h2>
<table><tr><th>Time</th><th>Service</th><th>Action</th><th>Detail</th></tr>{rows}</table>
</body></html>'''

with open(OUT_FILE, "w") as f:
    f.write(html)

print(f"Dashboard written to {OUT_FILE}")
