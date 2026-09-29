# Geeklog Plugin Administration Navigation

## Purpose

Geeklog already provides native administration building blocks, but they solve different problems.

Modernized plugins should reuse the native mechanisms where they fit and avoid inventing a replacement for functionality Geeklog already owns. A persistent plugin-local section navigation, however, has requirements that the current native action-menu helper does not fully cover.

This document defines a small theme-neutral convention for that remaining case.

---

## Native Geeklog mechanisms to use first

### 1. Global plugin administration entry

When a plugin has an administration area that should appear in Geeklog's plugin administration list, it should expose the native administration entry expected by Geeklog through:

```php
function plugin_getadminoption_myplugin()
{
    global $_CONF;

    if (!SEC_hasRights('myplugin.admin')) {
        return array();
    }

    return array(
        'My Plugin',
        $_CONF['site_admin_url'] . '/plugins/myplugin/index.php',
        ''
    );
}
```

The conventional return values are:

1. administration label;
2. administration URL;
3. optional item/submission count or an empty value.

This hook integrates the plugin into Geeklog's global administration navigation and allows themes or administration dashboards to discover the plugin without maintaining plugin-specific URL registries.

A plugin that has a real administration area should not rely on Eclipse, Denim, Hub or another consumer to invent or hard-code its administration URL. When the entry is relevant, expose `plugin_getadminoption_<plugin>()` and let Geeklog own discovery.

The hook should enforce the plugin's normal administration ACL and return an empty array when the current user is not authorized.

It is not intended to represent every internal administration section of a plugin; those sections remain plugin-local navigation.

### 2. Page action menus

Geeklog Core provides:

```php
ADMIN_createMenu($menu_arr, $text, $icon = '')
```

The helper lives in `system/lib-admin.php` and renders through the Core `admin/lists/topmenu.thtml` template.

Use `ADMIN_createMenu()` when a page needs a short action menu such as:

- create a new item;
- return to an administration list;
- open another related administration action;
- show a short instruction next to those actions.

This is the native choice when its link-only action-menu model fits the page.

Do not replace `ADMIN_createMenu()` with a custom toolbar merely for visual preference.

---

## Why ADMIN_createMenu() is not a full section-navigation contract

The current Core implementation is intentionally simple:

- entries are links;
- links use the `admin-menu-item` class;
- entries are separated by `|`;
- there is no native selected/current-section state;
- there is no first-class form item;
- it cannot directly represent the POST form required by Geeklog Configuration while preserving a single visual navigation row.

Therefore it is suitable for **page actions**, but not always for a persistent navigation such as:

```text
Questions | Categories | Associations | Coverage | Configuration
```

where one item must be marked current and Configuration may need to submit `conf_group` by POST.

This distinction should be preserved instead of overloading `ADMIN_createMenu()`.

---

## Persistent plugin-local navigation convention

When a plugin has several peer administration sections and `ADMIN_createMenu()` is insufficient, use the following semantic structure:

```html
<nav class="plugin-admin-nav" aria-label="Plugin administration">
    <div class="plugin-admin-nav__primary">
        <a class="plugin-admin-nav__item is-active"
           aria-current="page"
           href="...">Items</a>

        <a class="plugin-admin-nav__item"
           href="...">Categories</a>

        <form class="plugin-admin-nav__form"
              method="post"
              action="/admin/configuration.php">
            <input type="hidden" name="conf_group" value="myplugin">
            <button class="plugin-admin-nav__item" type="submit">
                Configuration
            </button>
        </form>
    </div>
</nav>
```

### Required class contract

- `plugin-admin-nav` — navigation landmark;
- `plugin-admin-nav__primary` — primary row;
- `plugin-admin-nav__item` — link or button representing one peer section;
- `plugin-admin-nav__form` — form wrapper when a navigation item must be submitted;
- `is-active` — current section;
- `aria-current="page"` — current link when the active item is an anchor.

Plugins may add plugin-specific classes in addition to these shared classes, but should not require a particular theme framework.

---

## Theme independence

The shared contract must not require:

- UIkit `uk-button`;
- Bootstrap classes;
- Eclipse-only classes;
- Denim-only classes.

A theme may style `plugin-admin-nav*` globally. Until themes do so, a plugin may ship a minimal fallback stylesheet using the shared selectors.

Recommended fallback behavior:

```css
.plugin-admin-nav {
    margin: 0 0 1.25rem;
}

.plugin-admin-nav__primary {
    display: flex;
    flex-wrap: wrap;
    gap: .5rem;
    align-items: center;
}

.plugin-admin-nav__item {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 2.4rem;
    padding: .5rem .8rem;
    border: 1px solid currentColor;
    border-radius: .35rem;
    background: transparent;
    color: inherit;
    font: inherit;
    text-decoration: none;
    cursor: pointer;
}

.plugin-admin-nav__item.is-active {
    font-weight: 700;
    box-shadow: inset 0 -2px 0 currentColor;
}

.plugin-admin-nav__form {
    display: inline-block;
    margin: 0;
}
```

The fallback should remain deliberately modest so the active Geeklog theme can own most of the visual language.

---

## Responsive behavior

On narrow screens the navigation should remain usable without horizontal overflow.

A safe fallback is:

```css
@media (max-width: 640px) {
    .plugin-admin-nav__primary {
        align-items: stretch;
        flex-direction: column;
    }

    .plugin-admin-nav__item,
    .plugin-admin-nav__form,
    .plugin-admin-nav__form .plugin-admin-nav__item {
        width: 100%;
        box-sizing: border-box;
    }
}
```

---

## Configuration navigation

Geeklog Configuration is a separate Core feature.

When a plugin needs a Configuration item in its persistent administration navigation, preserve the native Configuration entry contract rather than constructing a plugin-specific settings page.

Where the target Geeklog version expects `conf_group` by POST, use a form item as shown above.

Configuration labels and help remain owned by the normal Configuration API:

- `$LANG_configsections`;
- `$LANG_configsubgroups`;
- `$LANG_confignames`;
- `$LANG_tab`;
- `$LANG_fs`;
- `$LANG_configselects`;
- `plugin_getconfigtooltip_<plugin>()` for native contextual help.

See `plugin-configuration-migration-guide-2.2.2.md` and `plugin-configuration-tooltips.md`.

---

## Recommended decision order

Before creating plugin-local navigation, use this decision order:

1. **Does the plugin expose an administration area that should be discoverable by Geeklog?** Implement `plugin_getadminoption_<plugin>()`.
2. **A small set of page actions?** Use `ADMIN_createMenu()`.
3. **A persistent set of peer plugin sections with active state or POST items?** Use the `plugin-admin-nav*` convention.
4. Do not use a theme-framework class as the interoperability contract.

---

## Compatibility target

The convention is plain HTML/CSS and is suitable for the current modernization target:

- Geeklog 2.1.1 through 2.2.2;
- PHP 5.6 through PHP 8.1.

It complements Geeklog Core; it does not replace `ADMIN_createMenu()` or the Plugin API.

## Guiding principle

> Use Geeklog's native administration primitives first. Add only the smallest shared convention needed for persistent plugin-local section navigation that Core does not currently model.
