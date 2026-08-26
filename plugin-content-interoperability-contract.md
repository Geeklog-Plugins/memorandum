# Geeklog Plugin Content Interoperability Contract

## Purpose

This document defines a practical interoperability target for Geeklog content plugins such as **Maps, Documents, Videos, Store, Calendar, Links, Polls, Static Pages**, and similar extensions.

The objective is to let one plugin consume another plugin's content without knowing its SQL tables, column names, internal paths, or business logic.

This contract is intended to support several consumers over time:

- **Hello** — retrieve new or recently updated content for notifications and digests;
- **Hub** — identify content, maintain relations, build content hubs, and react to lifecycle changes;
- **IndexNow** — resolve URLs that should be submitted after changes;
- **Sitemap** — discover addressable content;
- **Content Syndication** — expose plugin content through Geeklog-managed RSS/Atom feeds;
- **Statistics** — let plugins contribute to Geeklog's global statistics views;
- **Search and recommendation features** — reuse structured metadata instead of plugin-specific SQL.

The recommended approach is to build on existing Geeklog Plugin APIs rather than create a separate integration API for every consumer.

> This document describes a recommended interoperability contract. Some capabilities already exist in Geeklog, while collection filtering conventions described here are proposed harmonization rules and are not currently universal Geeklog core requirements.

---

## Compatibility target

For plugins currently being modernized, the working target remains:

- **Geeklog 2.1.1 through 2.2.2**
- **PHP 5.6 through PHP 8.1**

The interoperability layer should therefore use the common safe subset of both Geeklog and PHP generations wherever practical.

Geeklog 2.2.2 provides additional lifecycle and URL-resolution capabilities that may not exist in the same form in Geeklog 2.1.1. New plugins should use those capabilities when available while retaining safe fallbacks for older supported versions.

---

# 1. Expose content through `plugin_getiteminfo_*()`

A content plugin should implement:

```php
function plugin_getiteminfo_PLUGIN($id, $what, $uid = 0, $options = array())
```

Example for Maps:

```php
function plugin_getiteminfo_maps($id, $what, $uid = 0, $options = array())
```

This should be the primary structured metadata interface used by other plugins.

At minimum, an addressable content item should be able to expose:

```text
id
title
url
description or excerpt
date-created
date-modified
```

Where meaningful, a plugin may also expose:

```text
uid
author
image
category
topic
type
subtype
```

The exact property set may vary by plugin, but commonly useful names should be kept consistent.

## Why this matters

A consumer should be able to request content metadata without accessing plugin tables directly.

For example, Hub or Hello should not need to know whether Maps stores a title in `map_name`, `title`, or another internal column.

The plugin remains responsible for:

- permissions;
- SQL structure;
- URL construction;
- content formatting;
- plugin-specific rules.

The consumer receives only the normalized information it requested.

---

# 2. Support collection retrieval

For interoperability use cases such as newsletters, recent-content lists, hubs, and recommendations, retrieving one item is not enough.

A modernized content plugin should support the existing Geeklog convention of using:

```php
$id = '*';
```

when its `plugin_getiteminfo_*()` implementation is capable of returning multiple items.

Example:

```php
plugin_getiteminfo_maps(
    '*',
    'id,title,url,excerpt,date-modified',
    0,
    $options
);
```

When `'*'` is used, the function should return an array of normalized content records rather than one record.

## Proposed common collection options

The `$options` parameter should gradually be harmonized across modernized content plugins.

Recommended initial options are:

```php
$options = array(
    'since' => $timestamp,
    'limit' => 20,
    'order' => 'modified-desc'
);
```

Suggested meanings:

- `since` — return items created or modified at or after this timestamp;
- `limit` — maximum number of items to return;
- `order` — requested ordering, initially supporting values such as `modified-desc` or `created-desc`.

Possible later extensions may include:

```text
until
author
topic
category
subtype
ids
```

These filtering options are **recommended interoperability conventions**, not a claim that current Geeklog core already enforces them.

---

# 3. Emit lifecycle events consistently

Content plugins should notify Geeklog when addressable content changes.

## Save or update

After a successful creation or modification:

```php
PLG_itemSaved($id, 'PLUGIN');
```

Example:

```php
PLG_itemSaved($map_id, 'maps');
```

## Delete

After a successful deletion:

```php
PLG_itemDeleted($id, 'PLUGIN');
```

Example:

```php
PLG_itemDeleted($map_id, 'maps');
```

