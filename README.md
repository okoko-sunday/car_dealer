# Dealer Showroom Platform

A reusable, multi-dealer website and staff workspace. The source brief is [`documentation.md`](documentation.md) and remains the product source of truth.

## Stack and boundaries

Django 5.2 supplies server-rendered, progressively enhanced pages, authentication, validation, migrations, and a mature ORM in one deployable application. SQLite keeps local setup tiny; `DATABASE_URL` switches production to PostgreSQL. WhiteNoise serves versioned static assets, while uploaded media is local only in development and must use object storage in production.

The `dealers` app currently contains the first vertical slice. Its code is divided into models (domain/persistence), forms (input validation), views and tenant-aware authorization, services (transactions/events), management commands (background delivery), and templates/static presentation. As the product grows, these modules can become separate Django apps without changing the public contract.

## Local setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py process_outbox
.venv/bin/python manage.py runserver
```

Open <http://atelier.localhost:8000/> (or <http://127.0.0.1:8000/?dealer=atelier-motors>). Dashboard login: `owner` / `demo-pass-2026`. These credentials and generated illustrations are development fixtures only.

Run checks with:

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py test
```

## Demonstration

1. Visit the homepage and inventory; cards come from persisted listings.
2. Sign in, open **Inventory**, edit a published car, and change its price.
3. Run `.venv/bin/python manage.py process_outbox`. In `/admin/dealers/marketplacelisting/`, its dealer-owned snapshot has the new price while visibility remains `Pending review` (or any admin-selected visibility).
4. Mark the car Sold and save, then process the outbox again. Its dealer site displays Sold and the simulator snapshot becomes Sold without changing the marketplace administrator's visibility choice.
5. Set Website publication to Unpublished. The delivered `vehicle.withdrawn.v1` forces simulator visibility to Withdrawn so the marketplace cannot continue advertising it publicly.

For continuous delivery, run `process_outbox` every minute through a platform scheduler. The web application remains available if delivery fails; failures, attempt counts, and errors are shown in the dashboard and retried with backoff.

## Production checklist

Use PostgreSQL, a strong `SECRET_KEY`, `DEBUG=0`, explicit `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`, HTTPS and secure cookies at the deployment edge. Configure S3-compatible private object storage plus image moderation/scanning, run `collectstatic`, schedule `process_outbox`, centralize logs/errors, rate-limit login and public forms at the proxy/application edge, and configure encrypted backups with restore drills. Add transactional email/SMS only after consent and retention policies are approved. The current release validates image type/size but production upload scanning and object storage are deliberately deployment responsibilities.

## Staff workflow and media controls

Buyer requests now support scheduled times, appointment outcomes, offer decisions, counteroffers, and staff notes. “Offer accepted” is intentionally a negotiation state and never marks a vehicle Sold. Every workflow update creates a tenant-scoped audit entry. Published vehicle image uploads, ordering changes, and removals increment the vehicle version and queue marketplace synchronization. Public buyer-request submissions are limited per dealer and source address, and each tenant exposes `/sitemap.xml` and `/robots.txt`.
