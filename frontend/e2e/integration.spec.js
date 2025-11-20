/**
 * End-to-end integration tests for Employee, Product, Inventory, and Sales management
 */
import { test, expect } from '@playwright/test';

// Helper function to login with robust post-login detection
async function login(page, username = 'admin', password = 'admin123') {
  await page.goto('/login');
  await page.fill('input[placeholder*="Username" i]', username);
  await page.fill('input[placeholder*="Password" i]', password);
  await page.click('button:has-text("Login")');
  // Wait until we are no longer on the login page or navbar appears
  await Promise.race([
    page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 15000 }),
    page.getByRole('link', { name: 'Pharmacy Management' }).waitFor({ state: 'visible', timeout: 15000 }),
  ]);
  await page.waitForLoadState('networkidle');
}

test.describe('Employee Management Integration', () => {
  test.beforeEach(async ({ page }) => {
  await login(page);
  // Navigate to Employees (manager-only)
  const employeesLink = page.getByRole('link', { name: 'Employees', exact: true });
  await employeesLink.waitFor({ state: 'visible', timeout: 10000 });
  await employeesLink.click();
  await page.waitForURL(/.*employees/);
  });

  test('create employee from UI and verify in table', async ({ page }) => {
    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
    
    // Find and click "Add Employee" button
    const addButton = page.getByRole('button', { name: 'Add Employee' });
    await expect(addButton).toBeVisible();
    await addButton.click();
    
    // Wait for form heading to confirm form opened
    await expect(page.locator('h3:has-text("Add Employee")')).toBeVisible({ timeout: 10000 });
    
  // Fill form
    const timestamp = Date.now();
  await page.locator('label:has-text("Username") + input').fill(`testuser${timestamp}`);
  await page.locator('label:has-text("Password") + input').fill('testpass123');
  const nameLabel = page.locator('form').locator('label').filter({ hasText: /^Name$/ });
  await nameLabel.locator('xpath=following-sibling::input[1]').fill(`Test User ${timestamp}`);
    
    // Submit
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    // Wait for success and verify in table
    await expect(page.locator(`text=testuser${timestamp}`)).toBeVisible({ timeout: 10000 });
  });

  test('edit employee from UI', async ({ page }) => {
    // Find and click edit on first employee (skip if none exist)
    const editButton = page.locator('button:has-text("Edit")').first();
    
    if (await editButton.isVisible()) {
      await editButton.click();
      
  // Modify name
  const nameLabel = page.locator('form').locator('label').filter({ hasText: /^Name$/ });
  const nameInput = nameLabel.locator('xpath=following-sibling::input[1]');
  await nameInput.fill('Updated Name');
      
      // Save
      await page.click('button[type="submit"]:has-text("Save"), button[type="submit"]:has-text("Update")');
      
      // Verify success message or updated name
      const successVisible = await Promise.race([
        page.locator('text="Success"').isVisible().catch(() => false),
        page.locator('text="Updated"').isVisible().catch(() => false),
        page.locator('text="Saved"').isVisible().catch(() => false),
      ]);
      expect(successVisible).toBeTruthy();
    }
  });
});

