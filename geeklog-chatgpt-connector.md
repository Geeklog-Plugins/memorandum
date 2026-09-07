# Geeklog ChatGPT Connector — Plugin and Connector Concept

Status: **Architectural concept**

This document defines a future integration between Geeklog and ChatGPT using a secure Geeklog-side API/resource layer and an external ChatGPT connector.

The objective is not to embed a generic chatbot inside Geeklog. The objective is to let ChatGPT discover, read and eventually perform authorized Geeklog actions through structured interfaces while preserving Geeklog as the system of record.

The connector must fit the wider architecture already documented in this repository:

- existing Geeklog Plugin API;
- Plugin Content Interoperability Contract;
- future common Data/API conventions;
- future common Events contract;
- Hub as internal relationship/context orchestrator;
- Hello as communication layer for registered users;
- IndexNow as indexing transport;
- future provider-neutral agent adapters.

---

## 1. Core principle

> **Geeklog owns the data and business rules. Shared Geeklog contracts expose capabilities. Hub provides content context. Hello communicates with registered users. IndexNow submits changed URLs. The Connector securely exposes selected capabilities to ChatGPT and other external clients.**

The Connector must not become a second internal application architecture.

---

## 2. Architectural position

Preferred long-term architecture:

```text
                      User
                       |
                       v
                    ChatGPT
                       |
                       v
               ChatGPT Connector
                       |
              HTTPS / structured tools
                       |
                       v
          Geeklog external API / resource layer
                       |
       +---------------+---------------+
       |               |               |
       v               v               v
      Hub            Hello        direct resources
 context/relations communication  Core + plugins
       |               |               |
       +---------------+---------------+
                       |
                 Geeklog Plugin API
                       |
       Stories / Static Pages / Maps / Documents
       Videos / Forum / Store / IndexNow / others
```

The Connector is an **external gateway**, not the owner of relationships, newsletters, indexing, commerce or other plugin logic.

---

## 3. No Core modification required for the first implementation

The initial implementation should use a normal Geeklog plugin or compatibility layer and reuse existing Geeklog mechanisms wherever practical.

Before inventing a new parallel API, implementation must evaluate the existing Geeklog webservice/resource architecture, including `PLG_invokeService()` and the historical AtomPub service layer.

The Memorandum already identifies a desirable evolution:

```text
Geeklog resource layer
        |
        +--> AtomPub compatibility
        +--> REST / JSON
        +--> future MCP / agent adapter
```

Therefore the first Connector implementation should:

1. reuse existing Plugin APIs and service semantics where practical;
2. provide modern JSON/HTTPS exposure as an adapter;
3. identify missing generic integration points;
4. propose Core changes only when a reusable need is proven.

No ChatGPT-specific Core modification should be required.

---

## 4. Shared contracts, not Connector-specific plugin APIs

The Connector must consume generic Geeklog contracts.

It should **not** introduce callbacks such as:

```php
plugin_connectorCapabilities_maps()
plugin_connectorTools_documents()
```

when the same information can be expressed through shared capability discovery, Item Info, search, services or future common Data/API conventions.

The same plugin capability should be reusable by:

```text
Hub
Hello
IndexNow
Connector
Search / Recommendations
future external clients
```

This prevents every consumer from creating its own integration contract.

---

## 5. Responsibilities by component

### Content-owning plugins and Core

Examples:

- Stories;
- Static Pages;
- Maps;
- Documents;
- Videos;
- Forum;
- Store.

They remain responsible for:

- their own data;
- permissions;
- canonical URLs;
- validation;
- business rules;
- specialized rendering;
- create/update/delete behavior.

### Hub

Hub is responsible for:

- pillars;
- stable `type + id` relationships;
- related-content context;
- dependency graph;
- orphan/broken relationship diagnostics;
- affected-page detection;
- editorial suggestions;
- delegation to specialized services.

The Connector must consume Hub capabilities where useful instead of duplicating Hub logic.

### Hello

Hello is responsible for communication with registered users:

- campaigns;
- newsletters and digests;
- recipient groups;
- queueing;
- throttling;
- delivery;
- unsubscribe/resubscribe;
- open tracking;
- click tracking;
- campaign and subscriber statistics.

The Connector may expose authorized Hello operations but must not directly read or write Hello tables.

### IndexNow

IndexNow remains responsible for:

- URL queueing;
- batch submission;
- deduplication;
- provider interaction;
- submission status.

The Connector or Hub may request IndexNow actions through its public service surface but must not reproduce its transport logic.

---

## 6. Connector use of Hub

Hub should be the preferred source when the request is about **relationships or thematic context**.

Example:

> Analyze everything connected to the Rocket Stove pillar and tell me what needs attention.

Possible flow:

```text
ChatGPT
   ↓
Connector
   ↓
Hub context
   ↓
pillar + related items + diagnostics + suggestions
   ↓
Connector retrieves selected full items only when needed
   ↓
ChatGPT analysis
```

