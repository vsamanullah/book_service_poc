# Book Service API - Performance Test Cases

## Overview
This document describes the performance test suite for the Book Service RESTful API. The tests validate the performance, scalability, and response times of all CRUD operations for Authors and Books endpoints under various load conditions.

## Test Environment
- **Base URL**: `http(s)://<ip>:port`
- **Target APIs**: `/api/Authors` and `/api/Books`
- **Testing Tool**: Apache JMeter 5.6.2
- **Profiling Tool**: Custom Python script with system monitoring

---

## Authors API Test Cases

### Test Case 01: GET All Authors
**File**: `01_Authors_GET_All.jmx`

**Objective**: Test the performance of retrieving all authors from the database

**Test Configuration**:
- **Virtual Users**: 50 concurrent threads
- **Ramp-up Time**: 10 seconds
- **Test Duration**: 300 seconds (5 minutes)
- **Loop**: Infinite loop during test duration

**Endpoint**: `GET /api/Authors`

**Expected Response**:
- Status Code: 200 OK
- Response Time: < 500ms (target)
- Content Type: application/json

**Success Criteria**:
- All requests return 200 status code
- Response times are within acceptable limits
- No server errors during sustained load

---

### Test Case 02: GET Author by ID
**File**: `02_Authors_GET_ById.jmx`

**Objective**: Test the performance of retrieving a specific author by ID

**Test Configuration**:
- **Virtual Users**: 50 concurrent threads
- **Ramp-up Time**: 10 seconds
- **Test Duration**: 300 seconds (5 minutes)
- **Data Source**: `author_ids.csv` - Contains valid author IDs

**Endpoint**: `GET /api/Authors/{id}`

**Test Flow**:
1. Read author ID from CSV file
2. Send GET request with specific author ID
3. Validate response

**Expected Response**:
- Status Code: 200 OK
- Response Time: < 300ms (target)
- Valid author object returned

**Success Criteria**:
- Successful retrieval of author data by ID
- Consistent response times across different IDs
- Proper handling of concurrent requests

---

### Test Case 03: POST Create Author
**File**: `03_Authors_POST_Create.jmx`

**Objective**: Test the performance of creating new authors

**Test Configuration**:
- **Virtual Users**: 20 concurrent threads
- **Ramp-up Time**: 5 seconds
- **Test Duration**: 120 seconds (2 minutes)
- **Data Source**: `author_data.csv` - Contains author test data

**Endpoint**: `POST /api/Authors`

**Request Body**:
```json
{
  "Name": "Author Name",
  "Bio": "Author Biography",
  "DateOfBirth": "YYYY-MM-DD"
}
```

**Expected Response**:
- Status Code: 201 Created
- Response Time: < 800ms (target)
- Created author object with assigned ID

**Success Criteria**:
- Successful creation of new authors
- Unique ID assigned to each author
- Database integrity maintained under load

---

### Test Case 04: PUT Update Author
**File**: `04_Authors_PUT_Update.jmx`

**Objective**: Test the performance of updating existing authors

**Test Configuration**:
- **Virtual Users**: 20 concurrent threads
- **Ramp-up Time**: 5 seconds
- **Test Duration**: 120 seconds (2 minutes)
- **Data Source**: `author_ids.csv` - Contains author IDs to update

**Endpoint**: `PUT /api/Authors/{id}`

**Request Body**:
```json
{
  "Id": "author_id",
  "Name": "Updated Name",
  "Bio": "Updated Biography",
  "DateOfBirth": "YYYY-MM-DD"
}
```

**Expected Response**:
- Status Code: 200 OK or 204 No Content
- Response Time: < 800ms (target)
- Author data successfully updated

**Success Criteria**:
- Successful update of author records
- Data consistency maintained
- No data corruption under concurrent updates

---

### Test Case 05: DELETE Author
**File**: `05_Authors_DELETE.jmx`

**Objective**: Test the performance of deleting authors

**Test Configuration**:
- **Virtual Users**: 20 concurrent threads
- **Ramp-up Time**: 5 seconds
- **Test Duration**: 120 seconds (2 minutes)

**Endpoint**: 
1. `POST /api/Authors` - Create author for deletion
2. `DELETE /api/Authors/{id}` - Delete the created author

**Test Flow**:
1. Create a new author with unique identifier
2. Extract the created author's ID
3. Delete the author using the extracted ID
4. Validate deletion

**Expected Response**:
- Status Code: 200 OK or 204 No Content
- Response Time: < 500ms (target)