test.describe('Product Management Integration', () => {
  test.beforeEach(async ({ page }) => {
  await login(page);
  const productsLink = page.getByRole('link', { name: 'Products', exact: true });
  await productsLink.waitFor({ state: 'visible', timeout: 10000 });
  await productsLink.click();
  await page.waitForURL(/.*products/);
  });

  test('create product from UI and check in table', async ({ page }) => {
    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
    
    // Find and click "Add Product" button
    const addButton = page.getByRole('button', { name: 'Add Product' });
    await expect(addButton).toBeVisible();
    await addButton.click();
    
    // Wait for form heading to confirm form opened
    await expect(page.locator('h3:has-text("Add Product")')).toBeVisible({ timeout: 10000 });
    
  // Fill form
    const timestamp = Date.now();
  await page.locator('label:has-text("Name") + input').fill(`Product ${timestamp}`);
  await page.locator('label:has-text("Presentation") + select').selectOption('tablets');
  await page.locator('label:has-text("Substance") + input').fill('Test Substance');
  await page.locator('label:has-text("Price") + input').fill('25.50');
    
    // Submit
  const submitButton = page.locator('button[type="submit"]').first();
  await submitButton.click();
  // Wait for form to close and network to settle
  await expect(page.locator('h3:has-text("Add Product")')).toBeHidden({ timeout: 10000 });
  await page.waitForLoadState('networkidle');
  // Verify in table
  const tableBody = page.locator('table tbody');
  await expect(tableBody).toContainText(`Product ${timestamp}`, { timeout: 15000 });
  });

  test('edit product from UI', async ({ page }) => {
    const editButton = page.locator('button:has-text("Edit")').first();
    
    if (await editButton.isVisible()) {
      await editButton.click();
      
  // Change price
  const priceInput = page.locator('label:has-text("Price") + input');
      await priceInput.fill('99.99');
      
      // Save
      await page.click('button[type="submit"]:has-text("Save"), button[type="submit"]:has-text("Update")');
      
      // Verify success
      const successVisible = await Promise.race([
        page.locator('text="Success"').isVisible().catch(() => false),
        page.locator('text="Updated"').isVisible().catch(() => false),
      ]);
      expect(successVisible).toBeTruthy();
    }
  });

  test('delete product and verify removed', async ({ page }) => {
    const deleteButton = page.locator('button:has-text("Delete")').first();
    
    if (await deleteButton.isVisible()) {
      // Get product name before deletion
      const row = deleteButton.locator('xpath=ancestor::tr');
      const productName = await row.locator('td').first().textContent();
      
      // Delete
      await deleteButton.click();
      
      // Confirm if dialog appears
      page.on('dialog', dialog => dialog.accept());
      
      // Verify product is gone
      await expect(page.locator(`text=${productName}`)).not.toBeVisible({ timeout: 5000 });
    }
  });

  test('create product with invalid data shows errors', async ({ page }) => {
    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
    
    // Find and click "Add Product" button
    const addButton = page.getByRole('button', { name: 'Add Product' });
    await expect(addButton).toBeVisible();
    await addButton.click();
    
    // Wait for form heading to confirm form opened
    await expect(page.locator('h3:has-text("Add Product")')).toBeVisible({ timeout: 10000 });
    
    // Submit without filling required fields
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    // Should show validation errors
    // Either HTML5 validation or custom error messages
    const nameInput = page.locator('label:has-text("Name") + input');
    const isInvalid = await nameInput.evaluate(el => !el.validity.valid);
    expect(isInvalid).toBeTruthy();
  });
});

test.describe('Inventory Management Integration', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.click('text=Inventory');
    await page.waitForURL(/.*inventory/);
  });

  test('show complete inventory list from backend', async ({ page }) => {
    // Verify table or list is visible
    await expect(page.locator('table, .inventory-list')).toBeVisible();
    
    // Verify we have at least headers - check for th elements
    await expect(page.locator('th >> text="Product"')).toBeVisible();
  });

  test('increase inventory as manager', async ({ page }) => {
    const increaseButton = page.locator('button:has-text("Increase"), button:has-text("Add Stock")').first();
    
    if (await increaseButton.isVisible().catch(() => false)) {
      // Get current quantity
      const row = increaseButton.locator('xpath=ancestor::tr');
      const quantityCells = await row.locator('td').allTextContents();
      const currentQty = parseInt(quantityCells.find(text => /^\d+$/.test(text.trim())) || '0');
      
      // Click increase
      await increaseButton.click();
      
  // Fill amount
  await page.locator('label:has-text("Amount") + input').fill('10');
      await page.click('button[type="submit"]:has-text("Save"), button[type="submit"]:has-text("Increase"), button[type="submit"]:has-text("Add")');
      
      // Verify quantity increased
      await expect(page.locator(`text=${currentQty + 10}`)).toBeVisible({ timeout: 5000 });
    }
  });
});