Conceptual Hub-facing tools might include:

```text
get_hub_context
get_related_items
get_affected_items
get_integrity_report
get_hub_suggestions
```

The exact API names are not frozen.

The Connector MUST NOT maintain its own Hub relationship graph.

---

## 7. Connector use of Hello

Hello should be treated as a communication/action plugin, not as a content plugin.

Potential read capabilities:

```text
hello.campaigns.read
hello.stats.read
hello.queue.read
hello.subscribers.summary
```

Potential write/action capabilities:

```text
hello.campaigns.draft
hello.campaigns.test
hello.campaigns.queue
hello.campaigns.pause
hello.campaigns.resume
hello.campaigns.stop
```

Sending a live campaign must be a high-risk operation with an explicit permission distinct from campaign drafting.

Potential high-risk scope:

```text
hello.campaigns.send
```

Subscriber personally identifiable information must be separately protected.

For example:

```text
hello.stats.read
```

must not automatically imply:

```text
hello.personal_data.read
```

The default Connector should prefer aggregated campaign/subscriber statistics when detailed personal data is not required.

---

## 8. Multi-plugin editorial workflow

A key future use case is cross-plugin editorial assistance without cross-plugin coupling.

Example request:

> Prepare a newsletter about the latest Rocket Stove content.

Possible flow:

```text
Hub
  ↓
relevant new/updated content
  ↓
Connector
  ↓
ChatGPT drafts summary/campaign copy
  ↓
Hello creates campaign draft
  ↓
Hello sends administrator test
  ↓
human validation
  ↓
Hello queues/sends campaign
```

Hub decides **what belongs together**.

Hello decides **how and to whom it is sent**.

ChatGPT assists with synthesis and wording.

Connector provides secure access between them.

---

## 9. Direct resource operations

Not every request should go through Hub.

Direct resource tools are appropriate for operations such as:

```text
get_story
search_stories
update_story
get_staticpage
update_staticpage
search_documents
get_document
search_markers
get_marker
search_videos
get_video
search_products
get_product
```

These operations should delegate to the owning Core/plugin APIs or service layer.

Hub should be called only when Hub-specific context, relations or diagnostics are needed.

---

## 10. Capability discovery

The external API should expose what a specific Geeklog installation actually supports.

Capability discovery should combine:

- existing Plugin API detection;
- installed/enabled plugin state;
- generic declared capabilities where runtime inference is insufficient;
- Connector credential scopes;
- Geeklog ACL permissions.

Conceptual result:

```json
{
  "site": "example.org",
  "capabilities": [
    "stories.read",
    "staticpages.read",
    "hub.context.read",
    "hello.campaigns.read",
    "indexnow.status.read"
  ]
}
```

Capability declaration belongs to shared Geeklog architecture, not specifically to Hub or Connector.

---

## 11. Initial read-only tools

A first proof of concept should remain small.

Recommended baseline:

```text
get_site_info
get_capabilities
list_topics
search_stories
get_story
search_staticpages
get_staticpage
list_plugins
```

If Hub is installed and exposes the required service:

```text
get_hub_context
get_related_items
get_integrity_report
```

If Hello is installed:

```text
list_hello_campaigns
get_hello_campaign_stats
get_hello_queue_status
```

No personal subscriber details should be exposed in the default proof of concept.

---

## 12. Controlled write progression

### Phase 1 — Read only

Validate:

- authentication;
- ACL;
- capability discovery;
- stable JSON schemas;
- Hub context reuse;
- Hello summary/statistics exposure;
- multisite isolation.

### Phase 2 — Draft creation and safe updates

Add:

```text
create_story_draft
update_story
create_staticpage_draft
update_staticpage
create_hello_campaign_draft
```

### Phase 3 — Test actions

Add controlled actions such as:

```text
send_hello_campaign_test
```

### Phase 4 — Explicit publishing/sending

Separate permissions for:

```text
publish_story
publish_staticpage
send_hello_campaign
```

A generic update call must never implicitly publish content or send a campaign.

### Phase 5 — Broader plugin actions

Expose explicit domain operations from compatible plugins only where stable public interfaces exist.

---

## 13. Authentication and authorization

Authentication and authorization remain separate.

Possible credential models:

- revocable personal access token;
- service token;
- OAuth-style authorization;
- future agent/client credentials.

Every credential should be:

- identifiable;
- revocable;
- scoped;
- optionally expiring;
- associated with a Geeklog identity or service identity;
- auditable.

Authorization concept:

```text
Allowed operation
=
Connector scope
AND
Geeklog ACL
AND
resource/plugin-specific permission
```

Connector scopes may only narrow access. They must never expand Geeklog permissions.

---

## 14. Risk classes

### Low risk

