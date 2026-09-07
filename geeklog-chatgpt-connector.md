# Geeklog ChatGPT Connector — Plugin and Connector Concept

Status: **Architectural concept**

This document defines a future integration between Geeklog and ChatGPT using a dedicated Geeklog plugin and an external ChatGPT connector.

The objective is not to embed a generic chatbot inside Geeklog. The objective is to allow ChatGPT to discover, read and eventually perform authorized actions on a Geeklog site through a secure, structured interface, in the same spirit as connectors that allow ChatGPT to work with external developer or productivity platforms.

---

## 1. Vision

Geeklog already exposes a mature publishing and plugin system, but most administration and content operations are still performed through the web interface or through direct PHP integrations.

A Geeklog connector for ChatGPT would add a conversational and agent-compatible interface on top of Geeklog without replacing the existing administration interface.

A user could ask ChatGPT to perform tasks such as:

- list the latest stories;
- search stories or static pages;
- retrieve a specific article;
- identify content missing a given internal link;
- list topics and plugins;
- inspect recent Geeklog errors;
- create an article draft;
- update a story or static page;
- publish content when explicitly authorized;
- query compatible plugin content such as Maps, Documents, Videos or Store;
- compare the state of several Geeklog installations.

Example:

> Find every article in the `rocket-stove` topic that does not link to the pillar page and return the list with title, URL and story ID.

A later write-enabled version could support:

> Add the pillar-page link to these three drafts, but do not publish them.

The central idea is:

> **ChatGPT becomes an authorized conversational client of Geeklog, not a replacement for Geeklog.**

---

## 2. Two distinct components

The project should be split into two responsibilities.

### 2.1 Geeklog API plugin

A dedicated Geeklog plugin exposes a secure API on the Geeklog installation.

Possible working names:

- `api`
- `connector`
- `ai_connector`
- `assistant_api`

The final name should avoid making the server-side API unnecessarily dependent on a single AI provider.

Responsibilities:

- expose structured endpoints;
- authenticate clients;
- enforce permissions;
- validate input;
- call Geeklog Core and Plugin APIs;
- normalize responses;
- log API operations;
- provide capability discovery;
- expose plugin-provided tools where available.

### 2.2 ChatGPT connector

The ChatGPT-side connector describes the operations that ChatGPT is allowed to call and maps them to the Geeklog API.

Responsibilities:

- authenticate against the Geeklog API;
- expose well-defined tools to ChatGPT;
- provide schemas for tool arguments and responses;
- distinguish read and write operations;
- avoid exposing arbitrary database or PHP execution;
- translate Geeklog capabilities into operations suitable for an AI client.

The architecture is therefore:

```text
ChatGPT
   |
   | structured connector tools
   v
ChatGPT Connector
   |
   | HTTPS / JSON
   v
Geeklog API Plugin
   |
   +--> Geeklog Core APIs
   |
   +--> Geeklog Plugin APIs
   |
   +--> compatible plugin capabilities
```

---

## 3. No Geeklog Core modification required for the first implementation

The initial implementation should be delivered as a normal Geeklog plugin.

The Geeklog Core should not need to be modified simply to expose the first API.

Reasons:

- easier installation and removal;
- no fork of Geeklog Core;
- compatibility with upstream Geeklog updates;
- independent release cycle;
- easier experimentation;
- easier security review;
- possible support for several Geeklog versions;
- lower adoption barrier for existing sites.

If the implementation later exposes limitations in the existing Plugin API, small generic hooks could be proposed upstream to Geeklog Core. Those hooks should be useful beyond ChatGPT itself.

The sequence should therefore be:

1. implement as a plugin;
2. identify missing generic integration points;
3. propose Core hooks only where there is a clear reusable need.

---

## 4. Relationship with the existing Geeklog Plugin API

The connector must use Geeklog APIs whenever practical instead of bypassing them with direct SQL.

This follows the interoperability direction documented in [`plugin-content-interoperability-contract.md`](plugin-content-interoperability-contract.md).

For content plugins, the preferred strategy is to reuse common contracts such as:

- Item Info;
- collection retrieval where supported;
- URL resolution;
- lifecycle events;
- plugin service functions;
- other documented Plugin API hooks.

Direct knowledge of another plugin's tables should be avoided.

The connector plugin should act as an orchestration layer, not as a parallel application that reimplements Geeklog internals.

---

## 5. API structure

A versioned REST-style API is a practical starting point.

Example base URL:

