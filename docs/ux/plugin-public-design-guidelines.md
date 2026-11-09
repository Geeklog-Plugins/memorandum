# Geeklog Plugin Public Design Guidelines

## Purpose

This document defines practical public-facing design, usability and accessibility expectations for modernized Geeklog plugins. The goal is not to impose one visual theme, but to make plugin pages pleasant to read and use under different Geeklog themes while keeping business logic and presentation responsibilities separate.

Compatibility target: Geeklog 2.1.1 through 2.2.2 and PHP 5.6 through PHP 8.1.

## Theme independence

A plugin should produce clear semantic HTML and let the active Geeklog theme own most of the visual language. Prefer semantic elements, small plugin-specific classes, templates for significant markup, and modest fallback CSS. Do not require Eclipse, Denim, UIkit or Bootstrap for core functionality.

## Information hierarchy and readability

Every public page should make its purpose obvious: where the user is, what the page is about, what can be done, and what comes next. Use one clear page title, logical heading levels, meaningful sections, breadcrumbs where useful, readable line length, and consistent spacing. Do not stretch long-form prose edge-to-edge on large screens.

## Responsive and touch design

Mobile is a first-class target. Verify that forms, filters, tables, galleries, media players and navigation remain usable without horizontal overflow. Controls must be large enough to tap reliably and actions must not crowd each other.

## Accessibility baseline

Associate labels with controls, preserve keyboard access, provide visible focus states, use native buttons for actions and links for navigation, do not rely on color alone, provide meaningful alternative text, and use ARIA only when it adds real semantics. Progressive enhancement is preferred: optional JavaScript failure must not make the page incomprehensible.

## States are part of the design

Deliberately handle normal, empty, loading, validation-error, permission-denied, missing-resource, disabled-plugin and external-service-failure states. Empty states should explain the next useful action. Error states should help recovery without exposing implementation details.

## Forms, lists and tables

Ask only for required information, use clear labels and local help, preserve safe values after validation errors, and separate destructive actions. Use lists for scan-friendly text, cards when several visual attributes belong together, and tables for genuinely columnar comparison. Do not turn every collection into cards merely because cards look modern.

## Contextual extension fragments

When a provider calls PLG_itemDisplay($id, $type), the provider owns the physical insertion point. A useful default order is primary content, contextual/plugin-contributed fragments, then comments or secondary actions. The host page should provide enough semantic structure and spacing that FAQ, Hub or other fragments do not look bolted on.

## Performance is part of design

Prefer server-rendered initial content, bounded collections, versioned assets, optimized media, and no unnecessary JavaScript framework for small interactions. Avoid N+1 provider lookups when a collection contract can return the required data.

## Public design acceptance checklist

- [ ] clear title and hierarchy
- [ ] semantic HTML
- [ ] theme-independent core use
- [ ] readable content width
- [ ] responsive/mobile layout
- [ ] keyboard-accessible interactions and visible focus
- [ ] labelled form controls
- [ ] useful empty/error states
- [ ] touch-friendly controls
- [ ] responsive images/media
- [ ] contextual fragments integrate naturally
- [ ] optional JavaScript failure remains understandable
- [ ] tested under at least one legacy-compatible and one modern target theme when practical

## Guiding principle

> A plugin should own clear semantic structure and usable behavior; the theme should own most of the visual identity.