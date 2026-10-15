-- Author: R. Gopalakrishnan. Production target schema, PostgreSQL.
CREATE SCHEMA IF NOT EXISTS master;
CREATE SCHEMA IF NOT EXISTS observations;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS planning;
CREATE TABLE master.version(version_id uuid PRIMARY KEY, status text NOT NULL CHECK(status IN ('draft','approved','superseded')), checksum text NOT NULL, approved_by text, approved_at timestamptz);
CREATE TABLE master.section(section_id uuid PRIMARY KEY, name text NOT NULL);
CREATE TABLE master.lc(lc_id uuid NOT NULL, version_id uuid REFERENCES master.version, section_id uuid REFERENCES master.section, gate_number text NOT NULL, latitude numeric CHECK(latitude BETWEEN -90 AND 90), longitude numeric CHECK(longitude BETWEEN -180 AND 180), attributes jsonb NOT NULL, PRIMARY KEY(lc_id,version_id));
CREATE TABLE master.alternative(alternative_id uuid PRIMARY KEY, lc_id uuid NOT NULL, version_id uuid NOT NULL, treatment text NOT NULL, feasible boolean NOT NULL, capital_rupees numeric NOT NULL CHECK(capital_rupees>=0), annual_maintenance numeric NOT NULL CHECK(annual_maintenance>=0), assumptions jsonb NOT NULL, FOREIGN KEY(lc_id,version_id) REFERENCES master.lc, UNIQUE(lc_id,version_id,treatment));
CREATE TABLE observations.batch(batch_id uuid PRIMARY KEY, lc_id uuid NOT NULL, source_hash text NOT NULL UNIQUE, timezone text NOT NULL, covered_from timestamptz NOT NULL, covered_to timestamptz NOT NULL, quality_status text NOT NULL, provenance jsonb NOT NULL, CHECK(covered_to>covered_from));
CREATE TABLE observations.road_bin(batch_id uuid REFERENCES observations.batch, bin_start timestamptz, vehicle_class text, direction text, arrivals numeric CHECK(arrivals>=0), quality_flags jsonb NOT NULL, PRIMARY KEY(batch_id,bin_start,vehicle_class,direction));
CREATE TABLE observations.gate_event(batch_id uuid REFERENCES observations.batch, source_event_id text, closed_at timestamptz NOT NULL, opened_at timestamptz NOT NULL, PRIMARY KEY(batch_id,source_event_id), CHECK(opened_at>closed_at));
CREATE TABLE analytics.scenario(scenario_id uuid PRIMARY KEY, lc_id uuid NOT NULL, master_version_id uuid NOT NULL, observation_batch_id uuid, model_version text NOT NULL, parameters jsonb NOT NULL, input_hash text NOT NULL, created_by text NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE analytics.appraisal_result(scenario_id uuid PRIMARY KEY REFERENCES analytics.scenario, metrics jsonb NOT NULL, warnings jsonb NOT NULL, completed_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE planning.portfolio(portfolio_id uuid PRIMARY KEY, budget_rupees numeric CHECK(budget_rupees>=0), budget_basis text CHECK(budget_basis IN ('capital','lifecycle')), policy_snapshot jsonb NOT NULL, solver_status text NOT NULL, model_version text NOT NULL, created_at timestamptz DEFAULT now());
CREATE TABLE planning.selection(portfolio_id uuid REFERENCES planning.portfolio, lc_id uuid NOT NULL, alternative_id uuid NOT NULL, scenario_id uuid NOT NULL, PRIMARY KEY(portfolio_id,lc_id));
CREATE TABLE planning.audit_event(event_id uuid PRIMARY KEY, entity_type text NOT NULL, entity_id uuid NOT NULL, actor text NOT NULL, action text NOT NULL, timestamp timestamptz DEFAULT now(), detail jsonb NOT NULL);
-- Cross-service UUIDs intentionally lack cross-schema FKs; validate via owner APIs.
