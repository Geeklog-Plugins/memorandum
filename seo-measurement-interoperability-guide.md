# Geeklog SEO & Measurement Interoperability Guide

## Purpose

This document defines how the next generations of **Hub**, **IndexNow**, **Analytics**, **Google Search Console**, **Bing Webmaster**, and Geeklog content plugins should cooperate without becoming tightly coupled.

It complements [`plugin-content-interoperability-contract.md`](plugin-content-interoperability-contract.md).

The content interoperability contract defines how a content-owning plugin exposes an item, its metadata, lifecycle events, and canonical URL. This guide defines how SEO, measurement, indexing, and orchestration plugins should consume and enrich that information.

The objective is to make it possible to answer, for any addressable Geeklog content item:

- what is this content?
- what is its canonical URL?
- when did it change?
- was the change submitted to search engines?
- how visible is it in Google Search?
- how visible is it in Bing Search?
- what happens after users reach the page?
- what action or optimization should be recommended?

The intended compatibility target for current modernization work remains:

- **Geeklog 2.1.1 through 2.2.2**
- **PHP 5.6 through PHP 8.1**

---

# 1. Architectural principle

Each plugin should keep one clear responsibility.

```text
IndexNow       = announce content changes
Search Console = measure Google Search visibility
Bing Webmaster = measure Bing Search visibility and indexing
Analytics      = measure on-site audience and behavior
Hub            = connect, consolidate, interpret and recommend
Content plugin = own the content, permissions and canonical URL
```

Hub should orchestrate these capabilities, but it should not become a duplicate implementation of Google Analytics, Search Console, Bing Webmaster, or IndexNow.

Likewise, Analytics should not become a generic container for every SEO provider.

The preferred model is:

```text
                    HUB
                     |
         type + id + canonical URL
                     |
       +-------------+-------------+
       |             |             |
       v             v             v
   Analytics   Search Console     Bing
   audience      Google SEO      Bing SEO

Content lifecycle
       |
       v
    IndexNow
       |
       v
 search engines
```

---

# 2. Common content identity

All participating plugins should share the same minimal content identity:

```text
type + id + url
```

Examples:

```text
article / welcome
staticpages / about
maps / 2
maps / marker:123
videos / 456
```

A normalized representation may use:

```php
array(
    'type' => 'maps',
    'id' => 'marker:123',
    'url' => 'https://example.org/maps/index.php?mode=marker&mkid=123'
);
```

The owning plugin remains authoritative for the relationship between `type + id` and the canonical URL.

Consumers must not reconstruct plugin URLs by duplicating another plugin's routing logic.

---

# 3. Content plugins: required interoperability baseline

Content-owning plugins such as Maps, Videos, Documents, Store, Forum extensions, and similar addressable plugins should follow the content interoperability contract.

At minimum, they should progressively support:

```php
plugin_getiteminfo_PLUGIN($id, $what, $uid = 0, $options = array())
```

with commonly useful fields such as:

```text
id
type
subtype
title
url
description
excerpt
date-created
date-modified
uid
author
```

They should emit lifecycle events on successful changes:

```php
PLG_itemSaved($id, 'PLUGIN');
PLG_itemDeleted($id, 'PLUGIN');
```

They should also expose deterministic item-to-URL resolution where appropriate:

```php
plugin_idtourl_PLUGIN($sub_type, $item_id)
```

For plugins supporting Geeklog 2.1.1, namespaced IDs should remain sufficient to identify subtypes when `sub_type` is unavailable.

Example:

```text
maps / marker:123
```

rather than requiring a newer-core-only subtype parameter.

---

# 4. Add URL-to-item resolution

The next important interoperability capability is the reverse direction:

```text
URL -> type + id
```

This is necessary because Search Console, Bing Webmaster, Analytics, log analyzers, crawlers, and external APIs usually identify content by URL rather than by Geeklog plugin ID.

A modernized content plugin should therefore progressively expose a URL resolver.

Recommended callback convention:

```php
function plugin_urltoid_PLUGIN($url)
```

Example result:

```php
array(
    'type' => 'maps',
    'id' => 'marker:123',
    'subtype' => 'marker'
);
```

A plugin should return an empty value when the URL does not belong to it.

The plugin remains responsible for its own routing rules.

Consumers should not parse another plugin's query string or path directly when a plugin resolver exists.

This capability is a **proposed interoperability convention**, not a claim that current Geeklog core already provides a universal `PLG_urlToId()` dispatcher.

A future Geeklog core or shared compatibility helper may provide a dispatcher once enough plugins implement this convention.

---

# 5. IndexNow responsibilities

IndexNow is an event consumer and submission transport.

It should listen to:

```php
PLG_itemSaved()
PLG_itemDeleted()
```

