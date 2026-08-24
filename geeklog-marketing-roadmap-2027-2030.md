# Addendum — Geeklog Marketing Plugin Roadmap 2027–2030

## Objective

Build a native, self-hosted **Marketing Automation layer for Geeklog** designed for the 2027–2030 ecosystem.

The plugin should not attempt to reproduce a complete SaaS platform such as HubSpot. Its role is to provide Geeklog with a common first-party marketing infrastructure that can be used by content and business plugins.

Core principle:

```text
Collect → Understand → Segment → Automate → Convert
```

The Marketing plugin should become the common marketing layer for Geeklog plugins such as:

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

The architecture must be designed around a few long-lived foundations:

1. **Event-driven architecture**
2. **First-party visitor and customer data**
3. **Stable public API for other Geeklog plugins**
4. **Privacy and consent by design**
5. **Strict multisite isolation**
6. **External providers through adapters**
7. **No mandatory external SaaS**
8. **AI must remain optional**
9. **Marketing features must work without AI**
10. **Plugins must never access Marketing database tables directly**

The three most important elements to freeze before development are:

```text
Database schema
      ↓
Universal event format
      ↓
Public Marketing API
```

---

# Phase 0 — Foundation and Architecture

**Priority: Critical**

Define the technical foundation before implementing visible marketing features.

### Requirements

- Geeklog 2.2.2 architecture;
- PHP 8.1+;
- mono-site support;
- multisite support;
- strict site-level data isolation;
- Geeklog ACL integration;
- CSRF protection;
- secure data storage;
- retention and anonymization strategy;
- installation and upgrade paths;
- plugin API conventions.

Suggested structure:

```text
marketing/
├── admin/
├── api/
├── classes/
├── language/
├── sql/
├── templates/
├── integrations/
├── functions.inc
└── autoinstall.php
```

### Deliverable

A documented architecture and initial database schema.

---

# Phase 1 — Universal Event API

**Priority: Critical**

Create the central API used by Geeklog and third-party plugins.

Initial concept:

```php
MARKETING_event($event, $data);
```

Standard events should include:

```text
page_view
article_view
search
download
form_submit
user_register
login

product_view
cart_add
purchase

document_view
document_download

video_view
video_complete

contact_request
```

Each event should support a common envelope:

```text
event_id
event_type
timestamp

site_id
visitor_id
session_id
uid

object_type
object_id

source
metadata
```

### Rule

Plugins should submit business events but should not need to understand how Marketing stores or processes them.

Example:

```php
MARKETING_event('purchase', array(
    'object_type' => 'product',
    'object_id'   => $productId,
    'value'       => $amount
));
```

---

# Phase 2 — Anonymous Visitor Identity

Introduce an anonymous:

```text
visitor_id
```

capable of linking several interactions to the same visitor where permitted.

The system should distinguish:

```text
Anonymous visitor
        ↓
visitor_id

Known Geeklog user
        ↓
uid
```

When identification becomes possible:

```text
visitor_id
     ↓
Geeklog uid
```

The system may associate previous eligible activity with the known profile according to consent and retention rules.

---

# Phase 3 — Marketing Profiles

Create a unified marketing profile.

Initial profile properties:

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

The profile becomes the common representation of an audience member.

It should complement Geeklog's user table rather than duplicate the Geeklog account system.

---

# Phase 4 — Consent and Privacy Layer

**Must exist before behavioral profiling becomes extensive.**

Initial consent categories:

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

The event infrastructure must be capable of determining whether an event can:

- be collected;
- remain anonymous;
- be associated with a profile;
- be used for personalization;
- trigger marketing communication.

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

Maintain initially:

```text
first_touch
last_touch
```

This provides the foundation for answering:

```text
Where did this visitor come from?

Which campaign generated the lead?

Which acquisition source generated the purchase?
```

Advanced multi-touch attribution should come later.

---

# Phase 6 — Tags

Implement reusable profile tags.

Examples:

```text
customer
prospect
newsletter

interest:rocket-stove
interest:libreoffice

high-engagement
repeat-customer
```

Public API:

```php
MARKETING_addTag();
MARKETING_removeTag();
MARKETING_hasTag();
```

Tags should be usable by:

