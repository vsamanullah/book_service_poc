import { request } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:50524';

interface Author {
  Id: number;
  Name: string;
}

interface Book {
  Id: number;
  Title: string;
  Year: number;
  Price: number;
  Genre: string;
  AuthorId: number;
}

/**
 * Check if the application is running
 */
async function checkApplicationRunning(baseUrl: string): Promise<boolean> {
  try {
    const context = await request.newContext();
    const response = await context.get(`${baseUrl}/api/Authors`);
    await context.dispose();
    return response.ok();
  } catch (error) {
    return false;
  }
}

/**
 * Reset and seed the database with fresh test data
 */
export async function resetDatabase(baseUrl: string = BASE_URL): Promise<void> {
  console.log('\n========================================');
  console.log('Database Reset and Seed');
  console.log('========================================\n');

  const context = await request.newContext();

  try {
    // Step 1: Check if application is running
    console.log('  [1/5] Checking if application is running...');
    if (!await checkApplicationRunning(baseUrl)) {
      throw new Error(`Application is not running at ${baseUrl}`);
    }
    console.log(`  [OK] Application is running on ${baseUrl}\n`);

    // Step 2: Delete all Books
    console.log('  [2/5] Deleting all Books...');
    try {
      const booksResponse = await context.get(`${baseUrl}/api/Books`);
      const books: Book[] = await booksResponse.json();
      
      for (const book of books) {
        await context.delete(`${baseUrl}/api/Books/${book.Id}`);
        console.log(`    Deleted Book ID: ${book.Id} - ${book.Title}`);
      }
      console.log(`  [OK] Deleted ${books.length} books\n`);
    } catch (error) {
      console.log(`  [WARNING] Error deleting books: ${error}\n`);
    }

    // Step 3: Delete all Authors
    console.log('  [3/5] Deleting all Authors...');
    try {
      const authorsResponse = await context.get(`${baseUrl}/api/Authors`);
      const authors: Author[] = await authorsResponse.json();
      
      for (const author of authors) {
        await context.delete(`${baseUrl}/api/Authors/${author.Id}`);
        console.log(`    Deleted Author ID: ${author.Id} - ${author.Name}`);
      }
      console.log(`  [OK] Deleted ${authors.length} authors\n`);
    } catch (error) {
      console.log(`  [WARNING] Error deleting authors: ${error}\n`);
    }

    // Step 4: Create 3 Authors (matching test expectations)
    console.log('  [4/5] Creating 3 new Authors...');
    const authorNames = [
      'Jane Austen',
      'Charles Dickens',
      'Miguel de Cervantes'
    ];

    const createdAuthors: Author[] = [];
    for (const name of authorNames) {
      try {
        const response = await context.post(`${baseUrl}/api/Authors`, {
          data: { Name: name },
          headers: { 'Content-Type': 'application/json' }
        });
        const author: Author = await response.json();
        createdAuthors.push(author);
        console.log(`    [OK] Created Author ID: ${author.Id} - ${author.Name}`);
      } catch (error) {
        console.log(`    [X] Failed to create author ${name}: ${error}`);
      }
    }
    console.log(`  [OK] Created ${createdAuthors.length} authors\n`);

    // Step 5: Create 4 Books (matching test expectations)
    console.log('  [5/5] Creating 4 new Books...');
    if (createdAuthors.length < 3) {
      console.log('  [WARNING] Not enough authors created, skipping book creation\n');
      return;
    }

    const booksData = [
      {
        Title: 'Pride and Prejudice',
        Year: 1813,
        Price: 12.99,
        Genre: 'Romance',
        AuthorId: createdAuthors[0].Id
      },
      {
        Title: 'Northanger Abbey',
        Year: 1817,
        Price: 11.99,
        Genre: 'Gothic',
        AuthorId: createdAuthors[0].Id
      },
      {
        Title: 'David Copperfield',
        Year: 1850,
        Price: 14.99,
        Genre: 'Fiction',
        AuthorId: createdAuthors[1].Id
      },
      {
        Title: 'Don Quixote',
        Year: 1605,
        Price: 16.99,
        Genre: 'Adventure',
        AuthorId: createdAuthors[2].Id
      }
    ];

    const createdBooks: Book[] = [];
    for (const bookData of booksData) {
      try {
        const response = await context.post(`${baseUrl}/api/Books`, {
          data: bookData,
          headers: { 'Content-Type': 'application/json' }
        });
        const book: Book = await response.json();
        createdBooks.push(book);
        console.log(`    [OK] Created Book ID: ${book.Id} - ${book.Title} (Author: ${book.AuthorId})`);
      } catch (error) {
        console.log(`    [X] Failed to create book ${bookData.Title}: ${error}`);
      }
    }
    console.log(`  [OK] Created ${createdBooks.length} books\n`);

    console.log('========================================');
    console.log('Database Reset Complete!');
    console.log('========================================\n');

  } finally {
    await context.dispose();
  }
}

/**
 * Standalone script execution
 */
if (require.main === module) {
  resetDatabase()
    .then(() => {
      console.log('Setup completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('Setup failed:', error);
      process.exit(1);
    });
}

/**
 * Global setup function for Playwright
 */
export default async function globalSetup() {
  await resetDatabase();
}