For core types with established behavior, existing URL resolution may remain in place.

For plugin-owned content, IndexNow should ask the owning plugin for the canonical URL rather than contain plugin-specific routing rules.

Preferred save resolution order:

```text
PLG_getItemInfo(type, id, 'url')
        |
        +-- URL found -> submit
        |
        +-- no URL -> optional plugin_idtourl_PLUGIN() fallback
```

Preferred delete resolution order:

```text
plugin_idtourl_PLUGIN()
        |
        +-- deterministic URL found -> submit
        |
        +-- no URL -> optional Item Info fallback
```

Deletion resolution should favor deterministic URL generation because the database record may already be gone.

IndexNow should not know the SQL schema of Maps, Videos, Documents, Store, or any other content plugin.

## Recommended IndexNow status exposure

IndexNow should progressively make its most recent result available to Hub or administration tools.

A minimal normalized state may look like:

```php
array(
    'provider' => 'indexnow',
    'event' => 'saved',
    'url' => $url,
    'submitted_at' => $timestamp,
    'status' => 'success',
    'http_code' => 202
);
```

Possible statuses:

```text
success
failed
not-configured
not-resolved
queued
```

This state is informational. Hub should not become responsible for performing the IndexNow submission itself.

---

# 6. Analytics responsibilities

The Analytics plugin should keep two clearly separated capabilities.

## Measurement

Continue to manage the site's analytics measurement integration.

## Reporting

Progressively support reading Google Analytics reporting data for a URL or page path.

The important interoperability interface is not Google-specific authentication or API details. It is the normalized result returned to a consumer such as Hub.

Recommended conceptual service:

```php
ANALYTICS_getUrlMetrics($url, $period, $options = array())
```

Recommended normalized result:

```php
array(
    'provider' => 'google-analytics',
    'period' => 28,
    'views' => 0,
    'users' => 0,
    'sessions' => 0,
    'engagement_seconds' => 0,
    'conversions' => 0
);
```

Provider-specific fields may be added, but common names should remain stable.

Analytics should accept URLs or canonical page paths. It should not need to understand a Maps marker ID, Video ID, Store product ID, or other plugin internals.

---

# 7. Google Search Console responsibilities

A Search Console integration should expose Google Search visibility by URL.

Recommended initial capability:

```php
SEARCHCONSOLE_getUrlMetrics($url, $period, $options = array())
```

Recommended normalized result:

```php
array(
    'provider' => 'google-search-console',
    'period' => 28,
    'clicks' => 0,
    'impressions' => 0,
    'ctr' => 0.0,
    'position' => null
);
```

Recommended query-level capability:

```php
SEARCHCONSOLE_getUrlQueries($url, $period, $limit = 20, $options = array())
```

Recommended row format:

```php
array(
    'query' => 'example query',
    'clicks' => 0,
    'impressions' => 0,
    'ctr' => 0.0,
    'position' => null
);
```

Future capabilities may include:

```text
URL inspection
indexing state
sitemap state
mobile/device segmentation
country segmentation
search appearance
```

Search Console should not need plugin-specific SQL or routing knowledge.

---

# 8. Bing Webmaster responsibilities

Bing Webmaster should follow the same interoperability philosophy as Search Console wherever the underlying Bing data allows it.

Recommended URL metrics service:

```php
BING_getUrlMetrics($url, $period, $options = array())
```

Recommended common result:

```php
array(
    'provider' => 'bing-webmaster',
    'period' => 28,
    'clicks' => 0,
    'impressions' => 0,
    'ctr' => 0.0,
    'position' => null
);
```

Recommended indexing/crawl status service:

```php
BING_getUrlStatus($url, $options = array())
```

Recommended normalized result:

```php
array(
    'provider' => 'bing-webmaster',
    'url' => $url,
    'indexed' => null,
    'last_crawl' => 0,
    'status' => 'unknown',
    'message' => ''
);
```

Bing-specific information may be added without changing the common fields.

Bing Webmaster should remain separate from IndexNow:

```text
IndexNow       = outbound change notification
Bing Webmaster = inbound search/indexing intelligence
```

---

# 9. Normalize search-performance metrics

Search Console and Bing Webmaster should use the same names for equivalent concepts whenever practical.

Baseline search-performance schema:

```php
array(
    'provider' => '',
    'period' => 28,
    'clicks' => 0,
    'impressions' => 0,
    'ctr' => 0.0,
    'position' => null
);
```

Rules:

- `provider` identifies the source;
- `period` represents the requested reporting period in days where applicable;
- `clicks` and `impressions` are integers or numeric values returned by the provider;
- `ctr` should preferably be normalized as a ratio from `0.0` to `1.0`;
- `position` may be `null` when the provider cannot supply a meaningful value.

