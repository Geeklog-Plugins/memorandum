# Geeklog External Data Integration Vision — 2030

## Purpose

Geeklog should not only expose its own content and plugin data to the outside world. It should also become capable of safely consuming, transforming, caching, synchronizing, and presenting data exposed by external services.

This objective does **not** start from zero. Geeklog already contains several important interoperability mechanisms created over many years: content syndication, external feed consumption through Portal Blocks, Atom Publishing Protocol webservices, plugin service hooks, remote authentication mechanisms, block caching, and scheduled maintenance mechanisms.

The objective for 2030 should therefore be:

> **Preserve Geeklog's existing interoperability concepts, modernize their protocols and security, and extend them into a coherent Data In / Data Out architecture.**

The long-term principle remains:

> **Data should be able to enter Geeklog, circulate through Geeklog, and leave Geeklog through well-defined interfaces.**

This document keeps a broad record of existing capabilities, modernization opportunities, and external data-source families that Geeklog or its plugins could exploit through 2030.

---

# 1. Existing Geeklog interoperability baseline

Before creating new integration features, development should identify and reuse the mechanisms that already exist in Geeklog Core.

## 1.1 Native syndication

Geeklog already contains a complete content-syndication administration system.

The Core can create, edit, enable, disable, and delete feeds. The syndication administration explicitly supports feeds for **Geeklog and its plugins**.

Existing capabilities include:

- multiple feeds;
- RSS;
- Atom and other formats supported by the syndication parser/writer classes;
- feeds for all stories;
- feeds restricted to the front page;
- feeds by topic;
- configurable item limits;
- limits expressed as item counts or recent hours;
- configurable content length;
- title and description;
- language and character set;
- feed file names;
- feed logos;
- update tracking;
- plugin extensions to feed elements.

The current architecture includes mechanisms such as:

```text
admin/syndication.php
system/lib-syndication.php
FeedParserFactory
PLG_getFeedElementExtensions()
```

This means RSS/Atom syndication should **not** be listed as a new 2030 capability.

The modernization goal is instead to make the existing syndication layer participate in the broader structured-data architecture.

---

## 1.2 Portal Blocks already consume external data

Geeklog has long supported **Portal Blocks**.

A Portal Block can retrieve an external RDF/RSS-style feed and display it inside Geeklog. Existing block fields include concepts such as:

```text
rdfurl
rdflimit
rdfupdated
cache_time
```

The historical model is therefore already:

```text
External feed
     |
 RSS / RDF
     |
Portal Block
     |
 Geeklog
```

This is the direct ancestor of the proposed **Remote Data Block**.

A future Remote Data Block should therefore preferably be designed as an evolution of the Portal Block concept rather than as an unrelated new subsystem.

Possible evolution:

```text
Portal Block today

RSS/RDF URL
    |
feed parser
    |
block
```

becomes:

```text
Remote / Portal Block

RSS / Atom / JSON / REST / OpenAPI source
                 |
          authentication
                 |
              cache
                 |
              mapping
                 |
             template
                 |
               block
```

Backward compatibility with existing Portal Blocks should be preserved where practical.

---

## 1.3 Geeklog already contains AtomPub webservices

Geeklog Core includes an implementation of the **Atom Publishing Protocol (AtomPub)** under its webservices layer.

The existing gateway handles HTTP methods including:

```text
GET
POST
PUT
DELETE
```

The implementation includes concepts already familiar in modern APIs:

- HTTP status codes;
- authentication;
- resource retrieval;
- resource creation;
- resource modification;
- resource deletion;
- service introspection;
- ETag-related handling;
- plugin dispatch.

The key architectural mechanism is the use of the Plugin API through calls such as:

```php
PLG_invokeService(...)
```

This means Geeklog already contains an early **resource/service abstraction**.

The future REST/JSON API should first investigate whether this resource layer can be modernized and reused instead of creating an entirely separate plugin-facing API.

A desirable architecture would be:

```text
                  Geeklog resource layer
                          |
                   PLG_invokeService
                          |
          +---------------+---------------+
          |                               |
      AtomPub                         REST / JSON
   compatibility API                   modern API
```

Later this could become:

```text
                  Geeklog resource layer
                          |
          +---------------+---------------+---------------+
          |               |               |               |
       AtomPub          REST/JSON       ActivityPub      MCP adapter
       legacy            modern          federation       agents
```

