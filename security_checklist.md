# CivicSignal Security Checklist

| Control | Status | Evidence / next action |
|---|---|---|
| Password hashing | Implemented | Werkzeug password hash |
| Role-based access | Partially implemented | Test all citizen/staff/admin routes |
| Object ownership checks | Implemented on complaint reads/verification | Add automated negative tests |
| HTTPS | Deployment pending | Enable TLS on cloud host |
| Secrets outside repository | Configuration prepared | Create private `.env`; use cloud secret store |
| SQL injection defense | ORM used | Review any future raw SQL |
| XSS protection | Pending UI | Escape all user-controlled output; CSP |
| CSRF protection | Pending | Add tokens to cookie-authenticated browser forms |
| Login rate limiting | Pending | Configure Flask-Limiter |
| Upload validation | Pending | MIME/type/size validation and safe Blob upload |
| Database firewall | Pending | Restrict to application network |
| Activity log | Implemented baseline | Test log coverage and restrict access |
| Data minimization | Planned | Use synthetic demo data only |
| Backup/recovery | Pending | Configure and document restore test |
| Dependency review | Pending | Pin and scan dependencies before deployment |
