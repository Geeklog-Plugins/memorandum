# Geeklog 2.2.2 Plugin Configuration Migration Guide

This document supplements the main Plugin API Reference and focuses specifically on modernizing plugin installation and configuration management for **Geeklog 2.2.2**.

It is particularly useful when migrating legacy plugins from custom database tables to the native Geeklog Configuration API.

These recommendations are based on the Geeklog core implementation and on official plugins such as **Polls**, which should be treated as a reference implementation for the structure of `install_defaults.php` and configuration language arrays.

---

## 1. Deprecating Manual Installation Scripts (`admin/install.php`)

Older Geeklog plugins often provided an `admin/install.php` script to create custom database tables and initialize plugin settings.

For modern Geeklog 2.2.2 plugins, this approach should be avoided whenever possible.

### Recommended approach

- Manage plugin installation through the root-level `autoinstall.php` file.
- Let Geeklog create the required security groups, features, permissions, and configuration entries.
- If the plugin no longer requires custom database tables, declare an empty table list in the plugin autoinstall definition.

```php
$tables = array();
```

The plugin installation process should be self-contained and compatible with Geeklog's standard plugin installer.

---

## 2. Integrating with the Native Configuration API (`config.class.php`)

Plugins should avoid storing ordinary configuration settings in custom SQL tables such as:

```text
gl_analytics
```

Instead, configuration values should be managed through Geeklog's native `config` object.

Configuration defaults are typically initialized from an `install_defaults.php` file.

### 2.1. Use the real `config::add()` parameter order

The Geeklog 2.2.2 `ConfigInterface` defines the method as:

```php
public function add(
    $param_name,
    $default_value,
    $type,
    $subgroup,
    $fieldset = null,
    $selection_array = null,
    $sort = 0,
    $set = true,
    $group = 'Core',
    $tab = null
);
```

The parameters most commonly confused during plugin modernization are therefore:

1. `$subgroup` — 4th parameter
2. `$fieldset` — 5th parameter
3. `$selection_array` — 6th parameter
4. `$group` — 9th parameter
5. `$tab` — 10th parameter

> **Important:** the 10th parameter is the **tab identifier**, not the subgroup identifier.

For a simple plugin configuration, follow the same hierarchy used by the official Polls plugin:

```php
$c->add('sg_main', NULL, 'subgroup', 0, 0, NULL, 0, true, 'myplugin', 0);
$c->add('tab_main', NULL, 'tab', 0, 0, NULL, 0, true, 'myplugin', 0);
$c->add('fs_main', NULL, 'fieldset', 0, 0, NULL, 0, true, 'myplugin', 0);
$c->add('my_setting', 'value', 'text', 0, 0, NULL, 10, true, 'myplugin', 0);
```

The recommended declaration order is:

```text
subgroup -> tab -> fieldset -> settings
```

This mirrors the official plugins and avoids relying on backward-compatibility behavior that creates implicit default tabs.

### 2.2. Do not use `0` as a placeholder for `selection_array`

Geeklog stores the `selection_array` value in `conf_values.selectionArray`.

When `$selection_array` is `NULL`, `config::add()` stores `-1`, meaning that the setting does not use a language-backed selection list.

Therefore, a plain text setting should normally use:

```php
$c->add(
    'my_setting',
    'value',
    'text',
    0,
    0,
    NULL,
    10,
    true,
    'myplugin',
    0
);
```

Do **not** write this unless selection list `0` really exists:

```php
$c->add('my_setting', 'value', 'text', 0, 0, 0, 10, true, 'myplugin', 0);
```

With `selection_array = 0`, Geeklog 2.2.2 may later execute logic equivalent to:

```php
$LANG_configselects['myplugin'][0]
```

If that entry is not defined, opening the configuration page can produce:

```text
E_WARNING - Undefined array key 0
```

inside `config.class.php::_get_extended()`.

### 2.3. Selection-backed controls must have matching language metadata

For configuration types such as `select`, `@select`, or other controls that intentionally use a selection array, the numeric identifier passed as `$selection_array` must correspond to an entry in:

```php
$LANG_configselects['myplugin']
```

Example:

```php
$LANG_configselects['myplugin'][0] = array(
    0 => 'Disabled',
    1 => 'Enabled'
);

$c->add('enabled', 1, 'select', 0, 0, 0, 10, true, 'myplugin', 0);
```

