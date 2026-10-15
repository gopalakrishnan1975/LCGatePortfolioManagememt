# Deployment, testing and release plan
Author: R. Gopalakrishnan

## Developer checks
`python -m pytest -q` verifies conservation, source example, economics, overlap, validation, portfolio optimum/exclusivity, policy floors and API/UI smoke paths. `python -m compileall core services app.py` checks syntax. CI repeats tests on Python 3.12. Docker Compose topology is provided; live container deployment must be checked on a Docker-enabled host.

## Production checklist
Use reviewed economic references; replace demo LC inventory. Pin validated dependencies and container digest. Put TLS and IR identity gateway ahead of APIs; services expose no built-in authorization. Configure network isolation, rate limits and upload-size limits. Add persistent scenario/audit stores per schema. Separate service credentials and restrict master publishes to stewards. Configure monitoring, structured logs, backups, recovery exercises and time synchronization. Add health/readiness checks and resource limits to deployed orchestration.

## Review gates
Unit/API/UI smoke tests → field queue calibration → independent appraisal review → corridor benefit-overlap review → zonal pilot acceptance → authority-approved rollout. Maintain a changelog and model version; a new risk model requires validation, not just a successful software test. Container network and concurrent-user load are not established by local calculation tests.
