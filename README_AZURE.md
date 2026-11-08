# CivicSignal – Azure deployment notes

## Target services
- Azure Database for MySQL Flexible Server: relational data.
- Azure Blob Storage: private evidence image storage.
- Azure App Service (or another approved Python host): Flask web application.
- Azure Key Vault / App Service settings: production secrets.

## MySQL setup
1. Create an Azure Database for MySQL Flexible Server.
2. Create database `civicsignal` and a least-privilege application DB user.
3. Restrict networking to the application host and approved developer IPs.
4. Require TLS for database connections.
5. Run `database/schema.sql` against the database.
6. Set `DATABASE_URL` in the hosting environment, for example:
   `mysql+pymysql://USER:PASSWORD@HOST:3306/civicsignal?ssl_ca=/path/to/ca.pem`
   Use the CA certificate and TLS settings required by your Azure server configuration.
7. Never commit this connection string.

## Blob Storage setup
1. Create a Storage Account.
2. Create a private container named `civic-evidence`.
3. Keep anonymous/public blob access disabled.
4. Grant the app identity only the required Blob Data Contributor permissions, or use a restricted connection string stored in Key Vault.
5. Configure `AZURE_STORAGE_CONNECTION_STRING` and `AZURE_STORAGE_CONTAINER`.
6. Use `azure/blob_storage.py` from a route that first verifies the logged-in user's role and complaint ownership/assignment.
7. Store blob name/container in the Evidence table. Generate short-lived read SAS URLs only after authorization; do not make the container public.

## App Service
- Configure Python runtime and startup command: `gunicorn app:app`
- Add environment variables in App Service Configuration / Key Vault references.
- Set `FLASK_SECRET_KEY` to a strong random secret.
- Set `COOKIE_SECURE=true`.
- Enable HTTPS-only and secure headers.
- Configure logs and health monitoring.
- Test database connectivity and image upload after deployment.

## Important
The code in this folder is an integration helper, not a completed Azure deployment. You must create the Azure resources, configure credentials and test connectivity in your own subscription. Never publish real user data or secrets in the academic repository.
