# Book Service Functional Testing

This directory contains Playwright-based functional tests for the Book Service application, including both API testing and end-to-end UI testing.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Test Types](#test-types)
- [Test Cases](#test-cases)

---

## Overview

The functional testing suite includes:
- **API Testing** - RESTful API endpoint testing for Authors and Books
- **UI Testing** - End-to-end browser automation tests
- **Database Integration** - Database setup and teardown utilities
- **Cross-Environment Support** - Configurable environment testing

---

## Prerequisites

### Required Software
- **Node.js 16+** and **npm**
- **Playwright** browser automation framework
- **TypeScript** for test development
- **SQL Server** access for database utilities

### Browser Support
- Chromium (default)
- Firefox
- WebKit (Safari engine)

---

## Project Structure

```
functional_tests/
├── package.json                    # Dependencies and scripts
├── playwright.config.ts           # Playwright configuration
├── readme.md                      # This documentation
├── testcases/                     # Test case documentation
│   ├── authors-api.spec.md        # Authors API test cases
│   ├── books-api.spec.md          # Books API test cases
│   └── ui-book-workflow.spec.md   # UI workflow test cases
├── tests/                         # Test implementations
│   ├── authors-api.spec.ts        # Authors API tests
│   ├── books-api.spec.ts          # Books API tests
│   ├── ui-book-workflow.spec.ts   # UI workflow tests
│   └── bk/                        # Additional UI tests
│       ├── ui-add-book-form.spec.ts
│       ├── ui-add-book-form.spec.md
│       └── ui-book-list.spec.ts
└── utils/                         # Utility functions
    ├── database-setup.ts          # Database utilities
    └── README.md                  # Utils documentation
```

---

## Installation

### 1. Install Dependencies
```bash
# Navigate to functional tests directory
cd functional_tests

# Install npm packages
npm install

# Install Playwright browsers
npx playwright install
```

### 2. Configure Database Access
Ensure `../db_config.json` is configured with proper database credentials:

```json
{
  "environments": {
    "source": {
      "server": "your-server:port",
      "database": "BookService-Master",
      "username": "testuser",
      "password": "your-password",
      "driver": "ODBC Driver 18 for SQL Server"
    }
  }
}
```

---

## Configuration

### Playwright Configuration
Configuration is managed in [playwright.config.ts](playwright.config.ts):

```typescript
export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: { timeout: 5000 },
  reporter: [['html'], ['list']],
  use: {
    baseURL: 'https://10.134.77.68',
    ignoreHTTPSErrors: true,
    trace: 'on-first-retry'
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } }
  ]
});
```

---

## Running Tests

### All Tests
```bash
# Run all tests
npx playwright test

# Run with UI mode (interactive)
npx playwright test --ui

# Run with headed browsers (visible)
npx playwright test --headed
```

### Specific Test Files
```bash
# API Tests
npx playwright test tests/authors-api.spec.ts
npx playwright test tests/books-api.spec.ts

# UI Tests
npx playwright test tests/ui-book-workflow.spec.ts
npx playwright test tests/bk/ui-add-book-form.spec.ts
```

### Specific Test Cases
```bash
# Run specific test by name
npx playwright test --grep "should create new author"
npx playwright test --grep "E2E: should create author and book via API"

# Run UI workflow with visible browser
npx playwright test tests/ui-book-workflow.spec.ts --headed --workers=1
npx playwright test tests/ui-book-workflow.spec.ts --headed --grep "E2E: should create author and book via API and verify in UI"
```

### Cross-Browser Testing
```bash
# Run on specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Run on all browsers
npx playwright test --reporter=html
```

---

## Test Types

### 1. API Tests
Located in `tests/authors-api.spec.ts` and `tests/books-api.spec.ts`

**Features:**
- CRUD operations testing
- Request/response validation
- Error handling verification
- Data integrity checks

**Example:**
```typescript
test('should create new author', async ({ request }) => {
  const response = await request.post('/api/authors', {
    data: { name: 'Test Author' }
  });
  expect(response.status()).toBe(201);
});
```

### 2. UI Tests
Located in `tests/ui-book-workflow.spec.ts` and `tests/bk/`

**Features:**
- End-to-end user workflows
- Form validation testing
- Page navigation verification
- Cross-browser compatibility

**Example:**
```typescript
test('should add book via UI form', async ({ page }) => {
  await page.goto('/books/create');
  await page.fill('[data-testid="title"]', 'New Book');
  await page.click('[data-testid="submit"]');
  await expect(page.locator('.success')).toBeVisible();
});
```

### 3. Database Integration Tests
Uses utilities from `utils/database-setup.ts`

**Features:**
- Test data setup/teardown
- Database state verification
- Data consistency checks

---

## Test Cases

### Authors API Tests
See [testcases/authors-api.spec.md](testcases/authors-api.spec.md)
- GET /api/authors (list all)
- GET /api/authors/:id (get by ID)
- POST /api/authors (create)
- PUT /api/authors/:id (update)
- DELETE /api/authors/:id (delete)

### Books API Tests  
See [testcases/books-api.spec.md](testcases/books-api.spec.md)
- GET /api/books (list all)
- GET /api/books/:id (get by ID)  
- POST /api/books (create)
- PUT /api/books/:id (update)
- DELETE /api/books/:id (delete)

### UI Workflow Tests
See [testcases/ui-book-workflow.spec.md](testcases/ui-book-workflow.spec.md)
- Book creation workflow
- Author management UI
- Form validation testing
- Navigation and routing

---

## Reports and Debugging

### Test Reports
```bash
# Generate HTML report
npx playwright test --reporter=html

# View last report
npx playwright show-report
```

### Debugging Failed Tests
```bash
# Run with debug mode
npx playwright test --debug

# Run with trace viewer
npx playwright test --trace=on
```

### Screenshots and Videos
Failed tests automatically capture:
- Screenshots of failures
- Video recordings (on failure)
- Browser traces for debugging

---

## Continuous Integration

### Package Scripts
```json
{
  "scripts": {
    "test": "playwright test",
    "test:headed": "playwright test --headed",
    "test:ui": "playwright test --ui",
    "test:report": "playwright show-report"
  }
}
```

### Environment Variables
- `CI=true` - Enables CI mode
- `PLAYWRIGHT_HTML_REPORT` - Custom report location
- `PLAYWRIGHT_BROWSERS_PATH` - Custom browser location

---

## Troubleshooting

### Common Issues

**Browser Installation Failed**
```bash
npx playwright install --force
```

**Test Timeout Issues**
```bash
# Increase timeout in playwright.config.ts
timeout: 60000  // 60 seconds
```

**Database Connection Failed**
- Verify `../db_config.json` configuration
- Check network connectivity
- Confirm database credentials

**SSL/HTTPS Issues**
```typescript
// In playwright.config.ts
use: {
  ignoreHTTPSErrors: true
}
```