AtomPub should not necessarily remain the primary public API forever, but its useful architecture should not be discarded without evaluation.

---

## 1.4 Service introspection already exists in an early form

The Atom webservice layer already contains service/plugin introspection concepts.

This is not equivalent to OpenAPI or GraphQL introspection, but the architectural intention is relevant:

```text
client
  |
service discovery
  |
plugin service
```

Modernization can therefore evolve an existing idea toward:

- OpenAPI descriptions;
- discoverable resources;
- schemas;
- authentication descriptions;
- capabilities;
- agent tool discovery.

---

## 1.5 Plugin API is already the central interoperability mechanism

Geeklog's Plugin API already allows plugins to participate in many Core processes.

For external-data work, this is strategically important because the Integration Layer should remain **plugin-oriented**.

The goal is not:

```text
Core knows Store
Core knows Maps
Core knows Calendar
```

but:

```text
Core provides integration primitives
             |
        Plugin API
             |
Store / Maps / Calendar / Documents / others
```

Existing plugin hooks and service functions should be reused whenever their semantics remain appropriate.

---

## 1.6 Existing block cache is another reusable concept

Geeklog blocks already expose a configurable `cache_time` concept.

A modern external-data cache will require additional capabilities such as:

- cache namespaces;
- HTTP validators;
- stale-if-error behavior;
- synchronization metadata;
- provider rate-limit awareness;
- per-site isolation;
- explicit invalidation.

Nevertheless, the Core already recognizes that dynamic blocks may need caching. This should be considered when designing the new integration cache.

---

## 1.7 Existing authentication and scheduled mechanisms

Geeklog already contains historical remote-authentication and scheduled-task mechanisms.

They should be audited before introducing:

- OAuth 2.x clients;
- OpenID Connect;
- external credential storage;
- synchronization schedulers;
- webhook processing jobs.

Existing mechanisms may not meet current security expectations, but they may contain reusable concepts, configuration conventions, or plugin hooks.

---

# 2. Capability classification for the 2030 roadmap

The roadmap should distinguish three categories.

## 2.1 Existing — preserve and document

These capabilities already exist in Geeklog in meaningful form:

- RSS syndication;
- Atom/RDF-style syndication;
- multiple configurable feeds;
- feeds generated from Geeklog content;
- plugin participation in feeds;
- external RSS/RDF consumption through Portal Blocks;
- block caching;
- AtomPub webservices;
- GET/POST/PUT/DELETE service operations through AtomPub;
- plugin service dispatch through `PLG_invokeService()`;
- early service introspection;
- Plugin API hooks;
- remote-authentication mechanisms;
- scheduled/cron-oriented maintenance mechanisms.

These should not be presented as greenfield features.

---

## 2.2 Existing concept — modernize

These are the most important modernization targets:

| Existing Geeklog concept | Modern evolution |
|---|---|
| RSS/RDF Portal Block | Remote Data Block |
| Syndication engine | General structured feed/data publishing |
| AtomPub webservices | REST/JSON resource API |
| `PLG_invokeService()` | Shared plugin resource/service layer |
| Atom service introspection | OpenAPI/service discovery |
| Basic/legacy remote authentication | Modern OAuth 2.x / OIDC / scoped credentials |
| Block cache | External-data cache with stale fallback and rate-limit awareness |
| Existing scheduled jobs | General synchronization scheduler |
| Plugin feed extensions | Structured plugin resource schemas |

This category should receive priority because it provides modern capabilities while preserving Geeklog's architecture.

---

## 2.3 Genuinely new capabilities

Capabilities with no equivalent general mechanism currently identified in the Core include:

- REST responses based primarily on JSON;
- OpenAPI generation/import;
- generic external API connector definitions;
- generic secure credential vault for connectors;
- Bearer/API-key/OAuth client management for arbitrary external APIs;
- webhook receiver framework;
- webhook signature verification;
- replay protection;
- generic field mapping;
- JSONPath-like field extraction or equivalent;
- generic scheduled synchronization engine;
- incremental synchronization state;
- generic API rate-limit management;
- stale-cache fallback for remote APIs;
- JSON-LD integration;
- GraphQL client support where justified;
- ActivityPub federation;
- AI-provider abstraction;
- MCP/agent adapters;
- auditable agent write operations.