Consumers should not assume that Google and Bing calculate every metric identically. Normalization creates a common presentation contract, not a claim that provider methodologies are identical.

---

# 10. Normalize indexing and crawl state

Where a provider exposes indexing or crawl state, plugins should converge on a common result shape.

Recommended baseline:

```php
array(
    'provider' => '',
    'url' => '',
    'indexed' => null,
    'last_crawl' => 0,
    'status' => 'unknown',
    'message' => ''
);
```

Recommended `status` values:

```text
ok
warning
error
excluded
unknown
```

Provider-specific raw state may also be returned in additional fields.

Hub should display normalized state while preserving access to provider detail when useful.

---

# 11. Hub responsibilities

Hub is the orchestrator and interpretation layer.

Given:

```text
type = maps
id = marker:123
```

Hub should be able to:

1. request structured metadata from Maps;
2. obtain the canonical URL;
3. request audience metrics from Analytics;
4. request Google Search performance from Search Console;
5. request Bing Search performance/indexing from Bing Webmaster;
6. obtain IndexNow submission state when available;
7. combine these signals with Hub relations and content context;
8. present useful recommendations.

Conceptual flow:

```text
Hub
 |
 +-- PLG_getItemInfo(type, id)
 |       -> title, URL, dates, metadata
 |
 +-- Analytics
 |       -> audience and engagement
 |
 +-- Search Console
 |       -> Google clicks, impressions, CTR, position
 |
 +-- Bing Webmaster
 |       -> Bing metrics and indexing/crawl state
 |
 +-- IndexNow
         -> last submission state
```

Hub should store only what it needs for relations, caching, historical comparison, alerts, or recommendation logic.

It should not duplicate whole provider datasets unless a deliberate reporting/history feature requires local persistence.

---

# 12. URL-first service design

SEO and measurement providers generally know pages by URL.

Therefore all provider plugins should expose services that can operate with a canonical URL independently of Hub.

Preferred pattern:

```text
content plugin
    type + id
        |
        v
canonical URL
        |
        +--> Analytics
        +--> Search Console
        +--> Bing Webmaster
```

This keeps providers reusable by:

- Hub;
- administration dashboards;
- content editors;
- scheduled reports;
- future recommendation plugins;
- maintenance and diagnostic tools.

---

# 13. Capability discovery

Plugins should progressively advertise which interoperability capabilities they support.

A future common capability description may use names such as:

```php
array(
    'content_info' => true,
    'collections' => true,
    'item_saved' => true,
    'item_deleted' => true,
    'id_to_url' => true,
    'url_to_id' => true,
    'audience_metrics' => false,
    'search_metrics' => false,
    'query_metrics' => false,
    'indexing_status' => false,
    'submission_status' => false
);
```

This is initially a documentation convention rather than a required Geeklog API.

The goal is to let Hub and administration tools detect available integrations instead of hard-coding assumptions.

A compatibility matrix can then show both plugin version and supported interoperability capabilities.

---

# 14. Recommended responsibilities by plugin

| Plugin | Primary responsibility | Should consume | Should expose |
| --- | --- | --- | --- |
| **Hub** | content relations, consolidation, recommendations | Item Info, metrics, provider states | relations, derived insights, capability view |
| **IndexNow** | notify search engines of changed/deleted URLs | lifecycle events, canonical URL | submission state |
| **Analytics** | audience measurement and GA reporting | canonical URL/page path | audience metrics |
| **Search Console** | Google Search intelligence | canonical URL | search metrics, queries, future indexing state |
| **Bing Webmaster** | Bing Search/indexing intelligence | canonical URL | search metrics, indexing/crawl state |
| **Maps / Videos / Documents / Store / etc.** | own content and routing | Geeklog context | Item Info, lifecycle events, ID-to-URL, URL-to-ID |

---

# 15. Recommended implementation priorities

## P1 — common content identity

All addressable content plugins should provide:

```text
type + id + canonical URL
```

and implement the existing content interoperability baseline.

## P1 — IndexNow generic lifecycle handling

IndexNow should resolve plugin-owned URLs generically for saves and deletions without plugin-specific SQL or routing knowledge.

## P1 — Search Console URL metrics

The first Search Console version should prioritize:

```text
property connection
URL metrics
clicks
impressions
CTR
position
query list
7 / 28 / 90 day periods
```

## P1 — Analytics URL metrics

Analytics should add a reporting layer that can return normalized audience metrics for a canonical URL or page path.

## P2 — URL-to-item resolution

Content plugins should add:

```php
plugin_urltoid_PLUGIN($url)
```

so external URL-based data can be attached back to Geeklog content.

## P2 — Hub consolidated content performance

Hub should display provider information for an item without requiring direct knowledge of provider APIs.

## P2 — Bing Webmaster

