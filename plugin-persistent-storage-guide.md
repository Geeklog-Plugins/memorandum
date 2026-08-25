# Geeklog Plugin Persistent Storage Guide

## Purpose

This guide defines practical rules for storing persistent plugin data safely across the current compatibility range:

- **Geeklog 2.1.1 through 2.2.2**
- **PHP 5.6 through PHP 8.1**

It is based on issues encountered while modernizing plugins that store documents, videos, generated assets or other data outside normal SQL tables.

## Core rule

Persistent plugin data must not be treated as disposable cache data.

A plugin must clearly distinguish between:

```text
cache
    temporary and rebuildable

generated data
    reproducible from another source

persistent plugin data
    required for the plugin to retain its state

user files
    uploaded or created content that must survive cache cleanup and upgrades
```

A cache cleanup must never remove persistent plugin content.

## Derive storage from the current site

Plugins should derive their persistent data location from the current site's `$_CONF['path_data']` rather than from one hard-coded global path.

A practical pattern used by modernized plugins is to create a sibling directory whose name is derived from the current site's data directory.

PHP 5.6-compatible example:

```php
function MYPLUGIN_dataDir()
{
    global $_CONF;

    $base = isset($_CONF['path_data']) ? rtrim($_CONF['path_data'], "/\\") : '';

    if ($base === '') {
        return '';
    }

    return dirname($base) . DIRECTORY_SEPARATOR
        . basename($base) . '-myplugin' . DIRECTORY_SEPARATOR;
}
```

If two sites use different `path_data` directories, this convention naturally creates different plugin storage directories.

## Why this matters for multisite

A plugin must never assume that all sites in one Geeklog installation share the same persistent data.

For example:

```text
/data-site-a/
/data-site-a-documents/

/data-site-b/
/data-site-b-documents/
```

This provides a straightforward isolation model without forcing every plugin to know the complete multisite topology.

## Migration rules

When moving legacy data to a new persistent directory:

1. detect the legacy directory;
2. create the new destination safely;
3. copy recursively;
4. do not overwrite an existing destination file automatically;
5. keep the legacy directory until migration has been verified;
6. make the migration safe to run again;
7. record or log failures clearly;
8. update the plugin version only after the required migration stage succeeds.

The preferred migration is non-destructive and idempotent.

## Installation rules

A new installation should:

- calculate the site-specific storage path;
- create it only when required;
- verify that the parent directory is appropriate and writable;
- fail clearly if persistent storage cannot be initialized;
- avoid creating user data beneath a directory documented as disposable cache.

## File security

Persistent storage outside the public web root is preferred when direct public access is not required.

When a file must be served publicly, prefer a controlled delivery mechanism when practical so that the plugin can enforce:

- permissions;
- ownership;
- access rules;
- logging;
- content type;
- safe filenames.

Never trust an uploaded filename as a filesystem path.

Normalize or generate storage names independently of user-controlled path components.

## Compatibility

Storage helpers intended for the current modernization period must remain valid on PHP 5.6.

Avoid syntax introduced after PHP 5.6 in shared plugin code.

The storage concept should work the same way on Geeklog 2.1.1 and 2.2.2 even if surrounding installer or configuration APIs require version-specific compatibility code.

## Recommended tests

For plugins with persistent data, test at least:

- fresh installation;
- upgrade from a legacy storage location;
- repeated migration;
- destination files already present;
- missing legacy directory;
- unwritable destination;
- cache cleanup;
- two separate sites using different `path_data` values;
- PHP 5.6;
- PHP 8.1.

## Guiding principle

> Persistent data belongs to the site and the plugin. It must survive cache cleanup, plugin upgrades and staged Geeklog migrations unless the administrator explicitly chooses to remove it.
