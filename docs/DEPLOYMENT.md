# Deployment guide

## Development

Copy `.env.example` to `.env`, change the owner credentials and secret, then run `docker compose up --build`.

## Production platform setup

### GitHub

1. Push the repo to GitHub and keep the default branch as `main`.
2. Enable branch protection if you want review gates before deploys.
3. Keep `.env`, `.env.production`, and any local secrets out of Git; use the dashboard environment editors on each platform instead.

### Vercel frontend deployment

1. Import the repo into Vercel.
2. Set the project root to `/frontend`.
3. Framework preset: Next.js.
4. Build command: `npm run build`
5. Output directory: `.next` (default for Next.js)
6. Production environment variables:
	- `NEXT_PUBLIC_SITE_URL=https://your-frontend-domain.com`
	- `NEXT_PUBLIC_API_URL=https://your-backend-domain.up.railway.app/api/v1`
	- `NEXT_PUBLIC_TURNSTILE_SITE_KEY=` (optional)
7. Add the same values in Vercel's preview environment if needed.
8. Ensure no `localhost` or Docker hostnames remain in production env values.

### Railway backend deployment

1. Create a new Railway project and add a new service for the backend.
2. Keep the Railway service root/build context at the repository root. The backend image uses `backend/Dockerfile` while copying the root `alembic.ini` and backend sources.
3. Add a PostgreSQL service and keep the generated `DATABASE_URL` for the backend service.
4. Use the production runtime settings in `.env.production.example` as the reference for the dashboard environment variables.
5. Configure the service to use `backend/Dockerfile`, or set the root Dockerfile path to `backend/Dockerfile`; do not use `backend` as the build context.
6. Set the port to use the `PORT` environment variable; the script already does `uvicorn ... --port ${PORT}`.
7. Production backend env keys:
	- `ENVIRONMENT=production`
	- `DATABASE_URL=<Railway Postgres URL>`
	- `SECRET_KEY=<32+ random chars>`
	- `OWNER_EMAIL=owner@example.com`
	- `OWNER_PASSWORD=<strong password>`
	- `CORS_ORIGINS=https://your-frontend-domain.com`
	- `AUTO_CREATE_TABLES=false`
	- `STORAGE_DRIVER=s3`
	- `S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com`
	- `S3_BUCKET=<bucket-name>`
	- `S3_REGION=auto`
	- `S3_ACCESS_KEY=<R2 access key>`
	- `S3_SECRET_KEY=<R2 secret key>`
	- `PUBLIC_SITE_URL=https://your-frontend-domain.com`
	- `INTERNAL_API_URL=https://your-backend-domain.up.railway.app/api/v1`
8. Use the repo's Alembic flow for first deploys: run `alembic upgrade head` once the database is reachable.

### Cloudflare R2-compatible object storage

1. Create an R2 bucket in Cloudflare.
2. Create an API token with object read/write permissions for that bucket.
3. Set `S3_ENDPOINT_URL` to the bucket endpoint in the format `https://<account-id>.r2.cloudflarestorage.com`.
4. Set `S3_BUCKET` to the bucket name and `S3_REGION=auto`.
5. Set `STORAGE_DRIVER=s3` in production.
6. Keep the bucket private unless a specific public asset needs public access; the app can still generate signed URLs for protected media.

### Production runtime notes

1. The backend runs Alembic before startup when `AUTO_CREATE_TABLES=false`.
2. The port is supplied by Railway via `PORT`; do not hard-code `localhost` or Docker service names in production values.
3. The frontend should never call `http://localhost:8000` in production; only the public HTTPS backend URL belongs in `NEXT_PUBLIC_API_URL`.
4. Request all public-facing URLs through HTTPS; `CORS_ORIGINS` must match the deployed frontend domain exactly.
5. Keep the database, media bucket, and backups on durable storage; avoid storing media in ephemeral filesystem mounts.
6. Schedule `ops/backup-postgres.sh` and validate the backup with `ops/verify-postgres-backup.sh` before relying on it for a restore drill.

## Production

1. Copy `.env.production.example` to a local production env file only for non-committed local testing.
2. Set a random `SECRET_KEY`, a strong owner password, and a strong PostgreSQL password.
3. Use the platform dashboard environment editors to set the actual values for Vercel and Railway; do not commit credentials.
4. Use `docker compose -f docker-compose.production.yml up -d --build` only for a local production-like smoke test.
5. The backend container runs `alembic upgrade head` before starting when `AUTO_CREATE_TABLES=false`.
6. Put a TLS reverse proxy (Caddy, Nginx, a managed load balancer, or your hosting provider) in front of ports 3000/8000 only for a self-hosted environment. Vercel and Railway manage their own edge/TLS layers for their hosted services.
7. Keep database and media volumes on persistent storage.
8. Schedule backup verification as noted above.

## Production validation

Check:

- `GET /api/v1/health/live` for process liveness.
- `GET /api/v1/health/ready` for database readiness.
- The public homepage, a published project, a research detail page, an idea page and collaboration form.
- Admin login, CSRF-protected mutation, agreement versioning, request approval, permission grant, restricted link, and revocation.
- Resume generation and media delivery.

Do not mark the system production-ready until the deployed environment also passes browser-level QA, TLS verification, backups/restore testing, and legal review of the agreement text.
