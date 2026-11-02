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