These calls should be present on **all important mutation paths**, including alternate administration paths, services, imports, moderation paths, or other save/delete routes where applicable.

## Why lifecycle events matter

Hello can periodically request recent content.

Hub has a different need: it should be able to react when content changes rather than repeatedly scan every plugin table.

A typical Hub flow can therefore become:

```text
Content saved
    ↓
PLG_itemSaved()
    ↓
Hub receives the event
    ↓
Hub asks the plugin for structured item information
    ↓
Relations, URLs, indexes or dependent pages can be refreshed
```

This separates **change detection** from **content retrieval**.

Lifecycle events are also useful to consumers such as XMLSitemap, which can react to saves and deletions for content types it tracks.

---

# 4. Preserve `sub_type` when available

Geeklog 2.1.1 and Geeklog 2.2.2 do not expose exactly the same lifecycle callback contract.

Older supported installations may use a legacy callback form without `sub_type`, while Geeklog 2.2.2 can provide a subtype-aware lifecycle contract.

Interoperability consumers such as Hub should therefore model identity as:

```text
plugin
item_id
item_sub_type = NULL when unavailable
```

A plugin should not require `sub_type` for its basic interoperability behavior unless the content model genuinely depends on it.

This allows the same logical relation model to work across Geeklog 2.1.1 and 2.2.2.

---

# 5. Expose item-to-URL resolution when supported

For Geeklog 2.2.2, modernized content plugins should implement:

```php
function plugin_idtourl_PLUGIN($sub_type, $item_id)
```

Example:

```php
function plugin_idtourl_maps($sub_type, $item_id)
{
    // Return the canonical URL for the requested map item.
}
```

This gives consumers a standard way to resolve an item URL without duplicating plugin routing rules.

Potential consumers include:

- Hub;
- IndexNow;
- sitemap generation;
- notifications;
- logs and audit tools.

## Compatibility fallback

Because this capability is not available in the same form across the full Geeklog 2.1.1–2.2.2 range, the item URL should also remain obtainable through:

```php
plugin_getiteminfo_PLUGIN(..., 'url', ...)
```

Consumers should treat `plugin_idtourl_*()` as an additional capability and fall back to Item Info when necessary.

---

# 6. Keep What's New as a presentation capability

Plugins whose content belongs in Geeklog's native **What's New** block may also implement:

```php
plugin_whatsnewsupported_PLUGIN()
plugin_getwhatsnew_PLUGIN()
```

Example:

```php
plugin_whatsnewsupported_maps()
plugin_getwhatsnew_maps()
```

These APIs remain useful and should be preserved where appropriate.

However, `plugin_getwhatsnew_*()` typically returns presentation-ready HTML. It should therefore not become the main data contract for Hello, Hub, or other structured consumers.

The preferred model is:

```text
plugin_getiteminfo_*()
        ↓
structured content metadata
        ↓
 ┌──────┼───────────────┐
 ↓      ↓               ↓
Hello   Hub        What's New renderer
```

What's New can reuse the same underlying plugin query logic while remaining responsible for HTML output.

---

# 7. Optional and distribution capabilities

Once the core interoperability layer is stable, plugins may add additional capabilities according to their role.

These capabilities should be detected and documented independently from the basic Hub/content readiness score. A plugin does not need every capability to be interoperable.

## Related items

```php
plugin_getrelateditems_PLUGIN()
```

Useful for:

- Hub suggestions;
- related-content modules;
- recommendation systems;
- navigation between semantically connected resources.

## Search

```php
plugin_dopluginsearch_PLUGIN()
```

Useful when plugin content should participate in Geeklog search.

## Autotags

```php
plugin_autotags_PLUGIN()
```

Useful for embedding plugin content in stories, static pages, or other supported content.

## Blocks

```php
plugin_getBlocks_PLUGIN()
```

Useful where the plugin provides reusable dynamic blocks.

## Statistics

Plugins may contribute to Geeklog's native statistics system and `/stats.php` through:

```php
plugin_showstats_PLUGIN()
plugin_statssummary_PLUGIN()
```

These callbacks represent a native aggregation contract: the plugin remains responsible for calculating and formatting its statistics while Geeklog provides the common statistics surface.

A useful capability classification is:

```text
Full     = both callbacks are implemented
Partial  = one callback is implemented
None     = neither callback is implemented
```

