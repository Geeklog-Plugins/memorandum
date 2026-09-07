# Geeklog ChatGPT Connector — Plugin and Connector Concept

Status: **Architectural concept**

This document defines a future integration between Geeklog and ChatGPT using a secure Geeklog-side API/resource layer and an external ChatGPT connector.

The objective is not to embed a generic chatbot inside Geeklog. The objective is to let ChatGPT discover, read and eventually perform authorized Geeklog actions through structured interfaces while preserving Geeklog as the system of record.

The connector must fit the wider architecture already documented in this repository:

- existing Geeklog Plugin API;
- Plugin Content Interoperability Contract;
- existing Geeklog webservice/service layer;
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
          Geeklog Plugin + Service APIs
                       |
       Stories / Static Pages / Maps / Documents
       Videos / Forum / Store / IndexNow / others
```

The Connector is an **external gateway**, not the owner of relationships, newsletters, indexing, commerce or other plugin logic.

---

## 3. Existing Geeklog mechanisms that can be reused

Review of Geeklog 2.2.x Core shows that the Connector does **not** need a completely new plugin capability mechanism from zero.

Geeklog already contains several useful building blocks.

### 3.1 Enabled-plugin registry

Geeklog already maintains the list of active plugins in `$_PLUGINS`.

This provides the first level of discovery:

```text
Which plugins are installed and enabled on this site?
```

The Connector should reuse active Geeklog site context instead of maintaining its own plugin registry.

### 3.2 Existing Plugin API feature detection

Many capabilities can already be inferred by testing whether a normal Geeklog Plugin API callback exists.

Examples:

```text
plugin_getiteminfo_PLUGIN
plugin_getrelateditems_PLUGIN
plugin_dopluginsearch_PLUGIN
plugin_idToURL_PLUGIN
plugin_getBlocks_PLUGIN
plugin_getfeednames_PLUGIN
plugin_getfeedcontent_PLUGIN
plugin_collectSitemapItems_PLUGIN
```

These callbacks can be mapped to generic capability categories without requiring a new declaration from the plugin.

Conceptually:

```text
plugin_getiteminfo_*      -> content.read / content.collection
plugin_dopluginsearch_*   -> content.search
plugin_getrelateditems_*  -> content.related
plugin_idToURL_*          -> content.url.resolve
```

This should be the preferred path whenever the capability can be inferred reliably.

### 3.3 Existing webservice enablement callback

Geeklog already provides:

```php
plugin_wsEnabled_PLUGIN()
```

through:

```php
PLG_wsEnabled($type)
```

This is already a basic declaration by a plugin that it exposes services through Geeklog's webservice layer.

It should be treated as an existing capability signal rather than replaced by a Connector-specific equivalent.

### 3.4 Existing generic service dispatcher

Geeklog already provides:

```php
PLG_invokeService($type, $action, $args, &$output, &$svc_msg)
```

The dispatcher resolves an action dynamically as:

```text
service_ACTION_PLUGIN()
```

and invokes it when the service function exists and `PLG_wsEnabled($type)` is true.

This is highly relevant to the future Connector because it already separates:

```text
consumer
   ↓
plugin + action
   ↓
PLG_invokeService()
   ↓
service_ACTION_PLUGIN()
   ↓
plugin business logic
```

The Connector should therefore prefer this service abstraction for plugin-specific actions where it is appropriate rather than inventing direct calls into plugin internals.

### 3.5 Existing service result contract

`PLG_invokeService()` already standardizes broad service results with constants such as:

```text
PLG_RET_OK
PLG_RET_ERROR
PLG_RET_PERMISSION_DENIED
PLG_RET_AUTH_FAILED
PLG_RET_PRECONDITION_FAILED
```

Services also use output and service-message structures.

This provides a useful starting point for normalizing future JSON error and result responses.

### 3.6 Existing AtomPub introspection

Geeklog's AtomPub webservice implementation already contains an introspection mode.

It:

- inspects Story plus active plugins;
- asks `PLG_wsEnabled()` whether each plugin exposes webservices;
- publishes a service collection for enabled providers;
- invokes the `getTopicList` service where available.

This proves that Geeklog already has the architectural concept:

```text
client
   ↓
