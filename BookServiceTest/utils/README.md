# Database Setup Utility

## Overview

This utility provides automated database reset and seeding functionality for the BookService test suite. It ensures a clean, consistent state before each test run by:

1. Clearing all existing books
2. Clearing all existing authors  
3. Creating 3 baseline authors (Jane Austen, Charles Dickens, Miguel de Cervantes)
4. Creating 4 baseline books

## Usage

### Automatic Setup (Recommended)

The database setup runs automatically before all tests via Playwright's `globalSetup` configuration:

```bash
npm test
# or
npm run test:headed
```

### Manual Setup

You can also run the setup script manually:

```bash
npm run setup:db
```

Or directly:

```bash
npx ts-node utils/database-setup.ts
```

### In Test Files

You can also import and use the utility in individual test files for per-test-suite setup:

```typescript
import { resetDatabase } from '../utils/database-setup';

describe('My Test Suite', () => {
  beforeAll(async () => {
    await resetDatabase();
  });
  
  // your tests...
});
```

## Configuration

The base URL can be configured via environment variable:

```bash
BASE_URL=http://localhost:50524 npm test
```

Default: `http://localhost:50524`

## Test Data Created

### Authors (3)
- **Jane Austen** (ID varies)
- **Charles Dickens** (ID varies)
- **Miguel de Cervantes** (ID varies)

### Books (4)
- **Pride and Prejudice** by Jane Austen (1813, Romance, $12.99)
- **Northanger Abbey** by Jane Austen (1817, Gothic, $11.99)
- **David Copperfield** by Charles Dickens (1850, Fiction, $14.99)
- **Don Quixote** by Miguel de Cervantes (1605, Adventure, $16.99)

## Troubleshooting

### Application Not Running

If you see errors about the application not being available:

```
Application is not running at http://localhost:50524
```

Make sure the BookService application is running before executing tests.

### Deletion Warnings

If you see warnings during deletion, it usually means the database was already clean:

```
[WARNING] Error deleting books: ...
```

This is normal and can be ignored.

### Test Failures Due to Data Inconsistency

If tests still fail due to unexpected data:

1. Manually run the setup: `npm run setup:db`
2. Check if the application is using a different database
3. Verify no other tests are running in parallel modifying the data

## Implementation Details

The utility uses Playwright's `request` context to make API calls directly to the BookService endpoints without launching a browser. This makes the setup fast and reliable.

## Notes

- The setup deletes **all** books and authors before seeding
- IDs are auto-generated and will vary between runs
- Tests should not rely on specific ID values
- For test isolation, consider using unique data in each test that won't conflict with baseline data
