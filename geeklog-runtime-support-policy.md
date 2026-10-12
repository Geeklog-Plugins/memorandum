# Geeklog runtime support policy (October 2026)

## Active baseline
- Geeklog **2.2.2** is the minimum supported Core release for new development and maintained plugins/themes. Do not require Geeklog 2.1.1 support.
- PHP **5.6.40** remains the minimum supported PHP runtime. Write syntax compatible with PHP 5.6, and validate on 5.6 and maintained PHP 8.x versions; PHP 8.1 and 8.3 are useful test targets. Do not confuse the Geeklog minimum with a PHP 8.1 minimum.
- Update native install metadata, compatibility callbacks, plugin.json, CI, README and release notes consistently when applying this policy.
- Continue preserving historical plugin configuration and persistent state during upgrades even though old Geeklog Core runtime support has ended. Shared-files multisite staggered upgrades must be safe across Geeklog 2.2.2 sites.
- Do not change historical release notes to imply a previously shipped release supported a different runtime. Historical migration guides may document Geeklog 2.1.1 but must clearly separate that history from the active baseline.

## Release gate
Validate the installable archive, PHP 5.6 lint, PHP 8.x lint, fresh install, upgrade, enable/disable, uninstall, front-end rendering, language resources, and shared-files multisite where applicable.
