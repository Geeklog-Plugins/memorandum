# Addendum — Geeklog Marketing Plugin Roadmap 2027–2030

## Status

**Architectural concept / future project.**

This roadmap does not override the current modernization priority for active plugins, which remains:

- Geeklog 2.1.1 through 2.2.2;
- PHP 5.6 through PHP 8.1.

When Marketing implementation begins, its exact minimum runtime may be reassessed. Until then, active plugin modernization should not depend on Marketing.

## Objective

Build a native, self-hosted **Marketing Automation layer for Geeklog** designed for the 2027–2030 ecosystem.

The plugin should not attempt to reproduce a complete SaaS platform such as HubSpot. Its role is to provide first-party marketing capabilities that consume structured activity from Geeklog and its plugins.

Core principle:

```text
Collect → Understand → Segment → Automate → Convert
```

Marketing may eventually consume activity from:

```text
Stories
Users
Contact
Documents
Videos
Store
Booking
Services
Forum
Maps
and future plugins
```

---

## Architectural Principles

1. **Consume common Geeklog events rather than become the universal event bus.**
2. **Use first-party visitor and customer data.**
3. **Expose a stable Marketing API for Marketing-specific capabilities.**
4. **Privacy and consent by design.**
5. **Strict multisite isolation.**
6. **External providers through adapters.**
7. **No mandatory external SaaS.**
8. **AI remains optional.**
9. **Marketing works without AI.**
10. **Other plugins must never access Marketing database tables directly.**

The most important elements to freeze before implementation are:

```text
Common Geeklog event contract
          ↓
Marketing data model
          ↓
Marketing public API
```

The common event contract belongs to the wider Geeklog architecture. Marketing is one consumer of it alongside Analytics, Notifications, Recommendations and external integrations.

---

# Phase 0 — Foundation and Architecture

**Priority when project becomes active: Critical**

Define the technical foundation before implementing visible marketing features.

### Requirements

- current Geeklog plugin architecture;
- explicit minimum PHP version chosen at implementation time;
- mono-site support;
- multisite support;
- strict site-level data isolation;
- Geeklog ACL integration;
- CSRF protection;
- secure data storage;
- retention and anonymization strategy;
- installation and upgrade paths;
- public API conventions;
- compatibility with the common Geeklog event contract.

### Deliverable

A documented architecture and initial database schema.

---

# Phase 1 — Event Consumption and Marketing Tracking

Marketing should consume a future common Geeklog event contract rather than require every plugin to call a Marketing-specific event function.

Preferred future flow:

```text
Store / Documents / Videos / Core
              ↓
       Geeklog Event Layer
              ↓
     ┌────────┼─────────┐
 Marketing  Analytics  Notifications
```

Possible common event names:

```text
content.article.viewed
content.search.performed
user.registered
user.logged_in

documents.file.viewed
documents.file.downloaded

videos.video.viewed
videos.video.completed

store.product.viewed
store.cart.item_added
store.order.completed

contact.request.created
```

Marketing may expose a dedicated function for events that are strictly internal to Marketing, but `MARKETING_event()` should not become the ecosystem-wide event bus.

A common event envelope should eventually support fields such as:

```text
event_id
event_type
timestamp
site_id
uid
object_type
object_id
source
metadata
```

Marketing can enrich eligible events with its own visitor/session context after consent rules are applied.

---

# Phase 2 — Anonymous Visitor Identity

Introduce an anonymous `visitor_id` capable of linking eligible interactions to the same visitor where permitted.

The system should distinguish:

```text
Anonymous visitor → visitor_id
Known Geeklog user → uid
```

When identification becomes possible, Marketing may associate eligible activity with a known profile according to consent and retention rules.

---

# Phase 3 — Marketing Profiles

Create a Marketing-specific profile containing properties such as:

```text
uid
visitor_id
first_seen
last_seen
first_source
last_source
first_landing_page
last_landing_page
visit_count
event_count
score
tags
segments
consents
```

The Marketing profile is not the canonical Geeklog identity layer. It complements Geeklog users and any future Entity/Knowledge layer.

---

# Phase 4 — Consent and Privacy Layer

This must exist before extensive behavioral profiling.

Initial consent categories may include:

```text
analytics
personalization
profiling
email_marketing
```

Store at least:

```text
consent_type
status
timestamp
source
policy_version
```

Marketing must determine whether an event may be collected, associated with a profile, used for personalization or used to trigger communication.

---

# Phase 5 — Acquisition and Attribution

Capture campaign information such as:

```text
utm_source
utm_medium
utm_campaign
utm_term
utm_content
referrer
landing_page
```

Start with first-touch and last-touch attribution. Advanced multi-touch attribution comes later.

---

# Phase 6 — Tags

Implement reusable profile tags and a stable Marketing API such as:

```php
MARKETING_addTag();
MARKETING_removeTag();
MARKETING_hasTag();
```

