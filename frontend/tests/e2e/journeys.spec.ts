import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Elevator Configuration User Journeys', () => {

  test('should load the Dashboard and verify basic accessibility', async ({ page }) => {
    // We expect the backend/mock to be up via MSW or actual backend.
    // For E2E, we'll assume the Vite dev server is running and MSW provides data if backend is offline,
    // OR we hit the real backend if configured.
    await page.goto('/');
    await expect(page.locator('h1')).toHaveText('Dashboard');
    
    // Accessibility check
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should complete the configuration creation journey', async ({ page }) => {
    await page.goto('/wizard');
    await expect(page.locator('h1')).toContainText('Configuration Wizard');
    
    // Fill out the creation form
    await page.fill('input[name="customer_reference"]', 'E2E-Test-Ref');
    await page.fill('input[name="selected_category"]', 'STANDARD_PASSENGER');
    await page.click('button[type="submit"]');

    // Wait for the success toast and active config state
    await expect(page.locator('text=Configuration created successfully')).toBeVisible();
    await expect(page.locator('text=Editing Config')).toBeVisible();

    // Now update the configuration
    await page.fill('input[name="selected_feature_options"]', 'OPT-DOOR-GLASS, OPT-FINISH-GOLD');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Configuration updated successfully')).toBeVisible();
  });

  test('should render validation failures and success', async ({ page }) => {
    await page.goto('/validation');
    
    // Check validation for a mock ID
    await page.fill('input[placeholder="e.g. CFG-123"]', 'CFG-TEST-123');
    await page.click('text=Validate');
    
    // Expect the status block to appear (mock data might be empty or valid)
    await expect(page.locator('h3:has-text("Configuration")')).toBeVisible();
  });

  test('should load pricing views and toggle taxes', async ({ page }) => {
    await page.goto('/pricing');
    await page.fill('input[placeholder="e.g. CFG-123"]', 'CFG-TEST-123');
    await page.click('text=View Pricing');
    
    // Expect Total Price to render
    await expect(page.locator('text=Total Price')).toBeVisible();
    
    // Toggle Post-Tax switch
    await page.click('button[role="switch"]');
    // Assuming the switch updates state and potentially re-calculates/displays different text.
  });

  test('should load BOM list', async ({ page }) => {
    await page.goto('/bom');
    await page.fill('input[placeholder="e.g. CFG-123"]', 'CFG-TEST-123');
    await page.click('text=View BOM');
    
    await expect(page.locator('text=BOM Items')).toBeVisible();
  });

  test('should initiate export downloads', async ({ page }) => {
    await page.goto('/quote');
    await page.fill('input[placeholder="e.g. CFG-123"]', 'CFG-TEST-123');
    await page.click('text=View Quote');
    
    await expect(page.locator('text=Quote Metadata')).toBeVisible();
    
    // Test export buttons (We can just click them and ensure they don't crash, 
    // real download interception requires more complex setup)
    await page.click('text=Export as JSON');
    await expect(page.locator('text=JSON Export started')).toBeVisible();
  });

  test('should handle backend offline/error gracefully', async ({ page }) => {
    // Route interception to simulate 500 error
    await page.route('**/api/v1/system/pipeline', route => route.fulfill({
      status: 500,
      body: JSON.stringify({ message: "Internal Server Error" })
    }));

    await page.goto('/');
    
    // React Query should handle the error and we should see a graceful message instead of a blank screen
    await expect(page.locator('text=Failed to load dashboard data')).toBeVisible();
  });

  test('should handle direct URL navigation', async ({ page }) => {
    await page.goto('/validation');
    await expect(page.locator('h1')).toHaveText('Validation View');
  });

});
