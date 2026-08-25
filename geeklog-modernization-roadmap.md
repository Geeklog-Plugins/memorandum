# Geeklog Modernization Roadmap

This roadmap focuses on the current priorities for the Geeklog ecosystem and keeps the scope intentionally simple.

## 1. Menu 1.3.0

**Goal:** make Menu a reliable navigation layer for modern Geeklog themes.

### Priorities
- Finalize configuration defaults for new installations and upgrades.
- Complete the admin menu preview.
- Fix remaining compatibility issues.
- Improve the integration with Eclipse.
- Define a clean and reusable navigation output for themes.
- Keep compatibility with existing Geeklog installations where practical.

## 2. Documents

**Goal:** stabilize the plugin before adding new features.

### Priorities
- Fix the security token issue when saving fields.
- Complete functional tests for document and field management.
- Finalize the persistent data migration strategy.
- Ensure safe and isolated storage for multisite installations.
- Confirm that upgrades are non-destructive and repeatable.
- Keep packaging and migration tests reliable.

## 3. Maps

**Goal:** restore a stable base before continuing modernization.

### Priorities
- Finish synchronization with the target 1.5.6 alpha18 archive.
- Align `functions.inc` with the expected version.
- Synchronize the remaining language and admin files.
- Validate the plugin before starting new development.
- Modernize Google Maps integration for current APIs.
- Improve PHP 8 compatibility, security, and search behavior.

## 4. Eclipse Theme

**Goal:** make Eclipse the reference modern theme for Geeklog 2.2.2.

### Priorities
- Stabilize the integration with Menu.
- Make navigation robust when Geeklog caches are rebuilt or cleared.
- Finalize the main frontend and admin layouts.
- Complete Theme Studio features.
- Keep theme data outside temporary Geeklog cache storage.
- Improve SEO, accessibility, and mobile behavior.
- Target Geeklog 2.2.2 as the main supported platform.

## 5. Store Plugin

**Goal:** stabilize Store as a modern application and distribution component for Geeklog.

### Priorities
- Complete the current functional base.
- Fix remaining PHP and packaging issues.
- Improve installation and upgrade reliability.
- Validate the product management workflow.
- Continue testing with realistic demo products.
- Document the architecture before expanding the feature set.
- Avoid making other major projects depend on Store until it is stable.

## 6. Videos

**Goal:** modernize data handling and prepare the plugin for current Geeklog installations.

### Priorities
- Move persistent plugin data outside disposable cache locations.
- Use a site-specific storage path compatible with multisite.
- Validate migration from existing installations.
- Improve PHP 8 compatibility.
- Review security and file handling.
- Complete functional tests before adding new features.

## 7. Multisite Manager

**Goal:** reduce manual configuration and make Geeklog multisite easier to operate.

### Priorities
- Define the master-site-only plugin architecture.
- Manage secondary site configuration from the master site.
- Support site enable/disable operations.
- Manage database prefixes or isolated site tables safely.
- Reuse official Geeklog installation functions where possible.
- Reduce direct manual edits to `db-config.php` and `siteconfig.php`.
- Keep the solution compatible with normal single-site installations where possible.

## 8. Geeklog 2030

**Goal:** prepare Geeklog for long-term evolution without trying to copy other CMS platforms.

### Priorities
- Define common plugin architecture conventions.
- Improve APIs and structured data access.
- Strengthen multisite support.
- Improve plugin interoperability.
- Prepare future integrations with automation and AI tools.
- Modernize documentation and developer workflows.
- Encourage new services and plugins built on a stable Geeklog core.

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

The immediate objective is to finish and stabilize the existing modernization work before opening too many new development fronts.

## Projects on Hold

### Plugin Toolkit

The Plugin Toolkit modernization is currently considered non-priority and may be put on hold. Work should only resume if it becomes necessary for the other active projects.
