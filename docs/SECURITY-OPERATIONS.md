# Security operations

## Before deployment

- Set a random `SECRET_KEY` (32+ characters) and a strong owner password.
- Keep `AUTO_CREATE_TABLES=false` in production.
- Use HTTPS behind the reverse proxy.
- Restrict direct access to the backend and database to the private network/reverse proxy.
- Configure `CORS_ORIGINS` to the exact frontend origin(s).
- Keep media and PostgreSQL volumes on persistent storage.
- Configure optional Turnstile and SMTP only with server-side secrets.

## Owner/IP workflow checks

The production system must preserve this chain:

`public idea → request → identity → exact agreement snapshot → site-terms snapshot → typed acceptance → owner review → permission grant → restricted link → access audit → expiry/revocation`.

Do not bypass the owner approval route to grant restricted access.

## Recovery

1. Stop or isolate the application if required.
2. Preserve the current PostgreSQL volume and application logs.
3. Verify the latest gzip backup with `ops/verify-postgres-backup.sh`.
4. Restore to a disposable database first for validation.
5. Run `alembic upgrade head` against the restored database.
6. Verify the health/readiness endpoints.
7. Test admin login, one public page, one private content record, one collaboration request, and permission revocation.

## Evidence retention

Agreement acceptance records and content revisions should not be manually edited or deleted through application endpoints. Database-level retention and legal hold requirements should be handled separately according to the owner's applicable legal/compliance obligations.