Tags can support segmentation, automation, personalization and integrations.

---

# Phase 7 — Dynamic Segmentation

Create a simple generic rules engine before considering a visual workflow builder.

Initial operators may include:

```text
=
!=
>
<
contains
exists
within_days
```

---

# Phase 8 — Lead and Engagement Scoring

Allow administrators to assign weights to eligible events and define decay or negative rules.

Expose the resulting score through the Marketing API, for example:

```php
MARKETING_getScore($uid);
```

---

# Phase 9 — Public Marketing API

Freeze a stable integration layer for Marketing-specific capabilities.

Possible functions include:

```php
MARKETING_getProfile();
MARKETING_addTag();
MARKETING_removeTag();
MARKETING_hasTag();
MARKETING_getScore();
MARKETING_hasSegment();
```

Business plugins should publish common Geeklog events rather than depend directly on this API unless they explicitly need a Marketing-specific operation.

---

# Phase 10 — Webhooks and External Integration

Add outgoing integration events for Marketing-owned state changes, such as:

```text
marketing.profile.created
marketing.profile.updated
marketing.segment.entered
marketing.segment.left
marketing.score.changed
```

This can connect Geeklog to tools such as n8n, Make, Zapier, CRM systems and email platforms.

---

# Phase 11 — Marketing Dashboard

Once reliable data exists, expose an administration dashboard for visitors, profiles, conversions, acquisition sources, campaigns, content interests, segments and lead scores.

---

# Milestone — Marketing 1.0

Marketing 1.0 should represent a **data and intelligence foundation**, not a complete marketing suite.

| Capability | 1.0 |
|---|---|
| Common event consumption | ✓ |
| Anonymous Visitor ID | ✓ |
| Marketing Profiles | ✓ |
| Consent | ✓ |
| UTM Tracking | ✓ |
| First/Last Touch | ✓ |
| Tags | ✓ |
| Dynamic Segments | ✓ |
| Lead Scoring | ✓ |
| Public Marketing API | ✓ |
| Webhooks | ✓ |
| Basic Dashboard | ✓ |
| Email campaigns | — |
| Automation workflows | — |
| AI | — |

---

# Marketing 1.1 — Conversion Layer

Possible features:

- marketing forms;
- newsletter forms;
- lead capture;
- progressive profiling;
- CTA manager;
- conditional CTA;
- Smart Blocks;
- conditional content;
- landing-page helpers;
- funnels;
- customer journey visualization.

Geeklog Blocks are a natural integration point for conditional content.

---

# Marketing 1.2 — Automation Engine

Introduce:

```text
Trigger → Conditions → Actions
```

Initial triggers may include events, tags, segment changes, score thresholds, registrations, purchases, inactivity and dates.

Initial actions may include tag changes, score changes, webhooks, notifications, workflows and email actions.

The automation engine must not depend on a specific email provider.

---

# Marketing 1.3 — Email Marketing

Add campaign and lifecycle email management through provider adapters rather than hard-coding one service.

Possible adapters include SMTP, Brevo, Amazon SES, Mailgun, Postmark, Resend and future providers.

---

# Marketing 1.4 — Optimization and Intelligence

Possible features:

- A/B testing;
- CTA testing;
- email testing;
- conversion attribution;
- advanced funnels;
- cohorts;
- content recommendations;
- product recommendations;
- behavioral recommendations.

---

# Marketing 2.x — AI-Assisted Marketing

AI should be implemented later through a replaceable provider abstraction.

Marketing must remain fully functional without an AI provider.

Potential AI-assisted functions include segment suggestions, behavioral pattern detection, intent classification, campaign suggestions, performance summaries, recommendations and next-best-action assistance.

---

# Development sequence

```text
COMMON GEEKLOG CONTRACTS
│
├── Event contract
├── Multisite rules
├── Data/API conventions
│
▼
MARKETING FOUNDATION
│
├── Data model
├── Event consumption
├── Visitor identity
├── Profiles
├── Consent
├── Acquisition
│
▼
INTELLIGENCE
│
├── Tags
├── Segments
├── Scoring
├── Attribution
│
▼
INTEGRATION
│
├── Marketing API
├── Webhooks
├── Dashboard
│
▼
CONVERSION
│
├── Forms
├── CTA
├── Personalization
├── Funnels
│
▼
AUTOMATION
│
▼
EMAIL
│
▼
OPTIMIZATION
│
▼
OPTIONAL AI
```

## Immediate starting point when the project becomes active

Do not begin with newsletters, AI, dashboards or a visual workflow builder.

Start with:

1. confirm the common Geeklog event contract;
2. define the Marketing database schema;
3. define multisite isolation;
4. implement common event consumption;
5. implement anonymous visitor identity;
6. implement profile association;
7. implement consent checks;
8. document the Marketing API.

The strategic rule is simple:

> Marketing consumes the shared Geeklog architecture; it does not replace it.