Bing should implement the same common search metric fields as Search Console where equivalent data exists, plus Bing indexing/crawl state.

## P3 — provider state and history

Add:

```text
IndexNow submission state
Google/Bing indexing state
period-over-period comparisons
local cache/history where justified
```

## P3 — recommendations

Hub may then derive recommendations from combined signals.

Examples:

```text
High impressions + good position + low CTR
    -> improve title / search snippet

Position 8-20 + high engagement
    -> strengthen internal links and content depth

High search CTR + weak engagement
    -> investigate search intent mismatch or page experience

Content changed + IndexNow submitted + no later crawl
    -> monitor indexing state

Strong supporting content + weak pillar visibility
    -> improve Hub linking strategy
```

---

# 16. What plugins must not do

To preserve a modular architecture:

- Hub must not directly query another plugin's SQL tables when an interoperability callback can provide the information;
- IndexNow must not contain routing rules for Maps, Videos, Store, or other content plugins;
- Search Console must not know Geeklog plugin IDs internally;
- Bing Webmaster must not duplicate IndexNow submission logic;
- Analytics must not become the container for Search Console and Bing Webmaster integrations;
- content plugins must not directly depend on Hub, Analytics, Search Console, Bing, or IndexNow merely to publish content;
- provider credentials must remain owned by the provider plugin that uses them;
- provider-specific API response formats should not leak into the common Hub contract when a normalized field exists.

---

# 17. Compatibility and failure rules

Interoperability must fail safely.

A content save or deletion must not fail because:

- IndexNow is not configured;
- Google credentials expired;
- Bing is unavailable;
- Hub is disabled;
- Analytics reporting cannot be reached.

Consumers should:

- detect unavailable callbacks;
- return empty or explicit unavailable states;
- log useful diagnostics;
- avoid PHP fatal errors;
- avoid blocking the owning plugin's successful transaction.

For PHP 5.6 compatibility, current modernization code should avoid newer syntax and use compatible feature detection such as:

```php
function_exists()
is_array()
is_string()
isset()
```

Newer Geeklog features may be used conditionally when safe fallbacks exist.

---

# 18. Suggested first implementation sequence

A practical sequence for the current Geeklog modernization work is:

```text
1. Finish generic IndexNow URL resolution
2. Preserve/extend content interoperability in Maps and other plugins
3. Add Search Console plugin with URL-based search metrics
4. Extend Analytics with URL-based reporting metrics
5. Add URL-to-ID callbacks to content plugins
6. Let Hub combine Item Info + Search Console + Analytics
7. Add Bing Webmaster using the same search metric contract
8. Add provider/indexing status views
9. Add Hub recommendations and alerts
```

This sequence validates the contracts with real implementations before adding broader abstractions.

---

# 19. Target developer checklist

Before declaring a content plugin ready for SEO/measurement interoperability, verify:

- [ ] addressable items have stable `type + id` identities;
- [ ] `plugin_getiteminfo_PLUGIN()` exposes canonical URL and useful metadata;
- [ ] save paths emit `PLG_itemSaved()`;
- [ ] delete paths emit `PLG_itemDeleted()`;
- [ ] deterministic `plugin_idtourl_PLUGIN()` resolution exists where useful;
- [ ] URL-to-item resolution is planned or implemented;
- [ ] no consumer needs direct SQL access to obtain the item's canonical metadata.

Before declaring a provider plugin ready for Hub integration, verify:

- [ ] it accepts canonical URLs independently of Hub;
- [ ] credentials remain internal to the provider plugin;
- [ ] common metrics use normalized field names;
- [ ] provider-specific fields remain optional extensions;
- [ ] unavailable API/network state fails safely;
- [ ] the provider can be disabled without breaking content workflows.

Before declaring Hub ready for a provider, verify:

- [ ] Hub detects whether the provider capability exists;
- [ ] Hub uses normalized results rather than raw provider payloads;
- [ ] Hub can operate when the provider is unavailable;
- [ ] Hub distinguishes source data from derived recommendations;
- [ ] caching/history has an explicit retention and refresh strategy.

---

# 20. Long-term direction

The target is not one large SEO plugin.

The target is a cooperative ecosystem in which each plugin remains focused while sharing enough structure for the whole CMS to become more intelligent.

The intended model is:

```text
Content owns meaning and URL
Events announce change
IndexNow announces change externally
Search Console measures Google visibility
Bing measures Bing visibility and indexing
Analytics measures user behavior
Hub connects the signals and recommends action
```

This architecture should allow additional providers later without redesigning every content plugin.

Possible future providers include other search engines, crawler diagnostics, accessibility audits, structured-data validators, social distribution metrics, commerce analytics, and AI discovery/visibility services.

The long-term principle remains:

> **Expose once, connect many times.**
