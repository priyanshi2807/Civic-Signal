# CivicSignal frontend

These are the browser templates and static assets for the Flask starter.

## Add to your existing repository
Copy `templates/` and `static/` into the same directory as `app.py`. Then apply the route additions in `backend_page_routes_patch.txt` to `app.py` (or ask for a merged app.py). The frontend calls the existing JSON endpoints.

## Current limitations
- This is a connected academic MVP UI, not a production-ready release.
- Staff accounts must be created by an administrator/database seed; public registration only creates citizen accounts.
- Admin assignment asks for the existing staff numeric user ID.
- Evidence uploads and Azure Blob Storage UI are not yet implemented.
- Add CSRF protection, rate limiting, server-side state-transition rules and automated tests before deployment.