Statistics support is **not required for basic content interoperability** and should not be part of the core Hub readiness score. It is nevertheless valuable for dashboards, administration, reporting, and future Hub aggregation features.

Consumers should prefer these native callbacks over direct reads of another plugin's tables when the goal is to obtain the plugin's own statistical presentation or summary.

## Content Syndication

Plugins that should be available through Geeklog's **Content Syndication** administration (`/admin/syndication.php`) can expose native feed support through:

```php
plugin_getfeednames_PLUGIN()
plugin_getfeedcontent_PLUGIN()
```

`plugin_getfeednames_PLUGIN()` exposes the feed choices a plugin makes available, while `plugin_getfeedcontent_PLUGIN()` supplies the feed entries and metadata used by Geeklog to generate RSS/Atom output.

A plugin may additionally implement:

```php
plugin_feedupdatecheck_PLUGIN()
```

This callback lets Geeklog determine efficiently whether an existing feed needs to be regenerated after content changes.

Recommended capability classification:

```text
Full     = getFeedNames + getFeedContent
Partial  = only one of the two primary callbacks
None     = neither primary callback
```

`plugin_feedupdatecheck_*()` is an optional optimization and should be reported separately rather than required for Full syndication support.

Content Syndication is a distribution capability, not a replacement for `plugin_getiteminfo_*()`. Feed rendering and structured inter-plugin metadata serve different consumers and should remain separate.

## XML Sitemap contribution

Geeklog's XMLSitemap integration has a specific collection contract that should be recognized explicitly.

Since Geeklog 2.1.1, sitemap collection can use:

```php
plugin_collectSitemapItems_PLUGIN($uid, $limit)
```

through the core dispatcher:

```php
PLG_collectSitemapItems($type, $uid, $limit)
```

A plugin implementing `plugin_collectSitemapItems_*()` provides the **native sitemap collector** for its content type.

If the plugin does not provide that callback, the XMLSitemap plugin can fall back to collection through:

```php
PLG_getItemInfo($type, '*', $what, $uid, $options)
```

Therefore sitemap interoperability should distinguish at least:

```text
Native collector      = plugin_collectSitemapItems_PLUGIN() exists
Item Info fallback    = collection can be obtained through plugin_getiteminfo_PLUGIN('*', ...)
None detected         = neither path is available
```

This distinction matters because implementing `plugin_getiteminfo_*()` with collection support already makes a content plugin useful to XMLSitemap even when it does not implement the specialized sitemap collector.

The specialized collector remains preferable when sitemap-specific behavior, permissions, filtering, priorities, or performance considerations justify it.

Lifecycle notifications complement this collection contract: XMLSitemap may listen to `PLG_itemSaved()` and `PLG_itemDeleted()` to know when tracked content changes, while the collector or Item Info interface remains responsible for supplying the addressable content itself.

## Services

Geeklog services should be added when another plugin genuinely needs a specialized action, transaction, or rendering capability that is not covered by content metadata.

Services should not be introduced merely to duplicate `plugin_getiteminfo_*()`.

---

# 8. Recommended implementation priorities

| Priority | Capability | Purpose |
| --- | --- | --- |
| **P1** | `plugin_getiteminfo_PLUGIN()` | Expose structured content metadata |
| **P1** | `'*'` collection support | Expose multiple content items and provide the XMLSitemap fallback path |
| **P1** | `since`, `limit`, `order` options | Retrieve recent or changed content |
| **P1** | `PLG_itemSaved()` | Signal create/update lifecycle changes |
| **P1** | `PLG_itemDeleted()` | Signal deletions |
| **P2** | `plugin_idtourl_PLUGIN()` | Resolve canonical item URLs where supported |
| **P2** | `plugin_collectSitemapItems_PLUGIN()` | Provide optimized/native XML Sitemap collection where useful |
| **P2/P3** | `plugin_getfeednames_PLUGIN()` + `plugin_getfeedcontent_PLUGIN()` | Participate in Content Syndication when the content type is feed-worthy |
| **P3** | `plugin_feedupdatecheck_PLUGIN()` | Optimize feed regeneration |
| **P3** | `plugin_showstats_PLUGIN()` + `plugin_statssummary_PLUGIN()` | Contribute to native Geeklog statistics where meaningful |
| **P3** | `plugin_whatsnewsupported_PLUGIN()` | Participate in Geeklog What's New |
| **P3** | `plugin_getwhatsnew_PLUGIN()` | Render recent items in What's New |
| Future | `plugin_getrelateditems_PLUGIN()` | Support Hub relations and recommendations |