service discovery
   ↓
plugin service
```

The future Connector should modernize and extend this idea instead of creating unrelated discovery infrastructure.

### 3.7 Existing standard service actions

The current AtomPub layer already maps HTTP operations to plugin services approximately as follows:

```text
GET     -> service_get_PLUGIN
POST    -> service_submit_PLUGIN
PUT     -> service_submit_PLUGIN with edit context
DELETE  -> service_delete_PLUGIN
```

It also uses:

```text
service_getTopicList_PLUGIN
```

for introspection/category information.

Stories and Static Pages already implement substantial parts of this pattern.

Therefore the first Connector proof of concept can use Stories and Static Pages as reference implementations when evaluating a modern JSON resource layer.

---

## 4. What Geeklog does not currently provide

The existing service layer is useful, but it is **not yet a complete capability contract for modern clients or agents**.

The current AtomPub introspection can identify which plugins expose webservices, but it does not provide a complete machine-readable declaration of:

- every action exposed by the plugin;
- semantic capability names;
- input argument schemas;
- output schemas;
- read versus write classification;
- destructive or sensitive action classification;
- required Geeklog feature/permission;
- whether human confirmation is recommended;
- whether personal data can be returned;
- pagination/filtering semantics;
- API stability/version of an action.

For example, knowing that `maps` has webservices enabled does not tell a client whether it supports:

```text
content.search
geo.nearby
marker.update
```

or what arguments `geo.nearby` expects.

This missing descriptive metadata is the main capability-discovery gap to solve.

---

## 5. Shared contracts, not Connector-specific plugin APIs

The Connector must consume generic Geeklog contracts.

It should **not** introduce callbacks such as:

```php
plugin_connectorCapabilities_maps()
plugin_connectorTools_documents()
```

when the same information can be expressed through existing Plugin APIs, Geeklog services or a shared capability descriptor.

The same plugin capability should be reusable by:

```text
Hub
Hello
IndexNow
Connector
Search / Recommendations
future REST clients
future MCP / agent clients
```

This prevents every consumer from creating its own integration contract.

---

## 6. Proposed capability-discovery model

Capability discovery should be built in layers, reusing existing Geeklog facilities first.

### Layer 1 — infer standard capabilities

The discovery layer detects existing callbacks and service support.

Example:

```text
plugin_getiteminfo_maps exists
    -> content.read

plugin_dopluginsearch_maps exists
    -> content.search

plugin_getrelateditems_maps exists
    -> content.related

plugin_idToURL_maps exists
    -> content.url.resolve

plugin_wsEnabled_maps returns true
    -> services.available
```

No new code is required in Maps for capabilities that can be inferred safely.

### Layer 2 — inspect known service actions

If webservices are enabled, the shared layer may detect known existing service functions such as:

```text
service_get_maps
service_submit_maps
service_delete_maps
service_getTopicList_maps
```

This may be useful for compatibility and auditing.

However, simple `function_exists()` discovery must not automatically make a sensitive action available to an external client.

Existence means only:

> the implementation is present.

It does not mean:

> this Connector credential is authorized to use it.

### Layer 3 — explicit metadata only where inference is insufficient

Specialized actions require an explicit shared descriptor.

Examples:

```text
maps.geo.nearby
hub.context.read
hello.campaigns.test
indexnow.submit
```

The exact implementation is not frozen.

Two possibilities should be evaluated.

#### Option A — extend service introspection

A plugin could expose a reserved service such as:

```text
service_capabilities_PLUGIN
```

or another generic service-description action invoked through `PLG_invokeService()`.

Conceptual call:

```php
PLG_invokeService(
    'maps',
    'capabilities',
    array(),
    $output,
    $svc_msg
);
```

This has the advantage of reusing the existing service architecture without adding a new Plugin API family.

#### Option B — introduce a generic Plugin API callback

If a dedicated callback proves cleaner, a future convention could be:

```php
plugin_getcapabilities_PLUGIN()
```

or a similarly named shared Geeklog callback.

This must be a **generic Geeklog capability declaration**, not a Connector callback.

Before choosing Option B, implementation should test whether extending `PLG_invokeService()` introspection is sufficient.

### Preferred evaluation order

```text
1. existing Plugin API inference
        ↓
