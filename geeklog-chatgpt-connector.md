# Geeklog ChatGPT Connector — External Adapter Concept

Status: **Architectural concept**

## Purpose

This document defines the future **ChatGPT-specific adapter** for Geeklog.

The Geeklog-side provider-neutral machine access layer is now assigned to the **Agent plugin**. The ChatGPT Connector must therefore remain a thin external/client adapter over Agent rather than becoming a second Geeklog API architecture.

See also:

- `agent-hub-connector-architecture.md`;
- `llm-agent-content-representation-contract.md`;
- `plugin-content-interoperability-contract.md`;
- `multisite-development-principles.md`.

The architectural rule is:

> **Hub provides context. Agent provides machine access. The ChatGPT Connector adapts Agent resources and capabilities to ChatGPT.**

---

## 1. Component boundary

### Geeklog Agent plugin

Agent is responsible for the Geeklog-side generic layer:

- `/llms.txt` discovery;
- normalized content resources;
- Markdown/JSON representations;
- collection retrieval;
- capability discovery;
- permission-aware access;
- multisite isolation;
- compatibility adapters across Geeklog 2.1.1–2.2.2;
- later authenticated resource/action APIs;
- reusable descriptors suitable for REST/OpenAPI/MCP/other clients.

### ChatGPT Connector

The Connector is responsible only for ChatGPT-facing adaptation:

- connecting/authenticating a ChatGPT client to Agent;
- translating Agent capability descriptors into ChatGPT tool schemas;
- translating Agent resources/results into the format expected by ChatGPT;
- applying ChatGPT-specific naming, descriptions and UX conventions;
- forwarding authorized calls to Agent;
- presenting errors/confirmation flows appropriately for the client.

The Connector does **not** own Geeklog content, permissions, plugin discovery, Hub relationships or plugin business logic.

---

## 2. Reference architecture

```text
Content plugins / Geeklog Core
          |
          v
 shared Geeklog contracts
          |
     +----+----+
     |         |
     v         v
    Hub      Agent
 context   machine access
     |         |
     +---->----+
          |
 resources + effective capabilities
          |
          v
  ChatGPT Connector
          |
          v
       ChatGPT
```

Agent may consume Hub services when context/relations are needed. The Connector must not query Hub directly in a way that bypasses Agent's authorization and site context.

---

## 3. No Connector-specific plugin API

Content plugins must not add callbacks such as:

```php
plugin_connectorCapabilities_maps()
plugin_chatgptTools_documents()
```

The Connector should consume Agent's normalized capability model, which itself is built from shared Geeklog contracts such as:

```text
plugin_getiteminfo_*
plugin_dopluginsearch_*
plugin_getrelateditems_*
plugin_idtourl_*
PLG_wsEnabled()
PLG_invokeService()
shared capability descriptors
```

A capability should be defined once and then reusable by:

```text
Hub
Agent
administration tools
REST/OpenAPI adapters
MCP adapters
ChatGPT Connector
future clients
```

---

## 4. Capability mapping

Agent exposes an effective capability set after applying site state and permissions.

Example Agent capability:

```text
maps.geo.nearby
```

Descriptor may include:

```text
capability id
service/action name
mode (read/write)
required permission
risk class
argument schema
result schema/type
description
version/stability
```

The Connector maps that descriptor to the ChatGPT-facing tool.

Conceptual flow:

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
ChatGPT tool
    maps_nearby(...)
```

Tool schemas should be generated or mapped from shared Agent metadata where practical instead of being duplicated manually in every Connector release.

---

## 5. Technical capability versus authorized capability

The Connector must use Agent's **effective authorized capability set**, not merely everything technically implemented by PHP/plugins.

Conceptually:

```text
implemented capability
AND plugin enabled state
AND active Geeklog site
AND credential scope
AND Geeklog ACL
AND plugin/resource permission
=
externally available capability
```

The Connector must never broaden access beyond Agent/Geeklog permissions.

---

## 6. Hub usage

Hub remains the internal content relationship and context orchestrator.

Potential Hub-derived Agent capabilities include:

```text
hub.context.read
hub.related.read
hub.affected.read
hub.integrity.read
hub.suggestions.read
```

When ChatGPT requests thematic/contextual information, the flow should be:

```text
ChatGPT
   ↓
Connector
   ↓
Agent
   ↓
Hub service
   ↓
Agent-normalized result
   ↓
Connector
   ↓
