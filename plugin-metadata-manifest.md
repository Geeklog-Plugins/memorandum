# Geeklog plugin metadata manifest

## Status

This document defines a **recommended modernization convention** for Geeklog plugins. It is not currently a Geeklog Core API requirement.

The goal is to expose basic plugin identity without executing plugin PHP code. This is useful for disabled plugins, pre-installation discovery, repository catalogs, administration tools, Monitor, Hub, Connector and future ecosystem tooling.

The convention complements, rather than replaces, existing Geeklog Plugin API callbacks such as `plugin_geticon_<plugin>()` and `PLG_getIcon()`.

## File name and location

A modernized plugin SHOULD provide this file at the repository/package root:

```text
plugin.json
```

The file MUST be valid UTF-8 JSON and MUST contain only static metadata.

## Schema version 1

The minimal form is:

```json
{
  "schema": 1,
  "id": "maps",
  "name": "Maps",
  "icon": "admin/images/maps.png"
}
```

### Required fields

- `schema` — integer manifest schema version. Version 1 is defined by this document.
- `id` — canonical Geeklog plugin identifier, normally the value used in `pi_name` and Plugin API callback suffixes.
- `name` — human-readable plugin name.

### Recommended field

- `icon` — repository/package-relative path to the plugin administrative icon.

The path MUST be relative. Absolute filesystem paths, site URLs and remote URLs MUST NOT be stored in `icon`.

For a traditional Geeklog plugin package, an icon exposed at runtime as:

```text
/site-admin/plugins/maps/images/maps.png
```

will commonly exist in the source package as:

```text
admin/images/maps.png
```

and the manifest should therefore contain:

```json
"icon": "admin/images/maps.png"
```

Consumers are responsible for translating package-relative paths to installed URLs where required.

## Icon resolution policy

Consumers SHOULD resolve an icon in this order:

1. use the native Geeklog `PLG_getIcon($plugin)` result when the installed plugin is enabled and its runtime API is available;
2. read local `plugin.json` and its `icon` path without loading disabled plugin PHP solely for metadata;
3. for repository discovery, read `plugin.json` from the repository and resolve the repository-relative icon;
4. use a neutral generic plugin icon if no declared icon can be resolved.

A consumer MUST NOT enable a plugin or load otherwise-disabled plugin runtime code merely to discover its icon.

## Relationship with existing Plugin API

`plugin_geticon_<plugin>()` remains the native runtime integration point. Existing plugins do not need to remove it.

The static manifest solves a different problem: metadata discovery when runtime callbacks are unavailable or should not be executed.

Where both mechanisms exist, their icons SHOULD represent the same asset.

## Safety and compatibility

The manifest:

- contains no executable code;
- can be inspected before installation;
- can be consumed for disabled plugins;
- is safe for GitHub repository catalogs;
- does not alter Geeklog Core;
- does not change plugin enable/disable behavior;
- does not replace installation metadata or database plugin records.

Consumers MUST validate JSON and paths. In particular, `icon` MUST NOT be allowed to escape the plugin/package root through `..` traversal.

## Automated adoption in Geeklog-Plugins

The organization-level metadata audit/generator SHOULD:

1. enumerate plugin repositories;
2. skip organization infrastructure and archived repositories;
3. leave an existing valid `plugin.json` untouched;
4. identify the plugin id from existing Plugin API code when possible;
5. locate an existing icon, preferring the asset referenced by `plugin_geticon_<plugin>()`;
6. generate only metadata that can be established confidently;
7. report repositories requiring manual review instead of inventing icons;
8. use pull requests for cross-repository changes rather than silently rewriting default branches.

The generator MUST be idempotent and MUST NOT overwrite an existing manifest merely because its generated proposal differs.

## Example: Maps

If Maps exposes its runtime icon through:

```php
function plugin_geticon_maps()
{
    global $_CONF;
    return $_CONF['site_admin_url'] . '/plugins/maps/images/maps.png';
}
```

and the repository contains:

```text
admin/images/maps.png
```

then the static manifest is:

```json
{
  "schema": 1,
  "id": "maps",
  "name": "Maps",
  "icon": "admin/images/maps.png"
}
```

This lets tooling identify the same icon without executing `functions.inc`.
