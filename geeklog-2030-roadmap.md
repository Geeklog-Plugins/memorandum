# Geeklog 2030 Roadmap

## Status

**Architectural direction — not the current implementation queue.**

The immediate modernization priority remains the stabilization of active plugins across:

- **Geeklog 2.1.1 through 2.2.2**
- **PHP 5.6 through PHP 8.1**

This roadmap describes dependency principles for future architecture. It should influence interfaces where useful, but it must not force unfinished abstractions into plugins that still need stabilization.

## Building the foundation for the next generation of Geeklog

Geeklog does not need to predict exactly what the web will look like in 2030.

It needs to make architectural choices that leave room for future capabilities without repeatedly redesigning the platform.

The central idea is:

> **Structure → Expose → Connect → Discover → Recommend → Automate → Act**

The priority is not artificial intelligence itself. The priority is to make Geeklog content, products, services, availability and actions understandable and reusable by people, search engines, applications, external services, AI assistants and future software agents.

---

## 1. Guiding principles

### Structured first

Important information should increasingly be represented as data, not only as rendered HTML.

### APIs before AI

Future AI features should consume stable Geeklog interfaces rather than access plugin internals directly.

### Plugins remain focused

Plugins should expose clear responsibilities and cooperate through documented interfaces.

For example:

- **Store** handles commerce and transactions;
- **Services** describes services and providers;
- **Booking** handles resources, availability and reservations.

These future components should integrate without becoming one monolithic plugin.

### Events connect the ecosystem

A future common event mechanism should let plugins announce meaningful events without knowing who consumes them.

Examples:

```text
store.order.created
store.payment.completed
services.request.created
booking.reservation.created
documents.file.downloaded
content.article.viewed
```

Marketing, Analytics, Notifications, Recommendations and external integrations could then subscribe independently.

### Multisite is a current constraint

Multisite-safe design applies now, even though the dedicated Multisite Manager is a later project.

Data isolation, persistent storage, configuration and permissions should already be site-aware in active plugins.

See [`multisite-development-principles.md`](multisite-development-principles.md).

---

# 2. Future foundation — Common Data/API conventions

Before advanced discovery, marketing or AI features are developed, future Geeklog components should converge on common conventions for:

- JSON responses;
- identifiers;
- API versioning;
- pagination;
- filtering;
- sorting;
- permissions;
- authentication;
- errors;
- metadata;
- multisite context;
- extension points.

Possible future resources might include:

```text
/api/content
/api/topics
/api/products
/api/services
/api/bookings
/api/events
/api/places
```

These are examples, not an existing Geeklog specification.

A future deliverable may be:

**Geeklog Data API 1.0 — Draft Specification**

---

# 3. Future foundation — Common Geeklog Events

A lightweight event contract should be designed alongside future Data/API conventions.

Possible concept:

```php
GEEKLOG_event('store.order.created', $data);
```

The name and implementation are intentionally not frozen yet.

The important architectural rule is that the event mechanism belongs to the shared Geeklog layer, not to Marketing or another consumer.

Preferred naming convention:

```text
domain.object.action
```

Examples:

```text
content.article.viewed
documents.file.downloaded
store.product.viewed
store.order.created
store.payment.completed
services.request.created
booking.reservation.created
booking.reservation.cancelled
```

Conceptual flow:

```text
Store
  ↓
store.payment.completed
  ↓
┌──────────────┬────────────┬────────────────┐
Marketing   Analytics   Notifications   Webhooks
```

---

# 4. Store — active project, future interoperability

**Status: Active project.**

Store is still under development and should first be stabilized across the current compatibility range.

Its future public interfaces should remain extensible enough to cooperate with shared data and event contracts later, without delaying present stabilization.

Store remains focused on commerce:

- products;
- variants;
- prices;
- carts;
- orders;
- payments;
- taxes;
- transactions;
- digital products;
- order states.

Store should not absorb calendars, service providers, appointment availability, booking resources, time slots or service-specific business logic.

---

# 5. Services