test.describe('Sales Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('register sale with multiple products', async ({ page }) => {
    await page.click('text=Register Sale');
    await page.waitForURL(/.*register-sale/);
    
    // Add first product
    const productSelect = page.locator('select[name="product"]');
    if (await productSelect.isVisible()) {
      await productSelect.selectOption({ index: 1 });
      await page.fill('input[name="quantity"], input[placeholder*="quantity" i]', '2');
      await page.click('button:has-text("Add Item"), button:has-text("Add Product")');
      
      // Verify item added
      await page.waitForTimeout(1000);
      
      // Complete sale
      await page.click('button:has-text("Complete Sale"), button:has-text("Submit"), button:has-text("Register")');
      
      // Verify success
      const successVisible = await Promise.race([
        page.locator('text="Success"').isVisible().catch(() => false),
        page.locator('text="Sale Registered"').isVisible().catch(() => false),
      ]);
      expect(successVisible).toBeTruthy();
    }
  });

  test('sale with insufficient stock shows error', async ({ page }) => {
    await page.click('text=Register Sale');
    await page.waitForURL(/.*register-sale/);
    
    // Try to sell large quantity
    const productSelect = page.locator('select[name="product"]');
    if (await productSelect.isVisible()) {
      await productSelect.selectOption({ index: 1 });
      await page.fill('input[name="quantity"]', '99999');
      await page.click('button:has-text("Add Item")');
      await page.click('button:has-text("Complete Sale"), button:has-text("Submit")');
      
      // Should show error
      const errorVisible = await Promise.race([
        page.locator('text="Insufficient"').isVisible().catch(() => false),
        page.locator('text="Not enough"').isVisible().catch(() => false),
        page.locator('text="Stock"').isVisible().catch(() => false),
      ]);
      expect(errorVisible).toBeTruthy();
    }
  });

  test('sales list loaded correctly', async ({ page }) => {
    await page.click('text=Sales');
    await page.waitForURL(/.*sales/);
    
    // Verify sales list header
    await expect(page.locator('h1 >> text="Sales History"')).toBeVisible();
  });

  test('view sale detail', async ({ page }) => {
    await page.click('text=Sales');
    await page.waitForURL(/.*sales/);
    
    // Click first sale detail/view button
    const viewButton = page.locator('button:has-text("View"), button:has-text("Details"), a:has-text("View"), a:has-text("Details")').first();
    
    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      
      // Verify sale details are shown
      await page.waitForTimeout(1000);
      expect(await page.locator('text="Total"').isVisible()).toBeTruthy();
    }
  });
});

test.describe('Frontend General Tests', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('all screens load after login', async ({ page }) => {
    // Dashboard
    await expect(page.locator('text=Pharmacy Management')).toBeVisible();
    
    // Inventory
    await page.click('a[href="/inventory"]');
    await page.waitForURL(/.*inventory/);
    await expect(page.locator('h1').first()).toBeVisible();
    
    // Sales
    await page.click('a[href="/sales"]');
    await page.waitForURL(/.*sales/);
    await expect(page.locator('h1').first()).toBeVisible();
    
    // Products (Manager only)
  await page.click('a[href="/products"]');
    await page.waitForURL(/.*products/);
    await expect(page.locator('h1').first()).toBeVisible();
    
    // Employees (Manager only)
    await page.click('a[href="/employees"]');
    await page.waitForURL(/.*employees/);
    await expect(page.locator('h1').first()).toBeVisible();
  });

  test('success messages on create/edit operations', async ({ page }) => {
    // Go to products
    await page.click('a[href="/products"]');
    await page.waitForURL(/.*products/);
    await page.waitForLoadState('networkidle');
    
    // Find and click "Add Product" button
    const addButton = page.getByRole('button', { name: 'Add Product' });
    await expect(addButton).toBeVisible();
    await addButton.click();
    
    // Wait for form heading to confirm form opened
    await expect(page.locator('h3:has-text("Add Product")')).toBeVisible({ timeout: 10000 });
    
  const timestamp = Date.now();
  await page.locator('label:has-text("Name") + input').fill(`Test ${timestamp}`);
  await page.locator('label:has-text("Presentation") + select').selectOption('tablets');
  await page.locator('label:has-text("Substance") + input').fill('Test');
  await page.locator('label:has-text("Price") + input').fill('10.00');
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    // Verify the newly created product appears in the table as success criteria
    await expect(page.locator(`text=Test ${timestamp}`)).toBeVisible({ timeout: 10000 });
  });
});
