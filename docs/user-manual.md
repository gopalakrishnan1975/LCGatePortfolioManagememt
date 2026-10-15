# User manual
R. Gopalakrishnan | Version 1.0 | 15 October 2026

## Start
Install Python 3.12, create a virtual environment, install requirements.txt and run `python -m streamlit run app.py` from the repository root. For microservice mode run `docker compose up --build`, then open localhost:8501. Docker must be installed separately. No GitHub hosting automatically starts the app; Streamlit deployment is a separate step.

## Single-LC workflow
1. Select ROB, RUB or closure. Defaults load from separate illustrative treatment master data.
2. Enter road vehicles/day, train movements/day, minutes of gate closure/event, open-gate discharge vehicles/minute and mean occupancy. Increase peak factor to explore bunching.
3. Enter INR/person-hour and freight vehicle operating cost INR/hour. Freight share is a decimal fraction; 0.15 means 15%.
4. Enter attributable rail delay minutes/train and INR/train-hour. Leave additional paths and path value at zero unless a corridor capacity study supports both. Check overlap with direct rail delay.
5. Enter expected annual accident cost, baseline expected fatalities/injuries and achievable treatment risk reduction. These are supplied estimates, not automatically fitted risk predictions.
6. Enter initial capital and incremental yearly maintenance in rupees; 6 crore = 60,000,000. Enter discount and growth as decimals; 0.08 means 8%. All values should share one constant-price base year.
7. For closure/diversion enter added detour minutes. Large detours can produce negative road benefit. Accessibility and vulnerable-share controls are supplied indicators.
8. Optionally upload observed-day JSON. `arrivals_10s` must contain exactly 8640 nonnegative counts; `closure_events` contains [start,end] minute pairs. Example `{"closure_events":[[480,486],[900,906]]}` overrides synthetic event times; reconcile train movements separately.
9. Click Simulate and appraise. Review queue chart, benefit composition, NPV/BCR, physical indicators and residual-queue warnings. The p95 is a queue-clearance proxy, not a passenger reliability guarantee.
10. Download scenario/results JSON for repeatable review. Sensitivity chart changes synthetic traffic volume; it does not perturb an uploaded observed profile. Re-run after any changed control; displayed prior results remain the last successful run.

## Portfolio workflow
Download candidate CSV template. Each row is one feasible LC treatment; multiple rows for an LC are allowed. Replace demo rows with independently reviewed appraisal outputs. Include capital cost, life-cycle PV, NPV and annual safety benefit. Use true/false boolean values. Strategic score is an explicitly agreed 0–1 policy score. Never include retain as a project counted toward rural/congested floors.
Choose budget in crore, capital or life-cycle basis, economic or strategic objective, and optional policy floors. Click Optimize. Check optimal/infeasible/feasible-not-proven status and solver gap. The selection may be empty where NPV is negative and no policy floor applies. Download portfolio results. Candidate CSV values are user supplied; the software does not verify their engineering provenance.

## Master-data administration
Master data tab displays versions and synthetic status. Analysts adjust scenario controls without changing masters. A designated steward edits master_data JSON through a reviewed repository change, creates a new version, validates feasibility/cost assumptions, and deploys it. Current master API is intentionally read-only; production approval and audit workflow is specified in the SRA.

## Troubleshooting
422: correct out-of-range fractions, negative costs or malformed observation arrays. 503: confirm simulation service health and SIM_URL. Infeasible portfolio: budget/policy floors conflict; examine constraints without silently relaxing them. Midnight queue: simulate a better representative day or reduce arrivals/increase discharge based on evidence; do not hide backlog. Blank BCR/EIRR indicates undefined/unbracketed result. Service UI failure: inspect container logs and service /health endpoints.

## Responsible review
Store field evidence, price year, assumptions and reviewer names with outputs. Validate drainage, approach design, land and alternatives independently. Use model results to inform sanctioned appraisal procedures; policy tradeoffs belong to the competent authority.
