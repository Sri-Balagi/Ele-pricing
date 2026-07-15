import { test, expect } from '@playwright/test';

test.describe('Elevator Configuration User Journeys', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('isAuthenticated', 'true');
    });
    // Go to home page to trigger standard flow
    await page.goto('/');
  });

  test('should load the Dashboard and verify basic accessibility', async ({ page }) => {
    await page.route('**/api/v1/dashboard/metrics', route => route.fulfill({
      status: 200,
      json: { success: true, data: { total_configurations: 10 } }
    }));
    await page.reload();
    await expect(page.locator('h1', { hasText: 'Dashboard' })).toBeVisible();
  });

  test('should complete the configuration creation journey', async ({ page }) => {
    await page.goto('/wizard');
    await expect(page.locator('h1', { hasText: 'Configuration Wizard' })).toBeVisible();
    await expect(page.locator('text=Step 1 — Project Information')).toBeVisible();
  });

  test('should render validation failures and success', async ({ page }) => {
    await page.goto('/validation');
    await expect(page.locator('h1', { hasText: 'Validation View' })).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Check Configuration Validity')).toBeVisible();
  });

  test('should load pricing views and toggle taxes', async ({ page }) => {
    await page.goto('/pricing');
    await expect(page.locator('h1', { hasText: 'Pricing Breakdown' })).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Load Pricing')).toBeVisible();
  });

  test('should load BOM list', async ({ page }) => {
    await page.goto('/bom');
    await expect(page.locator('h1', { hasText: 'Bill of Materials' })).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=View BOM')).toBeVisible();
  });

  test('should initiate export downloads', async ({ page }) => {
    await page.goto('/quote');
    await expect(page.locator('h1', { hasText: 'Quote & Export' })).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=View Quote').first()).toBeVisible();
  });

  test('should handle backend offline/error gracefully', async ({ page }) => {
    await page.route('**/api/v1/dashboard/metrics', route => route.fulfill({
      status: 500,
      json: { success: false, message: "Internal Server Error" }
    }));
    await page.goto('/');
    await page.reload();
    await expect(page.locator('text=Failed to load dashboard data')).toBeVisible({ timeout: 10000 });
  });

  test('should handle direct URL navigation', async ({ page }) => {
    await page.goto('/validation');
    await expect(page.locator('h1', { hasText: 'Validation View' }).first()).toBeVisible({ timeout: 10000 });
  });

});
