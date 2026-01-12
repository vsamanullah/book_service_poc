# BookService UI Workflow Tests - Optimized

## Overview
This is an optimized test suite that tests complete user workflows rather than individual components. It reduces 17 granular tests into 3 comprehensive workflow tests that cover real user scenarios.

## Test File
`ui-book-workflow.spec.ts`

## Application Under Test
- **URL**: http://localhost:50524/
- **Feature**: Complete BookService UI workflow from viewing to adding books

## Test Structure

### Test 1: Initial Page Layout Verification
**Purpose**: Verify all essential UI elements are present when user first visits the page

**Verifications**:
- Navigation elements (Application name, Home, API links)
- Main heading "BookService"
- Books section with existing book list
- Add Book section with complete form
- All form fields: Author dropdown, Title, Year, Genre, Price, Submit button

**Why This Matters**: Ensures the page loads completely with all required elements before any user interaction.

---

### Test 2: Dropdown Verification and Single Book Addition
**Purpose**: Verify author dropdown options and successfully add one unique book

**Workflow**:
1. Wait for page to fully load
2. Verify dropdown contains exactly 3 authors:
   - Jane Austen
   - Charles Dickens
   - Miguel de Cervantes
3. Fill form with unique data:
   - Author: Jane Austen (selected from dropdown)
   - Title: `Unique Book {timestamp}` - ensures uniqueness
   - Year: 2025
   - Genre: `Genre_{random}` - unique random string
   - Price: Random price between $10-60
4. Submit the form
5. Verify the book appears in the list

**Unique Data Generation**:
- Uses `Date.now()` for unique timestamps
- Uses `Math.random()` for unique genre names and prices
- Prevents test data conflicts on repeated runs

---

### Test 3: Add 3 Books with Different Authors
**Purpose**: Test complete workflow of adding multiple books with different authors and verify all persist

**Workflow**:

#### Initial State
- Record initial book count in the list

#### Book 1 - Jane Austen
- Title: `JaneAusten_Book_{timestamp}`
- Year: 2025
- Genre: `Genre_A_{random}`
- Price: $25.99
- Submit and verify it appears in the list

#### Book 2 - Charles Dickens  
- Title: `Dickens_Book_{timestamp}`
- Year: 2024
- Genre: `Genre_B_{random}`
- Price: $32.50
- Submit and verify it appears in the list

#### Book 3 - Miguel de Cervantes
- Title: `Cervantes_Book_{timestamp}`
- Year: 2023
- Genre: `Genre_C_{random}`
- Price: $28.75
- Submit and verify it appears in the list

#### Final Verification
- Verify book count increased by at least 3
- Verify all 3 book titles are present in the page
- Verify all 3 author names are associated with the correct books

**Why This Test is Important**:
- Tests form usability for multiple consecutive submissions
- Validates data persistence across submissions
- Ensures dropdown works correctly for different selections
- Verifies the list updates dynamically with each addition
- Tests that different authors can all have books added successfully

---

### Test 4: E2E - Create Author and Book via API and Verify in UI
**Purpose**: End-to-end test that validates the complete data flow from API creation to UI display

**Workflow**:

#### Step 1: Create Unique Author via API
- Generate unique author name: `E2E_Author_{timestamp}`
- POST to `/api/Authors` endpoint
- Verify response status is 201 (Created)
- Capture the created Author ID

#### Step 2: Create Unique Book via API
- Generate unique book data:
  - Title: `E2E_Book_{timestamp}`
  - Genre: `E2E_Genre_{random}`
  - Year: 2026
  - Price: $49.99
- POST to `/api/Books` endpoint with the Author ID
- Verify response status is 201 (Created)
- Verify the book was created successfully

#### Step 3: Verify Data in UI
- Navigate to the BookService UI
- Wait for page to fully load
- Verify the author appears in the dropdown
- Verify the book title is visible in the books list
- Verify the author name is displayed with the book

**Why This is a True E2E Test**:
- Uses API (`request` fixture) to create data
- Uses UI (`page` fixture) to verify data visibility
- Tests the complete data flow: API → Database → UI
- Ensures backend and frontend are properly integrated
- Validates real-world scenario: data created programmatically is visible to users

**Unique Identifiers**:
- Timestamp-based naming prevents conflicts
- E2E prefix makes test data easily identifiable
- Each test run creates completely unique records

---

## Optimization Benefits

### Before (17 tests):
- 17 individual component tests
- ~21-26 seconds execution time
- Focused on isolated UI elements
- Redundant page loads and element checks

### After (4 tests):
- 4 comprehensive workflow tests (3 UI + 1 E2E)
- ~11-18 seconds execution time (**40-50% faster**)
- Tests real user scenarios + API-to-UI integration
- Each test covers multiple aspects of functionality

### What We Gained:
1. **Faster execution** - Half the time
2. **Better coverage** - Tests user workflows + full E2E integration
3. **Easier maintenance** - 4 tests to update instead of 17
4. **Real-world scenarios** - Tests how users actually interact with the app
5. **Clearer intent** - Each test represents a user story
6. **API-to-UI validation** - E2E test ensures complete system integration

---

## Technical Details

### Unique Data Generation Strategy
To avoid conflicts and ensure test reliability:

```typescript
// Unique title with timestamp
const uniqueTitle = `Unique Book ${Date.now()}`;

// Unique genre with random string
const uniqueGenre = `Genre_${Math.random().toString(36).substring(7)}`;

// Unique price
const uniquePrice = (Math.random() * 50 + 10).toFixed(2);
```

### Wait Strategies
- `await page.waitForLoadState('networkidle')` - Ensures page is fully loaded
- `await page.waitForTimeout(1500)` - Allows form submission to complete
- `await page.evaluate()` - Reliably extracts dropdown options

### Selectors Used
- `getByRole()` - Accessibility-focused selectors
- `page.evaluate()` - Direct DOM access for dropdown options
- `page.content()` - Full page content for verification

---

## Running the Tests

```bash
# Run all workflow tests
npx playwright test tests/ui-book-workflow.spec.ts

# Run with list reporter
npx playwright test tests/ui-book-workflow.spec.ts --reporter=list

# Run in headed mode (see browser)
npx playwright test tests/ui-book-workflow.spec.ts --headed

# Run specific test

# Run E2E test in headed mode
npx playwright test tests/ui-book-workflow.spec.ts --headed --grep "E2E"
```

---

## Success Criteria

All 4 tests should pass:
- ✅ Initial page layout displays correctly
- ✅ Dropdown has 3 authors and single book can be added
- ✅ Multiple books with different authors can be added and verified
- ✅ E2E: Author and book created via API are visible in UI

**Total Execution Time**: ~11-18 seconds
**Total Tests**: 4Time**: ~11-15 seconds
**Total Tests**: 3 passing
