You are the lead product designer, senior full-stack engineer, and software architect for a new car dealer website product. Build a production-quality, reusable platform that my company can configure and sell to multiple car dealers.

Read this brief carefully before writing code. First inspect the existing repository and its instructions. If it is empty, create the project. Make sound implementation decisions, explain important tradeoffs briefly, and then implement the product. Do not stop after producing a plan or a visual mockup.

## The business model

There are TWO distinct products:

1. **Dealer website product — the product you are building now.** We create a premium website for each car dealer. Dealers have their own domain, logo, name, branding, profile, contact details, inventory, and staff dashboard. The underlying application should be reusable: adding another dealer should not require copying and maintaining another codebase.
2. **My separate car marketplace — a later project.** It is owned and managed by my company. Dealer cars will be sent to it automatically, but its administrators decide which cars appear publicly there.

Build product 1 now. Design and implement a reliable integration contract for product 2. Do not turn this task into building the entire marketplace.

## Core ownership and publishing rules

- Each car belongs to exactly one dealer account. A dealer can create and edit its own cars, prices, photos, details, and availability, including marking a car Sold. Its staff cannot access another dealer’s private data.
- A dealer’s site has its own publication controls. A dealer can save a draft, publish a car on its site, unpublish it, or mark it Sold.
- When a dealer publishes a car on its site, make it available to the marketplace integration automatically. On the marketplace side it must initially be visible **only to marketplace administrators as Pending review**. It must never become publicly visible there merely because the dealer published it.
- A marketplace administrator alone decides whether to publish, hide, or remove that dealer car from the public marketplace.
- When the dealer changes an already shared car’s price, photos, details, or availability, those dealer-owned fields must update in the marketplace. When the dealer marks it Sold, the marketplace must receive the Sold status, even if the marketplace listing is hidden from the public.
- Marketplace administrators must not be able to edit dealer-owned car details. They control marketplace visibility only. Cars created directly within the future marketplace will have a different owner and can be edited there.
- Do not silently republish a listing that a marketplace administrator has hidden or rejected when a dealer edits it.
- Preserve stable car IDs, dealer IDs, update versions, and an audit trail. Design for safe retries, duplicate deliveries, failures, and out-of-order updates so stale data cannot overwrite a newer price or Sold status.
- Decide and document how deleting or unpublishing a car on the dealer site affects its marketplace representation. Never leave a car publicly advertised as available after the dealer has withdrawn or sold it.
- Keep the dealer’s source-of-truth data separate from the marketplace’s publication decision.

## Dealer website experience

Create a distinctive, premium automotive design. It should feel like a carefully art-directed showroom, not a generic SaaS dashboard or a stock car-listing template. Use excellent typography, compelling photography, restrained colour, generous spacing, polished transitions, and thoughtful responsive layouts. Motion should support browsing and respect reduced-motion preferences. Avoid visual clutter, fake luxury cues, and heavy effects that slow down the site.

Build these customer-facing experiences:

- Homepage with a strong visual introduction, featured vehicles, new arrivals, dealer story, trust information, and clear paths to browse or book a viewing.
- Inventory page with fast search, useful filters, sorting, clear prices in Nigerian naira, and distinct Available, Reserved, and Sold states. Sold cars should not appear as available in search.
- Vehicle detail page with a strong photo gallery, optional video, asking price, location, make, model, year, mileage, transmission, fuel type, condition, notable features, known issues, seller-provided history, and clear calls to action.
- “New arrivals” presentation driven by actual listing data, not hard-coded cards.
- Dealer profile and contact information, address or showroom location, opening hours, and appropriate links.
- Buyer inquiry, appointment or test-drive request, and offer or negotiation request flows. Make the status and next step clear to buyers and staff. Do not imply that submitting an offer completes a sale.
- Useful empty, loading, error, and unavailable states. A sold vehicle’s page can remain accessible with a clear Sold badge and suggestions for similar available cars.

Treat claims carefully. Do not label a car “verified,” “inspected,” or “accident-free” unless the product has evidence and a defined verification process. Distinguish dealer-provided information from independently verified information.

## Dealer dashboard

Build an accessible, efficient dashboard for the dealer and its authorized staff:

- Overview of active, draft, reserved, and sold cars; recent inquiries, appointments, and offers.
- Create and edit listings with image upload, image ordering, validation, preview, draft saving, and publication controls.
- Change price and mark a car Reserved, Available, or Sold with appropriate confirmations and a clear activity history.
- Manage buyer inquiries, viewing requests, appointment outcomes, and offers or counteroffers.
- Manage dealer profile, branding, contact details, and relevant website settings.
- Staff roles with appropriate permissions. Enforce authorization on the server for every read and write; hiding a button is not authorization.
- Ensure every dealer-scoped query and uploaded asset respects the correct dealer boundary.

## Multi-dealer architecture

Design the application so many dealers can use the same maintained product while each presents a distinct branded website on their own domain. Explain how a domain maps to a dealer account, how local development works without owning domains, how branding is configured, and how one dealer’s content is kept separate from another’s.

Use a maintainable modular architecture. Keep domain rules, UI, persistence, authentication, background work, and the marketplace integration clearly separated. Use a relational database with sensible constraints and indexes. Store media appropriately rather than treating application disk as permanent storage. Choose a coherent modern stack appropriate for this repository, explain the choice, and avoid unnecessary infrastructure for the first release.

Build with production concerns in mind: secure authentication and sessions, password handling, rate limiting where appropriate, input validation, safe uploads, authorization, logging, error handling, backups and migrations, environment-based configuration, accessibility, mobile performance, image optimization, SEO, sitemap and metadata, and privacy-conscious inquiry handling. Do not put secrets in source control or expose them to the browser.

## Marketplace connection

Provide a concrete integration design and implementation boundary that the separate marketplace project can consume later. Prefer a versioned API and/or signed event delivery backed by durable delivery records. Document authentication between systems, payloads, retries, idempotency, update ordering, and reconciliation if an update fails.

At minimum, define and demonstrate these events or equivalent operations:

- Dealer profile created or updated
- Car published on dealer site
- Car details or price updated
- Car reserved or returned to Available
- Car marked Sold
- Car unpublished or withdrawn

The dealer website must remain usable if the marketplace is temporarily unavailable. Failed synchronization should be visible to operators and retry safely. Provide a practical local integration simulator or contract test so the upload → pending review → price update → Sold sequence can be demonstrated before the marketplace is built. Do not give dealer staff control over the marketplace’s public publication status.

## Implementation process

1. Inspect the repository and summarize what already exists.
2. Write a concise architecture and data model, including dealer isolation, roles, car lifecycle, domain mapping, and marketplace integration contract. Record important assumptions.
3. Implement a working vertical slice first: provision a dealer → configure its website → publish a car → see it on the dealer site → deliver it to the marketplace simulator as pending → update its price → mark it Sold → observe both updates.
4. Complete the customer-facing pages and dealer dashboard using real persisted data. Avoid hard-coded sample listings masquerading as functionality.
5. Add meaningful tests for tenant isolation, ownership permissions, publication boundaries, status transitions, and integration retries or duplicate updates. Run the relevant checks.
6. Review desktop and mobile layouts visually, fix obvious usability and accessibility issues, and provide setup instructions and a short demonstration guide.

Use sample dealer content and sample car images only as development fixtures, clearly labelled as such. Keep the site ready to replace them with real dealer assets.

If a decision is not specified, make a reasonable choice and document it. Ask me only when a missing answer blocks a major business decision. At the end, report what works, what was tested, what remains, and the exact steps to run and inspect the product locally.