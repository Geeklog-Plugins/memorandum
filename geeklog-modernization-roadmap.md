# Geeklog Modernization Roadmap

This roadmap focuses on the current implementation priorities for the Geeklog ecosystem.

## Current compatibility target

For plugins currently being modernized, the priority is to preserve compatibility across:

- **Geeklog 2.1.1 through 2.2.2**
- **PHP 5.6 through PHP 8.1**

This allows plugins to be upgraded before or during a staged Geeklog/PHP migration.

Modernization should therefore use the safe common subset of PHP 5.6–8.1 and isolate Geeklog-version compatibility code where newer APIs are not available in Geeklog 2.1.1.

The Eclipse theme is a separate case: its modern branch may target Geeklog 2.2.2 where required by the newer theme architecture.

---

## 1. Menu 1.3.0

**Status:** Active

**Goal:** make Menu a reliable navigation layer for Geeklog themes while preserving the current plugin compatibility range.

### Priorities
- Finalize configuration defaults for new installations and upgrades.
- Complete the admin menu preview.
- Fix remaining Geeklog 2.1.1–2.2.2 compatibility issues.
- Keep PHP 5.6–8.1 compatibility.
- Improve the optional integration with Eclipse.
- Define clean and reusable navigation output for themes.
- Avoid making the plugin dependent on one specific theme.

## 2. Documents

**Status:** Active

**Goal:** stabilize the plugin before adding new features.

### Priorities
- Fix the security token issue when saving fields.
- Complete functional tests for document and field management.
- Finalize the persistent data migration strategy.
- Ensure safe and isolated storage for multisite installations.
- Confirm that upgrades are non-destructive and repeatable.
- Keep packaging and migration tests reliable.
- Validate behavior on Geeklog 2.1.1 and 2.2.2.
- Validate PHP 5.6 and PHP 8.1 compatibility.

## 3. Maps

**Status:** Active

**Goal:** restore a stable historical base before continuing modernization.

### Priorities
- Finish synchronization with the target 1.5.6 alpha18 archive.
- Align `functions.inc` with the expected version.
- Synchronize the remaining language and admin files.
- Validate the synchronized plugin before new development.
- Modernize Google Maps integration for current APIs.
- Improve security and search behavior.
- Preserve Geeklog 2.1.1–2.2.2 compatibility where practical.
- Preserve PHP 5.6–8.1 compatibility.

## 4. Eclipse Theme

**Status:** Active

**Goal:** make Eclipse the reference modern theme for Geeklog 2.2.2.

### Priorities
- Stabilize the integration with Menu.
- Make navigation robust when Geeklog caches are rebuilt or cleared.
- Finalize the main frontend and admin layouts.
- Complete Theme Studio features.
- Keep theme data outside temporary Geeklog cache storage.
- Improve SEO, accessibility, and mobile behavior.
- Use Geeklog 2.2.2 as the primary platform for the modern Eclipse branch.

Eclipse should remain a reference implementation rather than a mandatory dependency for plugins.

## 5. Store Plugin

**Status:** Active

**Goal:** stabilize Store as a modern commerce component for Geeklog without prematurely expanding its scope.

### Priorities
- Complete the current functional base.
- Fix remaining PHP and packaging issues.
- Improve installation and upgrade reliability.
- Validate the product management workflow.
- Continue testing with realistic demo products.
- Preserve Geeklog 2.1.1–2.2.2 compatibility while the migration policy remains active.
- Preserve PHP 5.6–8.1 compatibility.
- Keep interfaces extensible enough for future interoperability without implementing unfinished future architecture now.
- Avoid making other major projects depend on Store until it is stable.

## 6. Videos

**Status:** Active

**Goal:** modernize data handling and stabilize the plugin for current Geeklog installations.

### Priorities
- Move persistent plugin data outside disposable cache locations.
- Use a site-specific storage path compatible with multisite.
- Validate migration from existing installations.
- Review security and file handling.
- Preserve Geeklog 2.1.1–2.2.2 compatibility.
- Preserve PHP 5.6–8.1 compatibility.
- Complete functional tests before adding new features.

## 7. Multisite Manager

**Status:** Planned

**Goal:** reduce manual configuration and make Geeklog multisite easier to operate.

### Priorities
- Define the master-site-only plugin architecture.
- Manage secondary site configuration from the master site.
- Support site enable/disable operations.
- Manage database prefixes or isolated site tables safely.
- Reuse official Geeklog installation functions where possible.
- Reduce direct manual edits to `db-config.php` and `siteconfig.php`.
- Keep the solution compatible with normal single-site installations where possible.

The Multisite Manager itself can remain a later project. Multisite-safe development principles apply immediately to active plugins.

See [`multisite-development-principles.md`](multisite-development-principles.md).

## 8. Geeklog 2030

**Status:** Architectural direction

**Goal:** prepare Geeklog for long-term evolution without confusing future architecture with current implementation priorities.

### Priorities
- Define common interoperability conventions.
- Improve structured data access over time.
- Strengthen multisite support.
- Improve plugin interoperability.
- Prepare future integrations with automation and AI tools.
- Modernize documentation and developer workflows.
- Encourage new services and plugins built on a stable Geeklog base.

The 2030 roadmap is a dependency and architecture guide, not the current development queue.

---

## Recommended Work Order

1. Menu 1.3.0
2. Documents
3. Maps
4. Eclipse
5. Store
6. Videos
7. Multisite Manager
8. Geeklog 2030 initiatives

The immediate objective is to finish and stabilize existing modernization work before opening too many new development fronts.

## Cross-project rules

All active plugins should progressively follow:

- [`plugin-persistent-storage-guide.md`](plugin-persistent-storage-guide.md)
- [`multisite-development-principles.md`](multisite-development-principles.md)
- [`plugin-configuration-migration-guide-2.2.2.md`](plugin-configuration-migration-guide-2.2.2.md) where Geeklog 2.2.2 configuration behavior is relevant
- [`plugin-api-reference-2.2.2.md`](plugin-api-reference-2.2.2.md) while checking for fallbacks required by Geeklog 2.1.1

## Projects on Hold

### Plugin Toolkit

**Status:** On hold

The Plugin Toolkit modernization is not a current priority. Work should resume only if it becomes necessary for active modernization projects or if its strategic value is reassessed later.
