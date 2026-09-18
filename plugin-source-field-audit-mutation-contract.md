# Geeklog Source Field Audit & Mutation Contract

## Purpose

This document defines a shared interoperability contract for consumers that need to inspect the **stored/source text fields** of Geeklog content and, when explicitly authorized, request controlled modifications without reading or updating another plugin's private SQL tables.

The immediate reference consumer is the **AdSense plugin**, which needs to audit and optionally remove historical advertising autotags such as:

```text
[adsense:1]
[leaderboard:1]
[inarticle:1]
[infeed:1]
```

The contract is intentionally generic so it can also support future consumers such as migration tools, language audits, refactoring tools, integrity checks, content cleanup utilities and administration assistants.

It complements:

- `plugin-content-interoperability-contract.md`;
- `llm-agent-content-representation-contract.md`;
- `plugin-capability-contract.md`;
- normal Geeklog Plugin APIs and services.

It does **not** replace `plugin_getiteminfo_*()`. Item Info remains the preferred normalized content contract. This document covers the cases where a consumer needs the exact source fields rather than a cleaned, truncated, rendered or normalized representation.

---

## Why Item Info alone is not always sufficient

A normalized content representation may intentionally:

- strip HTML;
- expand or remove autotags;
- truncate descriptions;
- sanitize markup;
- combine several storage fields into one logical description;
- hide implementation-specific source fields.

That is correct for ordinary consumers such as Agent, Hello, Hub, Sitemap or search.

It is not sufficient for an audit that must determine whether the stored source still contains a literal marker such as:

```text
[leaderboard:1]
```

or for a migration that must remove only that marker while preserving surrounding text.

Therefore source-field access must be an **explicit capability**, separate from ordinary `content.read`.

---

## Capability model

Recommended capability names, aligned with the shared capability contract:

```text
content.read
content.collection

content.source_fields.read
content.source_fields.collection

content.source_fields.update
```

Semantics:

- `content.read` — normalized/addressable content can be read.
- `content.collection` — normalized collections can be enumerated.
- `content.source_fields.read` — exact source/stored text fields for one authorized item can be inspected.
- `content.source_fields.collection` — source-auditable items can be enumerated safely in bounded collections.
- `content.source_fields.update` — one or more explicitly writable source fields can be changed through the owning plugin's own validation/save path.

A read capability must never imply a write capability.

A write capability must never be inferred from ACL visibility, Item Info availability or knowledge of the plugin's database schema.

---

## Source field descriptor

A source-capable provider should expose field metadata rather than forcing consumers to guess table columns.

Recommended descriptor shape:

```php
array(
    'provider' => 'forum',
    'type' => 'forum_post',
    'id' => '1234',
    'subtype' => '',
    'fields' => array(
        array(
            'name' => 'comment',
            'label' => 'Message',
            'format' => 'text/html',
            'value' => 'Stored source text...',
            'writable' => true
        )
    )
)
```

Recommended field properties:

```text
name
label
format
value
writable
optional revision/fingerprint
```

The `name` is a provider-owned stable field identifier. It does not have to equal a database column name.

The `value` must be the source representation that the owning plugin itself considers appropriate for editing/audit. Consumers must not assume it is raw SQL storage bytes if the plugin normally applies a reversible decoding step before editing.

---

## Stable identity

Consumers should identify source records using:

```text
provider/plugin
type
id
optional subtype
field name
```

Example:

```text
forum
forum_post
1234
comment
```

A consumer must not identify a source field only by:

- table name;
- row number;
- URL;
- title;
- display position.

---

## Read contract

The preferred implementation should use either:

1. a documented shared function contract owned by the plugin; or
2. a bounded Geeklog service callable through `PLG_invokeService()`.

A conceptual function contract is:

```php
function PLUGIN_getSourceFields($id, $options = array());
function PLUGIN_getSourceFieldContractVersion();
```

A conceptual Geeklog service is:

```text
source_fields_get
```

with arguments such as:

```php
array(
    'id' => '1234',
    'subtype' => '',
    'fields' => array('comment')
)
```

The exact naming is not mandated yet. What matters is that the contract is documented, versioned where necessary, permission-aware and provider-owned.

---

## Collection / audit contract

Large-site audits need bounded enumeration without direct SQL.

A source-capable provider should support a collection request equivalent to:

```php
array(
    'limit' => 100,
    'cursor' => '...',
    'fields' => array('comment', 'description'),
    'contains' => array('[adsense', '[leaderboard', '[inarticle', '[infeed')
)
```

Recommended semantics:

- `limit` — bounded page size;
- `cursor` — opaque provider-owned continuation token where useful;
- `fields` — optional requested source fields;
- `contains` — optional literal/prefix filters used only if the provider can apply them safely;
- provider returns stable item identities and matching source fields;
- unsupported filters are reported rather than silently reinterpreted;
- collection access remains permission-aware;
- one provider failure must not abort unrelated providers in a site-wide audit.

A provider may return all source-capable items when optimized filtering is not available, but consumers must still use bounded pagination.

---

## Write / mutation contract

Source modification must remain owned by the plugin that owns the content.

A conceptual mutation contract is:

```php
function PLUGIN_updateSourceFields($id, $changes, $options = array());
```

or a bounded service such as:

```text
source_fields_update
```

Recommended change structure:

