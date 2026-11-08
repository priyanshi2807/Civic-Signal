# CivicSignal – Design Document

## 1. Overview
CivicSignal centralizes civic issue reporting, municipal assignment, repair updates and resolution verification.

## 2. Actors
- Citizen: submits complaints, tracks them and verifies repair outcome.
- Municipal staff: sees assigned work, updates progress and submits repair evidence.
- Administrator: manages assignments, monitors system activity and reviews analytics.

## 3. Functional requirements
1. Citizens can register and authenticate.
2. Citizens can submit a complaint with category, description and location.
3. The system generates a unique tracking code.
4. Citizens can view only their own complaints.
5. Administrators can assign complaints to staff.
6. Staff can view only complaints assigned to them.
7. Staff can update complaint status and add repair notes.
8. Citizens can confirm a repair or report that the issue remains unresolved.
9. The system records status history and important user activity.
10. Administrators can view complaint statistics by status and category.

## 4. Non-functional requirements
- Security: hashed passwords, role checks, parameterized ORM operations, HTTPS in production.
- Performance: indexes on status, category, reporter and assignment lookup fields.
- Availability: cloud-hosted deployment with database backups configured.
- Usability: responsive interfaces and clear complaint status labels.
- Maintainability: separate data models, route modules and documentation.
- Privacy: dummy/public data only for the academic demonstration.

## 5. Architecture
Three-tier modular monolith:
1. Presentation tier: browser interface for citizen, staff and administrator.
2. Application tier: Flask routes, authentication, authorization and workflow rules.
3. Data tier: Azure-hosted MySQL for relational records; Blob Storage for uploaded evidence.

Flow: Browser -> HTTPS -> Flask REST API -> validation/RBAC -> MySQL. Evidence upload is validated by the API and stored in Blob Storage; only its storage reference and metadata are stored in MySQL.

## 6. Trade-off
A modular monolith is selected over microservices. It reduces deployment and operational complexity for a two-student academic team and a short deadline. Modules remain separated so they can be extracted into services if scale and independent deployment needs justify that later.

## 7. Initial API design
See README.md. All protected routes require an authenticated session and role/ownership checks.

## 8. Data model
Users 1—N Complaints; Categories 1—N Complaints; Complaints 1—N Assignments; Complaints 1—N StatusHistory; Complaints 1—N Evidence; Complaints 1—N Verifications. Users are referenced as reporter, staff, assigner, actor and verifier.

## 9. Data classification
- Public: category labels and public help text.
- Internal: complaint descriptions, locations, status history and operational metrics.
- Sensitive: user email, password hash, account identifiers and precise complaint location if it identifies a person. Restrict access; never use real personal data in the demo.
- Secrets: database passwords, Flask secret and cloud keys. Keep in environment/managed secret storage; never commit them.

## 10. Risks and mitigations
See threat_model.md and security_checklist.md.