---

# 3. Core architectural principle

Avoid this model:

```text
Plugin A -> custom cURL code -> Provider A
Plugin B -> custom HTTP code -> Provider B
Plugin C -> another OAuth implementation -> Provider C
```

Prefer:

```text
                     External services
                            |
        +-------------------+-------------------+
        |                   |                   |
      REST               GraphQL             Feeds
        |                   |                   |
        +-------------------+-------------------+
                            |
                Geeklog Integration Layer
                            |
       +--------------------+--------------------+
       |                    |                    |
 Authentication          Cache               Mapping
       |                    |                    |
 Retry / limits         Validation        Transformation
       |                    |                    |
       +--------------------+--------------------+
                            |
                  Geeklog resource layer
                            |
                      Plugin API
                            |
        +-------------------+-------------------+
        |                   |                   |
      Stories             Blocks             Plugins
```

Plugins should consume common Geeklog integration services instead of independently implementing networking, authentication, caching, rate limiting, and error handling.

---

# 4. Capabilities Geeklog should progressively support

## Priority A — Modernize the existing foundation

- audit the existing syndication subsystem;
- audit Portal Block parsing and caching;
- audit AtomPub and `PLG_invokeService()`;
- identify reusable resource semantics;
- define backward-compatibility requirements;
- introduce a modern HTTP/HTTPS client abstraction;
- REST APIs;
- JSON request and response handling;
- GET, POST, PUT, PATCH, DELETE;
- query parameters and headers;
- API keys;
- HTTP Basic where required;
- Bearer tokens;
- OAuth 2.x;
- configurable timeouts;
- redirects with safe limits;
- TLS verification;
- response-size limits;
- retries with backoff;
- HTTP status handling;
- rate-limit awareness;
- structured error reporting;
- cache with configurable TTL;
- stale-cache fallback;
- per-site configuration for multisite;
- secure credential storage outside templates and public files.

## Priority B — Discovery and automation

- OpenAPI document import;
- OpenAPI generation for Geeklog resources;
- endpoint discovery;
- schema inspection;
- parameter discovery;
- authentication discovery;
- field mapping;
- JSON-path-style field selection or equivalent;
- scheduled synchronization;
- incremental synchronization;
- webhook receiver framework;
- webhook signature verification;
- event dispatch into Plugin API hooks.

## Priority C — Broader interoperability

Already supported formats should be preserved while adding useful modern formats:

- RSS — existing, preserve;
- Atom — existing, preserve;
- RDF-style feeds — existing, preserve where compatibility requires it;
- XML — existing in several subsystems, rationalize;
- CSV — add generic import/export where useful;
- JSON-LD;
- GraphQL client support where real demand exists;
- iCalendar/CalDAV integration where useful;
- ActivityPub;
- generic event streams when practical.

## Priority D — Agent-oriented interoperability

- architecture compatible with AI agents;
- tool-oriented interfaces;
- Model Context Protocol evaluation;
- permission-scoped agent actions;
- read-only access by default;
- auditable write operations;
- human approval for sensitive operations.

MCP or any successor should remain an adapter over stable Geeklog resource APIs rather than replacing them.

---

# 5. External source families Geeklog could exploit

The following list is intentionally broad. It is not a list of mandatory integrations. It maps ecosystems that Geeklog Core or plugins may want to consume.

Provider names are examples only. Availability, pricing, licensing, authentication models, and API terms can change.

## 5.1 Open data and public administration

Possible sources:

- national open-data portals;
- European Union open data;
- local-government datasets;
- demographic statistics;
- public budgets;
- public procurement;
- company registries;
- geographic reference datasets;
- cadastral/land datasets where permitted;
- public transport datasets;
- national statistical institutes.

Uses:

- local information portals;
- civic dashboards;
- automatic statistics in articles;
- directories;
- Maps and Calendar integrations;
- data journalism.

## 5.2 Weather, climate, environment and natural risks

Possible sources:

- forecasts and observations;
- climate archives;
- rainfall and wind;
- air quality;
- pollen and UV;
- drought;
- river and flood data;
- wildfire alerts;
- earthquake feeds;
- storm/cyclone data;
- tides and ocean data;
- snow conditions;
- environmental sensor networks.

Possible ecosystems include national weather agencies, Open-Meteo-style services, NOAA-style public datasets, Copernicus, and local sensor networks.

