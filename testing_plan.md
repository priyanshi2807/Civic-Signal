# CivicSignal – Test Plan and Test Cases

## Test environment
- Python 3.11+
- Flask application running locally
- SQLite for quick development smoke tests; MySQL 8+ for RDBMS acceptance tests
- Synthetic accounts and complaint data only
- Separate citizen, staff and admin test accounts

## Test cases

| ID | Scenario | Expected result |
|---|---|---|
| TC01 | GET `/api/health` | HTTP 200 and database connected |
| TC02 | Register valid citizen | HTTP 201 |
| TC03 | Register duplicate email | HTTP 409 |
| TC04 | Register password shorter than 10 chars | HTTP 400 |
| TC05 | Login with valid credentials | HTTP 200 and role returned |
| TC06 | Login with wrong password | HTTP 401 |
| TC07 | Citizen submits valid complaint | HTTP 201 and tracking code |
| TC08 | Citizen omits required complaint field | HTTP 400 |
| TC09 | Citizen lists complaints | Only their own complaints returned |
| TC10 | Citizen requests another user's complaint | HTTP 403 |
| TC11 | Citizen calls admin analytics | HTTP 403 |
| TC12 | Admin assigns complaint to staff user | HTTP 200 |
| TC13 | Admin assigns to a citizen account | HTTP 404 / rejected |
| TC14 | Assigned staff updates complaint status | HTTP 200 |
| TC15 | Unassigned staff updates complaint | HTTP 403 |
| TC16 | Citizen verifies resolved complaint | Status becomes verified or reopened |
| TC17 | Verify complaint not in resolved state | HTTP 409 |
| TC18 | Admin analytics endpoint | Counts grouped by status/category |
| TC19 | Oversized request body | HTTP 413 |
| TC20 | Evidence upload with unsupported extension | Rejected before storage |

## Manual test sequence
1. Register two citizen accounts.
2. Provision one staff account and one admin account using a controlled seed script or admin process.
3. Log in as citizen A and create a complaint.
4. Confirm citizen A can see it and citizen B cannot.
5. Log in as admin and assign the complaint to staff.
6. Log in as assigned staff and change status to `in_progress`, then `resolved`.
7. Log in as citizen A and submit `confirmed_fixed`.
8. Confirm the status becomes `verified` and history contains each transition.
9. Log in as admin and inspect analytics.
10. Repeat with `still_unresolved` and confirm the complaint becomes `reopened`.

## Evidence to capture
- Screenshots of registration/login and each role dashboard.
- API request/response screenshots with test accounts.
- SQL output showing table rows, foreign keys, joins and grouped analytics.
- Azure database configuration (hide server secrets).
- Private Blob container configuration and one sample upload.
- Test execution log with pass/fail results.

## Release gate
Do not claim a test passed until it has actually been executed and its result recorded. Replace planned status with actual evidence in the final report.