```text
https://example.org/api/geeklog/v1/
```

Possible resources:

```text
/api/geeklog/v1/site
/api/geeklog/v1/capabilities
/api/geeklog/v1/stories
/api/geeklog/v1/stories/{id}
/api/geeklog/v1/topics
/api/geeklog/v1/staticpages
/api/geeklog/v1/staticpages/{id}
/api/geeklog/v1/plugins
/api/geeklog/v1/logs
```

Compatible plugins could be exposed through the same API namespace:

```text
/api/geeklog/v1/maps
/api/geeklog/v1/documents
/api/geeklog/v1/videos
/api/geeklog/v1/store
```

The public URL structure is secondary to the contract. The important requirement is that operations remain stable, versioned and machine-readable.

---

## 6. Capability-oriented connector tools

ChatGPT should not receive an unrestricted HTTP client or generic SQL interface.

It should receive explicit tools with narrow responsibilities.

### Initial read-only tools

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

Optional diagnostic tool:

```text
get_recent_errors
```

This operation must be permission-protected because logs can contain sensitive implementation details.

### Later content-authoring tools

```text
create_story_draft
update_story
publish_story
create_staticpage_draft
update_staticpage
publish_staticpage
```

Draft creation and publishing should remain separate operations.

### Future plugin tools

Examples:

```text
search_documents
get_document
search_markers
get_marker
update_marker
search_videos
get_video
search_products
get_product
```

Only installed plugins that explicitly expose a supported capability should appear.

---

## 7. Capability discovery

The API should expose what a specific Geeklog site actually supports.

Example conceptual response:

```json
{
  "api_version": "1",
  "site": "example.org",
  "capabilities": [
    "stories.read",
    "topics.read",
    "staticpages.read",
    "maps.read"
  ]
}
```

This is important because two Geeklog installations may have different plugins, versions and permissions.

ChatGPT should not assume that a capability exists simply because the connector specification knows about it.

---

## 8. Plugin extension contract

A longer-term objective is to allow Geeklog plugins to register their own connector capabilities without modifying the central API plugin.

Conceptual examples:

```php
function plugin_connectorCapabilities_maps()
{
    return array(
        'maps.read',
        'maps.write'
    );
}
```

or:

```php
function plugin_connectorTools_maps()
{
    return array(
        'search_markers',
        'get_marker',
        'update_marker'
    );
}
```

The exact API is intentionally not defined yet.

The important design principle is that the central connector plugin should not need hard-coded SQL knowledge for every Geeklog plugin.

A generic registration mechanism could later support clients other than ChatGPT.

---

## 9. Authentication

Authentication must be designed before write operations are exposed.

Possible mechanisms include:

- long-lived API tokens for controlled installations;
- revocable personal access tokens;
- OAuth-style authorization for a more general connector ecosystem;
- scoped service credentials for machine-to-machine integrations.

The first implementation may start with revocable tokens if that materially reduces complexity, but the storage and validation model must be designed so it can later evolve.

Tokens must never be stored in plaintext if a safer server-side representation is practical.

A token should be:

- identifiable;
- revocable;
- scoped;
- optionally expiring;
- associated with a Geeklog user or service identity;
- auditable.

---

## 10. Permission model

Authentication answers **who is calling**.

Authorization answers **what that caller may do**.

They must remain separate.

Example scopes:

```text
site.read
stories.read
stories.write
stories.publish
staticpages.read
staticpages.write
staticpages.publish
topics.read
plugins.read
logs.read
users.read
users.manage
configuration.read
configuration.write
```

Plugin-specific scopes could follow the same model:

```text
maps.read
maps.write
documents.read
documents.write
store.read
store.write
```

High-risk scopes should never be included automatically.

The default posture should be least privilege.

---

## 11. Geeklog ACL remains authoritative

The API permission system must not become a bypass around Geeklog security.

Where an API call maps to an existing Geeklog user, the operation should continue to respect:

- Geeklog groups;
- feature access;
- topic permissions;
- plugin ACL rules;
- ownership rules;
- any additional plugin-specific authorization.

Connector scopes should narrow access, not silently expand it beyond what the associated Geeklog identity can already perform.

Conceptually:

```text
Allowed operation
=
Connector scope
AND
Geeklog ACL
AND
resource-specific permission
```

---

## 12. Security principles

The connector creates an external administration surface and must therefore be treated as security-sensitive infrastructure.

Minimum requirements:

