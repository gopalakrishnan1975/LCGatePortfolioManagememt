# Software Requirements and Architecture (SRA)
Author: R. Gopalakrishnan | Version 1.0 | 15 October 2026
Status: implementation baseline; proposed production requirements are identified separately.

## Purpose and users
Support comparison of LC treatments and annual investment portfolios beyond TVU. Users: divisional data officers, engineering planners, operating analysts, zonal reviewers and Railway Board policy owners. Interpret SRA as Software Requirements and Architecture; this includes an SRS-style requirements specification.

## Functional requirements and acceptance
| ID | Requirement | Acceptance evidence | State |
|---|---|---|---|
| FR01 | Keep LC and treatment master separate from executable logic | Read-only service mount; scenario changes leave JSON unchanged | Implemented |
| FR02 | Validate traffic, costs, fractions, horizon and observed arrays | API rejects negative values and invalid 8640-bin arrays | Implemented |
| FR03 | Simulate a representative day in 10-second steps | Vehicle conservation and overlapping-event union tests | Implemented |
| FR04 | Show road, rail, safety and carbon components separately | Export contains units and individual components | Implemented |
| FR05 | Compute discounted benefits, maintenance, NPV, BCR, EIRR | Independent zero-discount reference calculation | Implemented |
| FR06 | Permit budget basis selection and one treatment per LC | MILP tests against small exhaustive enumeration | Implemented |
| FR07 | Apply safety floor and rural/congested project floors | Infeasible combinations reported without fabricated selection | Implemented |
| FR08 | Expose parameter controls, queues, charts, exports | Streamlit AppTest | Implemented |
| FR09 | Use independent microservice processes | Master, simulation, appraisal and portfolio FastAPI contracts | Implemented; Compose runtime requires deployment verification |
| FR10 | Save immutable scenario/master/model snapshots and audit | SQL target schema; persistence adapter required | Planned |
| FR11 | Generate Pareto portfolios and robustness frequencies | Repeated epsilon/weight scenarios and dominated-set verification | Planned |
| FR12 | Calculate class/direction-specific queue, GIS access and calibrated risk | Holdout/calibration acceptance report | Planned |

## Nonfunctional requirements
Production targets, not measured guarantees: 100 LC daily simulations in under five minutes on a defined benchmark machine; 99.5% service availability; HTTP timeouts and solver limits; structured request IDs; validated CSV/JSON contracts; TLS through a gateway; SSO roles (viewer, analyst, master steward, reviewer, approver); least-privilege service database roles; backup/restore and data retention as approved by IR. Current package has no production authentication and must be deployed behind controlled access.

## Data ownership
Master service owns approved LC attributes, feasibility and reference versions. Observation ingestion will own immutable source batches and quality flags. Simulation/appraisal own scenario-derived results, never authoritative master changes. Portfolio service owns selections and policy settings. Cross-service references use UUID/version; no direct database writes to another service's store.

## Constraints and exclusions
No train control, gate actuation, sanction automation or engineering design certification. Synthetic defaults are editable. Each rejected/modified data item must be reviewable in a production ingestion workflow. Geographic coordinates and sensitive source logs follow approved access rules.

## Traceability
Paper equations 1 and 7–10 map to simulation; 11–16 and 20 map to input-driven appraisal; 23–27 map to discounted economics; 29–35 map to MILP. Equations 15, 17–19, 21–22 and the recommended Pareto workflow are partially represented by supplied indicators or remain extensions. Tests cover implemented calculation contracts, not statistical validity of assumed coefficients.
