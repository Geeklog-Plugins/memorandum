# Geeklog Memorandum — documentation guide

This index is a decision aid, not another specification. **Current target: Geeklog 2.2.2+; PHP 5.6.40 minimum for projects following the shared runtime policy.** Historical Geeklog 2.1.1 migrations are retained as records, not current runtime requirements.

## Choose the right document

| If you need to… | Start here |
| --- | --- |
| Establish supported Core/PHP versions and release checks | [Runtime support policy](policy/geeklog-runtime-support-policy.md) |
| Build, upgrade or ship a plugin | [Plugin development guide](development/plugin-development-guide.md) |
| Check a real Geeklog 2.2.2 API | [Plugin API reference](reference/plugin-api-reference-2.2.2.md), then [Core 2.2.2 source](https://github.com/Geeklog-Core/geeklog/tree/v2.2.2) |
| Configure a plugin or migrate its settings | [Configuration migration guide](reference/plugin-configuration-migration-guide-2.2.2.md) |
| Design a safe multisite plugin | [Multisite principles](operations/multisite-development-principles.md) and [shared-files upgrade safety](operations/plugin-shared-files-upgrade-safety.md) |
| Plan current development | [Modernization roadmap](strategy/geeklog-modernization-roadmap.md) |
| Plan integration between content plugins | [Content interoperability contract](contracts/plugin-content-interoperability-contract.md) |
| Plan Agent, Hub and external AI integration | [Hub/Agent architecture](architecture/agent-hub-connector-architecture.md) |
| Review legacy upgrade incidents | [Historical Geeklog 2.1.1 → 2.2.2 migration](history/geeklog-2.1.1-to-2.2.2-multisite-upgrade-lessons.md) |

## Authority and status

1. **Implemented Core behavior:** [official documentation repository](https://github.com/Geeklog-Core/documentation), [published guides](https://geeklog-core.github.io/documentation/), version-specific Geeklog source and release notes. If documentation and actual versioned code differ, verify the code before asserting an API exists.
2. **Binding project policy:** [runtime policy](policy/geeklog-runtime-support-policy.md). It governs the supported minimum and supersedes any stale compatibility statement elsewhere in this repository.
3. **Recommended project conventions:** development, operations and UX guidelines. These are shared engineering preferences, **not automatically official Geeklog requirements**.
4. **Proposals and future architecture:** contracts, architecture and long-range strategy; do not describe proposed APIs as existing or mandatory until implementation and adoption are confirmed.
5. **Historical records:** migration notes and previously observed behavior. Historical examples may mention unsupported Core releases; they do not reopen the support matrix.

The official documentation project still contains migration work and version-scoped material. Check whether a guide is published, draft, source-verified or historical before using it as an implementation reference.

## Complete catalog by topic

### Policy
- [Geeklog runtime support policy](policy/geeklog-runtime-support-policy.md) — single source for version and release requirements.

### Development and Core reference
- [Plugin development guide](development/plugin-development-guide.md) — end-to-end workflow, installation, upgrades, packaging and acceptance.
- [Plugin metadata manifest](development/plugin-metadata-manifest.md) — proposed standardized metadata conventions.
- [Geeklog 2.2.2 Plugin API reference](reference/plugin-api-reference-2.2.2.md) — version-specific API inventory; confirm against Core source.
- [Plugin configuration migration guide](reference/plugin-configuration-migration-guide-2.2.2.md) — configuration API and upgrade patterns.

### Operations and multisite
- [Multisite development principles](operations/multisite-development-principles.md) — site isolation, bootstrap context and paths.
- [Persistent storage](operations/plugin-persistent-storage-guide.md) — protect data outside disposable cache.
- [Shared-files upgrade safety](operations/plugin-shared-files-upgrade-safety.md) — staggered state upgrades across sites.
- [Install / Upgrade / Rescue architecture](operations/geeklog-installer-upgrade-rescue-architecture.md) — **proposal**, not an implemented rescue feature.

### Administration, design and SEO
- [Administration navigation](ux/plugin-admin-navigation.md) — Core menus and section navigation.
- [Administration UX](ux/plugin-admin-ux-guidelines.md) — usability, first-use and help.
- [Configuration tooltips](ux/plugin-configuration-tooltips.md) — contextual help.
- [Asset loading and versioning](ux/plugin-asset-loading-versioning.md) — static CSS/JS and cache behavior.
- [Public design](ux/plugin-public-design-guidelines.md) — responsive, accessible, theme-neutral output.
- [Public-page SEO](ux/plugin-seo-public-page-guidelines.md) — canonical URLs, metadata and semantic markup.

### Shared contracts and integration proposals
- [Plugin content interoperability](contracts/plugin-content-interoperability-contract.md) — content identity, metadata, events and URLs.
- [Plugin capability contract](contracts/plugin-capability-contract.md) — reusable provider capabilities.
- [Source-field audit and mutation](contracts/plugin-source-field-audit-mutation-contract.md) — permission-aware inspection and controlled edits.
- [SEO and measurement interoperability](contracts/seo-measurement-interoperability-guide.md) — search, indexing and analytics boundaries.

### Agent, AI and external access
- [Hub, Agent and Connector architecture](architecture/agent-hub-connector-architecture.md) — ownership and interface boundaries.
- [ChatGPT connector concept](architecture/geeklog-chatgpt-connector.md) — **proposal** for an external adapter.
- [LLM / Agent content representation](architecture/llm-agent-content-representation-contract.md) — discovery, resources and actions contract.

### Strategy — not a development queue unless explicitly marked
- [Modernization roadmap](strategy/geeklog-modernization-roadmap.md) — current implementation order.
- [Geeklog 2030 roadmap](strategy/geeklog-2030-roadmap.md) — longer-term architectural direction.
- [External data integration vision](strategy/geeklog-external-data-integration-vision-2030.md) — future exchange and connectors.
- [Marketing roadmap 2027–2030](strategy/geeklog-marketing-roadmap-2027-2030.md) — future marketing concept.

### History — not normative
- [Geeklog 2.2.2 features / post-upgrade checklist](history/GEEKLOG_222_FEATURES_AND_POST_UPGRADE_CHECKLIST.md) — historical French field checklist.
- [Geeklog 2.1.1 → 2.2.2 multisite upgrade lessons](history/geeklog-2.1.1-to-2.2.2-multisite-upgrade-lessons.md) — incidents and recovery lessons.

## Rules for future documentation changes

- **Choose one home:** Core facts belong in the official documentation or a clearly versioned reference; project policy in `policy/`; implementation sequence in `development/`; design guidelines in `ux/`; operational procedures in `operations/`; proposals in `contracts/` or `architecture/`; time-bound priorities in `strategy/`; retired practices and one-off incidents in `history/`.
- **Link rather than duplicate:** each requirement should have a single authoritative home. In other documents, link to that home and state only the additional local decision.
- **Make status explicit:** mark new proposals as *proposed*, unverified material as *needs verification*, and migration material as *historical*. Do not use “required by Geeklog” for a Memorandum preference.
- **Require version evidence:** new Core API claims specify which Geeklog version was checked. Never bring back 2.1.1 runtime compatibility as a requirement without an explicit policy change.
- **Keep navigation current:** update this index when adding, renaming or moving a document; verify local links before merging. Avoid creating a new document when a short section in an existing guide would suffice.
- **Keep the roadmap lean:** active implementation milestones live in the modernization roadmap, not in long-range vision papers.
