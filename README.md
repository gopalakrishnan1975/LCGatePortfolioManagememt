# LC Grade Separation Planning Laboratory
**Concept and authorship: R. Gopalakrishnan**
A runnable implementation of the supplied multi-objective technical paper, with separated master data, four FastAPI microservices, and a Streamlit user interface.

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Local mode requires no backend services. For independently deployed services:
```bash
docker compose up --build
```
Open http://localhost:8501. API documentation: http://localhost:8001/docs through :8004/docs. The local and remote modes use the same tested calculation library; remote UI calls services through HTTP.

## Documents
- [Software requirements and architecture (SRA)](docs/SRA.md)
- [Architecture](docs/architecture.md)
- [ERD](docs/ERD.md) and [data model](docs/data-model.md)
- [Integrated revised technical paper (PDF)](docs/lc_grade_separation_paper.pdf)
- [Editable LaTeX source](docs/lc_grade_separation_paper.tex)
- [Implementation companion](docs/technical-documentation.md)
- [User manual](docs/user-manual.md)
- [Draft Railway Board business policy](docs/business-policy-draft.md)
- [Deployment and validation](docs/operations.md)
- [Original technical manuscript](docs/source-paper.pdf)

## Scope
Runnable: aggregate fluid queue at 10-second resolution; observed arrival/event JSON; road, rail, safety, carbon appraisal; NPV, BCR, EIRR; scenario export; traffic sensitivity; mixed-integer portfolio constraints. Master records are versioned external JSON.
Planned: calibrated accident regression, class/direction-specific queues, GIS routing and Hansen accessibility computation, network rail capacity simulation, Pareto frontier and robustness sampling, persisted multi-user scenarios and ingestion. The SQL schema specifies that production target, not an already deployed database.
Defaults are synthetic planning assumptions, not prescribed Indian Railways appraisal rates. The policy is a draft for PED/B&S review. No software license is asserted without the author's choice.

## Verification
```bash
python -m pytest -q
```

## Build the integrated technical paper
```bash
cd docs
pdflatex -interaction=nonstopmode -halt-on-error lc_grade_separation_paper.tex
pdflatex -interaction=nonstopmode -halt-on-error lc_grade_separation_paper.tex
```
The self-contained source integrates the original August 2026 paper and October 2026 software specification. Its compiled PDF replaces the Word technical document. The original source-paper.pdf remains as a provenance record.