For the next modernization work on **Maps, Documents, Videos, Store**, and similar content plugins, the P1 capabilities should be treated as the common interoperability baseline. P2/P3 distribution capabilities should be added when they fit the plugin's role and user value rather than mechanically implemented everywhere.

---

# 9. Example target for Maps

A Maps modernization should aim to expose at least:

```php
function plugin_getiteminfo_maps($id, $what, $uid = 0, $options = array())
```

with support for:

```text
id
title
url
description or excerpt
date-created
date-modified
```

and collection queries such as:

```php
$options = array(
    'since' => $timestamp,
    'limit' => 20,
    'order' => 'modified-desc'
);

$items = plugin_getiteminfo_maps(
    '*',
    'id,title,url,excerpt,date-modified',
    0,
    $options
);
```

Maps should also emit:

```php
PLG_itemSaved($map_id, 'maps');
PLG_itemDeleted($map_id, 'maps');
```

and, where supported:

```php
function plugin_idtourl_maps($sub_type, $item_id)
```

If Maps should participate directly in XMLSitemap with sitemap-specific collection logic, it may also implement:

```php
function plugin_collectSitemapItems_maps($uid, $limit)
```

Otherwise, a complete `plugin_getiteminfo_maps('*', ...)` implementation provides the supported XMLSitemap fallback path.

If Maps content is useful as an RSS/Atom source, it may additionally expose:

```php
plugin_getfeednames_maps()
plugin_getfeedcontent_maps()
plugin_feedupdatecheck_maps() // optional optimization
```

If Maps has meaningful site-level statistics, it may contribute them through:

```php
plugin_showstats_maps()
plugin_statssummary_maps()
```

The same pattern can then be applied to Documents, Videos, Store, and other addressable content plugins, while only implementing optional distribution/presentation capabilities that make sense for each plugin.

---

# 10. Consumer responsibilities

The contract also places requirements on consumers.

## Hello

Hello should:

- request structured content rather than read another plugin's SQL tables;
- use collection filters to retrieve items since the last digest;
- use Item Info fields to build email content;
- ignore unsupported plugins gracefully;
- preserve each plugin's permission model.

## Hub

Hub should:

- treat `plugin + item_id + nullable item_sub_type` as the external content identity;
- listen to lifecycle events rather than poll plugin tables where practical;
- retrieve metadata through Item Info after an event;
- resolve URLs through `plugin_idtourl_*()` when available, with an Item Info fallback;
- audit native Statistics, Content Syndication, and XML Sitemap capabilities separately from basic content readiness;
- avoid becoming the owner of another plugin's content.

## Content Syndication

Geeklog's syndication layer should remain the owner of feed generation. Plugins should expose feed choices/content through the native callbacks rather than external consumers duplicating plugin-specific feed SQL.

## XMLSitemap

XMLSitemap should prefer `PLG_collectSitemapItems()` / `plugin_collectSitemapItems_*()` where available and use the supported `PLG_getItemInfo($type, '*', ...)` fallback otherwise.

A plugin should not need XMLSitemap-specific SQL adapters merely to become discoverable if it already exposes a complete collection-capable Item Info contract.

## Other consumers

IndexNow, Search, AI/agent layers, dashboards, and future integrations should reuse the same normalized metadata and native Geeklog callback surfaces wherever practical rather than invent plugin-specific adapters.

---

# Design principle

The plugin remains the authority for its own content.

Other plugins should not need to know:

- database tables;
- column names;
- internal file paths;
- routing implementation;
- permission internals;
- business rules.

They should interact through a small, stable Geeklog interoperability surface:

```text
                         Content plugin
                              │
        ┌─────────────────────┼──────────────────────┐
        │                     │                      │
 getItemInfo              lifecycle            distribution
        │              saved / deleted                │
        │                     │            ┌──────────┼──────────┐
        │                     │            │          │          │
        ↓                     ↓          feeds     sitemap     stats
 structured data             Hub       syndication  collector  callbacks
        │
   ┌────┼───────────────┐
   ↓    ↓               ↓
 Hello  Hub          IndexNow / other consumers
```

The long-term objective is not to create a Hub-specific or Hello-specific API.

It is to make Geeklog plugins **interoperable by design**, so multiple consumers can reuse the same content contract and Geeklog's existing distribution surfaces without coupling themselves to plugin internals.
