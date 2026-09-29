# Architecture and data model

## Assumptions and decisions

- One deployment serves many dealers. A request hostname resolves through unique `DealerDomain.hostname` to one active `Dealer`; `?dealer=<slug>` or a remembered session is the local-only fallback on localhost.
- Branding is data: dealer logo, colours, story, contact details, address, and hours. No dealer-specific code fork is required.
- Every private row has a dealer relationship directly or through its vehicle. Views always start from `request.dealer`; object lookups include that dealer. Membership roles are Owner, Manager, Sales, and Viewer. Server decorators enforce each action.
- Owner/Manager edit vehicles and dealer settings; Sales can operate buyer-request workflow; Viewer is read-only. Platform provisioning/admin remains Django admin for this first release.
- PostgreSQL is the production relational store. UUIDs are stable external identifiers. Composite uniqueness and tenant/status indexes protect common query paths.
- Images use `ImageField` metadata but production bytes belong in S3-compatible object storage/CDN. Application disk is development-only.

## Lifecycle

Website publication (`Draft`, `Published`, `Unpublished`) is independent from availability (`Available`, `Reserved`, `Sold`). Public pages require Published. A Sold page remains available and suggests available alternatives. Publishing, changing a previously shared listing, availability changes, Sold, and withdrawal create versioned outbox events in the same database transaction as the change.

Unpublishing means withdrawal: the marketplace snapshot is retained for audit/reconciliation but is forced to non-public `Withdrawn`. Sold is always delivered, regardless of marketplace visibility. Hard deletion is intentionally absent from staff UI; records should be retained/archived for audit. Marketplace admins own only `MarketplaceListing.visibility` (`Pending review`, `Public`, `Hidden`, `Rejected`, `Withdrawn`). Dealer updates replace only `dealer_data` and never reset Hidden/Rejected/Public to Pending.

## Core data

- `Dealer` and `DealerDomain`: tenant, branding, profile, hostname mapping, profile version.
- `Membership`: unique user/dealer membership and role.
- `Vehicle`: UUID, tenant, descriptive fields, price, publication and availability, monotonic version.
- `VehicleImage`: ordered assets with required alternative text and tenant ownership inherited through vehicle.
- `BuyerRequest`: inquiry, viewing, or offer with explicit workflow; an offer is not a sale.
- `AuditEntry`: actor, action, entity, version/state snapshot, timestamp.
- `OutboxEvent`: immutable event identity, aggregate/version, payload, attempts, next attempt, delivery/error state.
- `MarketplaceListing`: local contract simulator. It models the future marketplace's separately owned publication decision.

## Security and operations

Django sessions are HTTP-only; passwords use Django's adaptive hashers and validators; CSRF applies to all writes. Forms validate data and uploads, UUID URLs avoid enumeration, and no secret is exposed to templates. Add proxy/application rate limits before public launch. Migrations are committed; deployment runs them once. Structured logs, error monitoring, database/object-storage backups, retention/deletion policy, malware scanning, and access review belong in the production runbook.

SEO includes semantic markup, canonical URLs, OpenGraph basics, and tenant-aware XML sitemap and robots endpoints. Production follow-up includes vehicle JSON-LD, verified canonical-domain redirects, and optimized responsive image derivatives.