Use `NULL` instead of a numeric selection identifier whenever no such list is required.

### 2.4. Safe default values

During the initial installation, the plugin configuration may not exist yet.

If your code references values such as:

```php
$_PI_CONF['myplugin']['my_setting']
```

always protect the access with `isset()` or the null coalescing operator (`??`) where the supported PHP range allows it, to prevent `Undefined array key` warnings.

Example:

```php
$my_setting = isset($_PI_CONF['myplugin']['my_setting'])
    ? $_PI_CONF['myplugin']['my_setting']
    : '';
```

---

## 3. Configuration language metadata in Geeklog 2.2.2

One of the less obvious issues encountered when migrating a plugin to Geeklog 2.2.2 appears when an administrator opens the plugin configuration page.

A typical error looks like:

```text
Undefined array key "myplugin"
```

and may originate from:

```text
/system/classes/config.class.php
```

inside `_UI_autocomplete_data()`.

### Cause

Geeklog 2.2.2 includes configuration search and autocomplete functionality.

For this interface to work correctly, the plugin configuration elements must be represented in the same language arrays used by official plugins such as Polls.

A generic `$LANG_config` array is not sufficient.

### Required language arrays

Add the following arrays to each supported plugin language file:

```php
$LANG_configsections['myplugin'] = array(
    'label' => 'Plugin Name',
    'title' => 'Plugin Configuration'
);

$LANG_confignames['myplugin'] = array(
    'my_setting' => 'Label for my setting'
);

$LANG_configsubgroups['myplugin'] = array(
    'sg_main' => 'Main Settings'
);

$LANG_tab['myplugin'] = array(
    'tab_main' => 'Main Tab'
);

$LANG_fs['myplugin'] = array(
    'fs_main' => 'General Settings'
);
```

The language keys must match the symbolic names registered through `$c->add()`.

For example:

```php
$c->add('tab_main', NULL, 'tab', ...);
```

must be represented as:

```php
$LANG_tab['myplugin']['tab_main'] = 'Main Tab';
```

Do not use the numeric tab id as the language-array key:

```php
// Wrong for a tab declared as "tab_main"
$LANG_tab['myplugin'][0] = 'Main Tab';
```

Official Geeklog plugins assign these arrays directly in their language files. Under normal plugin loading, `functions.inc` is included by Geeklog and then includes the active plugin language file at global scope. There is normally no need to replace the standard variables with custom `$GLOBALS[...]` assignments.

### Language filenames

Plugins should provide language filenames matching the Geeklog language identifiers they intend to support, with `english.php` as the fallback. Core plugins commonly also provide `english_utf-8.php` and translated `*_utf-8.php` files.

A typical loading pattern is:

```php
$plugin_path = $_CONF['path'] . 'plugins/myplugin/';
$langfile = $plugin_path . 'language/' . $_CONF['language'] . '.php';

if (file_exists($langfile)) {
    include_once $langfile;
} else {
    include_once $plugin_path . 'language/english.php';
}
```

> **Important:** missing or mismatched configuration language entries can make the administration configuration interface fail under PHP 8.x because warnings that were previously hidden become visible.

---

## 4. Diagnosing configuration-page warnings

### 4.1. `Undefined array key "myplugin"` in `_UI_autocomplete_data()`

Check first that all of the following exist for the active language:

```text
$LANG_configsections['myplugin']
$LANG_confignames['myplugin']
$LANG_configsubgroups['myplugin']
$LANG_tab['myplugin']
$LANG_fs['myplugin']
```

Also verify that the plugin's `functions.inc` loads the active language file.

### 4.2. `Undefined array key 0` in `_get_extended()`

Inspect the plugin rows in `conf_values`, especially the `selectionArray` column.

For text settings or other settings with no selection list, the expected value is normally:

```text
-1
```

A value such as `0` means Geeklog expects:

```php
$LANG_configselects['myplugin'][0]
```

to exist.

This commonly results from passing `0` instead of `NULL` as the 6th argument to `$c->add()`.

### 4.3. Missing or inconsistent tabs

Verify that a symbolic tab row exists, for example:

```php
$c->add('tab_main', NULL, 'tab', 0, 0, NULL, 0, true, 'myplugin', 0);
```

and that settings assigned to tab id `0` are accompanied by:

```php
$LANG_tab['myplugin']['tab_main'] = 'Main Tab';
```

Avoid depending on the implicit backward-compatible default tab for newly modernized plugins.

