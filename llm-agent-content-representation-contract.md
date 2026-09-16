# Geeklog LLM and Agent Content Representation Contract

## Purpose

This document defines a provider-neutral contract for exposing Geeklog content to AI assistants, LLMs, autonomous agents, MCP clients, search/retrieval systems, and future machine consumers.

It complements, rather than replaces:

- `plugin-content-interoperability-contract.md` for internal structured content interoperability;
- `geeklog-chatgpt-connector.md` for authenticated external capabilities and actions;
- native Geeklog Plugin APIs and service APIs;
- `robots.txt`, XML Sitemap, RSS/Atom, Schema.org and other web standards.

The objective is to ensure that content owned by Geeklog Core or a plugin can be consumed without scraping presentation HTML, reverse-engineering SQL tables, or creating provider-specific adapters.

The contract is intentionally provider-neutral. A plugin should expose content once in a stable Geeklog representation. ChatGPT, MCP clients, other LLMs, search tools and future agents should consume adapters built on that common representation.

---

## 1. Separate discovery, content, capabilities and actions

AI integration should be treated as four different layers:

```text
Discovery
    ↓
Resources / content
    ↓
Capabilities / tools
    ↓
Authorized actions
```

They must not be collapsed into one file or one endpoint.

### Discovery

Discovery helps an agent understand what the site contains and where useful resources live.

Examples:

```text
/llms.txt
sitemap.xml
RSS/Atom feeds
capability endpoint
```

### Resources / content

Resources provide clean machine-readable or LLM-readable representations of actual content.

Examples:

```text
Markdown representation of a story
Markdown representation of a static page
structured JSON representation of a video
structured metadata for a document
```

### Capabilities / tools

Capabilities describe what the installation or plugin can do.

Examples:

```text
content.search
content.read
content.collection
content.related
content.popular
maps.geo.nearby
hello.campaigns.draft
```

### Authorized actions

Actions modify state and require authentication, ACL enforcement, validation and sometimes explicit human confirmation.

Examples:

```text
update_story
create_staticpage
queue_newsletter
submit_indexnow
```

A public `llms.txt` file must never be treated as authorization for actions.

---

## 2. Canonical structured content fields

A content-owning plugin should expose a stable structured representation through the shared Geeklog content interoperability layer.

Recommended common fields are:

```text
id
type
subtype
title
url
canonical_url
description
excerpt
content
content_format
language
date-created
date-modified
uid
author
image
category
topic
tags
hits
license
```

Not every field is required for every plugin.

### Required baseline

For an addressable content item, the preferred minimum is:

```text
id
type
title
url
date-modified
```

and at least one of:

```text
content
excerpt
description
```

### Stable identity

`id` must be the stable identifier owned by the plugin. Consumers should model external identity as:

```text
plugin + type + id + optional subtype
```

A title or URL slug must not be used as the only identity when a stable internal content identifier exists.

---

## 3. Clean content representation

Agents should not be forced to consume navigation, advertising, theme chrome, administration controls or unrelated widgets when they request the content body.

Plugins should therefore distinguish between:

```text
presentation HTML
```

and:

```text
content representation
```

The preferred machine-facing representation is clean Markdown or normalized plain text when semantics can be preserved adequately.

If HTML is returned, it should be content HTML rather than a complete rendered page.

Recommended `content_format` values include:

```text
text/markdown
text/plain
text/html
application/json
```

Consumers should be able to request or discover the representation format rather than infer it from rendered markup.

---

## 4. Markdown representation

Where practical, addressable content should have an LLM-friendly Markdown representation.

A future shared Geeklog resource layer may provide this without requiring every plugin to implement a separate public PHP endpoint.

Conceptually:

```text
Human URL
https://example.org/staticpages/index.php/example

LLM-friendly representation
https://example.org/staticpages/index.php/example.md
```

or an equivalent negotiated/resource URL.

The exact routing convention is not frozen by this memorandum. What matters is that:

- the canonical human URL remains authoritative;
- the clean representation identifies its canonical source;
- permissions are preserved;
- the representation contains the substantive content, not the theme shell;
- the content can be regenerated from the owning plugin rather than maintained as an unrelated duplicate.

When HTML pages expose a Markdown alternative, a standard `Link` relation or `<link>` element should be preferred where compatible with the deployment.

---

## 5. `/llms.txt` as discovery, not as the content database

A site may expose `/llms.txt` as a concise, curated entry point for agents.

The recommended role of `llms.txt` is:

```text
site identity
short description
important interpretation notes
curated resource groups
links to LLM-friendly representations
links to machine capabilities where appropriate
```