2. existing PLG_wsEnabled / service discovery
        ↓
3. shared service-description extension
        ↓
4. new generic plugin_getcapabilities_* callback only if needed
```

This avoids unnecessary Core/API expansion.

---

## 7. Capability descriptor requirements

Whether implemented as a service or future Plugin API callback, the descriptor should be able to express more than a flat list.

Conceptual example:

```php
array(
    'geo.nearby' => array(
        'service' => 'nearby',
        'mode' => 'read',
        'permission' => 'maps.view',
        'risk' => 'low',
        'arguments' => array(
            'latitude' => 'number',
            'longitude' => 'number',
            'radius_km' => 'number',
            'category' => 'string|null'
        )
    ),

    'marker.update' => array(
        'service' => 'updateMarker',
        'mode' => 'write',
        'permission' => 'maps.edit',
        'risk' => 'medium'
    )
);
```

The schema shown above is illustrative, not frozen.

At minimum, a future descriptor should be able to communicate:

```text
capability id
service/action name
read/write classification
required permission
risk classification
argument schema
result schema or result type
optional description
version/stability
```

Later additions may include:

```text
confirmation recommendation
personal-data flag
bulk-action flag
idempotency indication
pagination support
filtering support
rate-limit hints
```

---

## 8. Technical capability versus authorized capability

This distinction is essential.

A plugin may technically implement:

```text
hello.campaigns.send
```

while the current Connector credential is allowed only:

```text
hello.campaigns.read
hello.stats.read
hello.campaigns.draft
hello.campaigns.test
```

The public capability endpoint must therefore expose the **effective authorized capability set**, not merely everything present in PHP.

Conceptually:

```text
implemented capability
        AND
plugin enabled state
        AND
Connector credential scope
        AND
Geeklog ACL
        AND
plugin/resource permission
        =
externally visible capability
```

A sensitive action that the caller cannot use should normally not be advertised as an available tool.

---

## 9. Responsibilities by component

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

## 10. Connector use of Hub

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

Conceptual Hub-facing capabilities might include:

```text
hub.context.read
hub.related.read
hub.affected.read
hub.integrity.read
hub.suggestions.read
```

Hub should expose these through shared services/capability metadata rather than Connector-specific callbacks.

The Connector MUST NOT maintain its own Hub relationship graph.

---

## 11. Connector use of Hello

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

Potential high-risk capability:

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

## 12. Multi-plugin editorial workflow

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

## 13. Direct resource operations

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

## 14. External capability endpoint

The external JSON/resource layer should expose what a specific Geeklog installation and authenticated caller actually support.

Conceptual endpoint:

```text
GET /api/geeklog/v1/capabilities
```

Conceptual result:

```json
{
  "site": "example.org",
  "resources": {
    "stories": [
      "content.read",
      "content.search"
    ],
    "maps": [
      "content.read",
      "content.search",
      "geo.nearby"
    ],
    "hub": [
      "hub.context.read"
    ],
    "hello": [
      "hello.campaigns.read",
      "hello.stats.read",
      "hello.campaigns.draft",
      "hello.campaigns.test"
    ]
  }
}
```

The result must be filtered by permissions before it is returned.

It should not simply dump every PHP function detected on the server.

---

## 15. Mapping capabilities to ChatGPT tools

The Connector adapter can translate effective Geeklog capabilities into tools understandable by ChatGPT.

Example:

```text
Geeklog capability
    maps.geo.nearby

        ↓ descriptor

service
    nearby

arguments
    latitude
    longitude
    radius_km
    category

        ↓ Connector

ChatGPT tool
    maps_nearby(...)
