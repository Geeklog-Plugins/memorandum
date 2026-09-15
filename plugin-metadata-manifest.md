# Geeklog plugin metadata manifest

## Status

This document defines a **recommended modernization convention** for Geeklog plugins. It is not currently a Geeklog Core API requirement.

The goal is to expose basic plugin identity and compatibility metadata without executing plugin PHP code. This is useful for disabled plugins, pre-installation discovery, repository catalogs, administration tools, Monitor, Hub, Connector and future ecosystem tooling.

The convention complements, rather than replaces, existing Geeklog Plugin API callbacks such as `plugin_geticon_<plugin>()` and `PLG_getIcon()` and installation metadata declared by the plugin itself.

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
  "name": "Maps"
}
```

A fuller form can expose an icon and minimum runtime requirements:

```json
{
  "schema": 1,
  "id": "maps",
  "name": "Maps",
  "icon": "admin/images/maps.png",
  "requires": {
    "geeklog": "2.1.1",
    "php": "5.6.0"
  }
}
```

### Required fields

- `schema` — integer manifest schema version. Version 1 is defined by this document.
- `id` — canonical Geeklog plugin identifier, normally the value used in `pi_name` and Plugin API callback suffixes.
- `name` — human-readable plugin name.

### Recommended fields

- `icon` — repository/package-relative path to the plugin administrative icon.
- `requires` — object containing minimum compatibility requirements that can be established confidently from the plugin source and release policy.

The `requires` object currently defines these keys:

- `geeklog` — minimum supported Geeklog version, for example `2.1.1`.
- `php` — minimum supported PHP version, for example `5.6.0`.

Consumers such as Monitor may use these values for repository discovery, compatibility reporting and pre-installation diagnostics without loading plugin PHP code.

These fields are descriptive metadata. They MUST NOT replace the plugin's native install or upgrade checks. In particular, `requires.geeklog` SHOULD remain consistent with the minimum Geeklog version declared by `pi_gl_version` in `autoinstall.php`, and `requires.php` SHOULD reflect the actual minimum PHP version supported by the code and release policy.

If a requirement cannot be determined confidently, it SHOULD be omitted rather than guessed.

## Icon path rules

The `icon` path MUST be relative. Absolute filesystem paths, site URLs and remote URLs MUST NOT be stored in `icon`.

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

## Relationship with existing Plugin API and installer metadata

`plugin_geticon_<plugin>()` remains the native runtime integration point. Existing plugins do not need to remove it.

Likewise, `plugin.json` does not replace the metadata and compatibility checks used by Geeklog during installation and upgrade. The static manifest solves a different problem: safe metadata discovery before installation, while disabled, or from a repository catalog.

Where both mechanisms exist:

- the manifest `id` SHOULD match the plugin `pi_name`;
- the manifest `name` SHOULD match the public plugin name;
- the manifest `icon` SHOULD represent the same asset as the native runtime icon;
- `requires.geeklog` SHOULD match the minimum supported Geeklog version declared by the plugin;
- `requires.php` SHOULD match the minimum PHP version actually supported by the codebase.

Consumers SHOULD treat native runtime/install checks as authoritative when a plugin is installed and active. The manifest is primarily a discovery and reporting source.

## Safety and compatibility

The manifest:

- contains no executable code;
- can be inspected before installation;
- can be consumed for disabled plugins;
- is safe for GitHub repository catalogs;
- can expose minimum Geeklog and PHP requirements without loading plugin PHP;
- does not alter Geeklog Core;
- does not change plugin enable/disable behavior;
- does not replace installation metadata or database plugin records.

Consumers MUST validate JSON and paths. In particular, `icon` MUST NOT be allowed to escape the plugin/package root through `..` traversal.

Consumers MUST also validate requirement values before using them for version comparisons. Unknown keys inside `requires` SHOULD be ignored by schema-1 consumers rather than causing the whole manifest to fail.

## Automated adoption in Geeklog-Plugins

The organization-level metadata audit/generator SHOULD:

1. enumerate plugin repositories;
2. skip organization infrastructure and archived repositories;
3. leave an existing valid `plugin.json` untouched unless a deliberate migration or normalization is requested;
4. identify the plugin id from existing Plugin API or installer code when possible;
5. locate an existing icon, preferring the asset referenced by `plugin_geticon_<plugin>()`;
6. derive `requires.geeklog` from authoritative plugin installer metadata such as `pi_gl_version` when available;
7. derive `requires.php` only when the minimum supported PHP version is explicit or can be established confidently from maintained release policy;
8. generate only metadata that can be established confidently;
9. report repositories requiring manual review instead of inventing icons or compatibility requirements;
10. use pull requests for cross-repository changes rather than silently rewriting default branches.

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

with Geeklog 2.1.1 and PHP 5.6.0 as its maintained minimum requirements, then the static manifest can be:

```json
{
  "schema": 1,
  "id": "maps",
  "name": "Maps",
  "icon": "admin/images/maps.png",
  "requires": {
    "geeklog": "2.1.1",
    "php": "5.6.0"
  }
}
```

This lets tooling identify the plugin, resolve its icon and report its minimum runtime requirements without executing `functions.inc` or installer code.

## Example: plugin without an icon

An icon is recommended but not mandatory. If a plugin has no reliable administrative icon, the manifest SHOULD omit the field rather than invent one:

```json
{
  "schema": 1,
  "id": "amazonlinks",
  "name": "Amazon Links",
  "requires": {
    "geeklog": "2.1.1",
    "php": "5.6.0"
  }
}
```

This remains a valid schema-1 manifest and can be consumed by Monitor and other ecosystem tooling.