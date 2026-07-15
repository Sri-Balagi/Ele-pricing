# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: journeys.spec.ts >> Elevator Configuration User Journeys >> should initiate export downloads
- Location: tests\e2e\journeys.spec.ts:47:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=View Quote')
Expected: visible
Error: strict mode violation: locator('text=View Quote') resolved to 2 elements:
    1) <div data-slot="card-description" class="text-sm text-muted-foreground">Enter a Configuration ID to view quote details an…</div> aka getByText('Enter a Configuration ID to')
    2) <button disabled tabindex="0" type="button" data-disabled="" data-slot="button" class="group/button inline-flex shrink-0 items-center justify-center rounded-lg border border-transparent bg-clip-padding text-sm font-medium whitespace-nowrap transition-all outline-none select-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 active:not-aria-[haspopup]:translate-y-px disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-inva…>View Quote</button> aka getByRole('button', { name: 'View Quote' })

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('text=View Quote')

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - generic [ref=e3]:
    - banner [ref=e4]:
      - heading "Elevator Configurator" [level=1] [ref=e5]:
        - img [ref=e6]
        - text: Elevator Configurator
    - generic [ref=e9]:
      - complementary [ref=e10]:
        - navigation [ref=e11]:
          - link "Dashboard" [ref=e12] [cursor=pointer]:
            - /url: /
            - img [ref=e13]
            - text: Dashboard
          - link "Database" [ref=e18] [cursor=pointer]:
            - /url: /database
            - img [ref=e19]
            - text: Database
          - link "Wizard" [ref=e22] [cursor=pointer]:
            - /url: /wizard
            - img [ref=e23]
            - text: Wizard
          - link "Pricing" [ref=e26] [cursor=pointer]:
            - /url: /pricing
            - img [ref=e27]
            - text: Pricing
          - link "BOM" [ref=e29] [cursor=pointer]:
            - /url: /bom
            - img [ref=e30]
            - text: BOM
          - link "Quote & Export" [ref=e33] [cursor=pointer]:
            - /url: /quote
            - img [ref=e34]
            - text: Quote & Export
        - button "Logout" [ref=e38]:
          - img [ref=e39]
          - text: Logout
      - main [ref=e42]:
        - generic [ref=e43]:
          - heading "Quote & Export" [level=1] [ref=e44]
          - generic [ref=e45]:
            - generic [ref=e46]:
              - generic [ref=e47]: Load Quote
              - generic [ref=e48]: Enter a Configuration ID to view quote details and export documents.
            - generic [ref=e50]:
              - generic [ref=e52]:
                - img [ref=e53]
                - textbox "Search config to view quote..." [ref=e56]
              - button "View Quote" [disabled]
    - generic [ref=e57]:
      - generic [ref=e58]:
        - img [ref=e59]
        - generic [ref=e62]:
          - text: "System Status:"
          - strong [ref=e63]: Healthy
      - generic [ref=e64]: v0.1.0 | development
  - region "Notifications alt+T"
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Elevator Configuration User Journeys', () => {
  4  | 
  5  |   test.beforeEach(async ({ page }) => {
  6  |     await page.goto('/login');
  7  |     await page.evaluate(() => {
  8  |       localStorage.setItem('isAuthenticated', 'true');
  9  |     });
  10 |     // Go to home page to trigger standard flow
  11 |     await page.goto('/');
  12 |   });
  13 | 
  14 |   test('should load the Dashboard and verify basic accessibility', async ({ page }) => {
  15 |     await page.route('**/api/v1/dashboard/metrics', route => route.fulfill({
  16 |       status: 200,
  17 |       json: { success: true, data: { total_configurations: 10 } }
  18 |     }));
  19 |     await page.reload();
  20 |     await expect(page.locator('h1', { hasText: 'Dashboard' })).toBeVisible();
  21 |   });
  22 | 
  23 |   test('should complete the configuration creation journey', async ({ page }) => {
  24 |     await page.goto('/wizard');
  25 |     await expect(page.locator('h1', { hasText: 'Configuration Wizard' })).toBeVisible();
  26 |     await expect(page.locator('text=Step 1 — Project Information')).toBeVisible();
  27 |   });
  28 | 
  29 |   test('should render validation failures and success', async ({ page }) => {
  30 |     await page.goto('/validation');
  31 |     await expect(page.locator('h1', { hasText: 'Validation View' })).toBeVisible({ timeout: 10000 });
  32 |     await expect(page.locator('text=Check Configuration Validity')).toBeVisible();
  33 |   });
  34 | 
  35 |   test('should load pricing views and toggle taxes', async ({ page }) => {
  36 |     await page.goto('/pricing');
  37 |     await expect(page.locator('h1', { hasText: 'Pricing Breakdown' })).toBeVisible({ timeout: 10000 });
  38 |     await expect(page.locator('text=Load Pricing')).toBeVisible();
  39 |   });
  40 | 
  41 |   test('should load BOM list', async ({ page }) => {
  42 |     await page.goto('/bom');
  43 |     await expect(page.locator('h1', { hasText: 'Bill of Materials' })).toBeVisible({ timeout: 10000 });
  44 |     await expect(page.locator('text=View BOM')).toBeVisible();
  45 |   });
  46 | 
  47 |   test('should initiate export downloads', async ({ page }) => {
  48 |     await page.goto('/quote');
  49 |     await expect(page.locator('h1', { hasText: 'Quote & Export' })).toBeVisible({ timeout: 10000 });
> 50 |     await expect(page.locator('text=View Quote')).toBeVisible();
     |                                                   ^ Error: expect(locator).toBeVisible() failed
  51 |   });
  52 | 
  53 |   test('should handle backend offline/error gracefully', async ({ page }) => {
  54 |     await page.route('**/api/v1/dashboard/metrics', route => route.fulfill({
  55 |       status: 500,
  56 |       json: { success: false, message: "Internal Server Error" }
  57 |     }));
  58 |     await page.goto('/');
  59 |     await page.reload();
  60 |     await expect(page.locator('text=Failed to load dashboard data')).toBeVisible({ timeout: 10000 });
  61 |   });
  62 | 
  63 |   test('should handle direct URL navigation', async ({ page }) => {
  64 |     await page.goto('/validation');
  65 |     await expect(page.locator('h1', { hasText: 'Validation View' }).first()).toBeVisible({ timeout: 10000 });
  66 |   });
  67 | 
  68 | });
  69 | 
```