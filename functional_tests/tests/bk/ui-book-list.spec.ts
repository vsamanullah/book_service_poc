import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:50524';

test.describe('BookService UI Tests - Book List Display', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    // Wait for books to load by waiting for the book list to be populated
    await page.waitForSelector('.list-unstyled li', { timeout: 10000 }).catch(() => {
      // If no books found, that's ok for some tests
    });
  });

  test('should display the page title', async ({ page }) => {
    await expect(page).toHaveTitle('Home Page');
  });

  test('should display the BookService heading', async ({ page }) => {
    const heading = page.getByRole('heading', { name: 'BookService', level: 1 });
    await expect(heading).toBeVisible();
  });

  test('should display the Books section heading', async ({ page }) => {
    const heading = page.getByRole('heading', { name: 'Books', level: 2 });
    await expect(heading).toBeVisible();
  });

  test('should display a list of books', async ({ page }) => {
    // Check if books list is visible
    const booksList = page.locator('ul').first();
    await expect(booksList).toBeVisible();
    
    // Check if there are book items
    const bookItems = page.locator('li');
    const count = await bookItems.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should display book details with author and title', async ({ page }) => {
    // Wait for books to load with strong tags (author names) inside the book list
    await page.waitForSelector('.list-unstyled li strong', { timeout: 10000 });
    
    // Wait a bit more for knockout binding to complete
    await page.waitForTimeout(500);
    
    // Verify first book structure (using more specific selector for book list)
    const firstBook = page.locator('.list-unstyled li').first();
    await expect(firstBook).toBeVisible();
    
    // Check that text content includes author and title
    const bookText = await firstBook.textContent();
    expect(bookText).toBeTruthy();
    expect(bookText).toContain(':');
    expect(bookText).toContain('Details');
    
    // Verify strong tag exists in the first book (author name)
    const strongCount = await firstBook.locator('strong').count();
    expect(strongCount).toBeGreaterThan(0);
  });

  test('should display specific books from initial data', async ({ page }) => {
    // Wait for books to load
    await page.waitForSelector('.list-unstyled li', { timeout: 10000 });
    
    const pageContent = await page.content();
    
    // Verify specific books are displayed
    expect(pageContent).toContain('Jane Austen');
    expect(pageContent).toContain('Pride and Prejudice');
    expect(pageContent).toContain('Northanger Abbey');
    expect(pageContent).toContain('Charles Dickens');
    expect(pageContent).toContain('David Copperfield');
    expect(pageContent).toContain('Miguel de Cervantes');
    expect(pageContent).toContain('Don Quixote');
  });

  test('should have Details links for each book', async ({ page }) => {
    // Wait for books to load
    await page.waitForSelector('.list-unstyled li', { timeout: 10000 });
    
    const detailsLinks = page.getByRole('link', { name: 'Details' });
    const count = await detailsLinks.count();
    
    expect(count).toBeGreaterThan(0);
    
    // Verify first details link is visible
    await expect(detailsLinks.first()).toBeVisible();
  });

  test('should have navigation menu', async ({ page }) => {
    // Check for navigation links
    const homeLink = page.getByRole('link', { name: 'Home' });
    const apiLink = page.getByRole('link', { name: 'API' });
    
    await expect(homeLink).toBeVisible();
    await expect(apiLink).toBeVisible();
  });

  test('should navigate to API help page', async ({ page }) => {
    await page.getByRole('link', { name: 'API' }).click();
    
    await expect(page).toHaveURL(/.*Help/);
    await expect(page).toHaveTitle('ASP.NET Web API Help Page');
    
    const heading = page.getByRole('heading', { name: 'ASP.NET Web API Help Page', level: 1 });
    await expect(heading).toBeVisible();
  });

  test('should display API documentation tables', async ({ page }) => {
    await page.getByRole('link', { name: 'API' }).click();
    
    // Check for Books API section
    const booksHeading = page.getByRole('heading', { name: 'Books', level: 2 });
    await expect(booksHeading).toBeVisible();
    
    // Check for Authors API section
    const authorsHeading = page.getByRole('heading', { name: 'Authors', level: 2 });
    await expect(authorsHeading).toBeVisible();
    
    // Check for API endpoint links
    await expect(page.getByRole('link', { name: 'GET api/Books', exact: true })).toBeVisible();
    await expect(page.getByRole('link', { name: 'POST api/Books' })).toBeVisible();
  });

  test('should have application footer', async ({ page }) => {
    const footer = page.locator('footer');
    await expect(footer).toBeVisible();
    
    const footerText = await footer.textContent();
    expect(footerText).toContain('© 2026');
    expect(footerText).toContain('My ASP.NET Application');
  });

  test('should display Application name link', async ({ page }) => {
    const appNameLink = page.getByRole('link', { name: 'Application name' });
    await expect(appNameLink).toBeVisible();
    
    // Click it to ensure it navigates properly
    await appNameLink.click();
    await expect(page).toHaveURL(BASE_URL + '/');
  });

  test('should maintain page layout responsiveness', async ({ page }) => {
    // Test default viewport
    await expect(page.getByRole('heading', { name: 'BookService' })).toBeVisible();
    
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.getByRole('heading', { name: 'BookService' })).toBeVisible();
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.getByRole('heading', { name: 'BookService' })).toBeVisible();
  });

  test('should load without JavaScript errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    
    expect(errors).toHaveLength(0);
  });
});
