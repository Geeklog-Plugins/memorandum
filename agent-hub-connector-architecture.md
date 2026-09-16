# Geeklog Hub, Agent and Connector Architecture

Status: **Architectural contract**

## Purpose

This document fixes the responsibility boundary between **Hub**, **Agent** and external **Connectors/adapters** so future AI, LLM, MCP and automation work does not duplicate Geeklog logic.

It complements:

- `plugin-content-interoperability-contract.md`;
- `llm-agent-content-representation-contract.md`;
- `geeklog-chatgpt-connector.md`;
- `multisite-development-principles.md`.

The guiding rule is:

> **Hub provides context. Agent provides machine access. Connectors adapt Agent to a client or provider.**

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
- later authenticated action endpoints;
- later protocol adapters such as MCP if useful.

Agent consumes shared Geeklog contracts. It must not become the owner of content, relations or plugin business logic.

### Connector — client/provider adapter

A Connector is external or client-facing adaptation code for a specific ecosystem.

Examples:

- ChatGPT Connector;
- an MCP client/server adapter where kept outside Agent core;
- another AI assistant adapter;
- an automation-platform adapter.

A Connector should translate Agent resources and capabilities into the schema and UX expected by that client.

A Connector must not:

- query Geeklog plugin tables directly;
- recreate Hub's graph;
- implement plugin business rules;
- maintain a second capability registry;
- bypass Agent ACL/capability filtering.

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
             resources + capabilities
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

## 4. Agent and Hub interaction

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

## 5. Agent and Connector interaction

Agent exposes provider-neutral machine resources and effective capabilities.

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

Therefore ChatGPT-specific schemas, naming and UX belong in the Connector, not in content plugins and not in Agent core.

---

## 6. `llms.txt` position

`llms.txt` is a public discovery/curation surface managed by Agent.

It is not the full machine API and must not become a second source of truth.

Agent should generate it from:

- site-specific editorial configuration;
- active Geeklog site context;
- shared content/provider contracts;
- selected Hub context where useful;
- canonical sitemap/feed/resource links.

The content exposed in `llms.txt` should point to richer Markdown/JSON resources rather than duplicate all site content in one file.

---

## 7. Mono-site and multisite

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

## 8. Compatibility target

For the current modernization period, Agent should target:

- Geeklog **2.1.1 through 2.2.2**;
- PHP **5.6 through 8.3**;
- mono-site and multisite installations;
- no Core modification for the initial roadmap.

Code must use the common safe PHP subset and feature-detect newer Geeklog APIs with compatible fallbacks.

---

## 9. Migration of the existing Connector concept

The existing `geeklog-chatgpt-connector.md` remains useful for security, capability discovery, ACL, scopes, auditability and progressive write access.

Its architecture should now be interpreted as two layers:

```text
Geeklog-side generic resource/capability layer
    -> Agent plugin

ChatGPT-specific adaptation
    -> ChatGPT Connector
```

Any Geeklog-side provider-neutral responsibility described in the older Connector concept belongs in Agent.

Any ChatGPT-specific tool mapping, authentication handshake or client UX belongs in the Connector.

The Connector should become thinner as Agent matures.

---

## 10. Development rule

> **Plugins expose shared data and capabilities. Hub interprets relationships. Agent exposes machine-readable access. Connectors adapt that access to a client.**

No layer should duplicate another layer's data ownership, relationship graph, permission model or business logic.