---

## 5. Retrieving Configuration Values Safely

Do not guess the name of a global configuration array such as:

```php
$_PI_CONF
```

or:

```php
$_MY_CONF
```

Avoid direct database queries such as `DB_getItem()` for configuration values on every page load.

Also avoid calling:

```php
$c->get()
```

because this is not the correct method for retrieving a plugin configuration group.

### Recommended approach

Use:

```php
$c->get_config('myplugin');
```

This retrieves the complete configuration array for the plugin through Geeklog's configuration system.

### Example implementation in `functions.inc`

```php
$my_setting = '';

if (class_exists('config')) {
    $c = config::get_instance();
    $pluginConfig = $c->get_config('myplugin');

    if (is_array($pluginConfig) && isset($pluginConfig['my_setting'])) {
        $my_setting = $pluginConfig['my_setting'];
    }
}
```

---

## 6. Upgrade Management: Initialize Before Migrating

When upgrading a legacy plugin from a custom configuration table to Geeklog's native Configuration API, the plugin configuration group may not exist yet when:

```php
plugin_upgrade_<plugin>()
```

is executed.

If you attempt to migrate values immediately with code such as:

```php
$c->set('my_setting', $old_value, 'myplugin');
```

before the configuration entries have been created, the migration may fail.

### Recommended migration sequence

1. Create the new Geeklog configuration entries.
2. Read the existing values from the legacy SQL table.
3. Transfer those values to the native Configuration API.
4. Verify that the migrated configuration is available.
5. Remove the obsolete SQL table only after the migration succeeds.

### Repairing already-persisted configuration metadata

Changing `install_defaults.php` only fixes **future installations**. Existing sites keep the rows already stored in `conf_values`.

If a released or test build stored incorrect metadata such as:

```text
selectionArray = 0
```

for a text setting, the plugin upgrade routine must repair the persisted rows explicitly or recreate the configuration group safely.

Do not assume that replacing plugin files will rewrite existing `conf_values` rows.

This is especially important in shared-files multisite installations, where each site may persist a different configuration schema version.

---

## 7. Recommended Migration Checklist

Use this checklist when modernizing a legacy plugin for Geeklog 2.2.2:

- [ ] Remove dependencies on `admin/install.php` where possible.
- [ ] Use `autoinstall.php` for the standard plugin installation process.
- [ ] Move ordinary settings from custom SQL tables to the native Configuration API.
- [ ] Confirm the exact `config::add()` argument order from `ConfigInterface.php`.
- [ ] Declare configuration hierarchy as `subgroup -> tab -> fieldset -> settings`.
- [ ] Use `NULL` for `$selection_array` when a setting has no selection list.
- [ ] When a numeric `$selection_array` is used, provide the matching `$LANG_configselects` entry.
- [ ] Add all required configuration language arrays.
- [ ] Match `$LANG_tab` and `$LANG_fs` keys to the symbolic names passed to `$c->add()`.
- [ ] Use `$c->get_config('myplugin')` to retrieve plugin settings.
- [ ] Protect configuration array access with `isset()` or an equivalent supported by the plugin's PHP compatibility range.
- [ ] Initialize new configuration before migrating legacy values.
- [ ] Repair incorrect persisted `conf_values` metadata during upgrade; changing defaults alone is insufficient.
- [ ] Verify migrated values before dropping obsolete database tables.
- [ ] Test fresh installation and upgrade paths separately.
- [ ] Test the configuration page with PHP warnings enabled.
- [ ] Compare the resulting configuration structure with an official plugin such as Polls.

---

## 8. Target Environment

This guide is intended primarily for plugins targeting:

- **Geeklog:** 2.2.2
- **PHP:** the compatibility range declared by the plugin; PHP 8.x warnings are particularly useful during testing
- **Database:** MySQL/MariaDB environments using strict SQL behavior

Legacy compatibility requirements may require additional handling.

---

## Reference implementation

When in doubt, compare the plugin against the current Geeklog core implementation, especially:

```text
system/classes/ConfigInterface.php
system/classes/config.class.php
plugins/polls/install_defaults.php
plugins/polls/functions.inc
plugins/polls/language/english.php
```

The core source is authoritative when it differs from older examples or third-party documentation.

---

## Related Documentation

This guide should be used together with the main Geeklog Plugin API Reference, the shared-files upgrade safety guide, and the plugin's installation and upgrade documentation.