## 5.3 Geographic, mapping and places data

Possible sources:

- geocoding and reverse geocoding;
- addresses;
- points of interest;
- boundaries;
- routing;
- travel time;
- elevation and terrain;
- map tiles;
- place search;
- business locations.

Possible ecosystems:

- OpenStreetMap;
- Nominatim-compatible services;
- Overpass;
- GeoNames;
- national geographic institutes;
- commercial providers.

**Geographic providers should remain replaceable.** The Maps plugin should not become permanently coupled to one commercial provider.

## 5.4 Transport and mobility

Possible sources:

- GTFS;
- GTFS Realtime;
- trains and buses;
- flight status;
- airports;
- traffic and incidents;
- parking;
- bicycle/scooter sharing;
- EV charging;
- fuel prices;
- maritime data where licensing permits it.

## 5.5 Events, tourism and leisure

Possible sources:

- tourism offices;
- public event feeds;
- ticketing services;
- cultural agendas;
- museums and exhibitions;
- concerts and festivals;
- sports events;
- attractions;
- opening hours;
- accommodation availability where APIs permit it.

Strong candidate for Calendar plugin integration.

## 5.6 News, publishing and syndication

Possible sources:

- RSS and Atom — already consumable in basic form through Portal Blocks;
- newsroom APIs;
- press releases;
- blogs;
- podcasts;
- newsletters exposing feeds;
- structured article APIs;
- content-syndication services.

Geeklog should preserve attribution and avoid automatic republication of copyrighted material without permission.

## 5.7 Knowledge and structured reference data

Possible sources:

- Wikidata;
- Wikipedia APIs;
- DBpedia-style datasets;
- library catalogues;
- authority files;
- dictionaries and thesauri;
- terminology databases;
- open educational resources;
- public-domain archives.

Uses include entity enrichment, knowledge panels, definitions, author pages, and semantic relationships.

## 5.8 Science and research

Possible sources:

- Crossref;
- ORCID;
- OpenAlex-style scholarly graphs;
- PubMed-style databases;
- DOI metadata;
- repositories;
- preprint servers;
- university catalogues.

## 5.9 Books, libraries and cultural heritage

Possible sources:

- ISBN metadata;
- Open Library-style catalogues;
- national libraries;
- museum collections;
- archive catalogues;
- public-domain image collections.

## 5.10 Images, video, audio and media metadata

Possible sources:

- image repositories;
- video platforms;
- podcast directories;
- audio catalogues;
- public-domain media archives;
- media metadata APIs;
- thumbnails;
- oEmbed endpoints.

Geeklog must distinguish **metadata retrieval**, **embedding**, and **copying remote files**.

## 5.11 Social and federated networks

Possible sources:

- ActivityPub;
- Mastodon-compatible servers;
- PeerTube;
- Pixelfed;
- other Fediverse services;
- proprietary social APIs where available.

ActivityPub is strategically attractive because it reduces dependence on individual proprietary networks.

## 5.12 Search engines and indexing

Possible services:

- IndexNow;
- webmaster/search-console APIs;
- indexing APIs where permitted;
- sitemap services;
- crawl status;
- search-performance data.

Uses include the IndexNow plugin, SEO dashboards, crawl monitoring, and content optimization.

## 5.13 Analytics and audience measurement

Possible sources:

- web analytics;
- privacy-oriented analytics;
- server-log analytics;
- search-console data;
- campaign analytics;
- UTM reporting;
- conversion APIs.

Imports should minimize personal data.

## 5.14 Marketing and communication

Possible services:

- email marketing;
- mailing lists;
- transactional email;
- SMS;
- push notifications;
- CRM;
- marketing automation;
- surveys;
- forms.

Provider-specific behavior belongs mainly in plugins while HTTP/authentication infrastructure belongs in the common layer.

## 5.15 E-commerce and product information

Possible sources:

- supplier catalogues;
- PIM;
- ERP;
- inventory systems;
- marketplaces;
- product and price feeds;
- tax services;
- shipping providers;
- payment providers;
- currencies;
- barcode databases.

Potential Store mapping:

```text
remote.product_name -> Store.name
remote.amount       -> Store.price
remote.picture      -> Store.image
remote.sku          -> Store.sku
```

## 5.16 Payments and financial services

Possible services:

