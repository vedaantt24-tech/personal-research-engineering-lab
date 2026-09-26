# Oracle Cloud Always Free deployment

This is the deployment runbook for the existing application on an Oracle ARM64 Always Free VM. The repository uses architecture-neutral base images and does not require `platform:` overrides.

## 1. Oracle VM and firewall

Create an Ampere A1 VM with Ubuntu 22.04 or newer. Attach a persistent boot volume sized for the database and backups. In the Oracle VCN security list or NSG, allow only:

- TCP 80 from `0.0.0.0/0` and `::/0`
- TCP 443 from `0.0.0.0/0` and `::/0`
- TCP 22 only from your administration IP, if remote SSH is required

Do not allow TCP 5432, 3000, or 8000 from the public internet. The production Compose file binds the application services to loopback and PostgreSQL has no host port mapping.

On the VM, apply the matching Ubuntu firewall rules:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from YOUR_ADMIN_IP to any port 22 proto tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

## 2. Install and checkout

Install Docker Engine and the Compose plugin using Docker's official Ubuntu instructions. Add the deployment user to the Docker group, then log in again. Clone the GitHub repository and stay on `main`:

```bash
git clone https://github.com/vedaantt24-tech/personal-research-engineering-lab.git
cd personal-research-engineering-lab
git checkout main
```

Do not copy `.env` from a development machine. Create it only on the VM:

```bash
cp .env.production.example .env
chmod 600 .env
```

## 3. Production environment

Set real values in `.env` on the VM only:

```dotenv
ENVIRONMENT=production
DATABASE_URL=postgresql+psycopg://postgres:CHANGE_ME@db:5432/personal_lab
POSTGRES_DB=personal_lab
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME
SECRET_KEY=CHANGE_ME_TO_32_PLUS_RANDOM_CHARACTERS
OWNER_EMAIL=CHANGE_ME
OWNER_PASSWORD=CHANGE_ME
AUTO_CREATE_TABLES=false
CORS_ORIGINS=https://www.example.com
PUBLIC_SITE_URL=https://www.example.com
INTERNAL_API_URL=http://frontend-backend-routing-is-not-used
NEXT_PUBLIC_API_URL=https://api.example.com/api/v1
NEXT_PUBLIC_SITE_URL=https://www.example.com
STORAGE_DRIVER=s3
S3_ENDPOINT_URL=https://ACCOUNT_ID.r2.cloudflarestorage.com
S3_BUCKET=private-media
S3_REGION=auto
S3_ACCESS_KEY=CHANGE_ME
S3_SECRET_KEY=CHANGE_ME
```

For the Compose deployment, set `INTERNAL_API_URL=http://backend:8000/api/v1` because server-rendered frontend requests use the private Compose network. `NEXT_PUBLIC_API_URL` is the public API URL used by browser requests and must never be a Docker hostname or localhost.

## 4. Start and migrate

From the repository root:

```bash
docker compose -f docker-compose.production.yml config
docker compose -f docker-compose.production.yml up -d --build
docker compose -f docker-compose.production.yml ps
```

The backend entrypoint runs `alembic upgrade head` before Uvicorn when `AUTO_CREATE_TABLES=false`. This is an in-place migration path. Never use `docker compose down -v`; named volumes contain the database and media.

Health checks:

```bash
curl -fsS https://api.example.com/api/v1/health/live
curl -fsS https://api.example.com/api/v1/health/ready
curl -fsS https://www.example.com/
```

## 5. Caddy and Cloudflare DNS

Install Caddy on the VM and copy `ops/Caddyfile.example` to `/etc/caddy/Caddyfile`. Replace the example hostnames:

```caddy
www.example.com {
    encode gzip
    reverse_proxy 127.0.0.1:3000
}

api.example.com {
    encode gzip
    reverse_proxy 127.0.0.1:8000
}
```

Create Cloudflare DNS records:

- `www` CNAME to the VM public hostname, proxied
- `api` CNAME to the VM public hostname, proxied
- Optional apex record according to the domain registrar setup, proxied

Point the domain to Cloudflare nameservers first. Keep Cloudflare SSL/TLS mode at `Full (strict)` after Caddy obtains a valid certificate. Caddy handles certificates and redirects HTTP to HTTPS. Do not expose the backend or frontend ports directly through Cloudflare DNS.

## 6. Private R2 media

Create a private R2 bucket and an API token scoped to that bucket with object read/write access. Set the `S3_*` values above. Do not add R2 keys to GitHub Actions, the repository, or frontend `NEXT_PUBLIC_*` variables. The backend uses signed URLs for protected media.

## 7. Backups and restore drills

Create a backup directory on a separate persistent volume when possible:

```bash
sudo mkdir -p /srv/personal-lab/backups
sudo chown "$USER":"$USER" /srv/personal-lab/backups
POSTGRES_CONTAINER=$(docker compose -f docker-compose.production.yml ps -q db) \\
BACKUP_DIR=/srv/personal-lab/backups \\
sh ops/backup-postgres.sh
```

Verify gzip integrity without modifying the database:

```bash
POSTGRES_CONTAINER=$(docker compose -f docker-compose.production.yml ps -q db) \\
BACKUP_FILE=/srv/personal-lab/backups/personal-lab-YYYYMMDDTHHMMSSZ.sql.gz \\
sh ops/verify-postgres-backup.sh
```

For a restore drill, use a separate temporary PostgreSQL instance or VM. Never restore over the production volume without a tested backup, a maintenance window, and an explicit operator decision.

## 8. Release checks

Before calling the release live, verify public/private/confidential visibility, the idea agreement and permission workflow, restricted-link revocation, audit logging, investor and funding request records, social links, admin login, media upload/download, and both health endpoints. Do not create sample content or fake analytics to satisfy these checks.