- segmentation;
- automation;
- personalization;
- external integrations.

---

# Phase 7 — Dynamic Segmentation

Create a generic rules engine.

Example:

```text
article topic = rocket-stove
AND
article views >= 3
AND
period <= 30 days
AND
purchase = false
```

Result:

```text
Rocket Stove Prospects
```

Initial operators:

```text
=
!=
>
<
contains
exists
within_days
```

Start with a simple rule editor.

Do not make the first version dependent on a complex visual workflow builder.

---

# Phase 8 — Lead and Engagement Scoring

Allow administrators to assign weights to events.

Example:

| Event | Score |
|---|---:|
| Article view | +1 |
| Internal search | +2 |
| Newsletter subscription | +5 |
| Document download | +5 |
| Product view | +5 |
| Contact request | +20 |
| Purchase | +30 |

Support negative or decay rules:

```text
90 days inactivity → -10
```

The score should become a standard profile property available through the public API.

Example:

```php
MARKETING_getScore($uid);
```

---

# Phase 9 — Public Plugin API

Before advanced features are developed, freeze a stable integration layer.

Initial public functions may include:

```php
MARKETING_event();

MARKETING_getProfile();

MARKETING_addTag();
MARKETING_removeTag();
MARKETING_hasTag();

MARKETING_getScore();

MARKETING_hasSegment();
```

The API should be stable enough for other plugins to depend upon it.

### Integration examples

Store:

```text
product_view
cart_add
purchase
```

Documents:

```text
document_view
document_download
```

Videos:

```text
video_view
video_complete
```

Contact:

```text
contact_request
lead_created
```

Core Stories:

```text
article_view
topic_interest
```

Internal Search:

```text
search
```

---

# Phase 10 — Webhooks and External Integration

Add an event publication system.

Initial outgoing events:

```text
event.created
profile.created
profile.updated

purchase.completed

segment.entered
segment.left

score.changed
```

This enables integration with:

```text
n8n
Make
Zapier

CRM systems
email platforms
analytics platforms
business applications
```

Geeklog should therefore remain useful even when an external automation system is preferred.

---

# Phase 11 — Marketing Dashboard

Once reliable data exists, expose an administration dashboard.

Initial indicators:

```text
Visitors
Known profiles
New contacts

Events
Conversions

Acquisition sources
Campaigns

Top content
Top interests

Segments
Lead scores
```

Initial funnels may include:

```text
Visit
 ↓
Content
 ↓
Download
 ↓
Registration
 ↓
Purchase
```

---

# Milestone — Marketing 1.0

Marketing 1.0 should represent a **data and intelligence foundation**, not a full marketing suite.

| Capability | 1.0 |
|---|---|
| Event API | ✓ |
| Anonymous Visitor ID | ✓ |
| Marketing Profiles | ✓ |
| Consent | ✓ |
| UTM Tracking | ✓ |
| First/Last Touch | ✓ |
| Tags | ✓ |
| Dynamic Segments | ✓ |
| Lead Scoring | ✓ |
| Public Plugin API | ✓ |
| Webhooks | ✓ |
| Basic Dashboard | ✓ |
| Email campaigns | — |
| Automation workflows | — |
| AI | — |

This milestone is important because all later functionality depends on trustworthy data.

---

# Marketing 1.1 — Conversion Layer

Build user-facing conversion tools.

### Features

- marketing forms;
- newsletter forms;
- lead capture;
- progressive profiling;
- CTA manager;
- conditional CTA;
- Smart Blocks;
- conditional content;
- simple landing-page helpers;
- funnels;
- customer journey visualization.

Example:

```text
IF
segment = rocket-stove-prospect

THEN
display CTA = rocket-stove-guide
```

Geeklog Blocks should be considered a natural integration point for conditional marketing content.

---

# Marketing 1.2 — Automation Engine

Introduce:

```text
Trigger
   ↓
Conditions
   ↓
Actions
```

Example:

```text
document_download
        ↓
wait 2 days
        ↓
purchase = false
        ↓
send webhook
        ↓
add tag
        ↓
score +5
```

Initial triggers:

```text
event
tag added
segment entered
score reached
registration
purchase
inactivity
date
```

