# Smart Linux Service Restart Manager

A Python supervisor for Linux services that monitors them, detects failures,
checks service dependencies, guards against restart loops (sliding window),
and then restarts, holds, or escalates. Restart history is logged to CSV and
shown on a dashboard.

## Run
    python3 src/monitor.py
    python3 src/dashboard.py

## Demo scenarios
- A: normal restart
- B: dependency hold (wait)
- C: restart-loop detection and escalation

## Layout
- src/   monitor and dashboard code
- tests/ crashy.sh (a deliberately failing test service)
- docs/  paper and Review-2 slides

## Setup (Ubuntu VM)
    # test services and monitor go in /home/ubuntu
    cp tests/*.sh src/monitor.py src/dashboard*.py src/dashboard.html /home/ubuntu/
    chmod +x /home/ubuntu/*.sh

    # install the systemd units
    sudo cp systemd/*.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl start database webapp crashy

    # run the manager
    python3 /home/ubuntu/monitor.py

## Notes
- `monitor.py` hardcodes the dependency map (`webapp.service` depends on
  `database.service`) and writes history to `/home/ubuntu/restart_history.csv`.
- Learning is a history-driven heuristic, not machine learning.
