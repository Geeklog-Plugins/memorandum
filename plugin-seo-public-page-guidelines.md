# Geeklog Plugin SEO Public Page Guidelines

## Purpose

This document defines the page-level SEO baseline for modernized Geeklog plugins that expose public addressable resources. It complements seo-measurement-interoperability-guide.md, which focuses on measurement and cooperation between Hub, IndexNow, Analytics, Search Console and Bing Webmaster.

## Canonical identity and indexability

Every canonical resource should have a stable provider-owned ID, meaningful title and canonical URL. Decide explicitly whether each route/resource type should be indexed. Administration pages, form-processing endpoints, duplicate query variants, previews, private resources and empty search/filter states should not become accidental canonical search pages.

## Titles and meta descriptions

Canonical pages should provide meaningful document titles and visible page headings describing the same subject. Avoid generic titles such as Details or Item. When useful descriptive content exists, provide a concise resource-specific meta description or normalized plain-text excerpt. Avoid duplicate generic descriptions and raw HTML.

## Canonical URLs

The owning plugin is authoritative for URL generation. Expose canonical URLs through Item Info and plugin_idtourl_PLUGIN() where supported. Keep one preferred public URL per logical resource and plan redirects/migration deliberately when canonical patterns change.

## Crawlable navigation and semantic HTML

Primary navigation should use normal HTML anchors, not only JavaScript click handlers. Use logical headings, semantic lists, article/nav/figure/details elements where appropriate, and do not manufacture headings merely for keyword placement.

## Structured data

Use Schema.org only when the visible page genuinely matches the schema type. Possible types include Article, FAQPage, VideoObject, Product, Event, BreadcrumbList and ImageObject. Avoid duplicate/conflicting schema from multiple plugins. The content owner normally owns the primary page schema; contextual plugins may contribute narrowly scoped schema where appropriate.

## Open Graph and social metadata

For share-worthy resources, cooperate with the site's metadata layer to expose title, description, canonical/social URL and representative image. Plugin metadata must not blindly overwrite better page-level metadata from the content owner, Core or theme.

## Images and media

Use descriptive alt text for informative images, responsive sizing, stable dimensions/aspect ratio when practical, and representative image metadata when relevant. Alt text is not a keyword field.

## Containers are real SEO resources when they have value

Categories, albums, forums, channels and root/catalogue pages may be indexable resources when they provide genuine navigation/editorial value. Such pages should have a unique title, canonical URL, useful context/introduction where possible, crawlable child links, stable pagination and no arbitrary crawlable filter explosion.

Examples include documents:category:12, mediagallery:album:45, forum:forum:8 and classifieds:category:4.

## Pagination and filters

Use bounded, deterministic pagination. Distinguish editorial categories from temporary filter/sort state. Do not generate a large crawlable URL space from every filter combination.

## Sitemap, lifecycle and IndexNow cooperation

Canonical resources intended for discovery should participate in XML Sitemap through plugin_collectSitemapItems_PLUGIN() or the Item Info collection fallback. Successful content mutations should emit lifecycle events so IndexNow and other consumers can react without private SQL access. Content publication must not fail merely because an SEO/measurement consumer is unavailable.

## Avoid stale duplicated metadata

Keep metadata tied to the provider's source of truth. On rename/update/delete, ensure titles, descriptions, canonical URLs, provider collections and sitemap output reflect current state. Redirect planning is required when canonical routes change.

## SEO acceptance checklist

- [ ] stable provider-owned ID
- [ ] canonical URL
- [ ] meaningful document title
- [ ] clear visible H1/page heading
- [ ] useful meta description when appropriate
- [ ] explicit indexability decision
- [ ] crawlable internal links
- [ ] semantic HTML
- [ ] valid structured data where implemented
- [ ] social metadata does not conflict with ownership
- [ ] informative images have appropriate alt text
- [ ] container pages have real value and stable pagination
- [ ] sitemap participation where appropriate
- [ ] lifecycle events emitted after successful changes
- [ ] consumers do not duplicate provider routing
- [ ] final rendered page has been inspected

## Relationship with measurement SEO

This guide answers: Is the page technically and semantically ready to be discovered and understood? seo-measurement-interoperability-guide.md answers: How do Geeklog plugins measure visibility, indexing and user behavior after publication?

## Guiding principle

> Own one canonical, useful page for each public resource; expose it clearly to users, Geeklog consumers and search engines.