- payment gateways;
- bank-data aggregation where legally permitted;
- invoices;
- tax/VAT validation;
- exchange rates;
- accounting tools.

Credentials must never be exposed to templates or public client-side code.

## 5.17 Markets, currencies and economic data

Possible sources:

- FX rates;
- central banks;
- economic indicators;
- equities;
- commodities;
- cryptocurrency prices;
- economic calendars.

Licensing and redistribution conditions must be checked provider by provider.

## 5.18 Jobs, companies and professional data

Possible sources:

- job boards;
- company registries;
- professional directories;
- corporate filings;
- certification databases.

## 5.19 Real estate and property

Possible sources:

- listings;
- open transaction data;
- energy ratings;
- cadastral datasets;
- rental indices;
- geographic property information.

## 5.20 Food, recipes and nutrition

Possible sources:

- food composition databases;
- barcode databases;
- allergens;
- recipe APIs;
- agricultural data;
- open food databases.

## 5.21 Health and public-health data

Possible sources:

- public-health datasets;
- legally reusable drug references;
- health alerts;
- epidemiological statistics;
- public practitioner or facility directories.

This category requires stronger provenance, safety, legal, and privacy controls.

## 5.22 Energy and utilities

Possible sources:

- electricity generation mix;
- carbon intensity;
- energy prices;
- solar production;
- authorized smart-meter data;
- EV charging;
- water data;
- utility outages.

## 5.23 IoT, sensors and home automation

Possible sources:

- controlled MQTT adapters;
- weather stations;
- environmental sensors;
- home automation;
- energy monitors;
- industrial sensors.

Unrestricted public frontend access to private IoT networks should be avoided.

## 5.24 Security and reputation services

Possible sources:

- CAPTCHA;
- spam/IP reputation;
- malware URL checks;
- vulnerability feeds;
- security advisories;
- certificate transparency.

Reputation data should be treated as signals, not unquestionable truth.

## 5.25 Authentication and identity providers

Possible services:

- OpenID Connect;
- OAuth identity providers;
- enterprise SSO;
- passkey-compatible systems;
- directory services.

This area deserves a dedicated security model rather than generic content-import settings.

## 5.26 Translation and linguistic services

Possible services:

- translation;
- terminology;
- spelling;
- grammar;
- language detection;
- transliteration.

Human review should remain possible before publication.

## 5.27 Artificial intelligence services

Possible services:

- text generation;
- summarization;
- classification;
- tagging;
- embeddings;
- semantic search;
- image analysis;
- transcription;
- text-to-speech;
- moderation assistance;
- retrieval systems;
- local/self-hosted models.

Geeklog should remain provider-neutral:

```text
Geeklog feature
      |
Geeklog AI adapter
      |
+-----+------+-----------+
|            |           |
Provider A Provider B Local model
```

AI transformations should retain provenance where appropriate and should not silently overwrite editorial originals.

## 5.28 Calendars and productivity

Possible sources:

- iCalendar;
- CalDAV-compatible systems;
- calendar APIs;
- task systems;
- project-management services.

## 5.29 Documents, storage and collaboration

Possible sources:

- cloud drives;
- document-management systems;
- object storage;
- collaborative documents;
- file-sharing systems;
- conversion services.

Remote files must still undergo MIME, permission, size, and security validation.

## 5.30 Developer and software ecosystems

Possible sources:

- GitHub;
- GitLab;
- package repositories;
- release feeds;
- changelogs;
- vulnerability databases;
- CI status;
- issue trackers.

This is particularly relevant to a future Geeklog Plugin Store or update catalogue.

---

# 6. External-data operating modes

Geeklog should explicitly distinguish several modes.

## Mode 1 — Live remote display

```text
Remote API -> cache -> template/block
```

The remote provider remains the source of truth.

Examples: weather, rates, transport, service status.

## Mode 2 — Cached remote data

```text
Remote API -> local cache -> Geeklog display
```

Useful when calls are slow, costly, rate-limited, or unreliable.

## Mode 3 — Import

```text
Remote source -> mapping -> Geeklog database
```

Geeklog stores a local copy.

Examples: events, products, directory entries, metadata.

## Mode 4 — Synchronization

```text
Remote API <-> Geeklog
```

Requires conflict rules, timestamps, source IDs, and ownership semantics.

## Mode 5 — Event-driven update