- HTTPS only in production;
- strict authentication;
- scoped tokens;
- revocation support;
- rate limiting;
- request-size limits;
- input validation;
- output filtering;
- Geeklog ACL enforcement;
- audit logging;
- safe error responses;
- no arbitrary SQL;
- no arbitrary PHP execution;
- no unrestricted filesystem access;
- no implicit publishing;
- protection against mass destructive operations;
- separate permission for diagnostics and logs.

Secrets from configuration files, database credentials, private paths and server environment data must never be returned through general-purpose endpoints.

---

## 13. Read operations before write operations

The project should deliberately begin as read-only.

This allows the architecture, authentication, schemas and compatibility model to be tested before introducing content mutations.

### Phase 1 — Read-only proof of concept

Recommended tools:

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

Success criteria:

- ChatGPT can connect securely;
- tools return predictable structured data;
- Geeklog permissions are respected;
- no Core modification is required;
- the connector can discover site capabilities;
- errors are safe and understandable.

### Phase 2 — Controlled drafting

Add:

```text
create_story_draft
update_story
create_staticpage_draft
update_staticpage
```

Publishing remains excluded initially.

### Phase 3 — Explicit publishing

Add separately authorized operations:

```text
publish_story
publish_staticpage
```

Publishing must never be an accidental side effect of a generic update call.

### Phase 4 — Plugin ecosystem

Allow compatible plugins to expose capabilities and tools through a common contract.

Potential first candidates:

- Documents;
- Maps;
- Videos;
- Store;
- IndexNow diagnostics;
- Hub.

### Phase 5 — Multi-site workflows

A user could register several independent Geeklog installations and ask ChatGPT to compare or operate across them while preserving the authentication and permissions of each site.

Example:

> Compare the installed plugin versions on my three Geeklog sites and show only the differences.

---

## 14. Multi-site considerations

The API plugin must follow the principles in [`multisite-development-principles.md`](multisite-development-principles.md).

Each request must resolve the active Geeklog site correctly.

Tokens, configuration, audit logs and permissions must not leak between sites that share plugin files.

A shared codebase does not imply shared credentials or shared authorization.

---

## 15. Compatibility target

During the current Geeklog modernization period, the project should evaluate compatibility with:

- Geeklog 2.1.1 through 2.2.2;
- PHP 5.6 through PHP 8.1 where the current repository policy applies.

However, security and protocol requirements must not be weakened merely to preserve old runtime compatibility.

If a secure connector implementation cannot reasonably support the full transition range, the project should document a narrower minimum version rather than silently compromise authentication or cryptographic requirements.

The compatibility target should therefore be validated during the proof of concept, not assumed.

---

## 16. Response format

Responses should be structured for machine consumption while remaining understandable during debugging.

Example:

```json
{
  "ok": true,
  "data": {
    "id": "20260907123000123",
    "title": "Example story",
    "url": "https://example.org/article.php/example-story",
    "status": "draft"
  }
}
```

Errors should be normalized:

```json
{
  "ok": false,
  "error": {
    "code": "permission_denied",
    "message": "The current credential cannot publish stories."
  }
}
```

Internal stack traces, SQL errors and filesystem paths should not be returned by default.

---

## 17. Audit trail

Every sensitive operation should be attributable.

A minimal audit entry should be able to record:

- timestamp;
- site;
- authenticated identity;
- token or client identifier;
- operation;
- target type;
- target ID;
- success or failure;
- request correlation ID.

For writes, it may also be useful to record a compact before/after summary without duplicating entire sensitive payloads.

The goal is to answer:

> Who asked the connector to change what, and when?

---

## 18. Human confirmation and destructive operations

The API should make risk levels visible to the ChatGPT connector.

Operations can be classified conceptually as:

### Low risk

- search content;
- retrieve content;
- list topics;
- list plugin versions.

### Medium risk

- create a draft;
- update unpublished content;
- modify metadata.

### High risk

- publish content;
- delete content;
- alter users;
- modify configuration;
- install or disable plugins;
- execute bulk changes.

The first public connector should avoid or heavily constrain high-risk administration actions.

A connector that can edit stories does not automatically need permission to install plugins or manage users.

---

## 19. What the connector must not become

The project should not expose:

```text
run_sql(query)
run_php(code)
execute_shell(command)
read_any_file(path)
write_any_file(path)
```

These are not useful abstractions for a safe Geeklog connector.

The connector should expose domain operations such as:

```text
search_stories
get_story
update_story
```

This keeps validation, permissions and auditing understandable.

---

