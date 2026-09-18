# Geeklog Hub, Agent and Connector Architecture

Status: **Architectural contract**

## Purpose

This document fixes the responsibility boundary between **Hub**, **Agent** and external **Connectors/adapters** so future AI, LLM, MCP and automation work does not duplicate Geeklog logic.

It complements:

- `plugin-content-interoperability-contract.md`;
- `plugin-capability-contract.md`;
- `llm-agent-content-representation-contract.md`;
- `geeklog-chatgpt-connector.md`;
- `multisite-development-principles.md`.

The guiding rule is:

> **Hub provides context. Agent provides machine access. Connectors adapt Agent to a client or provider.**

A second long-term rule applies to protocol evolution:

> **Agent defines the stable provider-neutral machine model. MCP, ChatGPT, REST/OpenAPI and future protocols are adapters over that model, not the model itself.**

---

## 1. Component responsibilities

### Content-owning Core features and plugins

Stories, Static Pages, Videos, Documents, Maps, MediaGallery, Forum, Store and similar components remain authoritative for their own:

- content and metadata;
- permissions;
- canonical URLs;
- lifecycle;
- business rules;
- specialized rendering;
- create/update/delete operations.

They should expose shared Geeklog contracts instead of Hub-, Agent- or provider-specific APIs.

### Hub — context layer

Hub owns relationships and editorial/contextual interpretation between content objects.

Hub is responsible for:

- pillar relationships;
- stable `type + id` relations;
- related-content context;
- dependency graph;
- affected-item detection;
- orphan/broken relation diagnostics;
- integrity reports;
- editorial suggestions;
- context explaining why content belongs together.

Hub is **not** the external API gateway, LLM endpoint, `llms.txt` generator, MCP server, ChatGPT adapter or owner of machine-facing representations.

### Agent — machine access layer

Agent is a Geeklog plugin installed inside the site.

Agent is provider-neutral and is responsible for exposing Geeklog safely to machine consumers.

Agent may provide:

- `/llms.txt` discovery;
- clean Markdown resources;
- structured JSON resources;
- content collections such as recent/popular/featured;
- capability discovery;
- read-only resource/search endpoints;
- compatibility adapters for older Geeklog/plugin APIs where necessary;
- later authenticated action endpoints.

Agent consumes shared Geeklog contracts. It must not become the owner of content, relations or plugin business logic.

Agent must also remain protocol-neutral. It may host optional protocol modules for deployment convenience, but MCP-, ChatGPT-, REST/OpenAPI- or other protocol-specific schemas must remain adapters over Agent's internal resource/capability/action model. Protocol changes must not force content plugins or Agent's internal model to change unless the underlying Geeklog capability itself changes.

### Connector — client/provider adapter

A Connector is external or client-facing adaptation code for a specific ecosystem.

Examples:

- ChatGPT Connector;
- an MCP client/server adapter;
- another AI assistant adapter;
- an automation-platform adapter;
- a REST/OpenAPI adapter when a separate client-facing contract is useful.

A Connector should translate Agent resources, capabilities and authorized actions into the schema and UX expected by that client.

A Connector must not:

- query Geeklog plugin tables directly;
- recreate Hub's graph;
- implement plugin business rules;
- maintain a second capability registry;
- bypass Agent ACL/capability filtering;
- redefine Agent's normalized resource identities as a protocol-specific data model.

---

## 2. Reference architecture

```text
Stories / Static Pages / Videos / Documents / Maps / Store / ...
                         |
                         v
              shared Geeklog contracts
                         |
             +-----------+-----------+
             |                       |
             v                       v
            Hub                    Agent
     context / relations      machine access layer
             |                       |
             +----------->-----------+
                         |
        resources + capabilities + actions
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
   ChatGPT Connector   MCP adapter   other clients
          |              |              |
          v              v              v
       ChatGPT       AI/agents     automation/apps
```

Hub may expose reusable services such as context, related items, affected items, integrity reports and suggestions. Agent consumes those services when a machine request needs relationship/context information.

---

## 3. Shared contracts are the integration point

Neither Hub nor Agent should create consumer-specific callbacks when normal Geeklog APIs can express the same capability.

Preferred shared mechanisms include:

- `plugin_getiteminfo_PLUGIN()`;
- collection support with `'*'`;
- common fields such as `id`, `title`, `url`, `excerpt`, dates and optional `hits`;
- common collection options such as `since`, `limit`, `order`, including `hits-desc` where supported;
- `PLG_itemSaved()` and `PLG_itemDeleted()`;
- `plugin_idtourl_PLUGIN()` where supported;
- `plugin_getrelateditems_PLUGIN()`;
- `plugin_dopluginsearch_PLUGIN()`;
- `PLG_invokeService()` for specialized actions;
- generic capability descriptions where inference is insufficient.

The same capability declaration must be reusable by Hub, Agent, administration tools, REST/OpenAPI generation and future clients.

Do not introduce parallel registries such as:

```text
Hub capability registry
Agent capability registry
Connector capability registry
```

Prefer one shared capability model consumed by all three layers.

---

## Shared capability declaration

Agent and Hub must consume the shared capability model defined in `plugin-capability-contract.md` rather than maintaining parallel registries.

A provider may explicitly declare capabilities such as:

```text
content.read
content.collection
content.search
dashboard.summary
maps.geo.nearby
navigation.tree
```

Existing Geeklog APIs remain the implementation surface. Capability declarations advertise and describe those surfaces; they do not replace them.

