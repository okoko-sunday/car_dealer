# Deployment: Vercel, Railway, PostgreSQL, and R2

## Railway backend

Create a Railway project with PostgreSQL plus two services from this repository using the root `Dockerfile`.

- Web start command: `python manage.py migrate && gunicorn showroom.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --access-logfile -`
- Worker start command: `while true; do python manage.py process_outbox --limit 100; sleep 10; done`
- Health path: `/health/`

Set `DEBUG=0`, a generated `SECRET_KEY`, Railway's `DATABASE_URL`, `DB_SSLMODE=require`, API `ALLOWED_HOSTS`, Vercel origins in `CORS_ALLOWED_ORIGINS`, `PUBLIC_API_URL`, and marketplace credentials. Run only one migration command during a release when scaling beyond the first web instance.

## Cloudflare R2

Create a private R2 bucket and API token. Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_ENDPOINT_URL`, `AWS_S3_REGION_NAME=auto`, and optionally an approved `AWS_S3_CUSTOM_DOMAIN`. With no bucket variable, Django deliberately uses development filesystem storage.

Configure lifecycle/retention, CORS, upload scanning, responsive derivatives, and CDN cache rules before real dealer media is accepted. The database stores keys and ordering, not durable media bytes.

## Vercel frontend

Create a Vercel project whose Root Directory is `frontend`. Set:

- `NEXT_PUBLIC_API_URL=https://<railway-api-domain>`
- `API_INTERNAL_URL=https://<railway-api-domain>`
- Do not set `DEALER_HOST_OVERRIDE` in production.

Add each verified dealer-owned domain to the same Vercel project and add the exact hostname as a `DealerDomain` row. DNS points to Vercel; the incoming host selects branding and inventory. The API still enforces dealer membership rather than trusting the UI.

## Security and operations

Use separate secrets per environment, rotate marketplace/R2 credentials, require HTTPS, enable Railway/PostgreSQL backups with restore drills, centralize logs and error reporting, and restrict Django admin. The Next server keeps staff tokens in Secure, HTTP-only, SameSite=Lax cookies; browser JavaScript never receives the token. Rate limits should also be enforced at Vercel/Railway's edge for distributed production traffic.
