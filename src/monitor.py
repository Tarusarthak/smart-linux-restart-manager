import subprocess
import time
import csv
import os
from datetime import datetime

DEPENDENCIES = {
    "webapp.service": ["database.service"],
    "database.service": [],
}

SERVICES = list(DEPENDENCIES.keys())

DEFAULT_MAX_RESTARTS = 3
WINDOW_SECONDS = 60
LOG_FILE = "/home/ubuntu/restart_history.csv"

restart_times = {s: [] for s in SERVICES}
given_up = {s: False for s in SERVICES}

def load_history():
    """Learn from past runs: services escalated before get a smaller
    restart budget (they've proven unreliable)."""
    budgets = {s: DEFAULT_MAX_RESTARTS for s in SERVICES}
    if not os.path.exists(LOG_FILE):
        return budgets
    with open(LOG_FILE, newline="") as f:
        for row in csv.DictReader(f):
            if row["action"] == "escalate" and row["service"] in budgets:
                budgets[row["service"]] = 2   # was escalated before → stricter
    return budgets

MAX_RESTARTS = load_history()

def log_event(service, state, action, detail):
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "service", "state", "action", "detail"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            service, state, action, detail
        ])

def is_active(service):
    result = subprocess.run(
        ["systemctl", "is-active", service],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def restart(service):
    subprocess.run(["sudo", "systemctl", "restart", service])

def recent_restarts(service):
    now = time.time()
    return [t for t in restart_times[service] if now - t < WINDOW_SECONDS]

def dependencies_ok(service):
    for dep in DEPENDENCIES[service]:
        if is_active(dep) != "active":
            return (False, dep)
    return (True, None)

print(f"Monitoring {SERVICES}. Logging to {LOG_FILE}. Press Ctrl+C to stop.")
for s in SERVICES:
    print(f"  {s}: restart budget = {MAX_RESTARTS[s]} (learned from history)")

try:
    while True:
        for service in SERVICES:
            if given_up[service]:
                print(f"[held] {service} in HOLD — needs admin.")
                continue

            state = is_active(service)
            print(f"[check] {service} is: {state}")

            if state == "failed":
                ok, broken = dependencies_ok(service)
                if not ok:
                    print(f"[wait] {service} failed, but its dependency "
                          f"{broken} is down. NOT restarting {service} yet.")
                    log_event(service, state, "wait",
                              f"dependency {broken} down")
                    continue

                recent = recent_restarts(service)
                limit = MAX_RESTARTS[service]
                if len(recent) >= limit:
                    print(f"[ESCALATE] {service} failed {len(recent)} times "
                          f"in {WINDOW_SECONDS}s (budget {limit}). Holding.")
                    log_event(service, state, "escalate",
                              f"{len(recent)} restarts, budget {limit}")
                    given_up[service] = True
                else:
                    print(f"[action] {service} failed — dependencies OK. "
                          f"Restart {len(recent)+1} of {limit}.")
                    restart(service)
                    restart_times[service].append(time.time())
                    log_event(service, state, "restart",
                              f"attempt {len(recent)+1} of {limit}")

        print("-" * 40)
        time.sleep(3)

except KeyboardInterrupt:
    print("\nMonitor stopped by user.")