```text
External service -> webhook -> Geeklog event -> plugin action
```

Examples: payment completed, shipment sent, release published, remote content changed.

---

# 7. Evolution of Portal Block into Remote Data Block

The Remote Data Block should be considered a modernization of an existing Geeklog feature.

Conceptual administrator flow:

```text
Add block
  -> Portal / Remote Data
  -> choose source type
  -> choose registered source
  -> choose endpoint/feed
  -> define parameters
  -> map fields
  -> choose template
  -> choose cache duration
```

Possible source types:

```text
RSS
Atom
JSON URL
REST endpoint
OpenAPI operation
```

Example:

```text
Source: Crypto prices
Remote field: bitcoin.eur
Geeklog variable: price
Template: Bitcoin: {price} EUR
Cache: 5 minutes
```

Existing RSS/RDF Portal Blocks should continue working without requiring migration to advanced connector configuration.

---

# 8. Generic registered data-source concept

A shared Integration Layer could allow administrators to register reusable sources.

Example:

```text
Name: Weather France
Type: REST
Base URL: https://api.example.org
Authentication: API key
Cache TTL: 15 minutes
Timeout: 5 seconds
Fallback: stale cache
```

Plugins could then request:

```text
source: Weather France
endpoint: /forecast
parameters:
  latitude: ...
  longitude: ...
```

Credentials remain outside plugin templates.

---

# 9. OpenAPI as modernization of service introspection

OpenAPI support could allow Geeklog to inspect an external API and discover:

- endpoints;
- methods;
- parameters;
- schemas;
- authentication requirements;
- request bodies;
- response formats;
- webhooks.

It could also allow Geeklog to document its own modern REST resources.

Conceptual flow:

```text
OpenAPI document
       |
Geeklog connector
       |
+------+-----------------------------+
| discover operations               |
| discover parameters               |
| discover schemas                  |
| configure authentication          |
| create field mappings             |
+-----------------------------------+
       |
Plugin / Remote Block / Scheduled Sync
```

OpenAPI accelerates configuration; it must not bypass security checks.

---

# 10. Webhooks and Geeklog events

Incoming webhooks deserve a common Core mechanism.

Possible route:

```text
POST /api/webhooks/{connector}
```

The Integration Layer should:

1. identify the registered connector;
2. enforce appropriate transport requirements;
3. verify signatures;
4. limit request size;
5. validate payloads;
6. prevent replay where supported;
7. log safely;
8. dispatch a normalized Geeklog event;
9. let plugins subscribe through the Plugin API.

Plugins should not each invent public webhook endpoints with inconsistent security.

---

# 11. Data provenance

Imported or transformed external information should ideally retain:

```text
source_provider
source_url
source_id
source_timestamp
retrieved_at
license
attribution
local_modified_at
sync_status
```

This becomes increasingly important when information is aggregated, summarized, translated, or processed by AI.

---

# 12. Security requirements

External integration expands the attack surface.

The common layer should protect against:

- SSRF;
- requests to localhost/private networks from untrusted URLs;
- malicious redirects;
- excessive response sizes;
- slow endpoints;
- decompression bombs;
- malformed JSON/XML;
- XXE;
- credential leakage;
- secrets in logs;
- unauthorized webhook calls;
- replay attacks;
- unsafe deserialization;
- HTML/script injection from remote data;
- uncontrolled file downloads.

Ordinary content editors should not automatically be allowed to configure arbitrary server-side URLs.

---

# 13. Privacy and legal requirements

Every connector should consider:

- terms of service;
- redistribution rights;
- copyright;
- database rights;
- API licensing;
- attribution;
- GDPR and privacy law;
- retention;
- user consent;
- transfer of personal data to third parties.

Technical access does not imply republication rights.

---

# 14. Multisite requirements

External integrations must preserve Geeklog multisite isolation.

Each site may need separate:

- provider accounts;
- API keys;
- OAuth credentials;
- cache namespaces;
- synchronization states;
- webhook secrets;
- rate-limit states;
- enabled connectors.

A credential configured for Site A must never silently become available to Site B.

---

# 15. Observability and administration

A future integration administration page should expose useful operational information:

```text
Connector
Status
Last successful request
Last failure
Last synchronization
Cache age
Response time
Rate-limit remaining
Next scheduled sync
Authentication status
```