**Success Criteria**:
- Successful deletion of authors
- Proper cleanup of database records
- No orphaned records or referential integrity issues

---

## Books API Test Cases

### Test Case 06: GET All Books
**File**: `06_Books_GET_All.jmx`

**Objective**: Test the performance of retrieving all books from the database

**Test Configuration**:
- **Virtual Users**: 50 concurrent threads
- **Ramp-up Time**: 10 seconds
- **Test Duration**: 300 seconds (5 minutes)
- **Loop**: Infinite loop during test duration

**Endpoint**: `GET /api/Books`

**Expected Response**:
- Status Code: 200 OK
- Response Time: < 500ms (target)
- Content Type: application/json
- Array of book objects with author relationships

**Success Criteria**:
- All requests return 200 status code
- Response times are within acceptable limits
- No server errors during sustained load
- Proper serialization of related author data

---

### Test Case 07: GET Book by ID
**File**: `07_Books_GET_ById.jmx`

**Objective**: Test the performance of retrieving a specific book by ID

**Test Configuration**:
- **Virtual Users**: 50 concurrent threads
- **Ramp-up Time**: 10 seconds
- **Test Duration**: 300 seconds (5 minutes)
- **Data Source**: `book_ids.csv` - Contains valid book IDs

**Endpoint**: `GET /api/Books/{id}`

**Test Flow**:
1. Read book ID from CSV file
2. Send GET request with specific book ID
3. Validate response includes book and author data

**Expected Response**:
- Status Code: 200 OK
- Response Time: < 300ms (target)
- Valid book object with author details

**Success Criteria**:
- Successful retrieval of book data by ID
- Author relationship properly loaded
- Consistent response times across different IDs

---

### Test Case 08: POST Create Book
**File**: `08_Books_POST_Create.jmx`

**Objective**: Test the performance of creating new books

**Test Configuration**:
- **Virtual Users**: 20 concurrent threads
- **Ramp-up Time**: 5 seconds
- **Test Duration**: 120 seconds (2 minutes)
- **Data Source**: `book_create_data.csv` - Contains book test data

**Endpoint**: `POST /api/Books`

**Request Body**:
```json
{
  "Title": "Book Title",
  "ISBN": "ISBN-Number",
  "PublishedDate": "YYYY-MM-DD",
  "AuthorId": "author_id"
}
```

**Expected Response**:
- Status Code: 201 Created
- Response Time: < 800ms (target)
- Created book object with assigned ID

**Success Criteria**:
- Successful creation of new books
- Unique ID assigned to each book
- Foreign key relationship validated (valid AuthorId)
- Database integrity maintained under load

---

### Test Case 09: PUT Update Book
**File**: `09_Books_PUT_Update.jmx`

**Objective**: Test the performance of updating existing books

**Test Configuration**:
- **Virtual Users**: 20 concurrent threads
- **Ramp-up Time**: 5 seconds
- **Test Duration**: 120 seconds (2 minutes)
- **Data Source**: `book_update_data.csv` - Contains book update data

**Endpoint**: `PUT /api/Books/{id}`

**Request Body**:
```json
{
  "Id": "book_id",
  "Title": "Updated Title",
  "ISBN": "Updated-ISBN",
  "PublishedDate": "YYYY-MM-DD",
  "AuthorId": "author_id"
}
```

**Expected Response**:
- Status Code: 200 OK or 204 No Content
- Response Time: < 800ms (target)
- Book data successfully updated

**Success Criteria**:
- Successful update of book records
- Foreign key integrity maintained
- Data consistency under concurrent updates
- No data corruption

---

### Test Case 10: DELETE Book
**File**: `10_Books_DELETE.jmx`

**Objective**: Test the performance of deleting books

**Test Configuration**:
- **Virtual Users**: 20 concurrent threads
- **Ramp-up Time**: 5 seconds
- **Test Duration**: 120 seconds (2 minutes)

**Endpoint**: 
1. `POST /api/Books` - Create book for deletion
2. `DELETE /api/Books/{id}` - Delete the created book

**Test Flow**:
1. Create a new book with unique identifier
2. Extract the created book's ID
3. Delete the book using the extracted ID
4. Validate deletion

**Expected Response**:
- Status Code: 200 OK or 204 No Content
- Response Time: < 500ms (target)

**Success Criteria**:
- Successful deletion of books
- Proper cleanup of database records
- No referential integrity violations
- Author records remain intact after book deletion

