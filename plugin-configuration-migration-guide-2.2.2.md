# Geeklog 2.2.2 Plugin Configuration Migration Guide

This document supplements the main Plugin API Reference and focuses specifically on modernizing plugin installation and configuration management for **Geeklog 2.2.2**.

It is particularly useful when migrating legacy plugins from custom database tables to the native Geeklog Configuration API.

These recommendations are based on real-world issues encountered while updating legacy plugins for **Geeklog 2.2.2** and **PHP 8.x**.

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

### 2.1. The `subgroup` Parameter Trap

When using `$c->add()`, an incorrect parameter value can cause an SQL error under PHP 8.x or MySQL Strict Mode, such as:

```text
Incorrect integer value
```

It may also cause the plugin installation to fail without an obvious error message.

#### Cause

The 10th parameter of the `add()` method represents the subgroup identifier.

It must be an **integer**, commonly `0` for the main subgroup. Do not pass a string such as a fieldset name.

#### Incorrect example

```php
$c->add('tab_main', NULL, 'tab', 0, 0, NULL, 0, true, 'myplugin', 'tab_main');
$c->add('fs_main', NULL, 'fieldset', 0, 0, NULL, 0, true, 'myplugin', 'fs_main');
$c->add('my_setting', 'value', 'text', 0, 0, NULL, 10, true, 'myplugin', 'fs_main');
```

#### Correct example for Geeklog 2.2.2

```php
// Declare the root subgroup before the tab.
$c->add('sg_main', NULL, 'subgroup', 0, 0, NULL, 0, true, 'myplugin', 0);

$c->add('tab_main', NULL, 'tab', 0, 0, NULL, 0, true, 'myplugin', 0);

$c->add('fs_main', NULL, 'fieldset', 0, 0, NULL, 0, true, 'myplugin', 0);

$c->add('my_setting', 'value', 'text', 0, 0, NULL, 10, true, 'myplugin', 0);
```

### 2.2. Safe Default Values

During the initial installation, the plugin configuration may not exist yet.

If your code references values such as:

```php
$_PI_CONF['myplugin']['my_setting']
```

always protect the access with `isset()` or the null coalescing operator (`??`) to prevent PHP 8.x `Undefined array key` warnings.

Example:

```php
$my_setting = $_PI_CONF['myplugin']['my_setting'] ?? '';
```

---

## 3. Fixing `Undefined array key` Errors in `_UI_autocomplete_data`

One of the less obvious issues encountered when migrating a plugin to Geeklog 2.2.2 appears when an administrator opens the plugin configuration page.

A typical error looks like:

```text
Undefined array key "myplugin"
```

and may originate from:

```text
/system/classes/config.class.php
```

inside the `_UI_autocomplete_data` function.

### Cause

Geeklog 2.2.2 includes configuration search and autocomplete functionality.

For this interface to work correctly, the plugin configuration elements must be represented in the expected language arrays.

A generic `$LANG_config` array is not sufficient.

### Required language arrays

Add the following arrays to the plugin language file, for example:

```text
language/english.php
```

```php
// Localization of the Admin Configuration UI.

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
    'fs_main' => 'Fieldset Group'
);
```

> **Important:** Missing configuration language entries can cause the administration configuration interface to fail under PHP 8.x.

---

## 4. Retrieving Configuration Values Safely

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

A shorter PHP 8-compatible variant can also be used when appropriate:

```php
$my_setting = '';

if (class_exists('config')) {
    $c = config::get_instance();
    $pluginConfig = $c->get_config('myplugin');

    $my_setting = is_array($pluginConfig)
        ? ($pluginConfig['my_setting'] ?? '')
        : '';
}
```

---

## 5. Upgrade Management: Initialize Before Migrating

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

### Example structure

Create an `install_updates.php` file containing a configuration initialization or upgrade function, for example:

```php
function myplugin_update_ConfValues_2_0_0()
{
    // Create or update configuration entries required by version 2.0.0.
}
```

Then call it near the beginning of the plugin upgrade process:

```php
function plugin_upgrade_myplugin()
{
    myplugin_update_ConfValues_2_0_0();

    // Read legacy configuration values.
    // Migrate them to Geeklog's Configuration API.
    // Verify the migration.
    // Drop the obsolete table only when safe.

    return true;
}
```

> **Migration rule:** Never delete the legacy configuration table before confirming that the new configuration entries exist and the old values have been transferred successfully.

---

## 6. Recommended Migration Checklist

Use this checklist when modernizing a legacy plugin for Geeklog 2.2.2:

- [ ] Remove dependencies on `admin/install.php` where possible.
- [ ] Use `autoinstall.php` for the standard plugin installation process.
- [ ] Move configuration settings from custom SQL tables to the native Configuration API.
- [ ] Initialize configuration entries through `install_defaults.php` or the appropriate upgrade routine.
- [ ] Ensure the `subgroup` parameter passed to `$c->add()` is an integer.
- [ ] Add all required configuration language arrays.
- [ ] Use `$c->get_config('myplugin')` to retrieve plugin settings.
- [ ] Protect configuration array access with `isset()` or `??`.
- [ ] Initialize the new configuration before migrating legacy values.
- [ ] Verify migrated values before dropping obsolete database tables.
- [ ] Test installation and upgrades with PHP 8.x warnings enabled.
- [ ] Test the plugin configuration page in the Geeklog administration interface.

---

## 7. Target Environment

This guide is intended primarily for plugins targeting:

- **Geeklog:** 2.2.2
- **PHP:** 8.1 or later
- **Database:** MySQL/MariaDB environments using strict SQL behavior

Legacy compatibility requirements may require additional handling.

---

## Related Documentation

This guide should be used together with the main Geeklog Plugin API Reference and the plugin's installation and upgrade documentation.