```

This means tool schemas can eventually be generated from shared Geeklog capability metadata instead of being manually duplicated in every Connector release.

The same descriptors may later generate or assist:

```text
REST documentation
OpenAPI descriptions
MCP tool descriptions
administration capability reports
Hub interoperability audits
```

---

## 16. Initial read-only tools

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

Stories and Static Pages are especially useful reference resources because Geeklog already implements webservice/service patterns for them.

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

## 17. Controlled write progression

### Phase 1 — Read only

Validate:

- authentication;
- ACL;
- capability discovery;
- service invocation;
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

Expose explicit domain operations from compatible plugins only where stable public interfaces and capability metadata exist.

---

## 18. Authentication and authorization

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

## 19. Risk classes

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

## 20. Security principles

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

Existing `PLG_RET_*` service results can inform normalized external error handling, but public errors should still be filtered and suitable for external clients.

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

## 21. Audit trail

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

## 22. Multisite

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

## 23. Provider independence

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

## 24. Relationship with future Data and Events APIs

The Connector should be considered an adapter over shared Geeklog architecture.

Short term:

```text
existing Plugin API
+ PLG_wsEnabled
+ PLG_invokeService
+ AtomPub introspection concepts
+ compatibility adapters
        ↓
capability/service discovery layer
        ↓
external JSON resource layer
        ↓
Connector
```

Long term:

```text
common Geeklog Data API
+ common Geeklog Events
+ shared capability descriptions
        ↓
REST / JSON / OpenAPI / agent adapters
        ↓
Connector
```

The Connector should become thinner as Geeklog's shared resource layer improves.

---

## 25. Relationship with future Marketing

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

## 26. Proof-of-concept success criteria

The first useful milestone is achieved when ChatGPT can securely:

1. identify the Geeklog site and available effective capabilities;
2. detect and reuse existing Geeklog service support;
3. search and retrieve stories/static pages;
4. retrieve Hub context when Hub is installed;
5. read non-sensitive Hello campaign statistics when Hello is installed;
6. read IndexNow status when available;
7. respect Geeklog ACL and Connector scopes;
8. operate safely in multisite context;
9. do all of the above without direct SQL access to another plugin's tables;
10. distinguish implemented services from externally authorized capabilities.

---

## 27. Recommended implementation sequence

1. Build a precise inventory of Geeklog 2.1.1 and 2.2.2 webservice/service behavior: `PLG_wsEnabled()`, `PLG_invokeService()`, AtomPub introspection and standard service actions.
2. Define a normalized internal capability model that can represent inferred Plugin API support and service-backed actions.
3. Implement capability inference from existing callbacks before requiring any new plugin declaration.
4. Prototype discovery of current service-enabled Stories and Static Pages.
5. Evaluate a shared `capabilities`/service-description action through `PLG_invokeService()`.
6. Introduce a new generic `plugin_getcapabilities_*()` convention only if the service-description approach proves insufficient or awkward.
7. Define the smallest provider-neutral external JSON resource layer.
8. Define authentication, token storage, scopes and audit model.
9. Ensure the capability endpoint returns only the effective authorized capability set.
10. Expose Hub read services without duplicating Hub logic.
11. Expose Hello aggregate campaign/status services without exposing personal data by default.
12. Expose IndexNow status/service operations.
13. Generate or map Connector tools from shared capability metadata where practical.
14. Build the ChatGPT connector adapter.
15. Test Geeklog 2.1.1 and 2.2.2 compatibility where practical.
16. Perform a security review.
17. Add draft/update actions.
18. Add test actions.
19. Add explicit publication/live-send actions only after the permission model is proven.

---

## 28. Key architectural decision still open

The investigation narrows the main design decision to this question:

> **Should richer capability metadata be exposed as a reserved Geeklog service through the existing `PLG_invokeService()` architecture, or does Geeklog need a new generic `plugin_getcapabilities_*()` callback?**

The default preference is to reuse and extend the existing service architecture first.

A new Plugin API callback should be proposed only if it produces a clearly simpler, safer or more reusable contract.

Either way, the result must remain provider-neutral and reusable by Hub, administration tools, REST/OpenAPI generation and future agent adapters.

---

## Project rule

> **The Connector is a secure external adapter over Geeklog capabilities. It must reuse existing Geeklog Plugin and Service APIs before adding new contracts, reuse Hub for relationships, Hello for communication, IndexNow for indexing transport, and expose only authorized capabilities. It must not create a competing internal API model for each plugin or consumer.**