---

## Performance Monitoring

### System Resources Monitored
The `run_with_profiling.py` script monitors the following metrics during test execution:

1. **CPU Usage**:
   - Overall CPU utilization percentage
   - Per-core CPU usage
   - CPU frequency

2. **Memory Usage**:
   - Available memory
   - Used memory
   - Memory percentage
   - Swap usage

3. **Disk I/O**:
   - Read/Write operations per second
   - Read/Write bytes per second
   - Disk utilization

4. **Network I/O**:
   - Bytes sent/received
   - Packets sent/received
   - Network errors

5. **JMeter Metrics**:
   - Response times (min, max, average, percentiles)
   - Throughput (requests/second)
   - Error rate
   - Active threads

### Test Execution
Each test can be executed using:
```bash
python run_with_profiling.py <test_file.jmx>
```

Example:
```bash
python run_with_profiling.py 01_Authors_GET_All.jmx
```

### Output Artifacts
After each test execution:
- **JTL Results File**: Raw test results
- **JMeter Log**: Detailed execution log
- **HTML Report**: Visual dashboard with graphs
- **Profiling Data CSV**: System resource metrics
- **Performance Graphs**: CPU, Memory, Disk, Network charts (PNG format)

---

## Test Data Files

| File | Purpose |
|------|---------|
| `author_data.csv` | Sample author data for create operations |
| `author_ids.csv` | Valid author IDs for read/update/delete operations |
| `book_create_data.csv` | Sample book data for create operations |
| `book_update_data.csv` | Book data for update operations |
| `book_ids.csv` | Valid book IDs for read/update/delete operations |
| `delete_author_ids.csv` | Author IDs marked for deletion testing |
| `delete_book_ids.csv` | Book IDs marked for deletion testing |

---

## Performance Benchmarks

### Response Time Targets

| Operation | Endpoint | Target Response Time |
|-----------|----------|---------------------|
| GET All Authors | `/api/Authors` | < 500ms |
| GET Author by ID | `/api/Authors/{id}` | < 300ms |
| POST Create Author | `/api/Authors` | < 800ms |
| PUT Update Author | `/api/Authors/{id}` | < 800ms |
| DELETE Author | `/api/Authors/{id}` | < 500ms |
| GET All Books | `/api/Books` | < 500ms |
| GET Book by ID | `/api/Books/{id}` | < 300ms |
| POST Create Book | `/api/Books` | < 800ms |
| PUT Update Book | `/api/Books/{id}` | < 800ms |
| DELETE Book | `/api/Books/{id}` | < 500ms |

### Load Profiles

**Read Operations (GET)**:
- 50 concurrent users
- 10 second ramp-up
- 5 minute sustained load

**Write Operations (POST/PUT/DELETE)**:
- 20 concurrent users
- 5 second ramp-up
- 2 minute sustained load

---

## Success Criteria

### Functional Requirements
- All HTTP status codes match expected values
- Response payloads contain valid JSON
- Data integrity maintained across operations
- Referential integrity preserved (Author-Book relationships)

### Performance Requirements
- Response times within target thresholds
- Throughput meets minimum requirements
- Error rate < 1% under normal load
- System resources remain stable throughout test

### Stability Requirements
- No memory leaks detected
- No connection pool exhaustion
- Graceful degradation under peak load
- Recovery after load spike

---

## Test Execution Order

### Recommended Sequence
1. **Setup**: Reset and seed database
2. **01_Authors_GET_All.jmx** - Baseline read performance
3. **02_Authors_GET_ById.jmx** - Single record retrieval
4. **03_Authors_POST_Create.jmx** - Create load test
5. **04_Authors_PUT_Update.jmx** - Update load test
6. **06_Books_GET_All.jmx** - Books read performance
7. **07_Books_GET_ById.jmx** - Single book retrieval
8. **08_Books_POST_Create.jmx** - Books create load test
9. **09_Books_PUT_Update.jmx** - Books update load test
10. **05_Authors_DELETE.jmx** - Author deletion (requires recreation)
11. **10_Books_DELETE.jmx** - Book deletion (requires recreation)

**Note**: DELETE tests should be run last as they modify the test data set.

---

## Notes
- Database should be reset before each test run for consistent results
- The Python profiling script requires `pandas` and `matplotlib` packages
- All tests target `http://localhost:50524` by default
- Test duration and thread counts can be adjusted based on performance requirements
- CSV data files should be properly formatted and contain sufficient test data
