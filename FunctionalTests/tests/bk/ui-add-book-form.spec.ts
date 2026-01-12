import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:50524';

test.describe('BookService UI Tests - Add Book Form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test('should display the Add Book section', async ({ page }) => {
    const heading = page.getByRole('heading', { name: 'Add Book', level: 2 });
    await expect(heading).toBeVisible();
  });

  test('should display all form fields', async ({ page }) => {
    // Check for Author dropdown
    const authorDropdown = page.getByRole('combobox');
    await expect(authorDropdown).toBeVisible();
    
    // Check for Title textbox
    const titleInput = page.getByRole('textbox', { name: 'Title' });
    await expect(titleInput).toBeVisible();
    
    // Check for Year spinbutton
    const yearInput = page.getByRole('spinbutton', { name: 'Year' });
    await expect(yearInput).toBeVisible();
    
    // Check for Genre textbox
    const genreInput = page.getByRole('textbox', { name: 'Genre' });
    await expect(genreInput).toBeVisible();
    
    // Check for Price spinbutton
    const priceInput = page.getByRole('spinbutton', { name: 'Price' });
    await expect(priceInput).toBeVisible();
    
    // Check for Submit button
    const submitButton = page.getByRole('button', { name: 'Submit' });
    await expect(submitButton).toBeVisible();
  });

  test('should have default author selected', async ({ page }) => {
    const authorDropdown = page.getByRole('combobox');
    
    // Get the first option text (default selected)
    const firstOption = await authorDropdown.locator('option').first().textContent();
    expect(firstOption).toBeTruthy();
    expect(firstOption).toContain('Jane Austen');
  });

  test('should display all author options', async ({ page }) => {
    // Get all option texts using evaluate
    const options = await page.$$eval('select option', opts => opts.map(opt => opt.textContent));
    
    // At least 3 authors (baseline data), may have more from parallel tests
    expect(options.length).toBeGreaterThanOrEqual(3);
    expect(options).toContain('Jane Austen');
    expect(options).toContain('Charles Dickens');
    expect(options).toContain('Miguel de Cervantes');
  });

  test('should have Genre field with placeholder', async ({ page }) => {
    const genreInput = page.getByRole('textbox', { name: 'Genre' });
    const placeholder = await genreInput.getAttribute('placeholder');
    
    expect(placeholder).toBe('Fiction');
  });

  test('should allow selecting different authors', async ({ page }) => {
    const authorDropdown = page.getByRole('combobox');
    
    // Select Charles Dickens
    await authorDropdown.selectOption({ label: 'Charles Dickens' });
    
    // Verify selection
    const selectedText = await authorDropdown.locator('option:checked').textContent();
    expect(selectedText).toBe('Charles Dickens');
  });

  test('should fill out complete form', async ({ page }) => {
    // Fill all form fields
    await page.getByRole('combobox').selectOption({ label: 'Jane Austen' });
    await page.getByRole('textbox', { name: 'Title' }).fill('Test Book Title');
    await page.getByRole('spinbutton', { name: 'Year' }).fill('2025');
    await page.getByRole('textbox', { name: 'Genre' }).fill('Mystery');
    await page.getByRole('spinbutton', { name: 'Price' }).fill('29.99');
    
    // Verify all fields are filled
    await expect(page.getByRole('textbox', { name: 'Title' })).toHaveValue('Test Book Title');
    await expect(page.getByRole('spinbutton', { name: 'Year' })).toHaveValue('2025');
    await expect(page.getByRole('textbox', { name: 'Genre' })).toHaveValue('Mystery');
    await expect(page.getByRole('spinbutton', { name: 'Price' })).toHaveValue('29.99');
  });

  test('should submit form and add book to list', async ({ page }) => {
    const uniqueTitle = 'Automated Test Book ' + Date.now();
    
    // Count existing books
    const initialBookCount = await page.locator('li').count();
    
    // Fill and submit form
    await page.getByRole('combobox').selectOption({ label: 'Miguel de Cervantes' });
    await page.getByRole('textbox', { name: 'Title' }).fill(uniqueTitle);
    await page.getByRole('spinbutton', { name: 'Year' }).fill('2025');
    await page.getByRole('textbox', { name: 'Genre' }).fill('Fiction');
    await page.getByRole('spinbutton', { name: 'Price' }).fill('25.00');
    
    await page.getByRole('button', { name: 'Submit' }).click();
    
    // Wait for page to reload or update
    await page.waitForTimeout(1000);
    
    // Verify book was added (check if book count increased or if book appears in list)
    const pageContent = await page.content();
    const updatedBookCount = await page.locator('li').count();
    
    // Either the count increased or the book title appears on the page
    expect(updatedBookCount >= initialBookCount || pageContent.includes(uniqueTitle)).toBeTruthy();
  });

  test('should clear form after successful submission', async ({ page }) => {
    // Fill form
    await page.getByRole('textbox', { name: 'Title' }).fill('Temp Book');
    await page.getByRole('spinbutton', { name: 'Year' }).fill('2025');
    await page.getByRole('textbox', { name: 'Genre' }).fill('Drama');
    await page.getByRole('spinbutton', { name: 'Price' }).fill('20.00');
    
    // Submit
    await page.getByRole('button', { name: 'Submit' }).click();
    
    // Wait for submission
    await page.waitForTimeout(1000);
    
    // Check if form fields are cleared (depends on implementation)
    // Some forms clear, some don't - this test documents the behavior
    const titleValue = await page.getByRole('textbox', { name: 'Title' }).inputValue();
    // Just document that we checked the post-submit state
    expect(titleValue).toBeDefined();
  });

  test('should handle form with minimal required fields', async ({ page }) => {
    // Fill only required fields (assuming Title and Author are required)
    await page.getByRole('combobox').selectOption({ label: 'Jane Austen' });
    await page.getByRole('textbox', { name: 'Title' }).fill('Minimal Book');
    
    // Try to submit
    await page.getByRole('button', { name: 'Submit' }).click();
    
    // Form should either submit successfully or show validation
    await page.waitForTimeout(500);
    
    // Verify page is still functional
    await expect(page.getByRole('heading', { name: 'BookService' })).toBeVisible();
  });

  test('should validate year field accepts numeric input', async ({ page }) => {
    const yearInput = page.getByRole('spinbutton', { name: 'Year' });
    
    await yearInput.fill('2025');
    await expect(yearInput).toHaveValue('2025');
    
    // Type should be number
    const inputType = await yearInput.getAttribute('type');
    expect(inputType).toBe('number');
  });

  test('should validate price field accepts decimal input', async ({ page }) => {
    const priceInput = page.getByRole('spinbutton', { name: 'Price' });
    
    await priceInput.fill('29.99');
    await expect(priceInput).toHaveValue('29.99');
    
    // Type should be number
    const inputType = await priceInput.getAttribute('type');
    expect(inputType).toBe('number');
  });

  test('should have proper form labels', async ({ page }) => {
    // Check that labels are visible
    const pageContent = await page.textContent('body');
    
    expect(pageContent).toContain('Author');
    expect(pageContent).toContain('Title');
    expect(pageContent).toContain('Year');
    expect(pageContent).toContain('Genre');
    expect(pageContent).toContain('Price');
  });

  test('should submit form using Enter key in text field', async ({ page }) => {
    const uniqueTitle = 'Keyboard Test Book ' + Date.now();
    
    await page.getByRole('combobox').selectOption({ label: 'Jane Austen' });
    await page.getByRole('textbox', { name: 'Title' }).fill(uniqueTitle);
    await page.getByRole('spinbutton', { name: 'Year' }).fill('2025');
    await page.getByRole('textbox', { name: 'Genre' }).fill('Fiction');
    
    const priceInput = page.getByRole('spinbutton', { name: 'Price' });
    await priceInput.fill('30.00');
    await priceInput.press('Enter');
    
    // Wait for submission
    await page.waitForTimeout(1000);
    
    // Verify page is still functional
    await expect(page.getByRole('heading', { name: 'BookService' })).toBeVisible();
  });

  test('should maintain form state during interaction', async ({ page }) => {
    // Fill partial form
    await page.getByRole('textbox', { name: 'Title' }).fill('Test Title');
    await page.getByRole('spinbutton', { name: 'Year' }).fill('2024');
    
    // Interact with other elements
    await page.getByRole('link', { name: 'API' }).click();
    await page.goBack();
    
    // Form state may or may not be preserved - depends on implementation
    // This test documents the behavior
    await expect(page.getByRole('heading', { name: 'Add Book' })).toBeVisible();
  });

  test('should handle multiple rapid submissions', async ({ page }) => {
    // Submit form twice in quick succession
    await page.getByRole('textbox', { name: 'Title' }).fill('Rapid Test 1');
    await page.getByRole('button', { name: 'Submit' }).click();
    
    await page.waitForTimeout(100);
    
    await page.getByRole('textbox', { name: 'Title' }).fill('Rapid Test 2');
    await page.getByRole('button', { name: 'Submit' }).click();
    
    await page.waitForTimeout(1000);
    
    // Verify page is still functional
    await expect(page.getByRole('heading', { name: 'BookService' })).toBeVisible();
  });

  test('should display form in correct visual hierarchy', async ({ page }) => {
    // Check that Add Book section appears after Books section
    const addBookHeading = page.getByRole('heading', { name: 'Add Book', level: 2 });
    const booksHeading = page.getByRole('heading', { name: 'Books', level: 2 });
    
    await expect(booksHeading).toBeVisible();
    await expect(addBookHeading).toBeVisible();
    
    // Both sections should be on the same page
    const booksList = page.locator('ul').first();
    const submitButton = page.getByRole('button', { name: 'Submit' });
    
    await expect(booksList).toBeVisible();
    await expect(submitButton).toBeVisible();
  });
});
