# Data model and dictionary
Author: R. Gopalakrishnan | v1.0

## Layers
1. Master: immutable approved versions of LC inventory, section classification, feasible alternatives and economic references.
2. Observation: arrival counts, classes/directions, gate/train events, accident evidence, source timestamps, provenance and quality flags.
3. Scenario: snapshot of master/observation references plus overrides and model version.
4. Derived: queue trajectories, benefit components, financial indicators and nonmonetary indicators.
5. Policy/portfolio: objective, weights, budget basis, floors, selections and review decisions.

## Runtime Scenario dictionary
| Fields | Units/meaning | Validation |
|---|---|---|
| vehicles_day, trains_day | vehicles/day, movements/day | nonnegative; bounded |
| closure_minutes, discharge_per_minute | minutes/event, vehicles/minute | closure >=0; discharge >0 |
| peak_factor, occupancy | peak profile coefficient; persons/vehicle | peak >=1; occupancy >0 |
| arrivals_10s | vehicle counts per 10-second bin | exactly 8640, nonnegative |
| closure_events | start/end minutes from midnight | 0 <= start < end <=1440 |
| value_time, freight_cost_hour | INR/person-hour; INR/freight-vehicle-hour | >=0 |
| freight_share | fraction of vehicles | 0–1 |
| rail_delay_minutes, rail_cost_hour | minutes/train; INR/train-hour | >=0 |
| additional_paths_day, path_value | extra paths/day; INR/path | >=0 |
| safety_cost_year | baseline expected accident cost INR/year | >=0 |
| fatalities_year, injuries_year | expected baseline casualties/year | >=0 |
| safety_reduction, delay_reduction | treatment reduction fractions | 0–1 |
| detour_minutes | added travel minutes/vehicle | >=0 |
| idling_co2_kg_hour, co2_price_kg | kg/vehicle-hour; INR/kg | >=0 |
| accessibility_index_gain | externally estimated index change | >=0; cannot model negative access yet |
| vulnerable_benefit_share | supplied share, not estimated equity | 0–1 |
| capital_rupees, maintenance_year | INR initial; INR/year incremental O&M | >=0 |
| discount, growth | annual decimal rates | 0–.5; -.5–.2 |
| years | appraisal years | 1–60 |

All flows are incremental to retain, in constant-price rupees. Current growth uniformly scales all benefit components; production should use separate component trajectories. The simulation uses observed arrivals when supplied; vehicles_day then serves only as an inactive control. Train count still drives TVU and rail delay, so observed event counts must be reconciled separately.

## Portfolio contract
Rows require lc_id, treatment, section_id, capital_rupees, lifecycle_rupees, npv_rupees, safety_rupees. Optional rural, congested, feasible and capacity_claim are booleans; strategic_score is a user-supplied 0–1 score. safety_rupees is annual incremental safety benefit. Budget basis capital/lifecycle; objective npv/strategic. Candidate LC+treatment unique. Capacity claims are restricted per section. Nonselection means retain; retain rows should not count toward project floors.

## Output contract
vehicle_hours_day, person_hours_day, arrivals, departures, residual_queue, max_queue, closed_minutes, p95_queue_clearance_minutes, tvu and minute series. Appraisal returns annual components in INR/year, present values and NPV in INR, BCR ratio or null, eirR decimal or null, CO2 kg/year, expected casualties avoided/year and supplied strategic indicators. Queue-clearance p95 is a time-bin proxy, not an empirically estimated traveller-delay percentile.

## Production schema
See schema.sql for keys, versioning and state. Validate temporal ordering, duplicate source IDs, missing-bin flags and known LC identifiers before use. Missing observations must not become zero counts silently. Versioned published master rows are never edited in place. Currency, price base year, timezone (Asia/Kolkata for Indian source records), observation coverage, source hash and quality status belong in every production batch.
