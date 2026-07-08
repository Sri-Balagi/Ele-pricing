# Dynamic Pricing Engine (Milestone 4)

## Overview

The Dynamic Pricing Engine is the final computation step in the elevator configuration pipeline. 
It receives a fully resolved, structurally valid `Configuration` aggregate (from the Dependency Engine) and the immutable `ProductCatalogue`.

It computes:
1. **Category Base Price**
2. **Feature Costs**
3. **Component Costs**
4. **Subtotal & Taxes**
5. **Final Total**

## Architecture

The Pricing Engine strictly conforms to the `BaseEngine[PricingContext, PricingReport]` interface.

- **PricingRepository**: Loads `pricing.json` into a structured `PricingCatalogue` model.
- **PricingValidator**: Checks for duplicates, negative prices, and missing tax configurations.
- **PricingRegistry**: Caches valid pricing data for O(1) lookups and provides a future extension point for cache invalidation.
- **PricingCalculator**: Pure function module computing sums and precise Decimal logic.
- **TaxCalculator**: Pluggable module reading data-driven tax rules.
- **BOMCostResolver**: Populates `BOMItem.unit_cost` for downstream ERP/Export usage.

## Data Structures

The backend acts as the source of truth, returning both "with tax" and "without tax" values to the frontend.
All calculations use `Decimal` with `ROUND_HALF_UP` precision.

### PricingSummary

```json
{
  "currency": "EUR",
  "currency_symbol": "€",
  "category_cost": 10000.00,
  "feature_cost": 500.00,
  "component_cost": 2350.00,
  "subtotal_before_tax": 12850.00,
  "tax_amount": 2570.00,
  "total_after_tax": 15420.00
}
```

## Missing Price Policy
The engine operates on a strict **fail-fast** policy. If any mandatory price record is missing, it will:
1. Log an Error.
2. Abort Pricing execution gracefully.
3. Preserve the previous `ConfigurationStatus.VALIDATED`.
4. Return the errors in the `PricingReport`.

## Lifecycle Events
The engine supports structured logging events:
- `BeforePricing` / `AfterPricing`
- `BeforeTax` / `AfterTax`
- `BeforeBOM` / `AfterBOM`
- `BeforeSummary` / `AfterSummary`