```php
array(
    'comment' => array(
        'old_fingerprint' => '...',
        'new_value' => 'Updated source text...'
    )
)
```

Requirements:

- explicit server-side ACL check;
- explicit declaration that the field is writable;
- input validation by the owning plugin;
- optimistic concurrency protection where practical using a revision/fingerprint/date-modified value;
- normal save/update logic must be reused;
- normal lifecycle notifications such as `PLG_itemSaved()` should fire when appropriate;
- plugin caches/indexes must be invalidated by the owning plugin;
- the consumer must never issue direct SQL UPDATE statements against another plugin's tables;
- partial failures must be reported per item/field;
- the operation must be idempotent or safely retryable where practical.

---

## AdSense requirements

The AdSense plugin needs this contract for two separate purposes.

### 1. Read-only historical autotag audit

AdSense needs to locate exact stored occurrences of:

```text
[adsense]
[adsense:*]
[leaderboard]
[leaderboard:*]
[inarticle]
[inarticle:*]
[infeed]
[infeed:*]
```

The suffix parameter may be historical syntax with no semantic meaning. AdSense must therefore inspect the literal source rather than depend only on rendered output.

The audit should be able to report:

```text
provider
type
id
field
autotag name
occurrence count
short source excerpt
writable yes/no
```

No content must be modified during audit.

### 2. Explicit removal/migration

If an administrator chooses to remove historical AdSense-compatible autotags, AdSense must:

- request the exact current source field from the provider;
- calculate the proposed new value;
- show a dry-run/preview;
- submit the updated field only through the provider's write contract;
- preserve unrelated markup/content;
- never remove `[amazon]` or `[youtube]`;
- never perform cross-site migration;
- never infer another plugin's database columns.

Automatic render-time AdSense placement should remain separate from stored-content migration.

---

## Current plugin readiness observed during AdSense design

This table records the current state observed in the modernized plugin branches reviewed for AdSense integration. It is a development snapshot, not a permanent compatibility guarantee.

| Plugin | Current useful exposure | Adequate for AdSense source audit? | Missing capability |
| --- | --- | --- | --- |
| Forum | `plugin_getiteminfo_forum()` exposes post `description/excerpt` from stored comment text | **Partial** | Explicit source-field descriptor, bounded source collection contract, provider-owned source update contract |
| Documents | `plugin_getiteminfo_documents()`, collections, lifecycle/URL interoperability, capability helper | **Partial** | Explicit source-field access for all relevant document fields, not only normalized description; controlled write contract |
| MediaGallery | Album Item Info exposes `raw-description`; album/media list services exist | **Closest to ready for read audit** | Generalize raw/source field semantics beyond album description and add controlled write contract if migration is desired |
| Videos | `plugin_getiteminfo_videos()` exists, but description is normalized through `Videos_Description::excerpt()` | **No for exact source audit** | Exact source-description capability and optional write contract |
| Maps | `plugin_getiteminfo_maps()` exposes decoded description and collections; marker services exist | **Partial** | Explicit source field contract for map/marker text fields and controlled mutation path for migration |
| Core stories/static pages/blocks | Existing Geeklog storage/rendering support exists | **Requires compatibility adapter or shared core contract** | Common source-field abstraction so consumers do not hard-code Core tables indefinitely |

---

## Provider implementation priority for AdSense

Recommended order:

1. **Forum** — historical autotags are likely to appear in long-lived posts and replies.
2. **Documents** — documents can contain multiple configurable text fields, so field-level exposure is important.
3. **MediaGallery** — extend the existing `raw-description` idea into the common source-field model.
4. **Maps** — expose map and marker textual source fields consistently.
5. **Videos** — expose the unnormalized stored/editorial description separately from public excerpts.
6. other modernized content plugins as they are touched.

The objective is not to make every plugin AdSense-aware. The objective is to make plugins expose a reusable source-field capability that AdSense, Agent tooling, migration utilities and future audits can all consume.

---

## Security and privacy

Source-field access may reveal text that is intentionally hidden from ordinary public representations.

Therefore:

- source capabilities are not automatically public;
- provider permissions remain authoritative;
- administrative consumers should use authenticated Geeklog context;
- draft/private/inaccessible items must remain inaccessible unless the caller already has the corresponding permission;
- source APIs must not expose unrelated secret configuration or credentials;
- public Agent capability discovery may advertise the existence of a capability, but it must not expose private source values.

---

## Multisite

All source-field operations must use the active Geeklog site context.

A provider must not:

- enumerate sibling-site tables;
- infer another site's path/database prefix;
- cache source data across site namespaces;
- migrate multiple sites because plugin files are shared.

A site-wide AdSense audit means the **active site only**.

---

## Relationship with Agent

Agent and AdSense should be independent consumers of the same provider-owned contracts.

```text
Owning plugin
     │
     ├── normalized Item Info ──> Agent / Hub / Hello / Sitemap
     │
     └── source-field capability ──> AdSense audit / migration tools / future admin agents
```

Agent may eventually expose authenticated source-audit capabilities through its own protocol adapters, but the underlying contract must remain owned by the content plugin and must not depend on Agent.

---

## Design principle

> **Normalized content is for consumption; source fields are for controlled inspection and editing.**

A plugin should expose both only when needed, keep the two concepts distinct, and remain the sole authority for permission and mutation of its own content.
