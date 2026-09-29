# Multi-dealer showroom platform

`documentation.md` is the product source of truth. This repository contains one reusable dealer website product; the future marketplace remains a separate project and deployment.

## Technology

- `frontend/`: Next.js 16, React, and strict TypeScript. Designed for Vercel and custom dealer domains.
- Django 5.2 modular monolith with Django REST Framework. Designed for Railway.
- PostgreSQL in Docker Compose and production. SQLite remains available only for quick backend-only development.
- Cloudflare R2/S3-compatible production media through `django-storages`; local media in development.
- Database-backed transactional outbox and a separate worker process. Redis is not required.

## Run the complete system

Docker Desktop/Engine must be running. From `/home/l2euser/cars`:

```bash
docker compose up --build
```

The first start creates PostgreSQL, applies migrations, and loads clearly labelled development fixtures. Open:

- Next.js dealer website: http://localhost:3000
- Dealer login: http://localhost:3000/dashboard/login
- Django REST API: http://localhost:8001/api/v1/site/ (tenant header normally comes from Next.js)
- Django administration/API fallback: http://localhost:8001/admin/

Development login:

```text
username: owner
password: demo-pass-2026
```

The React dashboard can change prices, website publication, availability, appointment workflow, and offer decisions. The worker sends database-backed marketplace events every ten seconds.

Stop without deleting data:

```bash
docker compose down
```

Delete development containers and PostgreSQL/media volumes only when you intentionally want a clean database:

```bash
docker compose down --volumes
```

If port 3000 or 8001 is occupied, stop the process using it before starting Compose. `docker compose ps` shows service health.

## Run checks

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py test
cd frontend
npm install
npm run typecheck
npm run build
```

The test suite covers tenant isolation, roles, publication boundaries, offers, out-of-order/duplicate events, visibility ownership, withdrawals, and DRF authentication. The production Next build validates server and client TypeScript.

## Multi-domain development

Production requests use their incoming hostname. Next forwards it as `X-Dealer-Host`; Django resolves the unique `DealerDomain` and independently re-checks membership on private operations. `DEALER_HOST_OVERRIDE=atelier.localhost` gives Docker a predictable development tenant. Remove that override in Vercel.

For two local dealers, add `DealerDomain` rows such as `atelier.localhost` and `second.localhost`, remove the override, then visit `http://atelier.localhost:3000` and `http://second.localhost:3000`. Browsers resolve `*.localhost` to loopback without owning domains.

## Marketplace delivery

Dealer changes and immutable versioned events commit in one PostgreSQL transaction. The worker POSTs signed events with stable IDs and retries failed records with exponential backoff. Without `MARKETPLACE_WEBHOOK_URL`, it writes to the local simulator. Marketplace review/visibility remains separate and cannot be changed by dealer staff. See [`docs/marketplace-contract.md`](docs/marketplace-contract.md).

## Deployment

See [`docs/deployment.md`](docs/deployment.md) and [`.env.example`](.env.example). Never commit actual credentials.
