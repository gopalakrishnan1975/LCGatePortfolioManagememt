# Validation report
Author: R. Gopalakrishnan | 15 October 2026

- 10 pytest checks passed, including Streamlit simulation and portfolio interaction.
- Four live FastAPI services passed health checks; appraisal invoked simulation over HTTP.
- Remote Streamlit mode passed both simulation and portfolio workflows against live services.
- Editable policy, manual and technical specification were rendered and all eight pages inspected.
- Python compile checks passed.
- Docker Compose runtime, field calibration, production authentication, persisted audit storage and concurrent-user load testing remain outstanding.

Repeat: `python -m pytest -q`; live integration: `PYTHONPATH=. python tests/live_integration.py` from repository root. Live integration uses ports 8001–8004 and clears proxy variables within its own process for local requests.
