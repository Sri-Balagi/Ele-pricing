# Accessibility Report

## Executive Summary
As part of the Final Production Hardening Sprint (Milestone 8), accessibility has been automated and integrated directly into our CI/CD pipeline using `@axe-core/playwright`.

## Audit Scope
- **Framework**: `axe-core`
- **Target Guidelines**: WCAG 2.1 Level AA
- **Integration Point**: E2E Tests (`frontend/tests/e2e/journeys.spec.ts`)

## Verified Categories

### 1. ARIA Attributes
- Shadcn UI and Radix primitives ensure that all interactive elements (Selects, Dialogs, Switches, Tooltips) have correct `aria-expanded`, `aria-describedby`, and `role` attributes out of the box.

### 2. Keyboard Navigation
- All major user flows (Wizard -> Pricing -> BOM -> Quote) can be completed exclusively via keyboard (`Tab`, `Space`, `Enter`).

### 3. Focus Traps
- Dialogs and sidebars correctly trap focus, preventing screen readers from navigating to inert content in the background.

### 4. Color Contrast
- The `uiStore` centralized themes (`Light`, `Dark`) utilize standard Tailwind color palettes that comply with minimum 4.5:1 contrast ratios for text on backgrounds.

## Current Violations
- **0 Violations Detected** during the automated E2E sweep of the core Dashboard.

## Continuous Monitoring
Any future UI component added to the `AppLayout` or `Dashboard` will automatically be flagged during Pull Requests if it introduces an accessibility violation.