Administrators should be able to test a connector without exposing its credentials.

---

# 16. Suggested implementation phases

## Phase 0 — Audit what already exists

Before writing a replacement system:

- document syndication formats and extension points;
- document Portal Block parsing and caching;
- document AtomPub routes and authentication;
- document `PLG_invokeService()` operations and plugin implementations;
- identify existing cron/scheduled mechanisms;
- identify reusable remote-authentication code;
- define compatibility tests.

This phase prevents duplicating existing Core capabilities.

## Phase 1 — Modern transport and resource foundation

Build on existing concepts:

- common modern HTTP client;
- REST + JSON representation;
- reusable plugin resource layer;
- authentication abstraction;
- secure credentials;
- modern cache;
- timeouts and retries;
- logging;
- multisite isolation;
- retain AtomPub compatibility where practical.

## Phase 2 — Modernize Portal Blocks and add mapping

- evolve Portal Blocks into Remote Data Blocks;
- preserve RSS/RDF behavior;
- registered remote sources;
- endpoint definitions;
- field mapping;
- scheduled retrieval;
- imports;
- templates for structured remote data.

## Phase 3 — OpenAPI and webhooks

- OpenAPI discovery;
- OpenAPI publication for Geeklog resources;
- schema-aware configuration;
- normalized webhook receiver;
- Geeklog event dispatch.

## Phase 4 — Advanced protocols

Add according to real demand:

- JSON-LD;
- GraphQL client;
- ActivityPub;
- deeper calendar interoperability;
- event/streaming protocols.

## Phase 5 — Agent interoperability

Expose controlled resource operations to agents through stable Geeklog APIs and evaluate:

- MCP adapters;
- tool discovery;
- scoped permissions;
- audited writes;
- human approval for sensitive operations.

---

# 17. Recommended architectural rule for plugins

Future plugins should ideally declare needs such as:

```text
I need:
- HTTP client
- credential X
- cache Y
- scheduled job Z
```

rather than implementing each component internally.

Examples:

```text
Store
   |
Geeklog Integration Layer
   |
Supplier / ERP / Payment / Shipping APIs
```

```text
Maps
   |
Geeklog Integration Layer
   |
Geocoder / Route / Places / Open Data APIs
```

```text
Calendar
   |
Geeklog Integration Layer
   |
Events / iCalendar / Tourism / Transport APIs
```

```text
Analytics
   |
Geeklog Integration Layer
   |
Analytics / Search / Campaign APIs
```

One solid Integration Layer can therefore improve many plugins simultaneously.

---

# 18. What should not go into Geeklog Core

The Core should generally not contain permanent hard-coded support for every provider.

Avoid:

```text
COM_googleWeather()
COM_stripePayment()
COM_openaiSummary()
COM_someVendorProducts()
```

Prefer generic primitives:

```text
HTTP client
Credentials
OAuth
Cache
Scheduler
Mapping
Webhooks
Events
Resource API
```

Provider-specific behavior can live in plugins or connector packages.

---

# 19. Strategic outcome

The objective is larger than simply "support APIs".

Geeklog already demonstrates an historical philosophy of interoperability through syndication, Portal Blocks, webservices, and its Plugin API. The 2030 objective should extend that philosophy rather than replace it.

```text
                External world
                      |
         +------------+------------+
         |                         |
      DATA IN                   DATA OUT
         |                         |
feeds / APIs / events       feeds / APIs / events
         |                         |
         +------------+------------+
                      |
             Geeklog resource layer
                      |
                 Plugin API
                      |
        Content + Users + Plugins
                      |
          Search / AI / Agents
```

The strongest long-term principle is therefore:

> **Geeklog should not try to own every function. It should preserve and modernize its existing interoperability strengths, then become exceptionally good at connecting trusted external functions and data to its content, users, plugins, and publishing workflow.**

This turns interoperability into a platform capability instead of a collection of isolated plugin features.

---

## Living document

This list should remain open-ended.

External services will appear, disappear, change business models, or move to new protocols before 2030. The provider list is therefore less important than an integration architecture that lets Geeklog adopt useful new sources without redesigning the CMS every time.

Likewise, future development should periodically re-audit the Geeklog Core before adding a new integration feature. Historical mechanisms may already provide part of the required architecture and should be modernized rather than duplicated whenever that remains technically sound.