- search/read public or authorized content;
- list topics/plugins;
- read Hub context;
- read aggregated Hello campaign statistics;
- read IndexNow status.

### Medium risk

- create drafts;
- update unpublished content;
- create Hello campaign drafts;
- send administrator tests.

### High risk

- publish content;
- send a live newsletter;
- delete content;
- modify subscribers;
- access subscriber personal data;
- modify configuration;
- manage users;
- install/disable plugins;
- bulk mutations.

High-risk actions require explicit scopes and strong auditability.

---

## 15. Security principles

Minimum requirements:

- HTTPS only in production;
- strict authentication;
- scoped and revocable credentials;
- rate limiting;
- request-size limits;
- input validation;
- output filtering;
- Geeklog ACL enforcement;
- plugin-specific permission checks;
- audit logging;
- safe error responses;
- multisite isolation;
- no arbitrary SQL;
- no arbitrary PHP execution;
- no shell execution;
- no unrestricted filesystem access;
- no implicit publication or sending;
- explicit protection of personal subscriber/user data.

The Connector should expose domain actions, not generic execution primitives.

Do not expose:

```text
run_sql
run_php
execute_shell
read_any_file
write_any_file
```

---

## 16. Audit trail

Sensitive operations must be attributable.

A useful audit record includes:

```text
timestamp
site
identity
client/token id
operation
object type
object id
result
correlation id
risk class
```

For Hello actions, the audit should distinguish clearly between:

```text
campaign draft created
campaign test sent
campaign queued
campaign live send initiated
campaign paused/resumed/stopped
```

---

## 17. Multisite

The Connector must follow [`multisite-development-principles.md`](multisite-development-principles.md).

Each request must use the active site's:

- configuration;
- database mapping;
- permissions;
- plugin state;
- credentials;
- audit context.

Credentials and permissions must never leak across sites sharing plugin files.

Cross-site administration should be explicit and should not arise accidentally from a shared installation.

---

## 18. Provider independence

Although ChatGPT is the first target, the Geeklog-side resource/API layer must remain provider-neutral.

Possible future consumers:

```text
ChatGPT
other AI assistants
MCP-compatible clients
n8n / Make / Zapier-style automation
mobile applications
administrative integrations
trusted custom clients
```

ChatGPT-specific schemas and UX belong in the external connector adapter.

---

## 19. Relationship with future Data and Events APIs

The Connector should be considered an adapter over shared Geeklog architecture.

Short term:

```text
existing Plugin API
+ PLG_invokeService
+ compatibility adapters
        ↓
external JSON resource layer
        ↓
Connector
```

Long term:

```text
common Geeklog Data API
+ common Geeklog Events
        ↓
REST / JSON / agent adapters
        ↓
Connector
```

The Connector should become thinner as Geeklog's shared resource layer improves.

---

## 20. Relationship with future Marketing

Hello currently owns newsletter delivery and registered-user communication.

A future Marketing plugin may later own:

- consent projections;
- segmentation;
- tags;
- scoring;
- attribution;
- automation rules.

The Connector must keep those responsibilities separate.

Possible future flow:

```text
Marketing chooses/defines segment
        ↓
Hello delivers campaign
        ↓
Connector exposes authorized operations
        ↓
ChatGPT assists with analysis/copy
```

Hello must not be replaced prematurely by speculative Marketing features.

---

## 21. Proof-of-concept success criteria

The first useful milestone is achieved when ChatGPT can securely:

1. identify the Geeklog site and available capabilities;
2. search and retrieve stories/static pages;
3. retrieve Hub context when Hub is installed;
4. read non-sensitive Hello campaign statistics when Hello is installed;
5. read IndexNow status when available;
6. respect Geeklog ACL and Connector scopes;
7. operate safely in multisite context;
8. do all of the above without direct SQL access to another plugin's tables.

---

## 22. Recommended implementation sequence

1. Audit existing AtomPub/resource/service architecture and `PLG_invokeService()`.
2. Define the smallest provider-neutral external JSON resource layer.
3. Define authentication, token storage and audit model.
4. Define generic capability discovery shared with other consumers.
5. Implement read-only Core/Static Pages resources.
6. Expose Hub read services without duplicating Hub logic.
7. Expose Hello aggregate campaign/status services without exposing personal data by default.
8. Expose IndexNow status/service operations.
9. Build the ChatGPT connector adapter.
10. Test Geeklog 2.1.1 and 2.2.2 compatibility where practical.
11. Perform a security review.
12. Add draft/update actions.
13. Add test actions.
14. Add explicit publication/live-send actions only after the permission model is proven.

---

## Project rule

> **The Connector is a secure external adapter over Geeklog capabilities. It must reuse Hub for relationships, Hello for communication, IndexNow for indexing transport, and shared Geeklog contracts for plugin interoperability. It must not create a competing internal API model for each plugin or consumer.**
