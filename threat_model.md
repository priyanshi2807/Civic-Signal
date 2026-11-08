# CivicSignal – One-page Threat Model

## Assets
User accounts, complaint records, location details, uploaded evidence, staff assignments, verification records, database credentials and cloud resources.

## Trust boundaries
1. Public browser to HTTPS application.
2. Citizen/staff/admin role boundary inside the application.
3. Flask application to Azure MySQL.
4. Flask application to Azure Blob Storage.
5. Developer workstation/Git repository to cloud deployment.

## Threats and mitigations
| Threat | Impact | Mitigation |
|---|---|---|
| SQL injection | Data disclosure/modification | ORM/parameterized queries; validate inputs |
| Cross-site scripting | Session theft or malicious actions | Escape output; avoid unsafe HTML; CSP in deployment |
| Broken access control | Citizens see others' complaints | Role checks plus owner/assignee checks on every object |
| Credential theft | Account takeover | Strong password hashing, HTTPS, rate limiting, secure cookies |
| Secret leakage | Cloud/database compromise | Environment variables or managed secrets; ignore `.env`; rotate leaked keys |
| Malicious file upload | Malware/storage abuse | Allowlist image types, size limits, content inspection, randomized object names |
| CSRF | Unauthorized browser actions | CSRF tokens for cookie-authenticated state-changing forms |
| Data exposure | Privacy harm | Least privilege, data minimization, TLS, restricted database network access |
| False repair evidence | Incorrect resolution | Before/after evidence, citizen verification, immutable status history |
| Abuse/complaint spam | Operational overload | Rate limits, validation, audit logs and admin review |

## Residual risks
This academic starter does not yet implement a production file scanning pipeline, full CSRF integration for every API route, authentication rate limiting, alerting or backup recovery testing. These must be completed and tested before public deployment.
