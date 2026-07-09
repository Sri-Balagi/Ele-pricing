# Performance Budget

This document establishes the hard performance ceilings for the Elevator Configurator UI. CI/CD pipelines and PR reviews must ensure these limits are never breached.

## 1. Web Vitals Targets
- **Largest Contentful Paint (LCP)**: < 1.5 seconds (Target), < 2.5 seconds (Max)
- **Cumulative Layout Shift (CLS)**: < 0.05
- **First Input Delay (FID) / INP**: < 100 milliseconds
- **Time to Interactive (TTI)**: < 2.5 seconds

## 2. Network & Payload Budgets
- **Total Initial JS Payload (Gzipped)**: < 150 KB
- **Total Initial CSS Payload (Gzipped)**: < 25 KB
- **Total Initial Request Count**: < 10

## 3. Backend Latency Thresholds (95th Percentile)
- **Configuration Creation (`POST /configurations`)**: < 200ms
- **BOM Generation (`GET /configurations/{id}`)**: < 150ms
- **Pricing Resolution (`GET /configurations/{id}/pricing`)**: < 250ms
- **Export Document Generation (`GET /configurations/{id}/export/*`)**: < 800ms
