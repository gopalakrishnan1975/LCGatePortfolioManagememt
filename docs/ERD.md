# Entity relationship diagram
Author: R. Gopalakrishnan | Production target; current runtime uses JSON and stateless services.

```mermaid
erDiagram
 SECTION ||--o{ LC : contains
 LC ||--o{ ALTERNATIVE : offers
 MASTER_VERSION ||--o{ LC : versions
 LC ||--o{ OBSERVATION_BATCH : measures
 OBSERVATION_BATCH ||--o{ ROAD_BIN : records
 OBSERVATION_BATCH ||--o{ GATE_EVENT : records
 LC ||--o{ SCENARIO : evaluates
 SCENARIO ||--|| APPRAISAL_RESULT : produces
 PORTFOLIO ||--o{ PORTFOLIO_SELECTION : includes
 ALTERNATIVE ||--o{ PORTFOLIO_SELECTION : selected
 SCENARIO ||--o{ PORTFOLIO_SELECTION : supports
 MASTER_VERSION {
 uuid version_id PK
 string status
 string checksum
 }
 LC {
 uuid lc_id PK
 uuid version_id FK
 uuid section_id FK
 string gate_number
 }
 SCENARIO {
 uuid scenario_id PK
 uuid lc_id FK
 uuid observation_batch_id FK
 json parameters
 string model_version
 }
```

Relationships across service boundaries are logical references and must not require distributed foreign-key writes. LC versions use composite (lc_id,version_id) keys. A scenario fixes its LC/master version and input snapshot. Retain is implicit in current optimizer; production stores an explicit retain alternative with zero incremental benefit and cost.
