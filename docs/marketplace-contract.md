# Marketplace integration contract v1

## Delivery

The dealer service owns vehicle facts; the marketplace owns public visibility. Each committed source change creates an `OutboxEvent`. A worker POSTs JSON to `MARKETPLACE_WEBHOOK_URL`; without a URL, the local simulator consumes it. The request includes `X-Event-ID` and `X-Showroom-Signature: sha256=<hex HMAC-SHA256>` computed over the exact body using the shared secret. Production should rotate per-environment secrets and optionally add mTLS/IP restrictions.

The marketplace returns any 2xx only after durably recording the event. It deduplicates by `event_id` and keeps, per aggregate, the greatest `data.version`. An event with a lower or equal version is acknowledged but ignored. Delivery is at least once, attempts use exponential backoff (up to one hour), and operators can see failures. Reconciliation compares dealer/car UUID plus latest version; a future authenticated `GET /integrations/v1/dealers/{id}/vehicles?updated_after=...` can repair gaps without changing event semantics.

## Envelope

```json
{
  "event_id": "uuid",
  "event_type": "vehicle.updated.v1",
  "occurred_at": "2026-09-29T12:00:00+00:00",
  "data": {
    "id": "stable-vehicle-uuid",
    "dealer_id": "stable-dealer-uuid",
    "version": 4,
    "price": "68500000.00",
    "currency": "NGN",
    "availability": "available",
    "publication_status": "published"
  }
}
```

Vehicle payloads also contain title, slug, make/model/year, mileage, transmission, fuel, dealer-described condition/history/issues, location, description, features, ordered image URLs, and update time. Decimal values are strings. Fields are additive within v1; breaking changes require v2.

## Events

- `dealer.created.v1`, `dealer.updated.v1`
- `vehicle.published.v1`: marketplace creates/updates source data; a new marketplace-owned record starts `Pending review`, never Public.
- `vehicle.updated.v1`: updates dealer-owned fields only; visibility is unchanged.
- `vehicle.availability_changed.v1`: Reserved or returned to Available; visibility is unchanged.
- `vehicle.sold.v1`: always updates availability to Sold; marketplace must prevent it from being advertised as available, regardless of visibility.
- `vehicle.withdrawn.v1`: sets marketplace visibility to Withdrawn immediately while retaining the record and audit history.

Marketplace admins cannot edit `dealer_data`; their moderation action changes only visibility and its own audit log. Dealer edits cannot resurrect Hidden, Rejected, or Withdrawn content. A later republish after withdrawal should create a new review request/business workflow rather than silently become public; v1 leaves the existing simulator record Withdrawn, requiring marketplace-admin review.
