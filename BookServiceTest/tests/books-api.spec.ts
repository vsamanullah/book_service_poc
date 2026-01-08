import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:50524';

test.describe('Books API Tests', () => {
  let createdBookId: number;

  test('GET /api/Books - should return all books', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/Books`);
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);
    
    const books = await response.json();
    expect(Array.isArray(books)).toBeTruthy();
    expect(books.length).toBeGreaterThan(0);
    
    // Verify book structure
    expect(books[0]).toHaveProperty('Id');
    expect(books[0]).toHaveProperty('Title');
    expect(books[0]).toHaveProperty('AuthorName');
  });

  test('GET /api/Books/{id} - should return a specific book', async ({ request }) => {
    // First get all books to get a valid ID
    const booksResponse = await request.get(`${BASE_URL}/api/Books`);
    const books = await booksResponse.json();
    const bookId = books[0].Id;
    
    // Get specific book
    const response = await request.get(`${BASE_URL}/api/Books/${bookId}`);
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);
    
    const book = await response.json();
    expect(book.Id).toBe(bookId);
    expect(book).toHaveProperty('Title');
    expect(book).toHaveProperty('AuthorName');
  });

  test('GET /api/Books/{id} - should return 404 for non-existent book', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/Books/99999`);
    
    expect(response.status()).toBe(404);
  });

  test('POST /api/Books - should create a new book', async ({ request }) => {
    // Get a valid author ID first
    const authorsResponse = await request.get(`${BASE_URL}/api/Authors`);
    const authors = await authorsResponse.json();
    const validAuthorId = authors[0].Id;
    
    const newBook = {
      Title: 'Test Book',
      AuthorId: validAuthorId,
      Year: 2025,
      Genre: 'Fiction',
      Price: 29.99
    };
    
    const response = await request.post(`${BASE_URL}/api/Books`, {
      data: newBook,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(201);
    
    const createdBook = await response.json();
    expect(createdBook).toHaveProperty('Id');
    expect(createdBook.Title).toBe(newBook.Title);
    
    // Store the ID for cleanup
    createdBookId = createdBook.Id;
  });

  test('POST /api/Books - should validate required fields', async ({ request }) => {
    const invalidBook = {
      // Missing required fields
      Genre: 'Fiction'
    };
    
    const response = await request.post(`${BASE_URL}/api/Books`, {
      data: invalidBook,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    expect(response.ok()).toBeFalsy();
    expect([400, 500]).toContain(response.status());
  });

  test('PUT /api/Books/{id} - should update an existing book', async ({ request }) => {
    // Get a valid author ID first
    const authorsResponse = await request.get(`${BASE_URL}/api/Authors`);
    const authors = await authorsResponse.json();
    const validAuthorId = authors[0].Id;
    
    // First create a book to update
    const newBook = {
      Title: 'Book to Update',
      AuthorId: validAuthorId,
      Year: 2024,
      Genre: 'Drama',
      Price: 25.00
    };
    
    const createResponse = await request.post(`${BASE_URL}/api/Books`, {
      data: newBook,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const createdBook = await createResponse.json();
    const bookId = createdBook.Id;
    
    // Get second author for update (or use first if only one exists)
    const updateAuthorId = authors.length > 1 ? authors[1].Id : authors[0].Id;
    
    // Update the book
    const updatedBook = {
      Id: bookId,
      Title: 'Updated Book Title',
      AuthorId: updateAuthorId,
      Year: 2025,
      Genre: 'Comedy',
      Price: 35.00
    };
    
    const response = await request.put(`${BASE_URL}/api/Books/${bookId}`, {
      data: updatedBook,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    expect([200, 204]).toContain(response.status());
    
    // Verify the update
    const getResponse = await request.get(`${BASE_URL}/api/Books/${bookId}`);
    const book = await getResponse.json();
    expect(book.Title).toBe('Updated Book Title');
  });

  test('PUT /api/Books/{id} - should return 404 for non-existent book', async ({ request }) => {
    const updatedBook = {
      Id: 99999,
      Title: 'Non-existent Book',
      AuthorId: 1,
      Year: 2025,
      Genre: 'Fiction',
      Price: 20.00
    };
    
    const response = await request.put(`${BASE_URL}/api/Books/99999`, {
      data: updatedBook,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    expect(response.status()).toBe(404);
  });

  test('DELETE /api/Books/{id} - should delete an existing book', async ({ request }) => {
    // Get a valid author ID first
    const authorsResponse = await request.get(`${BASE_URL}/api/Authors`);
    const authors = await authorsResponse.json();
    const validAuthorId = authors[0].Id;
    
    // First create a book to delete
    const newBook = {
      Title: 'Book to Delete',
      AuthorId: validAuthorId,
      Year: 2024,
      Genre: 'Thriller',
      Price: 22.00
    };
    
    const createResponse = await request.post(`${BASE_URL}/api/Books`, {
      data: newBook,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const createdBook = await createResponse.json();
    const bookId = createdBook.Id;
    
    // Delete the book
    const response = await request.delete(`${BASE_URL}/api/Books/${bookId}`);
    
    expect(response.ok()).toBeTruthy();
    expect([200, 204]).toContain(response.status());
    
    // Verify deletion
    const getResponse = await request.get(`${BASE_URL}/api/Books/${bookId}`);
    expect(getResponse.status()).toBe(404);
  });

  test('DELETE /api/Books/{id} - should return 404 for non-existent book', async ({ request }) => {
    const response = await request.delete(`${BASE_URL}/api/Books/99999`);
    
    expect(response.status()).toBe(404);
  });

  test('GET /api/Books - should return books with correct content type', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/Books`, {
      headers: {
        'Accept': 'application/json'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const contentType = response.headers()['content-type'];
    expect(contentType).toContain('application/json');
  });
});
