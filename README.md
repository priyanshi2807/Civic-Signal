# CivicSignal

CivicSignal is a civic issue reporting and resolution-verification application.

## Team
- Student 1: [Name: Priyanshi Nigam / UID-25lbcs3054]
- Student 2: [Name: Shaan Srivastava / UID-25lbcs3026]

## Stack
- Frontend: HTML, CSS, JavaScript, Bootstrap (UI implementation milestone)
- Backend: Python Flask REST API
- RDBMS: MySQL 8+
- Cloud target: Azure Database for MySQL + Azure Blob Storage
- Analytics: SQL aggregation and dashboard

## Current implementation
This starter contains:
- Citizen registration and login with hashed passwords
- Session-based authentication
- Citizen complaint submission and complaint listing
- Admin assignment of complaints to staff
- Staff status updates
- Citizen/admin resolution verification and reopening
- Role checks and activity logging
- Analytics endpoint for administrators
- MySQL schema with seven core domain tables plus activity logs, indexes, a view, stored procedure and query examples

## Run locally
1. Install Python 3.11 or later.
2. Create a virtual environment:
   `python -m venv .venv`
3. Activate it and install dependencies:
   `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and set a strong `FLASK_SECRET_KEY`.
5. For the fastest local test, set:
   `DATABASE_URL=sqlite:///civicsignal.db`
6. Run:
   `python app.py`
7. Open `http://127.0.0.1:5000/`.

The app creates its development tables and starter categories on first run. For MySQL, create the database and run `database/schema.sql`, then set `DATABASE_URL` to the MySQL connection string. The ORM model and SQL schema are the two representations of the same initial domain; validate them together before deployment.

## API overview
| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/api/health` | Public | Health check |
| POST | `/api/auth/register` | Public | Citizen registration |
| POST | `/api/auth/login` | Public | Login |
| POST | `/api/auth/logout` | Authenticated | Logout |
| GET | `/api/me` | Authenticated | Current user |
| GET | `/api/categories` | Public | Complaint categories |
| POST | `/api/complaints` | Citizen | Submit complaint |
| GET | `/api/complaints` | Authenticated | List permitted complaints |
| GET | `/api/complaints/<id>` | Authorized owner/assignee/admin | Complaint details |
| POST | `/api/complaints/<id>/assign` | Admin | Assign staff |
| PATCH | `/api/complaints/<id>/status` | Staff/Admin | Update status |
| POST | `/api/complaints/<id>/verify` | Complaint owner/Admin | Verify or reopen |
| GET | `/api/admin/analytics` | Admin | Aggregate analytics |

## Example API payloads
Registration:
```json
{"full_name":"Demo Citizen","email":"citizen@example.test","password":"ChangeThisPassword123!"}
```
Login:
```json
{"email":"citizen@example.test","password":"ChangeThisPassword123!"}
```
Complaint:
```json
{"category_id":1,"title":"Pothole near bus stop","description":"Large pothole on the road.","location_text":"Sector 15, sample city","priority":"high"}
```
Assignment:
```json
{"staff_id":2,"note":"Please inspect and repair."}
```
Status:
```json
{"status":"resolved","note":"Repair completed; evidence should be attached in the next milestone."}
```
Verification:
```json
{"result":"still_unresolved","comment":"The pothole is still present."}
```

## Important next steps
- Add HTML templates and browser forms for all three roles.
- Implement secure image upload to Azure Blob Storage; do not accept arbitrary external blob URLs from users.
- Add CSRF protection to browser form flows and rate limiting to authentication endpoints.
- Add admin/staff provisioning (public registration intentionally creates citizens only).
- Add state-transition validation and tests.
- Configure HTTPS, production secret management and Azure database network restrictions.
- Complete the data-classification report, threat model, security checklist, analytics report and deployment evidence.

## Security notes
- Never commit `.env`, credentials, real personal data or production connection strings.
- The development fallback secret is not suitable for deployment.
- Use dummy/public data only.
- This starter is a development baseline, not a production-certified system.
- Declare AI assistance and ensure both students understand and can explain every submitted component, as required by the course guide.
