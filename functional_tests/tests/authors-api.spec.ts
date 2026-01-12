import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:50524';

test.describe('Authors API Tests', () => {
  let createdAuthorId: number;

  test('GET /api/Authors - should return all authors', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/Authors`);
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);
    
    const authors = await response.json();
    expect(Array.isArray(authors)).toBeTruthy();
    expect(authors.length).toBeGreaterThan(0);
    
    // Verify author structure
    expect(authors[0]).toHaveProperty('Id');
    expect(authors[0]).toHaveProperty('Name');
  });

  test('GET /api/Authors/{id} - should return a specific author', async ({ request }) => {
    // First get all authors to get a valid ID
    const authorsResponse = await request.get(`${BASE_URL}/api/Authors`);
    const authors = await authorsResponse.json();
    const authorId = authors[0].Id;
    
    // Get specific author
    const response = await request.get(`${BASE_URL}/api/Authors/${authorId}`);
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);
    
    const author = await response.json();
    expect(author.Id).toBe(authorId);
    expect(author).toHaveProperty('Name');
  });

  test('GET /api/Authors/{id} - should return 404 for non-existent author', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/Authors/99999`);
    
    expect(response.status()).toBe(404);
  });

  test('POST /api/Authors - should create a new author', async ({ request }) => {
    const newAuthor = {
      Name: 'Test Author ' + Date.now()
    };
    
    const response = await request.post(`${BASE_URL}/api/Authors`, {
      data: newAuthor,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(201);
    
    const createdAuthor = await response.json();
    expect(createdAuthor).toHaveProperty('Id');
    expect(createdAuthor.Name).toBe(newAuthor.Name);
    
    // Store the ID for potential cleanup
    createdAuthorId = createdAuthor.Id;
  });

  test('POST /api/Authors - should validate required fields', async ({ request }) => {
    const invalidAuthor = {
      // Missing required Name field
    };
    
    const response = await request.post(`${BASE_URL}/api/Authors`, {
      data: invalidAuthor,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    expect(response.ok()).toBeFalsy();
    expect([400, 500]).toContain(response.status());
  });

  test('PUT /api/Authors/{id} - should update an existing author', async ({ request }) => {
    // First create an author to update
    const newAuthor = {
      Name: 'Author to Update ' + Date.now()
    };
    
    const createResponse = await request.post(`${BASE_URL}/api/Authors`, {
      data: newAuthor,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const createdAuthor = await createResponse.json();
    const authorId = createdAuthor.Id;
    
    // Update the author
    const updatedAuthor = {
      Id: authorId,
      Name: 'Updated Author Name ' + Date.now()
    };
    
    const response = await request.put(`${BASE_URL}/api/Authors/${authorId}`, {
      data: updatedAuthor,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    expect([200, 204]).toContain(response.status());
    
    // Verify the update
    const getResponse = await request.get(`${BASE_URL}/api/Authors/${authorId}`);
    const author = await getResponse.json();
    expect(author.Name).toBe(updatedAuthor.Name);
  });

  test('PUT /api/Authors/{id} - should return 404 for non-existent author', async ({ request }) => {
    const updatedAuthor = {
      Id: 99999,
      Name: 'Non-existent Author'
    };
    
    const response = await request.put(`${BASE_URL}/api/Authors/99999`, {
      data: updatedAuthor,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    expect(response.status()).toBe(404);
  });

  test('DELETE /api/Authors/{id} - should delete an existing author', async ({ request }) => {
    // First create an author to delete
    const newAuthor = {
      Name: 'Author to Delete ' + Date.now()
    };
    
    const createResponse = await request.post(`${BASE_URL}/api/Authors`, {
      data: newAuthor,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const createdAuthor = await createResponse.json();
    const authorId = createdAuthor.Id;
    
    // Delete the author
    const response = await request.delete(`${BASE_URL}/api/Authors/${authorId}`);
    
    expect(response.ok()).toBeTruthy();
    expect([200, 204]).toContain(response.status());
    
    // Verify deletion
    const getResponse = await request.get(`${BASE_URL}/api/Authors/${authorId}`);
    expect(getResponse.status()).toBe(404);
  });

  test('DELETE /api/Authors/{id} - should return 404 for non-existent author', async ({ request }) => {
    const response = await request.delete(`${BASE_URL}/api/Authors/99999`);
    
    expect(response.status()).toBe(404);
  });

  test('GET /api/Authors - should return authors with correct content type', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/Authors`, {
      headers: {
        'Accept': 'application/json'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const contentType = response.headers()['content-type'];
    expect(contentType).toContain('application/json');
  });

  test('GET /api/Authors - should support XML format', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/Authors`, {
      headers: {
        'Accept': 'application/xml'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const contentType = response.headers()['content-type'];
    expect(contentType).toContain('xml');
  });
});
