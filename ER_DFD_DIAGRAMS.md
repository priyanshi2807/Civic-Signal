# CivicSignal – ER Diagram and DFDs

## ER diagram (Mermaid)

```mermaid
erDiagram
    USERS ||--o{ COMPLAINTS : reports
    CATEGORIES ||--o{ COMPLAINTS : classifies
    COMPLAINTS ||--o{ ASSIGNMENTS : receives
    USERS ||--o{ ASSIGNMENTS : assigned_staff
    USERS ||--o{ ASSIGNMENTS : assigns
    COMPLAINTS ||--o{ STATUS_HISTORY : tracks
    USERS ||--o{ STATUS_HISTORY : changes
    COMPLAINTS ||--o{ EVIDENCE : has
    USERS ||--o{ EVIDENCE : uploads
    COMPLAINTS ||--o{ VERIFICATIONS : receives
    USERS ||--o{ VERIFICATIONS : verifies
    USERS ||--o{ ACTIVITY_LOGS : performs

    USERS {
      bigint user_id PK
      varchar full_name
      varchar email UK
      varchar password_hash
      enum role
      boolean is_active
    }
    CATEGORIES {
      bigint category_id PK
      varchar category_name UK
      varchar description
    }
    COMPLAINTS {
      bigint complaint_id PK
      varchar tracking_code UK
      bigint reporter_id FK
      bigint category_id FK
      varchar title
      text description
      varchar location_text
      enum priority
      enum status
      timestamp created_at
    }
    ASSIGNMENTS {
      bigint assignment_id PK
      bigint complaint_id FK
      bigint staff_id FK
      bigint assigned_by FK
      timestamp assigned_at
    }
    STATUS_HISTORY {
      bigint history_id PK
      bigint complaint_id FK
      bigint changed_by FK
      varchar old_status
      varchar new_status
      timestamp changed_at
    }
    EVIDENCE {
      bigint evidence_id PK
      bigint complaint_id FK
      bigint uploaded_by FK
      varchar blob_url
      varchar evidence_type
    }
    VERIFICATIONS {
      bigint verification_id PK
      bigint complaint_id FK
      bigint verified_by FK
      enum result
      timestamp verified_at
    }
    ACTIVITY_LOGS {
      bigint log_id PK
      bigint actor_id FK
      varchar action
      varchar entity_type
      bigint entity_id
    }
```

## DFD Level 0 – Context diagram

```mermaid
flowchart LR
  Citizen[Citizen] -->|Complaint details, location, evidence| CS((CivicSignal))
  CS -->|Tracking code, status, outcome| Citizen
  Staff[Municipal Staff] -->|Work updates, repair evidence| CS
  CS -->|Assigned complaints| Staff
  Admin[Administrator] -->|Assignments, account actions| CS
  CS -->|Reports, analytics, audit information| Admin
  CS <--> DB[(Relational Database)]
  CS <--> Blob[(Private Blob Storage)]
```

## DFD Level 1 – Main processes

```mermaid
flowchart TB
  C[Citizen] --> P1((1.0 Authenticate User))
  P1 <--> U[(Users)]
  C --> P2((2.0 Submit Complaint))
  P2 <--> CAT[(Categories)]
  P2 --> D1[(Complaints)]
  P2 --> H[(Status History)]
  A[Administrator] --> P3((3.0 Assign Complaint))
  P3 --> AS[(Assignments)]
  S[Municipal Staff] --> P4((4.0 Update Repair))
  P4 --> D1
  P4 --> H
  P4 --> E[(Evidence Metadata)]
  P4 <--> B[(Private Blob Storage)]
  C --> P5((5.0 Verify Resolution))
  P5 --> V[(Verifications)]
  P5 --> H
  A --> P6((6.0 View Analytics))
  D1 --> P6
  AS --> P6
  P6 --> A
```

## DFD Level 2 – Complaint submission

```mermaid
flowchart TD
  C[Citizen] --> A[Validate session and citizen role]
  A --> B[Validate category, title, description and location]
  B -->|Invalid| X[Return validation error]
  B -->|Valid| D[Generate unique tracking code]
  D --> E[Insert complaint row]
  E --> F[Insert initial status history]
  F --> G[Commit database transaction]
  G --> H[Return complaint ID and tracking code]
```

## Notes for the report
- USERS has three roles: citizen, staff and admin.
- A complaint belongs to exactly one reporter and one category.
- A complaint may have multiple assignment records over time.
- Status history records each workflow transition.
- Evidence binaries live in private Blob Storage; the relational database stores metadata and storage references.
- Analytics are derived from relational complaint, assignment and status data.
