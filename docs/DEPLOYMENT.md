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
	- `NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api/v1`
	- `NEXT_PUBLIC_TURNSTILE_SITE_KEY=` (optional)
7. Add the same values in Vercel's preview environment if needed.
8. Ensure no `localhost` or Docker hostnames remain in production env values.

### Render backend deployment

1. Create a Render Web Service from the GitHub repository.
2. Set the service root directory to `backend` and use Python/FastAPI with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3. Create or connect a Neon PostgreSQL database and set its pooled `DATABASE_URL` on Render.
4. Use the production runtime settings in `.env.production.example` as the reference for the dashboard environment variables.
5. Set the Render health check path to `/api/v1/health/ready`.
6. Set the port to use the `PORT` environment variable; `backend/entrypoint.sh` supports it for container deployments.
7. Production backend env keys:
	- `ENVIRONMENT=production`
	- `DATABASE_URL=<Neon Postgres URL>`
	- `SECRET_KEY=<32+ random chars>`
	- `OWNER_EMAIL=owner@example.com`
	- `OWNER_PASSWORD=<strong password>`
	- `CORS_ORIGINS=https://your-frontend-domain.com`
	- `AUTO_CREATE_TABLES=false`
	- `STORAGE_DRIVER=s3`
	- `S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com`
	- `S3_BUCKET_NAME=<bucket-name>`
	- `S3_REGION=auto`
	- `S3_ACCESS_KEY_ID=<R2 access key>`
	- `S3_SECRET_ACCESS_KEY=<R2 secret key>`
	- `PUBLIC_SITE_URL=https://your-frontend-domain.com`
	- `INTERNAL_API_URL=https://your-render-service.onrender.com/api/v1`
8. Run `alembic -c alembic.ini upgrade head` from the backend service before enabling traffic; keep `AUTO_CREATE_TABLES=false`.

### Cloudflare R2-compatible object storage

1. Create an R2 bucket in Cloudflare.
2. Create an API token with object read/write permissions for that bucket.
3. Set `S3_ENDPOINT_URL` to the bucket endpoint in the format `https://<account-id>.r2.cloudflarestorage.com`.
4. Set `S3_BUCKET_NAME` to the bucket name and `S3_REGION=auto`.
5. Set `STORAGE_DRIVER=s3` in production.
6. Keep the bucket private unless a specific public asset needs public access; the app can still generate signed URLs for protected media.

### Production runtime notes

1. Run Alembic against Neon before the first Render deploy and after reviewed schema changes.
2. The port is supplied by Render via `PORT`; do not hard-code `localhost` or Docker service names in production values.
3. The frontend should never call `http://localhost:8000` in production; only the public HTTPS backend URL belongs in `NEXT_PUBLIC_API_URL`.
4. Request all public-facing URLs through HTTPS; `CORS_ORIGINS` must match the deployed frontend domain exactly.
5. Keep the database, media bucket, and backups on durable storage; avoid storing media in ephemeral filesystem mounts.
6. Schedule `ops/backup-postgres.sh` and validate the backup with `ops/verify-postgres-backup.sh` before relying on it for a restore drill.

## Production

1. Copy `.env.production.example` to a local production env file only for non-committed local testing.
2. Set a random `SECRET_KEY`, a strong owner password, and a strong PostgreSQL password.
3. Use the platform dashboard environment editors to set the actual values for Vercel and Render; do not commit credentials.
4. Use `docker compose -f docker-compose.production.yml up -d --build` only for a local production-like smoke test.
5. The backend container runs `alembic upgrade head` before starting when `AUTO_CREATE_TABLES=false`.
6. Put a TLS reverse proxy (Caddy, Nginx, a managed load balancer, or your hosting provider) in front of ports 3000/8000 only for a self-hosted environment. Vercel and Render manage their own edge/TLS layers for their hosted services.
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
