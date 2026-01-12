# Authors API Test Suite

## Overview
This test suite validates all CRUD (Create, Read, Update, Delete) operations for the Authors API endpoints. It ensures the API handles valid requests, validates data, and returns appropriate error codes.

## Test File
`authors-api.spec.ts`

## Base URL
`http://localhost:50524`

## API Endpoints Tested
- `GET /api/Authors` - Get all authors
- `GET /api/Authors/{id}` - Get specific author by ID
- `POST /api/Authors` - Create new author
- `PUT /api/Authors/{id}` - Update existing author
- `DELETE /api/Authors/{id}` - Delete author

---

## Test Cases (11 Total)

### 1. GET /api/Authors - should return all authors
**Purpose**: Verify the endpoint returns a list of all authors

**Steps**:
1. Send GET request to `/api/Authors`
2. Verify response status is 200 OK
3. Verify response is an array
4. Verify array has at least one author
5. Verify author object has required properties: `Id`, `Name`

**Expected Result**: 
- Status: 200
- Response: Array of author objects

---

### 2. GET /api/Authors/{id} - should return a specific author
**Purpose**: Verify retrieving a single author by ID

**Steps**:
1. First, get all authors to obtain a valid ID
2. Send GET request to `/api/Authors/{validId}`
3. Verify response status is 200 OK
4. Verify returned author has correct ID
5. Verify author has `Name` property

**Expected Result**:
- Status: 200
- Response: Author object with matching ID

---

### 3. GET /api/Authors/{id} - should return 404 for non-existent author
**Purpose**: Verify proper error handling for invalid author ID

**Steps**:
1. Send GET request to `/api/Authors/99999` (non-existent ID)
2. Verify response status is 404 Not Found

**Expected Result**:
- Status: 404

---

### 4. POST /api/Authors - should create a new author
**Purpose**: Verify successful author creation

**Steps**:
1. Prepare new author data with unique name (using timestamp)
2. Send POST request with author data
3. Verify response status is 201 Created
4. Verify response contains new author with `Id`
5. Verify `Name` matches the sent data

**Request Body**:
```json
{
  "Name": "Test Author {timestamp}"
}
```

**Expected Result**:
- Status: 201
- Response: Created author with ID

---

### 5. POST /api/Authors - should validate required fields
**Purpose**: Verify API validates required fields

**Steps**:
1. Send POST request with empty/invalid data (missing `Name`)
2. Verify response status is 400 or 500 (validation error)

**Request Body**:
```json
{}
```

**Expected Result**:
- Status: 400 or 500 (validation error)

---

### 6. PUT /api/Authors/{id} - should update an existing author
**Purpose**: Verify successful author update

**Steps**:
1. Create a new author via POST
2. Prepare updated author data with new unique name
3. Send PUT request to `/api/Authors/{id}` with updated data
4. Verify response status is 200 or 204
5. Verify changes by sending GET request
6. Verify name was updated successfully

**Request Body**:
```json
{
  "Id": 123,
  "Name": "Updated Author Name {timestamp}"
}
```

**Expected Result**:
- Status: 200 or 204
- GET verification shows updated name

---

### 7. PUT /api/Authors/{id} - should return 404 for non-existent author
**Purpose**: Verify proper error handling when updating non-existent author

**Steps**:
1. Send PUT request to `/api/Authors/99999` (non-existent ID)
2. Include valid author data in body
3. Verify response status is 404 Not Found

**Expected Result**:
- Status: 404

---

### 8. DELETE /api/Authors/{id} - should delete an existing author
**Purpose**: Verify successful author deletion

**Steps**:
1. Create a new author via POST
2. Send DELETE request to `/api/Authors/{id}`
3. Verify response status is 200 or 204
4. Verify deletion by sending GET request to same ID
5. Verify GET returns 404 (author no longer exists)

**Expected Result**:
- Status: 200 or 204
- Subsequent GET returns 404

---

### 9. DELETE /api/Authors/{id} - should return 404 for non-existent author
**Purpose**: Verify proper error handling when deleting non-existent author

**Steps**:
1. Send DELETE request to `/api/Authors/99999` (non-existent ID)
2. Verify response status is 404 Not Found

**Expected Result**:
- Status: 404

---

### 10. GET /api/Authors - should return authors with correct content type
**Purpose**: Verify API returns proper JSON content type

**Steps**:
1. Send GET request with `Accept: application/json` header
2. Verify response status is 200 OK
3. Verify `Content-Type` header contains `application/json`

**Expected Result**:
- Status: 200
- Content-Type: application/json

---

### 11. GET /api/Authors - should support XML format
**Purpose**: Verify API supports XML content negotiation

**Steps**:
1. Send GET request with `Accept: application/xml` header
2. Verify response status is 200 OK
3. Verify `Content-Type` header contains `xml`

**Expected Result**:
- Status: 200
- Content-Type: application/xml or text/xml

---

## Data Model

### Author Object
```json
{
  "Id": 1,
  "Name": "Jane Austen"
}
```

**Properties**:
- `Id` (integer): Unique identifier for the author
- `Name` (string): Author's full name

---

## Test Strategy

### Unique Data Generation
Uses timestamps to ensure unique author names:
```typescript
const newAuthor = {
  Name: 'Test Author ' + Date.now()
};
```

### Test Isolation
- Each test that creates data uses unique names
- Tests that modify data create their own test records
- No dependencies between tests
- Tests can run in parallel

### Error Handling
- Tests verify both success and failure scenarios
- 404 errors tested for non-existent resources
- Validation errors tested with invalid data

---

## Running the Tests

```bash
# Run all Authors API tests
npx playwright test tests/authors-api.spec.ts

# Run with list reporter
npx playwright test tests/authors-api.spec.ts --reporter=list

# Run specific test
npx playwright test tests/authors-api.spec.ts -g "should create a new author"

# Run in debug mode
npx playwright test tests/authors-api.spec.ts --debug
```

---

## Success Criteria

All 11 tests should pass:
- ✅ GET all authors (1 test)
- ✅ GET specific author (2 tests - success + 404)
- ✅ POST create author (2 tests - success + validation)
- ✅ PUT update author (2 tests - success + 404)
- ✅ DELETE author (2 tests - success + 404)
- ✅ Content negotiation (2 tests - JSON + XML)

**Expected Execution Time**: ~1-2 seconds
**Total Tests**: 11 passing