## 20. Relationship with future Geeklog Data and Events APIs

The Memorandum already distinguishes:

- the existing Geeklog Plugin API;
- the Plugin Content Interoperability Contract;
- a possible future Data API;
- a possible future Events API.

The ChatGPT connector should not invent a competing content model if reusable Geeklog contracts already exist.

In the short term, the API plugin can adapt existing Geeklog and plugin interfaces into external JSON operations.

In the longer term, if Geeklog gains a common Data API, the connector should become primarily a consumer and secure exposure layer for that API.

This gives the project a useful role today without locking the future architecture to ChatGPT-specific assumptions.

---

## 21. Provider independence

Although the initial target is ChatGPT, the Geeklog-side API should remain provider-neutral.

The server should not need to know whether the caller is:

- ChatGPT;
- another AI assistant;
- an automation service;
- a mobile application;
- an administrative integration;
- another trusted external client.

The ChatGPT-specific logic belongs primarily in the connector definition, not in Geeklog's content and permission model.

This suggests a separation such as:

```text
Geeklog Connector API
        |
        +--> ChatGPT Connector
        +--> future assistant connector
        +--> automation client
        +--> administrative client
```

---

## 22. Possible repository structure

A future implementation could be separated into two repositories.

Example:

```text
hostellerie/geeklog-connector
hostellerie/geeklog-chatgpt-connector
```

or:

```text
hostellerie/api
hostellerie/chatgpt-connector
```

The Geeklog plugin repository would contain the server-side API.

The ChatGPT connector repository would contain the connector schema, documentation, examples and any ChatGPT-specific integration assets.

Keeping them separate reinforces the provider-neutral API design.

---

## 23. Initial proof-of-concept scope

A useful first milestone should stay intentionally small.

### Server plugin

Implement:

```text
GET site information
GET capabilities
GET topics
SEARCH stories
GET one story
SEARCH static pages
GET one static page
GET installed plugin names and versions
```

### Authentication

Implement:

- one revocable credential type;
- read-only scopes;
- server-side permission checks;
- audit logging.

### ChatGPT connector

Expose:

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

### Explicitly excluded from the proof of concept

- publishing;
- deletion;
- user management;
- plugin installation;
- configuration changes;
- arbitrary filesystem access;
- arbitrary SQL;
- arbitrary PHP or shell execution.

This scope is large enough to validate the concept while keeping the initial security surface understandable.

---

## 24. Example user workflows

### Editorial inventory

> List the 20 most recently published stories with ID, title, topic and publication date.

### Internal linking audit

> Find stories in the `google-chrome-gratuit` topic that do not contain a link to the Chrome pillar page.

### Content retrieval

> Retrieve the full story with ID X and summarize the changes I should make for SEO.

The SEO analysis is performed by ChatGPT. The Geeklog connector only retrieves the authorized source content.

### Plugin inventory

> List installed plugins with their versions and enabled state.

### Future draft workflow

> Create a draft from this text in the `rocket-stove` topic and return its draft ID. Do not publish it.

---

## 25. Strategic value for Geeklog

The connector can give Geeklog a modern integration surface without requiring a rewrite of the CMS.

It can make existing Geeklog data accessible to conversational tools while preserving:

- Geeklog as the system of record;
- existing permissions;
- existing plugin ownership of data;
- existing administration interfaces;
- compatibility with non-AI clients.

The most important architectural opportunity is not simply "adding ChatGPT to Geeklog".

It is creating a controlled external action layer that allows modern agents and applications to work with Geeklog through stable, permission-aware operations.

The long-term direction can be summarized as:

> **Geeklog structures and owns the data. The API exposes authorized capabilities. The connector makes those capabilities understandable to ChatGPT.**

---

## 26. Recommended next steps

1. Confirm the name and scope of the Geeklog-side API plugin.
2. Inventory the Geeklog Core and Plugin APIs needed for the read-only proof of concept.
3. Define the authentication and token model.
4. Define the capability and scope model.
5. Specify the first JSON request/response contracts.
6. Implement the read-only Geeklog plugin prototype.
7. Build the ChatGPT connector against that prototype.
8. Test on Geeklog 2.1.1 and 2.2.2 where practical.
9. Perform a security review before any write capability is added.
10. Add draft creation and controlled update operations only after the read-only model is stable.

---

## Project principle

> **Do not modify Geeklog Core merely to make ChatGPT work. Build a secure plugin API first, reuse Geeklog's existing contracts, and make the ChatGPT connector a client of that API.**