Hub's interoperability audit may infer capabilities from existing Plugin APIs when an explicit declaration is absent, but explicit provider declarations should take precedence for capabilities that cannot be inferred safely.

Agent should expose the same provider declarations through its normalized machine model. Eclipse and other administrative consumers may consume the same declarations directly without routing through Agent.


## 4. Stable machine model

Agent should normalize Geeklog data into a stable provider-neutral model before rendering any protocol or output format.

The model should preserve at least these concepts where available:

```text
identity        = stable type + id
provider        = owning Core feature or plugin
canonical_url   = canonical public/internal URL
content         = normalized machine-readable payload
language        = explicit language when known
visibility      = effective access/visibility state
schema_version  = version of the normalized representation
capabilities    = operations supported by the resource/provider/context
```

Not every provider must expose every field, but protocol adapters should consume this normalized model rather than raw database rows or protocol-specific structures.

### Resources, Capabilities and Actions

These concepts must remain distinct:

```text
Resources     = what a machine can read or retrieve
Capabilities  = what the current site/provider/context can do
Actions       = operations the current caller is authorized to trigger
```

A capability existing does not imply that the current caller may execute it. Public discovery must never be interpreted as write authorization.

This distinction should survive every adapter, including MCP, ChatGPT, REST/OpenAPI and future protocols.

---

## 5. Agent and Hub interaction

When a request is about raw content, Agent should talk to the owning Core/plugin interface directly.

Examples:

```text
read story
list recent videos
search documents
get popular static pages
```

When a request is about relationships or context, Agent should delegate to Hub if Hub is installed and exposes the needed service.

Examples:

```text
get pillar context
get related items
get affected items
get integrity report
get editorial suggestions
```

Agent must not rebuild those answers from Hub tables or duplicate Hub algorithms.

Hub must remain usable without Agent, ChatGPT or any external AI provider.

Agent must remain useful without Hub; Hub enrichment is optional.

---

## 6. Agent and Connector interaction

Agent exposes provider-neutral machine resources, effective capabilities and later authorized actions.

Connector translates them into provider/client-specific concepts.

Example:

```text
Agent capability
    maps.geo.nearby
        |
        v
shared descriptor
        |
        v
ChatGPT Connector
        |
        v
ChatGPT tool schema
```

For another client, the same Agent capability may become an MCP tool or another protocol action without modifying Maps.

Therefore ChatGPT-specific schemas, MCP tool/resource naming, protocol version details and UX belong in the Connector or protocol adapter, not in content plugins and not in Agent core.

---

## 7. `llms.txt` position

`llms.txt` is a public discovery/curation surface managed by Agent.

It is not the full machine API and must not become a second source of truth.

Agent should generate it from:

- site-specific editorial configuration;
- active Geeklog site context;
- shared content/provider contracts;
- selected Hub context where useful;
- canonical sitemap/feed/resource links.

The content exposed in `llms.txt` should point to richer Markdown/JSON resources rather than duplicate all site content in one file.

`llms.txt` must remain optional from an architectural perspective: Agent's normalized resource model, capability discovery and future authenticated API must continue to work even if discovery conventions evolve or `llms.txt` is replaced by another mechanism.

---

## 8. Configuration exposure rule

A visible Configuration Manager option should correspond to functionality that is actually implemented in the installed Agent version, unless it is clearly presented as read-only diagnostic/status information.

Future roadmap concepts should not appear as active administrator controls before the corresponding behavior exists.

Examples:

- do not expose a Markdown enable/disable control before Markdown resources exist;
- do not expose JSON controls before JSON endpoints exist;
- do not expose authenticated-action settings before authenticated actions exist;
- diagnostic feature detection may be displayed before a feature is implemented because it reports environment state rather than promising functionality.

This rule keeps the administration interface aligned with real capabilities and prevents configuration from becoming a second roadmap.

---

## 9. Mono-site and multisite

Agent and Hub must resolve all operations in the active Geeklog site context.

Shared plugin files must not imply shared runtime state.

Each site keeps its own:

- configuration;
- database/table mapping;
- active plugin set;
- permissions;
- editorial Agent description;
- cache namespace;
- credentials/tokens when authenticated APIs are introduced;
- audit trail.

A hostname switch hard-coded in Agent should not be required for normal multisite operation.

---

## 10. Compatibility target

For the current modernization period, Agent should target:

- Geeklog **2.1.1 through 2.2.2**;
- PHP **5.6 through 8.3**;
- mono-site and multisite installations;
- no Core modification for the initial roadmap.

Code must use the common safe PHP subset and feature-detect newer Geeklog APIs with compatible fallbacks.

---

## 11. Migration of the existing Connector concept

The existing `geeklog-chatgpt-connector.md` remains useful for security, capability discovery, ACL, scopes, auditability and progressive write access.

Its architecture should now be interpreted as two layers:

```text
Geeklog-side generic resource/capability/action layer
    -> Agent plugin

ChatGPT-specific adaptation
    -> ChatGPT Connector
```

Any Geeklog-side provider-neutral responsibility described in the older Connector concept belongs in Agent.

Any ChatGPT-specific tool mapping, authentication handshake or client UX belongs in the Connector.

The Connector should become thinner as Agent matures.

---

## 12. Development rule

> **Plugins expose shared data and capabilities. Hub interprets relationships. Agent exposes machine-readable access. Connectors adapt that access to a client.**

No layer should duplicate another layer's data ownership, relationship graph, permission model or business logic.

Protocol-specific evolution must remain outside the stable Agent core whenever possible, so future changes to MCP, ChatGPT or other clients do not force rewrites of Geeklog content integrations.
