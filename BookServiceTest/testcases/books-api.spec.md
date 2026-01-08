# Books API Test Suite

## Overview
This test suite validates all CRUD (Create, Read, Update, Delete) operations for the Books API endpoints. It ensures the API handles valid requests, validates data, and returns appropriate error codes for book management.

## Test File
`books-api.spec.ts`

## Base URL
`http://localhost:50524`

## API Endpoints Tested
- `GET /api/Books` - Get all books
- `GET /api/Books/{id}` - Get specific book by ID
- `POST /api/Books` - Create new book
- `PUT /api/Books/{id}` - Update existing book
- `DELETE /api/Books/{id}` - Delete book

---

## Test Cases (11 Total)

### 1. GET /api/Books - should return all books
**Purpose**: Verify the endpoint returns a list of all books

**Steps**:
1. Send GET request to `/api/Books`
2. Verify response status is 200 OK
3. Verify response is an array
4. Verify array has at least one book
5. Verify book object has required properties: `Id`, `Title`, `AuthorName`

**Expected Result**: 
- Status: 200
- Response: Array of book objects with author information

---

### 2. GET /api/Books/{id} - should return a specific book
**Purpose**: Verify retrieving a single book by ID

**Steps**:
1. First, get all books to obtain a valid ID
2. Send GET request to `/api/Books/{validId}`
3. Verify response status is 200 OK
4. Verify returned book has correct ID
5. Verify book has `Title` and `AuthorName` properties

**Expected Result**:
- Status: 200
- Response: Book object with matching ID

---

### 3. GET /api/Books/{id} - should return 404 for non-existent book
**Purpose**: Verify proper error handling for invalid book ID

**Steps**:
1. Send GET request to `/api/Books/99999` (non-existent ID)
2. Verify response status is 404 Not Found

**Expected Result**:
- Status: 404

---

### 4. POST /api/Books - should create a new book
**Purpose**: Verify successful book creation

**Steps**:
1. Prepare new book data with all required fields
2. Send POST request with book data
3. Verify response status is 201 Created
4. Verify response contains new book with `Id`
5. Verify `Title` matches the sent data

**Request Body**:
```json
{
  "Title": "Test Book",
  "AuthorId": 1,
  "Year": 2025,
  "Genre": "Fiction",
  "Price": 29.99
}
```

**Expected Result**:
- Status: 201
- Response: Created book with ID

---

### 5. POST /api/Books - should validate required fields
**Purpose**: Verify API validates required fields

**Steps**:
1. Send POST request with incomplete data (missing required fields)
2. Verify response status is 400 or 500 (validation error)

**Request Body**:
```json
{
  "Genre": "Fiction"
}
```

**Expected Result**:
- Status: 400 or 500 (validation error)

---

### 6. PUT /api/Books/{id} - should update an existing book
**Purpose**: Verify successful book update

**Steps**:
1. Create a new book via POST
2. Prepare updated book data with modified values
3. Send PUT request to `/api/Books/{id}` with updated data
4. Verify response status is 200 or 204
5. Verify changes by sending GET request
6. Verify all fields were updated successfully

**Request Body**:
```json
{
  "Id": 123,
  "Title": "Updated Book Title",
  "AuthorId": 2,
  "Year": 2025,
  "Genre": "Comedy",
  "Price": 35.00
}
```

**Expected Result**:
- Status: 200 or 204
- GET verification shows updated values

---

### 7. PUT /api/Books/{id} - should return 404 for non-existent book
**Purpose**: Verify proper error handling when updating non-existent book

**Steps**:
1. Send PUT request to `/api/Books/99999` (non-existent ID)
2. Include valid book data in body
3. Verify response status is 404 Not Found

**Expected Result**:
- Status: 404

---

### 8. DELETE /api/Books/{id} - should delete an existing book
**Purpose**: Verify successful book deletion

**Steps**:
1. Create a new book via POST
2. Send DELETE request to `/api/Books/{id}`
3. Verify response status is 200 or 204
4. Verify deletion by sending GET request to same ID
5. Verify GET returns 404 (book no longer exists)

**Expected Result**:
- Status: 200 or 204
- Subsequent GET returns 404

---

### 9. DELETE /api/Books/{id} - should return 404 for non-existent book
**Purpose**: Verify proper error handling when deleting non-existent book

**Steps**:
1. Send DELETE request to `/api/Books/99999` (non-existent ID)
2. Verify response status is 404 Not Found

**Expected Result**:
- Status: 404

---

### 10. GET /api/Books - should return books with correct content type
**Purpose**: Verify API returns proper JSON content type

**Steps**:
1. Send GET request with `Accept: application/json` header
2. Verify response status is 200 OK
3. Verify `Content-Type` header contains `application/json`

**Expected Result**:
- Status: 200
- Content-Type: application/json

---

## Data Model

### Book Object (Response DTO)
```json
{
  "Id": 1,
  "Title": "Pride and Prejudice",
  "AuthorName": "Jane Austen"
}
```

### Book Object (Request)
```json
{
  "Id": 1,
  "Title": "Pride and Prejudice",
  "AuthorId": 1,
  "Year": 1813,
  "Genre": "Romance",
  "Price": 29.99
}
```

**Properties**:
- `Id` (integer): Unique identifier for the book
- `Title` (string): Book title - **Required**
- `AuthorId` (integer): Foreign key to Author - **Required**
- `AuthorName` (string): Author's name (in response only)
- `Year` (integer): Publication year
- `Genre` (string): Book genre/category
- `Price` (decimal): Book price

---

## Test Strategy

### Test Data
- Uses generic test values that don't conflict
- Each creation test uses unique or disposable data
- Tests clean up by verifying deletion

### Test Isolation
- Each test that creates data performs its own cleanup or uses unique identifiers
- No dependencies between tests
- Tests can run in parallel safely

### Error Handling
- Tests verify both success and failure scenarios
- 404 errors tested for non-existent resources
- Validation errors tested with incomplete data

### Verification Strategy
- Create → Verify via GET
- Update → Verify changes via GET
- Delete → Verify 404 via GET

---

## Running the Tests

```bash
# Run all Books API tests
npx playwright test tests/books-api.spec.ts

# Run with list reporter
npx playwright test tests/books-api.spec.ts --reporter=list

# Run specific test
npx playwright test tests/books-api.spec.ts -g "should create a new book"

# Run in debug mode
npx playwright test tests/books-api.spec.ts --debug

# Run both API test suites
npx playwright test tests/books-api.spec.ts tests/authors-api.spec.ts
```

---

## Success Criteria

All 11 tests should pass:
- ✅ GET all books (2 tests - list + content type)
- ✅ GET specific book (2 tests - success + 404)
- ✅ POST create book (2 tests - success + validation)
- ✅ PUT update book (2 tests - success + 404)
- ✅ DELETE book (2 tests - success + 404)

**Expected Execution Time**: ~1-2 seconds
**Total Tests**: 11 passing

---

## API Integration Notes

### Author Relationship
- Books reference authors via `AuthorId` field
- Response includes `AuthorName` for convenience
- Must use valid `AuthorId` from existing authors
- Common author IDs used in tests: 1 (Jane Austen), 2 (Charles Dickens)

### Data Persistence
- All data persists in the application's data store
- Multiple test runs will accumulate books
- Consider database cleanup between full test runs if needed