It should remain concise enough to be useful as initial context.

It should not attempt to contain every article, every page, every product, every video or every plugin record.

Detailed content should live behind referenced resource URLs and be fetched only when needed.

### Canonical filename

`/llms.txt` is the preferred public discovery filename.

Aliases such as `/llm.txt` may redirect to or serve the same representation for compatibility, but integrations should advertise `/llms.txt` as canonical.

### Dynamic generation

A generated `llms.txt` is preferable to a manually duplicated catalog when Geeklog already knows the relevant content.

A good generator can combine:

```text
site-level editorial introduction
+ selected static resource links
+ dynamically discovered plugin resources
+ sitemap/feed links
+ optional capability/API links
```

The source of truth should remain Geeklog and its plugins.

---

## 6. Collection access for retrieval and RAG

An agent frequently needs a collection rather than one item.

Plugins should therefore follow the collection conventions in `plugin-content-interoperability-contract.md`, including `id='*'` where supported and common options such as:

```php
array(
    'since' => $timestamp,
    'limit' => 20,
    'order' => 'modified-desc'
)
```

Useful future/common filters include:

```text
until
topic
category
tag
author
language
subtype
ids
```

Useful ordering includes:

```text
modified-desc
created-desc
hits-desc
```

This collection layer is the preferred source for retrieval, indexing, recommendation and RAG pipelines. Consumers should not query plugin SQL tables directly.

---

## 7. Long content, sections and chunking

Long content must remain addressable as one canonical resource, but consumers may need smaller retrieval units.

The shared resource layer may expose optional section or chunk metadata:

```text
resource_id
parent_id
section_id
heading
sequence
text
start_offset
end_offset
```

Chunking must not create a second editorial source of truth.

Recommended principles:

- preserve the canonical item identity;
- retain heading/section context;
- use deterministic chunk identifiers when possible;
- regenerate chunks when source content changes;
- expose the parent canonical URL;
- avoid splitting in the middle of structural elements when practical.

Chunk size is a consumer/runtime concern and should not be permanently baked into plugin database schemas unless the plugin has a separate reason to store chunks.

---

## 8. Freshness and version information

Agents need to know whether a representation is current.

Recommended metadata includes:

```text
date-modified
version or revision when available
etag or representation fingerprint when available
canonical_url
```

HTTP resources should use normal cache validators where practical:

```text
ETag
Last-Modified
Cache-Control
```

A consumer should be able to revalidate content without downloading every resource again.

Lifecycle events such as `PLG_itemSaved()` and `PLG_itemDeleted()` remain the preferred internal signal that dependent indexes or agent resources may need refreshing.

---

## 9. Provenance and citation

Every resource intended for agent use should make provenance recoverable.

At minimum a consumer should be able to determine:

```text
owning plugin/type
stable item id
canonical URL
title
last modification date
```

Where relevant it should also expose:

```text
author
publisher/site
license
language
```

Generated summaries must not silently replace the original source content. If summaries are exposed, they should be identifiable as summaries and linked to the canonical item.

This allows agents to cite the actual source rather than a transient generated representation.

---

## 10. Permissions and visibility

Machine-readable representations must enforce the same visibility rules as the human-facing resource.

A plugin must not expose through Item Info, Markdown, JSON, collection endpoints, search, MCP resources or another agent adapter any item the caller is not allowed to read.

Public resources may be exposed anonymously.

Private or administrative resources require authenticated context and normal Geeklog permissions.

The following must never become a permission bypass:

```text
/llms.txt
Markdown alternatives
MCP resources
JSON APIs
search endpoints
collection endpoints
```

Drafts, private content, embargoed content and ACL-restricted records remain restricted regardless of their usefulness to an agent.

---

## 11. Personal and sensitive data

Plugins should expose the minimum data needed for the requested capability.

A normal content-read capability must not automatically imply access to personal information.

Examples of separate scopes may include:

```text
content.read
content.private.read
users.summary.read
users.personal_data.read
```

Aggregated statistics should be preferred when detailed personal records are not required.

Capability descriptors should identify personal-data or sensitive-data exposure where applicable.

---

## 12. Search and retrieval semantics

Machine consumers should be able to search content without knowing plugin SQL.

Existing Geeklog search APIs should be reused where they provide adequate structured results.

Future shared search/resource APIs should return normalized fields such as:

```text
id
type
title
url
excerpt
score
date-modified
```

A search result should be usable to locate a resource; it does not need to contain the entire resource body.

The agent should retrieve the selected resource separately when full content is needed.