ChatGPT
```

The Connector must not maintain a second Hub relationship graph or reproduce Hub's orphan/dependency logic.

---

## 7. Other plugin responsibilities

### Hello

Hello owns registered-user communication:

- campaigns;
- newsletters/digests;
- recipient groups;
- queueing/throttling;
- delivery;
- unsubscribe handling;
- campaign statistics.

Agent may later expose authorized Hello capabilities. Connector merely maps them to ChatGPT tools.

### IndexNow

IndexNow owns URL queueing, deduplication, provider submission and status.

Agent may expose IndexNow status/actions through shared services. Connector does not reproduce transport logic.

### Content plugins

Stories, Static Pages, Maps, Documents, Videos, Forum, Store and similar plugins remain authoritative for their own data, validation, permissions and mutations.

---

## 8. Read-only first

The first Connector implementation should consume a proven read-only Agent API.

Useful initial capabilities may include:

```text
site.info.read
capabilities.read
content.read
content.collection
content.search
content.recent
content.popular
content.featured
hub.context.read
hub.related.read
hub.integrity.read
```

No write action is required for the first production-ready Connector.

---

## 9. Controlled write progression

Write support should be introduced only after Agent implements scoped authentication, auditing and risk classification.

Recommended progression:

### Phase 1 — Read only

- retrieve resources;
- search/list content;
- read Hub context;
- read aggregate service/plugin status.

### Phase 2 — Draft/safe changes

Potential capabilities:

```text
story.draft.create
story.draft.update
staticpage.draft.create
staticpage.draft.update
hello.campaign.draft
```

### Phase 3 — Test actions

Example:

```text
hello.campaign.test
```

### Phase 4 — Explicit high-risk actions

Separate permissions for:

```text
story.publish
staticpage.publish
hello.campaign.send
content.delete
```

A generic update action must never implicitly publish or send.

---

## 10. Authentication and authorization

Credential and authorization enforcement belong primarily to Agent/Geeklog.

Possible models:

- revocable personal access token;
- service token;
- OAuth-style flow;
- future client/agent credentials.

Credentials should be:

- identifiable;
- revocable;
- scoped;
- optionally expiring;
- associated with a Geeklog/service identity;
- auditable;
- isolated by site in multisite deployments.

Connector-side credentials must never bypass Agent-side ACL enforcement.

---

## 11. Risk classes

### Low risk

- public/authorized reads;
- search/list resources;
- Hub context reads;
- aggregate statistics/status.

### Medium risk

- create drafts;
- update unpublished content;
- create campaign drafts;
- send administrator tests.

### High risk

- publish content;
- send live campaigns;
- delete content;
- modify subscribers/users/configuration;
- access personal data;
- bulk mutations.

High-risk actions require explicit scopes, strong auditability and client-side confirmation UX where appropriate.

---

## 12. Security principles

Connector + Agent integration must preserve:

- HTTPS in production;
- strict authentication for non-public capabilities;
- scoped/revocable credentials;
- request bounds;
- rate limits where appropriate;
- input validation;
- output filtering;
- Geeklog ACL;
- plugin-specific permissions;
- audit logging;
- multisite isolation;
- safe errors;
- explicit protection of personal data.

Never expose generic execution primitives such as:

```text
run_sql
run_php
execute_shell
read_any_file
write_any_file
```

Expose domain capabilities only.

---

## 13. Audit trail

Sensitive operations should remain attributable end-to-end.

A useful Agent-side audit record includes:

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

The Connector should preserve/pass a correlation identifier where possible so one client request can be traced through Agent and the owning service/plugin.

---

## 14. Multisite

The Connector must never choose a Geeklog site by accessing shared data directly.

Agent resolves the active site and isolates:

- configuration;
- database mapping;
- plugins;
- permissions;
- credentials;
- cache;
- audit context.

Cross-site administration must be explicit and separately authorized.

---

## 15. Provider independence

ChatGPT is only one consumer of Agent.

The same Agent model should remain reusable by:

```text
MCP clients
other AI assistants
REST clients
OpenAPI-generated clients
n8n / Make / Zapier-style automation
mobile applications
trusted custom clients
```

Only ChatGPT-specific tool mapping and UX belong in this Connector.

---

## 16. Implementation sequence

1. Stabilize Agent read-only resources/capability model.
2. Define the Connector-to-Agent authentication model for the first deployment.
3. Map Agent capability descriptors to ChatGPT tool schemas.
4. Implement site/capability discovery.
5. Implement content read/search/list operations.
6. Implement optional Hub context tools through Agent.
7. Validate multisite isolation.
8. Perform security review.
9. Add scoped draft/test actions only after Agent write/security model is proven.
10. Add high-risk publish/send/delete actions only after explicit permissions, auditing and confirmation flows are proven.

---

## Project rule

> **The ChatGPT Connector is a thin client/provider adapter over Agent. Agent is the Geeklog-side machine access layer. Hub remains the context/relationship layer. Content plugins remain authoritative for their own data and business rules.**
