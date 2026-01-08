import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:50524';

test.describe('BookService UI Workflow Tests', () => {
  
  test('should display initial page layout with all sections', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Verify navigation elements
    await expect(page.getByRole('link', { name: 'Application name' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Home' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'API' })).toBeVisible();
    
    // Verify main heading
    await expect(page.getByRole('heading', { name: 'BookService', level: 1 })).toBeVisible();
    
    // Verify Books section
    await expect(page.getByRole('heading', { name: 'Books', level: 2 })).toBeVisible();
    const booksList = page.locator('ul').first();
    await expect(booksList).toBeVisible();
    
    // Verify Add Book section
    await expect(page.getByRole('heading', { name: 'Add Book', level: 2 })).toBeVisible();
    
    // Verify all form elements are present
    await expect(page.getByRole('combobox')).toBeVisible();
    await expect(page.getByRole('textbox', { name: 'Title' })).toBeVisible();
    await expect(page.getByRole('spinbutton', { name: 'Year' })).toBeVisible();
    await expect(page.getByRole('textbox', { name: 'Genre' })).toBeVisible();
    await expect(page.getByRole('spinbutton', { name: 'Price' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Submit' })).toBeVisible();
  });

  test('should have 3 authors in dropdown and add a book successfully', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    
    // Verify dropdown has 3 authors - wait and then get options
    await page.waitForTimeout(500);
    const authorOptions = await page.evaluate(() => {
      const select = document.querySelector('select');
      if (!select) return [];
      return Array.from(select.options).map(opt => opt.textContent);
    });
    
    // At least 3 authors (baseline data), may have more from parallel tests
    expect(authorOptions.length).toBeGreaterThanOrEqual(3);
    expect(authorOptions).toContain('Jane Austen');
    expect(authorOptions).toContain('Charles Dickens');
    expect(authorOptions).toContain('Miguel de Cervantes');
    
    // Add a unique book
    const uniqueTitle = `Unique Book ${Date.now()}`;
    const uniqueGenre = `Genre_${Math.random().toString(36).substring(7)}`;
    const uniquePrice = (Math.random() * 50 + 10).toFixed(2);
    
    await page.getByRole('combobox').selectOption({ label: 'Jane Austen' });
    await page.getByRole('textbox', { name: 'Title' }).fill(uniqueTitle);
    await page.getByRole('spinbutton', { name: 'Year' }).fill('2025');
    await page.getByRole('textbox', { name: 'Genre' }).fill(uniqueGenre);
    await page.getByRole('spinbutton', { name: 'Price' }).fill(uniquePrice);
    
    // Submit the form
    await page.getByRole('button', { name: 'Submit' }).click();
    
    // Wait for page to update
    await page.waitForTimeout(1500);
    
    // Verify the book appears in the list
    const pageContent = await page.content();
    expect(pageContent).toContain(uniqueTitle);
  });

  test('should add 3 books with different authors and verify all appear in list', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Get initial book count
    const initialCount = await page.locator('li').count();
    
    // Book 1 - Jane Austen
    const book1Title = `JaneAusten_Book_${Date.now()}`;
    await page.getByRole('combobox').selectOption({ label: 'Jane Austen' });
    await page.getByRole('textbox', { name: 'Title' }).fill(book1Title);
    await page.getByRole('spinbutton', { name: 'Year' }).fill('2025');
    await page.getByRole('textbox', { name: 'Genre' }).fill(`Genre_A_${Math.random().toString(36).substring(7)}`);
    await page.getByRole('spinbutton', { name: 'Price' }).fill('25.99');
    await page.getByRole('button', { name: 'Submit' }).click();
    await page.waitForTimeout(1500);
    
    // Verify book 1 was added
    let pageContent = await page.content();
    expect(pageContent).toContain(book1Title);
    expect(pageContent).toContain('Jane Austen');
    
    // Book 2 - Charles Dickens
    const book2Title = `Dickens_Book_${Date.now()}`;
    await page.getByRole('combobox').selectOption({ label: 'Charles Dickens' });
    await page.getByRole('textbox', { name: 'Title' }).fill(book2Title);
    await page.getByRole('spinbutton', { name: 'Year' }).fill('2024');
    await page.getByRole('textbox', { name: 'Genre' }).fill(`Genre_B_${Math.random().toString(36).substring(7)}`);
    await page.getByRole('spinbutton', { name: 'Price' }).fill('32.50');
    await page.getByRole('button', { name: 'Submit' }).click();
    await page.waitForTimeout(1500);
    
    // Verify book 2 was added
    pageContent = await page.content();
    expect(pageContent).toContain(book2Title);
    expect(pageContent).toContain('Charles Dickens');
    
    // Book 3 - Miguel de Cervantes
    const book3Title = `Cervantes_Book_${Date.now()}`;
    await page.getByRole('combobox').selectOption({ label: 'Miguel de Cervantes' });
    await page.getByRole('textbox', { name: 'Title' }).fill(book3Title);
    await page.getByRole('spinbutton', { name: 'Year' }).fill('2023');
    await page.getByRole('textbox', { name: 'Genre' }).fill(`Genre_C_${Math.random().toString(36).substring(7)}`);
    await page.getByRole('spinbutton', { name: 'Price' }).fill('28.75');
    await page.getByRole('button', { name: 'Submit' }).click();
    await page.waitForTimeout(1500);
    
    // Verify book 3 was added
    pageContent = await page.content();
    expect(pageContent).toContain(book3Title);
    expect(pageContent).toContain('Miguel de Cervantes');
    
    // Verify all three books are in the list
    const finalCount = await page.locator('li').count();
    expect(finalCount).toBeGreaterThanOrEqual(initialCount + 3);
    
    // Verify all books and authors are present
    expect(pageContent).toContain(book1Title);
    expect(pageContent).toContain(book2Title);
    expect(pageContent).toContain(book3Title);
  });

  test('E2E: should create author and book via API and verify in UI', async ({ page, request }) => {
    // Generate unique identifiers using timestamp
    const timestamp = Date.now();
    const uniqueAuthorName = `E2E_Author_${timestamp}`;
    const uniqueBookTitle = `E2E_Book_${timestamp}`;
    const uniqueGenre = `E2E_Genre_${Math.random().toString(36).substring(2, 8)}`;
    const bookYear = 2026;
    const bookPrice = 49.99;

    // Step 1: Create a unique author via API
    const authorResponse = await request.post(`${BASE_URL}/api/Authors`, {
      data: {
        Name: uniqueAuthorName
      },
      headers: {
        'Content-Type': 'application/json'
      }
    });

    expect(authorResponse.status()).toBe(201);
    const createdAuthor = await authorResponse.json();
    expect(createdAuthor).toHaveProperty('Id');
    expect(createdAuthor.Name).toBe(uniqueAuthorName);
    const authorId = createdAuthor.Id;

    // Step 2: Create a unique book for this author via API
    const bookResponse = await request.post(`${BASE_URL}/api/Books`, {
      data: {
        Title: uniqueBookTitle,
        AuthorId: authorId,
        Year: bookYear,
        Genre: uniqueGenre,
        Price: bookPrice
      },
      headers: {
        'Content-Type': 'application/json'
      }
    });

    expect(bookResponse.status()).toBe(201);
    const createdBook = await bookResponse.json();
    expect(createdBook).toHaveProperty('Id');
    expect(createdBook.Title).toBe(uniqueBookTitle);

    // Step 3: Navigate to the UI and verify the data is visible
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // Verify the author appears in the dropdown
    const authorInDropdown = await page.evaluate((authorName) => {
      const select = document.querySelector('select');
      if (!select) return false;
      const options = Array.from(select.options);
      return options.some(opt => opt.textContent === authorName);
    }, uniqueAuthorName);
    expect(authorInDropdown).toBeTruthy();

    // Verify the book and author appear in the books list
    const pageContent = await page.content();
    expect(pageContent).toContain(uniqueBookTitle);
    expect(pageContent).toContain(uniqueAuthorName);
    
    // Verify the book is visible in the list
    const bookListItem = page.locator('li', { hasText: uniqueBookTitle });
    await expect(bookListItem).toBeVisible();
    await expect(bookListItem).toContainText(uniqueAuthorName);
  });
});
