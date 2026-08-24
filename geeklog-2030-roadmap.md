# Geeklog 2030 Roadmap

## Building the foundation for the next generation of Geeklog

Geeklog does not need to predict exactly what the web will look like in 2030.

It needs to make the right architectural choices today so that future capabilities can be added without repeatedly redesigning the platform.

The central idea of this roadmap is simple:

> **Structure → Expose → Connect → Discover → Recommend → Automate → Act**

The priority is not artificial intelligence itself.  
The priority is to make Geeklog content, products, services, availability and actions understandable and reusable by:

- people;
- search engines;
- applications;
- external services;
- AI assistants;
- future software agents.

This document proposes a practical starting point.

---

## 1. Guiding principles

Future Geeklog development should favor a few long-lived principles.

### Structured first

Important information should be represented as data, not only as rendered HTML.

A product should be identifiable as a product.

A service should be identifiable as a service.

An event, place, document, person or booking should follow the same principle.

### APIs before AI

AI features should consume stable Geeklog APIs rather than access plugin internals directly.

This keeps Geeklog independent from any particular AI provider.

### Plugins remain focused

Plugins should expose clear responsibilities and cooperate through documented interfaces.

For example:

- **Store** handles commerce and transactions;
- **Services** describes services and providers;
- **Booking** handles resources, availability and reservations.

They should integrate closely without becoming one monolithic plugin.

### Events connect the ecosystem

Plugins should be able to announce important events without knowing who consumes them.

Examples:

```text
store.order.created
store.payment.completed
services.request.created
booking.reservation.created
document.downloaded
content.viewed
```

Marketing, analytics, notifications, recommendations and external integrations can then subscribe independently.

### Multisite must be designed in from the beginning

Data isolation, API context, persistent storage and permissions must work correctly on both single-site and multisite installations.

---

# 2. Priority 0 — Define the common Data/API layer

This is the first architectural task.

Before adding advanced discovery, marketing or AI features, Geeklog plugins need a common way to expose their data.

## Goals

Define conventions for:

- JSON responses;
- object identifiers;
- API versioning;
- pagination;
- filtering;
- sorting;
- permissions;
- authentication;
- error responses;
- metadata;
- multisite context;
- plugin extensions.

Initial resources could eventually include:

```text
/api/content
/api/topics
/api/products
/api/services
/api/bookings
/api/events
/api/places
```

These endpoints are examples, not a frozen specification.

The first deliverable should be a small document:

**Geeklog Data API 1.0 — Draft Specification**

The goal is to establish conventions before individual plugins invent incompatible APIs.

---

# 3. Priority 0 — Define Geeklog Events

A lightweight common event mechanism should be defined alongside the Data API.

Possible API concept:

```php
GEEKLOG_event('store.order.created', $data);
```

The exact implementation remains to be designed.

The important part is the contract.

## Event naming

Use predictable names:

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

## Why events matter

A shared event model would allow future plugins to cooperate without hard dependencies.

For example:

```text
Store
  ↓
store.payment.completed
  ↓
Marketing
Analytics
Notifications
Recommendations
Webhooks
```

One event can serve many consumers.

---

# 4. Priority 1 — Develop Store on top of these contracts

The Store plugin is still under development.

That makes the present moment especially important: its public interfaces can still be designed with future interoperability in mind.

Store should remain focused on commerce.

## Store responsibilities

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

## Store should prepare for

- products without stock;
- free products;
- digital products;
- extensible metadata;
- external payment providers;
- API-created orders;
- webhooks;
- common Geeklog events;
- future links to Services and Booking.

## Store should not become responsible for

- calendars;
- service providers;
- appointment availability;
- booking resources;
- time slots;
- service-specific business logic.

Those belong elsewhere.

---

# 5. Priority 2 — Create the Services plugin

Services should describe what a person, organization or site can provide.

A service is not necessarily a traditional Store product.

Examples:

- consulting;
- training;
- audit;
- repair;
- installation;
- accommodation;
- rental;
- professional intervention;
- online service.

## Initial service model

A service may contain:

- title;
- description;
- provider;
- categories;
- service area;
- delivery method;
- indicative duration;
- location;
- metadata;
- whether it is bookable;
- whether it is paid;
- optional Store product reference.

Services answers the question:

> **What can be provided?**

Store answers:

> **What does it cost and how is it purchased?**

---

# 6. Priority 3 — Create the Booking plugin

Booking should manage scarce resources over time.

It should not merely be an appointment calendar.

## Core concepts

- resources;
- providers;
- calendars;
- availability;
- time slots;
- duration;
- capacity;
- reservations;
- cancellations;
- status;
- waiting lists.

Possible resources could later include:

```text
PERSON
ROOM
VEHICLE
EQUIPMENT
SEAT
ACCOMMODATION
EVENT
SERVICE
```

Booking answers:

> **When is it available?**

This creates a clean relationship:

```text
Services
   ↓
what is offered

Booking
   ↓
when it is available

Store
   ↓
how it is purchased
```

Not every service requires all three plugins.

Examples:

```text
Free consultation
Services + Booking

Digital ebook
Store

Paid training session
Services + Booking + Store

Audit delivered within five days
Services + Store
```

---

# 7. Priority 4 — Introduce an Entity / Knowledge layer

Once plugins expose structured data, Geeklog can begin connecting it.