**Status: Architectural concept.**

Services could describe what a person, organization or site provides.

Examples include consulting, training, audits, repair, installation, accommodation, rental or online services.

Services answers:

> **What can be provided?**

Store answers:

> **What does it cost and how is it purchased?**

---

# 6. Booking

**Status: Architectural concept.**

Booking could manage scarce resources over time: providers, rooms, equipment, availability, time slots, capacity, reservations and cancellations.

Booking answers:

> **When is it available?**

Future relationship:

```text
Services → what is offered
Booking  → when it is available
Store    → how it is purchased
```

---

# 7. Entity / Knowledge layer

**Status: Architectural concept.**

A future interoperability layer could connect concepts such as:

```text
PERSON
ORGANIZATION
PLACE
PRODUCT
SERVICE
EVENT
DOCUMENT
TOPIC
```

This should complement existing Geeklog data rather than require replacement of existing tables.

A future Marketing profile must remain a Marketing projection, not the canonical identity for this layer.

---

# 8. Cross-plugin Search and Discovery

**Status: Architectural concept.**

Future search could work across articles, static pages, documents, videos, forums, products, services, events and places.

A first stage should rely on good information architecture, metadata, filters and relationships before optional semantic or AI capabilities are considered.

> AI should improve a good information architecture, not hide a poor one.

---

# 9. Tools framework

**Status: Architectural concept.**

A future Tools framework could support calculators, simulators, diagnostics, questionnaires, configurators and comparison tools.

---

# 10. Recommendations

**Status: Architectural concept.**

Recommendations should eventually be a cross-plugin capability rather than a separate implementation inside every plugin.

A first version need not require AI.

---

# 11. Marketing

**Status: Architectural concept / future project.**

Marketing should consume shared Geeklog data and events rather than create a second universal event architecture.

Potential capabilities include consent, visitor profiles, tags, segments, scoring, attribution, UTM tracking, journeys and integrations.

See [`geeklog-marketing-roadmap-2027-2030.md`](geeklog-marketing-roadmap-2027-2030.md).

---

# 12. AI assistants and agents

**Status: Long-term architectural concept.**

Advanced AI should be considered only after Geeklog can expose information and authorized actions through clear interfaces.

AI providers should remain replaceable adapters.

Read operations and action operations must remain clearly separated, with strict authentication, permissions, validation and audit trails for actions.

---

# 13. Dependency sequence

```text
1. DATA / API CONVENTIONS
       ↓
2. COMMON EVENTS
       ↓
3. STORE INTEROPERABILITY
       ↓
4. SERVICES
       ↓
5. BOOKING
       ↓
6. ENTITIES / KNOWLEDGE
       ↓
7. SEARCH / DISCOVERY
       ↓
8. TOOLS
       ↓
9. RECOMMENDATIONS
       ↓
10. MARKETING
       ↓
11. AI / AGENTS
```

This is a **dependency order**, not a multi-year calendar and not the current task list.

The operational task list remains in [`geeklog-modernization-roadmap.md`](geeklog-modernization-roadmap.md).

---

# 14. When future architecture work should start

Architecture work becomes useful when an active project reaches a point where a public interface is about to become difficult to change.

At that moment, the smallest useful deliverables are:

1. a draft shared data/API convention;
2. a draft common event contract;
3. a review of Store or another active plugin against those contracts.

Do not block stabilization work merely to implement speculative infrastructure.

---

# 15. What success looks like

The first milestone is not an AI chatbot.

It is a Geeklog ecosystem where plugins can expose predictable information, remain multisite-safe and cooperate without direct knowledge of each other's internals.

Once those foundations exist, Search, Recommendations, Marketing and AI can be added with much less coupling.

---

# 16. Long-term direction

Geeklog already knows how to publish.

The next step is to make what it publishes easier to structure, expose and connect.

> **Structure → Expose → Connect → Discover → Recommend → Automate → Act**

We do not need to build 2030 today.

We need to make sure that what we build today does not prevent 2030.
