# Geeklog Plugin Configuration Tooltips

## Purpose

Geeklog provides a native Plugin API hook that allows a plugin to add contextual help to individual settings in the Configuration administration interface.

This is useful for technical or ambiguous settings whose label alone does not explain the effect of changing the value. Plugins should prefer this native mechanism over adding custom JavaScript, custom tooltip libraries, or plugin-specific configuration templates.

The hook has existed in Geeklog since at least **1.8.0** through the core dispatcher `PLG_getConfigTooltip()` and is therefore suitable for plugins that currently target Geeklog **2.1.1 through 2.2.2**.

---

## Native Plugin API hook

For a plugin named `myplugin`, implement:

```php
function plugin_getconfigtooltip_myplugin($id)
{
    // Return contextual help for one configuration option.
}
```

Geeklog calls the hook with the configuration option identifier while rendering the Configuration UI.

The plugin does not need to modify Geeklog's configuration templates or call `COM_getTooltip()` itself. Geeklog owns the final rendering of the tooltip.

Core dispatch follows the pattern:

```text
PLG_getConfigTooltip('myplugin', $id)
        ↓
plugin_getconfigtooltip_myplugin($id)
        ↓
Geeklog Configuration UI
```

---

## Recommended implementation

Keep tooltip text in the plugin language files so the help follows the active interface language.

Example language file:

```php
$LANG_configtooltips['myplugin'] = array(
    'enable_cache' => 'Caches generated output to reduce repeated processing.',
    'legacy_rendering' => 'Uses the historical plugin renderer for compatibility with older themes.',
);
```

Example hook:

```php
function plugin_getconfigtooltip_myplugin($id)
{
    global $LANG_configtooltips;

    if (isset($LANG_configtooltips['myplugin'])
        && isset($LANG_configtooltips['myplugin'][$id])) {
        return $LANG_configtooltips['myplugin'][$id];
    }

    return '';
}
```

This pattern is compatible with PHP 5.6 and avoids hardcoded interface help inside the callback itself.

A plugin already using an English-first language overlay may naturally obtain English fallback through that existing mechanism. Otherwise, each maintained language should define the same tooltip keys or the plugin should deliberately provide an English fallback.

---

## Return values

The native hook supports three useful behaviors:

- return a **non-empty string** to use that text as the regular configuration tooltip;
- return an **empty string** when no tooltip is available for that option;
- return `NULL` / no explicit value only when intentionally relying on Geeklog's configuration-documentation tooltip fallback used by some core plugins.

For third-party modernized plugins, returning an explicit localized string or an empty string is generally clearer than relying on the documentation fallback unless that fallback has been deliberately implemented and tested.

---

## Which options should receive tooltips?

Do not mechanically add help to every setting.

Tooltips are most useful for options where changing the value has consequences that are not obvious from the label, for example:

- compatibility or legacy modes;
- cache behavior;
- generated assets;
- security-sensitive behavior;
- external-link handling;
- optional PHP or executable capabilities;
- migration/compatibility settings;
- settings whose values are terse (`0/1`, modes, strategies) but whose effect needs explanation.

Simple and self-explanatory settings such as an obvious alignment, color, page size, or title normally do not need additional help.

The objective is to reduce configuration mistakes without making the administration screen noisy.

---

## Writing good tooltip text

A tooltip should explain the **effect** of the setting rather than repeat its label.

Prefer:

```text
Uses the historical renderer required by older themes. Disable only when the active theme explicitly handles this plugin's presentation.
```

Avoid:

```text
Enable or disable legacy rendering.
```

Good tooltip text should normally be:

- one or two short sentences;
- understandable without reading source code;
- explicit about compatibility or security consequences;
- neutral about the current value unless one value is genuinely required;
- free of raw HTML unless the exact Geeklog rendering path has been verified to allow it safely.

---

## Localization and fallback

Configuration labels and configuration tooltips are separate concerns.

A plugin may have:

```php
$LANG_confignames['myplugin']['enable_cache']
```

for the setting label and:

```php
$LANG_configtooltips['myplugin']['enable_cache']
```

for contextual help.

The tooltip identifier should match the actual configuration option name passed to the hook.

For modernization work in the current Geeklog-Plugins compatibility range:

1. English should remain the canonical interface contract;
2. translated tooltip arrays should overlay or mirror English keys;
3. missing translations should fail safely to English when the plugin's language loader supports fallback;
4. a missing tooltip must not produce PHP warnings such as `Undefined array key`.

---

## Compatibility notes

The configuration tooltip hook is part of Geeklog's native Plugin API and is preferable to a custom UI implementation.

Plugins supporting Geeklog 2.1.1 through 2.2.2 should still test the resulting Configuration page on both generations because surrounding configuration rendering differs between Geeklog versions even when the hook itself is available.

The callback should remain lightweight. Do not perform database migrations, expensive scans, or state-changing actions while Geeklog is merely rendering configuration help.

---

## Recommended tests

For plugins that expose configuration tooltips, verify at least:

- the callback exists under the correct plugin-specific name;
- known configuration IDs return the expected non-empty text;
- an unknown ID returns an empty string without warnings;
- English tooltips are available;
- maintained translations resolve correctly or fall back safely;
- the Geeklog Configuration page renders normally on all declared supported versions;
- tooltip text does not expose sensitive configuration values or internal filesystem information.

A simple source-contract test can also ensure that important technical settings retain help during future refactoring.

---

## Example from a Menu-style plugin

A plugin with technical rendering options could expose:

```php
$LANG_configtooltips['myplugin'] = array(
    'enable_cache' => 'Caches generated output to reduce repeated processing.',
    'load_legacy_css' => 'Loads plugin-generated styles when the active theme does not own presentation.',
    'load_legacy_js' => 'Loads historical JavaScript required by legacy interactive navigation.',
    'legacy_rendering' => 'Keeps the historical rendering path for compatibility with older themes.',
);
```

Only settings that benefit from additional explanation need entries.

---

## Relationship with the configuration migration guide

This document complements [`plugin-configuration-migration-guide-2.2.2.md`](plugin-configuration-migration-guide-2.2.2.md).

The migration guide covers configuration storage, hierarchy, selection arrays, language metadata, and upgrade behavior. Configuration tooltips are a presentation/help capability layered on top of a correctly registered Geeklog configuration group; they do not replace `$LANG_confignames`, `$LANG_configsections`, `$LANG_configsubgroups`, `$LANG_tab`, `$LANG_fs`, or `$LANG_configselects` where those arrays are required.

## Guiding principle

> Use Geeklog's native configuration help mechanism to explain consequential settings at the point where administrators make the decision, while keeping help localized, concise and optional.