Initial actions:

```text
add tag
remove tag

change score

call webhook

send notification

start workflow

send email
```

The automation engine must not depend on a specific email provider.

---

# Marketing 1.3 — Email Marketing

Add campaign and lifecycle email management.

Geeklog Marketing should manage:

```text
Campaign
Audience
Segment
Template
Automation
Statistics
```

Delivery should use provider adapters.

Possible adapters:

```text
SMTP
Brevo
Amazon SES
Mailgun
Postmark
Resend
Other providers
```

Provider-specific code must remain isolated from the marketing engine.

Initial features:

- newsletters;
- segmented campaigns;
- transactional marketing messages;
- welcome sequences;
- nurturing sequences;
- reactivation campaigns;
- post-purchase sequences.

---

# Marketing 1.4 — Optimization and Intelligence

Add advanced measurement and optimization.

### Features

- A/B testing;
- CTA testing;
- email testing;
- conversion attribution;
- advanced funnels;
- customer journey;
- cohorts;
- content recommendations;
- product recommendations;
- behavioral recommendations.

Multi-touch attribution can be introduced here.

---

# Marketing 2.x — AI-Assisted Marketing

**Target: later 2028–2030 development**

AI should be implemented through a provider abstraction.

Concept:

```text
Marketing
   ↓
AI Provider API
   ├── OpenAI
   ├── Anthropic
   ├── Gemini
   ├── Mistral
   ├── Local model
   └── Custom API
```

The Marketing plugin must remain fully functional without an AI provider.

Potential AI-assisted functions:

- segment suggestions;
- behavioral pattern detection;
- intent classification;
- campaign suggestions;
- campaign content generation;
- performance summaries;
- content recommendations;
- customer journey analysis;
- next-best-action recommendations.

AI should advise or enhance the marketing engine rather than become its architectural foundation.

---

# 2027–2030 Development Sequence

```text
FOUNDATION
│
├── Architecture / Multisite
├── Database Schema
├── Event Format
├── Public API
│
▼
DATA
│
├── Events
├── Visitor Identity
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
├── Plugin API
├── Webhooks
├── Dashboard
│
▼
MARKETING 1.0
│
├── Forms
├── CTA
├── Personalization
├── Funnels
│
▼
MARKETING 1.1
│
├── Automation Engine
│
▼
MARKETING 1.2
│
├── Email Campaigns
├── Email Providers
│
▼
MARKETING 1.3
│
├── A/B Testing
├── Advanced Attribution
├── Recommendations
│
▼
MARKETING 1.4
│
├── AI Assistance
├── Predictive Analysis
├── Next Best Action
│
▼
MARKETING 2.x / 2028–2030
```

## Immediate Development Starting Point

Development should **not** begin with newsletters, AI, dashboards, or a visual automation builder.

The first implementation milestone should be limited to:

```text
1. Define database schema
2. Define universal event format
3. Define multisite isolation model
4. Implement MARKETING_event()
5. Implement anonymous visitor identity
6. Implement profile association
7. Implement consent checks
8. Document the public plugin API
```

Only after these foundations have been tested should Tags, Segments and Scoring be implemented.

The long-term objective is for Geeklog plugins to share a common marketing vocabulary:

```text
Store ───────┐
Booking ─────┤
Services ────┤
Documents ───┤
Videos ──────┤
Contact ─────┤
Stories ─────┤
Forum ───────┤
             ▼
       MARKETING EVENT API
             │
             ▼
        First-Party Data
             │
             ▼
   Segmentation & Intelligence
             │
             ▼
        Automation
```

This common event and profile layer is the strategic component: it prevents Store, Booking, Services and future Geeklog plugins from each implementing their own incompatible marketing logic.

---

## Memorandum Integration Note

This level of detail should be preserved in **Memorandum**: it is precise enough to serve as a development specification when implementation begins, while deliberately avoiding premature decisions about table names or the final SQL schema.

The next dedicated technical document should focus exclusively on:

**Marketing 1.0 Data Model & Event API Specification**

That specification should define the database model, universal event envelope, multisite isolation rules, consent-aware data lifecycle, public API contracts, extension points and compatibility requirements before implementation of higher-level marketing features begins.
