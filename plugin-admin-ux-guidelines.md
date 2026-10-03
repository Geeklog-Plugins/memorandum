# Geeklog Plugin Administration UX Guidelines

## Purpose

Administration is not merely a set of forms that technically work. It is an application surface used by people who may discover the plugin for the first time or return to it only occasionally. Administration should be understandable, efficient, documented, safe, visually coherent, theme-neutral and responsive.

This guide complements plugin-admin-navigation.md: that document defines discovery/navigation; this document defines how the pages themselves should behave.

## First page: orientation

The main administration page should normally explain, briefly, what the plugin does, the main objects it manages, the most common first action, links to principal sections, important prerequisites, and the current empty/status state.

A useful first-use structure is:

```text
Plugin name
Short purpose statement

Getting started
1. Configure the essential settings.
2. Create or import the first item.
3. Verify the public result.

Primary actions / sections
Status or recent items
```

## Built-in help for new users

For any non-trivial plugin, provide a concise Getting started, Help or How to use path. It may be a short block on the administration home page, a collapsible help section, a dedicated Help page, or contextual help around a complex workflow.

The minimum guide should answer: what is the plugin for, what should be configured first, how to create/manage the main object, where the result appears publicly, and what to check when nothing appears. Link to deeper README/manual documentation when useful, but keep the essential first-use workflow inside the installed plugin.

## Navigation consistency

Use plugin_getadminoption_PLUGIN() and plugin_cclabel_PLUGIN() where appropriate. Use ADMIN_createMenu() for page actions when it fits, and the shared plugin-admin-nav convention for persistent peer sections. Keep section order stable, mark the current section, keep Configuration easy to find, and avoid duplicate destinations.

## One primary task per page

Prefer: page title, short context/help, filters or primary form, primary action, result/list, then secondary/destructive actions. Split unrelated workflows into peer sections rather than accumulating visual patches.

## Separate forms and lists visually

Create/edit forms, filters, result lists and destructive controls must be visually distinct through headings, spacing and container structure. Do not rely on accidental theme spacing.

## Forms and progressive disclosure

Use explicit labels, sensible defaults, local help, and native configuration tooltips for consequential settings. Provider-discovered values should be selected rather than typed manually. Advanced or legacy fallbacks should be disclosed progressively and not given the same visual weight as the normal workflow.

## Lists should be actionable

Show human-readable titles first and technical IDs as secondary information. Provide direct public links where useful, concise status, deterministic sorting and filters for large datasets. Do not show only raw identities such as documents:3-airbus-a321-neo when the provider can supply a title.

## Destructive actions

Delete, purge, reset, rebuild and migration actions must be separated visually, protected by CSRF checks, confirmed when consequential, and documented so the administrator understands what will and will not be removed.

## Feedback, diagnostics and empty states

After an action, explicitly report saved, updated, deleted, skipped, failed, partial or unavailable states. Diagnostics should identify the affected subsystem, consequence and next action without exposing secrets. Empty states should teach the next step rather than merely show 0 rows.

## Administration CSS and JavaScript

If administration requires plugin-specific CSS or JavaScript, keep reusable/static assets in external plugin-owned files rather than embedding large `<style>` or `<script>` blocks in templates.

Admin-only assets should be loaded only on the plugin's administration routes where practical and must use deterministic cache-busting/versioning so an upgrade does not leave stale browser assets. The installable archive must contain the referenced files.

See [Plugin asset loading and cache versioning](plugin-asset-loading-versioning.md).

## Responsive and accessible administration

Test navigation wrapping, form widths, tables, long IDs/URLs, action buttons and dialogs on narrow screens. Preserve keyboard operation, visible focus, labels, accessible names for icon-only controls, and status communication that does not rely on color alone.

## Documentation ownership

Installed help must match the shipped UI. When workflows change, update the Getting started text, Help page, README/ROADMAP references and tooltips, and remove obsolete instructions.

## Administration acceptance checklist

- [ ] native admin entry is discoverable
- [ ] first page explains the plugin purpose
- [ ] concise Getting started/Help exists for non-trivial workflows
- [ ] current section is obvious
- [ ] page has one primary task or clear grouping
- [ ] forms and lists are visually separated
- [ ] advanced fallbacks are not the normal path
- [ ] human titles are preferred over raw IDs
- [ ] useful public links are available
- [ ] action feedback is explicit
- [ ] empty states explain the next step
- [ ] destructive actions are separated and confirmed
- [ ] mobile layout is usable
- [ ] keyboard/focus behavior is usable
- [ ] help and tooltips are current
- [ ] no theme framework is required for core administration use
- [ ] plugin-specific admin CSS/JS is externalized where reusable/static
- [ ] admin assets are loaded only where needed
- [ ] admin asset URLs are deterministically versioned
- [ ] packaged archive contains every referenced admin asset

## Guiding principle

> An administrator should be able to discover the plugin, understand its purpose, perform the first useful task, and verify the result without reading the source code.