---

## 13. Relations and context

Where a plugin or Hub can expose relationships, machine-readable resources may include structured links such as:

```text
related
parent
children
topic
category
tags
references
```

Hub remains the preferred owner of cross-plugin thematic relationships and dependency context.

Content plugins remain the owners of their own intrinsic relationships.

An agent adapter should consume these relationships rather than infer a permanent graph from rendered HTML links alone.

---

## 14. Capabilities must be machine describable

Read resources and executable actions are different things.

A future shared Geeklog capability descriptor should expose enough metadata to generate REST/OpenAPI/MCP/agent schemas without duplicating definitions for every provider.

For an executable capability, useful fields include:

```text
capability id
description
service/action
read/write mode
required permission
risk level
input schema
output schema
version/stability
idempotency when relevant
personal-data flag when relevant
human-confirmation recommendation when relevant
```

JSON Schema-compatible input and output descriptions are preferred for new machine-facing contracts because they can be adapted readily to contemporary agent tooling.

---

## 15. MCP mapping

MCP should be treated as an adapter over Geeklog contracts, not as the source of truth.

A future Geeklog MCP server can map:

```text
Geeklog content representation -> MCP resources
Geeklog search/read operations  -> MCP tools or resources
Geeklog capability descriptors  -> MCP tool schemas
Geeklog authorized actions      -> MCP tools
```

The same Geeklog contracts should also remain usable by REST, OpenAPI, ChatGPT connectors and future protocols.

No content plugin should need to implement its own MCP server merely to become agent-compatible.

---

## 16. Recommended HTTP/resource behavior

For public machine-readable resources, prefer normal web semantics:

```text
stable URLs
correct Content-Type
UTF-8
canonical links
ETag / Last-Modified where practical
cacheable GET requests
clear 404/403 behavior
```

Read endpoints should be safe and side-effect free.

State changes should not be hidden behind GET requests.

Machine resources should support deterministic output where practical so caches and agent prompt caches remain useful.

---

## 17. Relationship with robots, sitemap, feeds and structured data

These mechanisms are complementary:

```text
robots.txt   -> crawler access policy
sitemap.xml  -> broad URL discovery
RSS/Atom     -> chronological distribution
Schema.org   -> structured semantics embedded in human pages
llms.txt     -> curated agent-oriented discovery/context
Markdown     -> efficient LLM-readable content representation
JSON/Data API-> structured application/resource access
MCP          -> standardized agent resources/tools/actions
```

No single mechanism replaces the others.

---

## 18. Plugin modernization checklist

When modernizing a content plugin, evaluate:

- [ ] stable item identity;
- [ ] `plugin_getiteminfo_PLUGIN()` support;
- [ ] collection support where appropriate;
- [ ] clean `content` / `excerpt` representation;
- [ ] canonical URL exposure;
- [ ] language exposure where known;
- [ ] created/modified timestamps;
- [ ] optional `hits` and `hits-desc` when views are tracked;
- [ ] permission-safe retrieval;
- [ ] lifecycle saved/deleted events;
- [ ] search integration where appropriate;
- [ ] relation/context exposure where appropriate;
- [ ] capability/service description for specialized operations;
- [ ] machine-readable representations generated from the owning data rather than manually duplicated;
- [ ] no provider-specific ChatGPT/Claude/Gemini/MCP logic in ordinary content business code.

---

## 19. Recommended Geeklog architecture

The target architecture is:

```text
                 Geeklog Core + plugins
                         │
              normalized content contract
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ↓                 ↓                 ↓
   llms.txt          Data/resources    capabilities
  discovery          Markdown/JSON       services
       │                 │                 │
       └──────────────┬──┴──────────────┬──┘
                      │                 │
                      ↓                 ↓
                adapter layer      authorization
                      │                 │
          ┌───────────┼───────────┐     │
          ↓           ↓           ↓     ↓
        MCP         REST       OpenAPI  actions
          │           │           │
          └───────────┼───────────┘
                      ↓
              AI assistants / agents
```

The plugin owning the content remains authoritative.

A shared Geeklog AI/agent integration layer may publish discovery files, resources and protocol adapters, but it must not become a second content database.

---

# Design principle

> **Expose once, adapt many times.**

Geeklog plugins should expose stable structured content and capabilities through shared Geeklog contracts. Public discovery files, Markdown representations, REST APIs, MCP servers and provider-specific connectors should be adapters over those contracts.

This avoids coupling plugin development to one LLM vendor or one agent protocol and gives Geeklog a migration path as AI integration standards continue to evolve.