A future Entity or Knowledge layer could describe common concepts such as:

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

and relationships such as:

```text
PERSON → provides → SERVICE
PERSON → writes → ARTICLE
SERVICE → available_at → PLACE
SERVICE → bookable_with → BOOKING
PRODUCT → purchasable_with → STORE
ARTICLE → explains → TOPIC
```

This does not require replacing existing Geeklog tables.

It can be an additional interoperability layer.

Its purpose is to transform isolated plugin data into connected knowledge.

---

# 8. Priority 5 — Build cross-plugin Search and Discovery

Search should eventually work across:

- articles;
- static pages;
- documents;
- videos;
- forums;
- products;
- services;
- events;
- places.

## Search 1.0

Start without requiring AI:

- full-text search;
- content types;
- filters;
- facets;
- topics;
- metadata;
- entity relationships.

## Search 2.0

Add optional semantic capabilities later:

- embeddings;
- semantic search;
- intent detection;
- conversational queries;
- source-backed answers;
- retrieval-augmented generation.

The principle should remain:

> AI improves a good information architecture; it should not be used to hide a poor one.

---

# 9. Priority 6 — Build a Tools framework

Some users do not need another article.

They need to solve something.

A future Tools plugin could provide a reusable framework for:

- calculators;
- simulators;
- diagnostics;
- questionnaires;
- configurators;
- comparison tools.

Example:

```text
ARTICLE
   ↓
explains the problem

TOOL
   ↓
helps solve the problem
```

Tools should also expose structured inputs and results so that they can later be used by Search, Recommendations and AI assistants.

---

# 10. Priority 7 — Add Recommendations

Recommendations should be a cross-plugin service rather than a feature implemented separately by every plugin.

A first version does not require AI.

It can use:

- topics;
- tags;
- entity relationships;
- popularity;
- content type;
- user history when permitted.

A visitor reading an article could then be guided toward:

```text
Article
Document
Video
Tool
Forum discussion
Service
Product
Event
```

The goal is to move from simple related content to useful discovery.

---

# 11. Priority 8 — Build Marketing on the shared foundation

Marketing should come after the event and data layers are established.

It can then consume activity from the whole Geeklog ecosystem.

Possible future capabilities include:

- consent management;
- visitor profiles;
- tags;
- dynamic segments;
- lead scoring;
- campaign attribution;
- UTM tracking;
- automated journeys;
- personalized recommendations;
- email integrations.

Example:

```text
content.viewed
document.downloaded
service.viewed
booking.reservation.created
store.order.completed
          ↓
      Marketing
          ↓
profile → interest → segment → action
```

Marketing should consume common data and events rather than create a second tracking architecture.

---

# 12. Priority 9 — Add AI assistants and agents

Advanced AI should be built only after Geeklog can clearly expose both information and actions.

An AI assistant could then:

- search;
- explain;
- compare;
- recommend;
- find a service;
- check availability.

Future authorized agents could potentially:

- request a quote;
- create a booking;
- prepare an order;
- initiate other controlled actions.

Read operations and action operations should remain clearly separated.

For example:

```text
READ
search
compare
availability

ACTION
contact
booking
order
```

Actions must use strict authentication, permissions, validation and audit trails.

AI providers should remain replaceable adapters rather than become dependencies of the core architecture.

---

# 13. Recommended implementation sequence

```text
1. DATA / API
       ↓
2. EVENTS
       ↓
3. STORE
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

This is a dependency order, not a multi-year calendar.

Several stages can overlap once their interfaces are stable.

---

# 14. Immediate starting point

The roadmap can begin with three concrete tasks.

## Task 1 — Draft the Geeklog Data API 1.0 specification

Define:

- resource structure;
- identifiers;
- JSON conventions;
- errors;
- pagination;
- filtering;
- permissions;
- versioning;
- multisite behavior.

**Deliverable:** a reviewable Markdown specification.

---

## Task 2 — Draft Geeklog Events 1.0

Define:

- event naming;
- payload conventions;
- dispatch mechanism;
- listener mechanism;
- error isolation;
- synchronous vs future asynchronous considerations.

**Deliverable:** a small event specification and reference implementation proposal.

---

## Task 3 — Review Store against the future contracts

Before the Store plugin architecture becomes stable, verify that it can support:

- the Data API;
- common events;
- extensible metadata;
- clean external integrations;
- future Services links;
- future Booking links;
- multisite isolation.

The goal is not to add Services or Booking logic to Store.

The goal is to ensure Store can cooperate with them later.

---

# 15. What success looks like

The first milestone is not an AI chatbot.

It is much simpler.

A Geeklog installation should be able to describe its important information through predictable interfaces.

A plugin should be able to announce important events.

Another plugin should be able to consume those events without modifying the original plugin.

Store, Services and Booking should remain independent but interoperable.

Once these foundations exist, future development becomes significantly easier.

Search can discover more.

Recommendations can connect more.

Marketing can understand more.

AI can answer better.

Agents can eventually act safely.

---

# 16. The long-term direction

Geeklog already knows how to publish.

The next step is to help it understand, expose and connect what it publishes.

The long-term direction can therefore remain deliberately simple:

> **Structure → Expose → Connect → Discover → Recommend → Automate → Act**

We do not need to build 2030 today.

We need to make sure that what we build today does not prevent 2030.
