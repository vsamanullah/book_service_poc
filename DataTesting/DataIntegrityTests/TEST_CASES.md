# BookService Test Data Integrity - Test Cases

## Document Information

| Property | Value |
|----------|-------|
| **Module** | BookServiceTestDataIntegrity |
| **Version** | 1.0 |
| **Last Updated** | January 10, 2026 |
| **Test Framework** | Python + pyodbc |
| **Total Test Cases** | 42 |

---

## Table of Contents

1. [Test Environment Setup](#test-environment-setup)
2. [Schema Validation Tests](#schema-validation-tests)
3. [Data Integrity Tests](#data-integrity-tests)
4. [Migration Verification Tests](#migration-verification-tests)
5. [Referential Integrity Tests](#referential-integrity-tests)
6. [Test Data Population Tests](#test-data-population-tests)
7. [Performance Tests](#performance-tests)
8. [Negative Tests](#negative-tests)
9. [Edge Case Tests](#edge-case-tests)

---

## Test Environment Setup

### Test Prerequisites

| Prerequisite | Description | Verification Command |
|--------------|-------------|---------------------|
| Python 3.8+ | Python runtime | `python --version` |
| pyodbc | Database connectivity | `pip show pyodbc` |
| ODBC Driver | SQL Server driver (17 or 18) | `odbcinst -q -d` |
| Database Access | Read/Write permissions | Connection test |
| db_config.json | Configuration file | File exists |

### Test Data Configuration

```json
{
  "test_data_sizes": {
    "small": 10,
    "medium": 50,
    "large": 100,
    "xlarge": 500
  },
  "test_environments": ["local", "source", "target"]
}
```

---

## Schema Validation Tests

### TC-SV-001: Verify Authors Table Schema

**Objective**: Validate Authors table structure matches expected schema

**Prerequisites**:
- Database connection established
- Authors table exists

**Test Steps**:
1. Run `check_schema.py`
2. Verify Authors table structure

**Expected Results**:
```
Authors Table Structure:
  Id                   int             NULL=NO (Primary Key)
  Name                 nvarchar        NULL=NO
  Bio                  nvarchar        NULL=YES
  Nationality          nvarchar        NULL=YES
```

**Pass Criteria**:
- All columns present
- Data types match
- Nullability constraints correct

**Priority**: High  
**Automated**: Yes  
**Script**: check_schema.py

---

### TC-SV-002: Verify Books Table Schema

**Objective**: Validate Books table structure with foreign key relationships

**Test Steps**:
1. Run schema inspection
2. Verify column definitions
3. Validate foreign key to Authors and Genres

**Expected Results**:
```
Books Table Structure:
  Id                   int             NULL=NO (Primary Key)
  Title                nvarchar        NULL=NO
  AuthorId             int             NULL=NO (Foreign Key → Authors)
  GenreId              int             NULL=YES (Foreign Key → Genres)
  ISBN                 nvarchar        NULL=NO
  Price                decimal         NULL=NO
  Rating               decimal         NULL=YES
  PublishedDate        datetime        NULL=YES
```

**Pass Criteria**:
- All columns present with correct types
- Foreign keys defined
- ISBN unique constraint exists

**Priority**: High  
**Automated**: Yes

---

### TC-SV-003: Verify Customers Table Schema

**Objective**: Validate customer data structure

**Expected Results**:
```
Customers Table Structure:
  Id                   int             NULL=NO (Primary Key)
  Name                 nvarchar        NULL=NO
  Email                nvarchar        NULL=NO (Unique)
  Phone                nvarchar        NULL=YES
  RegistrationDate     datetime        NULL=NO
```

**Pass Criteria**:
- Email field has unique constraint
- RegistrationDate not nullable

**Priority**: High  
**Automated**: Yes

---

### TC-SV-004: Verify Stocks Table Schema

**Objective**: Validate inventory table structure

**Expected Results**:
```
Stocks Table Structure:
  Id                   int             NULL=NO (Primary Key)
  BookId               int             NULL=NO (Foreign Key → Books)
  BranchName           nvarchar        NULL=NO
  Quantity             int             NULL=NO
  IsAvailable          bit             NULL=NO
```

**Pass Criteria**:
- Foreign key to Books table exists
- Quantity default value is 1
- IsAvailable default is True

**Priority**: High  
**Automated**: Yes

---

### TC-SV-005: Verify Rentals Table Schema

**Objective**: Validate rental transaction structure

**Expected Results**:
```
Rentals Table Structure:
  Id                   int             NULL=NO (Primary Key)
  CustomerId           int             NULL=NO (Foreign Key → Customers)
  StockId              int             NULL=NO (Foreign Key → Stocks)
  RentalDate           datetime        NULL=NO
  ReturnDate           datetime        NULL=YES
  Status               nvarchar        NULL=NO
```

**Pass Criteria**:
- Two foreign keys defined (CustomerId, StockId)
- Status has check constraint (Rented, Returned, Overdue)

**Priority**: High  
**Automated**: Yes

---

### TC-SV-006: Verify Genres Table Schema

**Objective**: Validate genre reference table

**Expected Results**:
```
Genres Table Structure:
  Id                   int             NULL=NO (Primary Key)
  Name                 nvarchar        NULL=NO (Unique)
  Description          nvarchar        NULL=YES
```

**Pass Criteria**:
- Name has unique constraint
- Table contains standard genres

**Priority**: Medium  
**Automated**: Yes

---

## Data Integrity Tests

### TC-DI-001: Row Count Verification - Authors

**Objective**: Verify no records lost during migration for Authors table

**Prerequisites**:
- Baseline created with known record count
- Migration completed

**Test Steps**:
1. Run `create_baseline.py --env source` (before migration)
2. Perform migration
3. Run `verify_migration.py --env target`

**Expected Results**:
```
✓ Authors: Row count matched
  Baseline: 100 records
  Current:  100 records
  Difference: 0
```

**Pass Criteria**:
- Row counts match exactly
- No data loss detected

**Priority**: Critical  
**Automated**: Yes  
**Script**: verify_migration.py

---

### TC-DI-002: Row Count Verification - Books

**Objective**: Verify Books table record integrity

**Test Data**: 200 book records (2 per author)

**Expected Results**:
```
✓ Books: Row count matched
  Baseline: 200 records
  Current:  200 records
```

**Pass Criteria**: Exact match

**Priority**: Critical  
**Automated**: Yes

---

### TC-DI-003: Row Count Verification - Customers

**Objective**: Verify customer data integrity

**Expected Results**:
```
✓ Customers: Row count matched
  Baseline: 100 records
  Current:  100 records
```

**Priority**: Critical  
**Automated**: Yes

---

### TC-DI-004: Row Count Verification - Stocks

**Objective**: Verify inventory data integrity

**Test Data**: 600 stock records (3 copies × 2 branches per book)

**Expected Results**:
```
✓ Stocks: Row count matched
  Baseline: 600 records
  Current:  600 records
```

**Priority**: Critical  
**Automated**: Yes

---

### TC-DI-005: Row Count Verification - Rentals

**Objective**: Verify rental transaction integrity

**Expected Results**:
```
✓ Rentals: Row count matched
  Baseline: 300 records
  Current:  300 records
```

**Priority**: Critical  
**Automated**: Yes

---

### TC-DI-006: Data Checksum Validation - Authors

**Objective**: Verify Authors data content integrity using MD5 checksums

**Test Steps**:
1. Baseline creates checksum of sorted Authors data
2. Post-migration, calculate current checksum
3. Compare checksums

**Expected Results**:
```
✓ Authors: Data checksum matched
  Baseline Checksum: a7f3c4d2e8b9...
  Current Checksum:  a7f3c4d2e8b9...
```

**Pass Criteria**:
- Checksums match exactly
- Indicates no data corruption
- Proves data fidelity

**Priority**: Critical  
**Automated**: Yes  
**Detects**: Any data modification, corruption, or loss

---

### TC-DI-007: Data Checksum Validation - Books

**Objective**: Verify Books data integrity through checksums

**Sensitivity**: Detects any change in Title, ISBN, Price, Rating, etc.

**Expected Results**:
```
✓ Books: Data checksum matched
```

**Priority**: Critical  
**Automated**: Yes

---

### TC-DI-008: Data Checksum Validation - Customers

**Objective**: Verify customer data hasn't been corrupted

**Expected Results**:
```
✓ Customers: Data checksum matched
```

**Priority**: Critical  
**Automated**: Yes

---

### TC-DI-009: Data Checksum Validation - Stocks

**Objective**: Verify inventory data integrity

**Expected Results**:
```
✓ Stocks: Data checksum matched
```

**Priority**: High  
**Automated**: Yes

---

### TC-DI-010: Data Checksum Validation - Rentals

**Objective**: Verify rental transaction data integrity

**Expected Results**:
```
✓ Rentals: Data checksum matched
```

**Priority**: High  
**Automated**: Yes

---

## Migration Verification Tests

### TC-MV-001: Complete Migration Verification

**Objective**: Execute full migration verification suite

**Test Steps**:
1. Populate source database: `python populate_test_data.py 100 --env source`
2. Create baseline: `python create_baseline.py --env source`
3. Perform migration (external process)
4. Verify migration: `python verify_migration.py --env target`

**Expected Results**:
```
========================================
VERIFICATION SUMMARY
========================================
Tests Passed: 34
Tests Failed: 0
Warnings: 0
Overall Status: PASSED
```

**Detailed Checks**:
- ✓ All 6 main tables: Row counts match
- ✓ All 6 main tables: Checksums match
- ✓ Schema structure preserved
- ✓ Foreign keys intact
- ✓ Indexes present

**Pass Criteria**:
- 0 failed tests
- All critical checks pass
- Warnings acceptable if documented

**Priority**: Critical  
**Automated**: Yes  
**Duration**: ~30-60 seconds

---

### TC-MV-002: Schema Migration Verification

**Objective**: Verify schema structure preserved during migration

**Test Steps**:
1. Compare baseline schema with current schema
2. Validate column definitions
3. Check data types and constraints

**Expected Results**:
```
✓ Authors: Schema structure matched
✓ Books: Schema structure matched
✓ Customers: Schema structure matched
✓ Stocks: Schema structure matched
✓ Rentals: Schema structure matched
✓ Genres: Schema structure matched
```

**Pass Criteria**:
- All columns present
- Data types unchanged
- Nullability constraints preserved

**Priority**: Critical  
**Automated**: Yes

---

### TC-MV-003: Foreign Key Preservation

**Objective**: Verify all foreign key relationships maintained

**Test Steps**:
1. Extract foreign key definitions from baseline
2. Compare with current database
3. Validate all relationships exist

**Expected Results**:
```
✓ Books.AuthorId → Authors.Id: Preserved
✓ Books.GenreId → Genres.Id: Preserved
✓ Stocks.BookId → Books.Id: Preserved
✓ Rentals.CustomerId → Customers.Id: Preserved
✓ Rentals.StockId → Stocks.Id: Preserved
```

**Pass Criteria**:
- All foreign keys present
- Cascade rules preserved
- No orphaned records

**Priority**: Critical  
**Automated**: Yes

---

### TC-MV-004: Index Preservation

**Objective**: Verify critical indexes maintained

**Test Steps**:
1. Compare index definitions
2. Check clustered and non-clustered indexes
3. Validate unique indexes

**Expected Results**:
```
✓ Authors.PK_Authors (Clustered): Present
✓ Books.PK_Books (Clustered): Present
✓ Books.IX_Books_AuthorId: Present
✓ Books.IX_Books_ISBN (Unique): Present
✓ Customers.PK_Customers (Clustered): Present
✓ Customers.IX_Customers_Email (Unique): Present
```

**Pass Criteria**:
- All primary key indexes present
- Foreign key indexes exist
- Unique constraints maintained

**Priority**: High  
**Automated**: Yes

---

### TC-MV-005: Migration with Large Dataset

**Objective**: Test migration verification with substantial data volume

**Test Data**:
- 500 Authors
- 1000 Books
- 500 Customers
- 3000 Stocks
- 1500 Rentals

**Test Steps**:
```bash
python populate_test_data.py 500 --env source
python create_baseline.py --env source --output large_baseline.json
# Perform migration
python verify_migration.py --env target --baseline large_baseline.json
```

**Expected Results**:
- All checksums match
- Verification completes within 120 seconds
- No memory issues

**Pass Criteria**:
- 100% data integrity
- Performance acceptable

**Priority**: High  
**Automated**: Yes  
**Duration**: ~2 minutes

---

## Referential Integrity Tests

### TC-RI-001: Books-Authors Relationship

**Objective**: Verify every Book has a valid Author reference

**Test Steps**:
1. Query all BookId → AuthorId relationships
2. Validate all AuthorIds exist in Authors table
3. Check for orphaned books

**SQL Validation**:
```sql
-- Should return 0 orphaned books
SELECT COUNT(*) 
FROM Books b
LEFT JOIN Authors a ON b.AuthorId = a.Id
WHERE a.Id IS NULL
```

**Expected Results**:
```
✓ Books-Authors: No orphaned records
  Total Books: 200
  Valid References: 200
  Orphaned: 0
```

**Pass Criteria**: 0 orphaned records

**Priority**: Critical  
**Automated**: Yes

---

### TC-RI-002: Books-Genres Relationship

**Objective**: Verify Book-Genre references are valid

**SQL Validation**:
```sql
-- Should return 0 invalid genre references
SELECT COUNT(*) 
FROM Books b
LEFT JOIN Genres g ON b.GenreId = g.Id
WHERE b.GenreId IS NOT NULL AND g.Id IS NULL
```

**Expected Results**:
```
✓ Books-Genres: All references valid
  Books with Genre: 200
  Invalid References: 0
```

**Priority**: High  
**Automated**: Yes

---

### TC-RI-003: Stocks-Books Relationship

**Objective**: Verify every Stock entry references a valid Book

**SQL Validation**:
```sql
-- Should return 0 orphaned stocks
SELECT COUNT(*) 
FROM Stocks s
LEFT JOIN Books b ON s.BookId = b.Id
WHERE b.Id IS NULL
```

**Expected Results**:
```
✓ Stocks-Books: No orphaned records
  Total Stocks: 600
  Valid References: 600
  Orphaned: 0
```

**Priority**: Critical  
**Automated**: Yes

---

### TC-RI-004: Rentals-Customers Relationship

**Objective**: Verify all Rentals have valid Customer references

**SQL Validation**:
```sql
-- Should return 0 orphaned rentals
SELECT COUNT(*) 
FROM Rentals r
LEFT JOIN Customers c ON r.CustomerId = c.Id
WHERE c.Id IS NULL
```

**Expected Results**:
```
✓ Rentals-Customers: All references valid
  Total Rentals: 300
  Valid Customer Refs: 300
```

**Priority**: Critical  
**Automated**: Yes

---

### TC-RI-005: Rentals-Stocks Relationship

**Objective**: Verify all Rentals reference valid Stock items

**SQL Validation**:
```sql
-- Should return 0 invalid stock references
SELECT COUNT(*) 
FROM Rentals r
LEFT JOIN Stocks s ON r.StockId = s.Id
WHERE s.Id IS NULL
```

**Expected Results**:
```
✓ Rentals-Stocks: All references valid
  Total Rentals: 300
  Valid Stock Refs: 300
```

**Priority**: Critical  
**Automated**: Yes

---

### TC-RI-006: Cascade Delete Validation

**Objective**: Verify cascade delete rules work correctly

**Test Steps**:
1. Create test data with relationships
2. Attempt to delete an Author with Books
3. Verify cascade behavior or constraint enforcement

**Expected Behavior**:
```
Option A: Cascade Delete Enabled
  - Delete Author → Books also deleted
  
Option B: Restrict Delete (Recommended)
  - Delete Author → Error: FK constraint violation
  - Must delete Books first
```

**Pass Criteria**: Behavior matches database design specification

**Priority**: High  
**Automated**: Partial  
**Note**: May require manual verification

---

## Test Data Population Tests

### TC-TP-001: Populate Small Dataset (10 records)

**Objective**: Verify test data generation with small dataset

**Test Command**:
```bash
python populate_test_data.py 10 --env local
```

**Expected Results**:
```
Data Population Summary:
  Authors Created: 10
  Books Created: 20 (2 per author)
  Genres Created: 5
  Customers Created: 10
  Stocks Created: 60 (3 per book × 2 branches)
  Rentals Created: ~30 (50% of stocks)
```

**Validation**:
```sql
SELECT 
  (SELECT COUNT(*) FROM Authors) as Authors,
  (SELECT COUNT(*) FROM Books) as Books,
  (SELECT COUNT(*) FROM Customers) as Customers,
  (SELECT COUNT(*) FROM Stocks) as Stocks,
  (SELECT COUNT(*) FROM Rentals) as Rentals
```

**Pass Criteria**:
- All tables populated
- Relationships valid
- No duplicate ISBNs or emails
- Execution time < 5 seconds

**Priority**: High  
**Automated**: Yes

---

### TC-TP-002: Populate Medium Dataset (50 records)

**Objective**: Test data generation with medium volume

**Test Command**:
```bash
python populate_test_data.py 50 --env source
```

**Expected Results**:
- 50 Authors
- 100 Books
- 50 Customers
- 300 Stocks
- ~150 Rentals

**Priority**: High  
**Automated**: Yes

---

### TC-TP-003: Populate Large Dataset (100 records)

**Objective**: Verify data generation scales to larger volumes

**Test Command**:
```bash
python populate_test_data.py 100 --env target
```

**Expected Results**:
- 100 Authors
- 200 Books
- 100 Customers
- 600 Stocks
- ~300 Rentals

**Performance**: Should complete within 30 seconds

**Priority**: High  
**Automated**: Yes

---

### TC-TP-004: Verify Unique Constraints

**Objective**: Ensure generated data respects unique constraints

**Test Steps**:
1. Populate test data
2. Verify no duplicate ISBNs
3. Verify no duplicate email addresses
4. Check genre uniqueness

**SQL Validation**:
```sql
-- Should return 0 duplicates
SELECT ISBN, COUNT(*) as Count
FROM Books
GROUP BY ISBN
HAVING COUNT(*) > 1

SELECT Email, COUNT(*) as Count
FROM Customers
GROUP BY Email
HAVING COUNT(*) > 1
```

**Expected Results**:
```
✓ No duplicate ISBNs found
✓ No duplicate email addresses
✓ All unique constraints honored
```

**Pass Criteria**: 0 duplicates

**Priority**: Critical  
**Automated**: Yes

---

### TC-TP-005: Verify Data Relationships

**Objective**: Ensure populated data has correct relationships

**Validations**:
1. Every Book has exactly 1 Author
2. Every Book has 0 or 1 Genre
3. Every Stock references existing Book
4. Every Rental has valid Customer and Stock

**Expected Results**:
```
✓ Book-Author: 100% valid (200/200)
✓ Book-Genre: 100% valid (200/200)
✓ Stock-Book: 100% valid (600/600)
✓ Rental-Customer: 100% valid (300/300)
✓ Rental-Stock: 100% valid (300/300)
```

**Priority**: Critical  
**Automated**: Yes

---

### TC-TP-006: Data Cleanup Before Population

**Objective**: Verify cleanup deletes all existing data

**Test Steps**:
1. Populate initial data
2. Run population script again (includes cleanup)
3. Verify old data removed, new data created

**Expected Behavior**:
```
Starting data cleanup...
  Deleting Rentals: 300 records deleted
  Deleting Stocks: 600 records deleted
  Deleting Customers: 100 records deleted
  Deleting Books: 200 records deleted
  Deleting Authors: 100 records deleted
  Deleting Genres: 5 records deleted

Populating new data...
  [New records created]
```

**Pass Criteria**:
- All tables emptied before population
- No foreign key constraint violations
- Clean slate for testing

**Priority**: High  
**Automated**: Yes

---

## Performance Tests

### TC-PF-001: Baseline Creation Performance

**Objective**: Verify baseline creation completes within acceptable time

**Test Scenarios**:

| Data Size | Record Count | Expected Duration |
|-----------|--------------|-------------------|
| Small | 10 authors + related | < 5 seconds |
| Medium | 50 authors + related | < 15 seconds |
| Large | 100 authors + related | < 30 seconds |
| XLarge | 500 authors + related | < 120 seconds |

**Test Command**:
```bash
time python create_baseline.py --env local
```

**Pass Criteria**: Completes within expected duration

**Priority**: Medium  
**Automated**: Yes

---

### TC-PF-002: Verification Performance

**Objective**: Verify migration verification completes efficiently

**Test Scenarios**:

| Data Size | Record Count | Expected Duration |
|-----------|--------------|-------------------|
| Small | 10 authors + related | < 10 seconds |
| Medium | 50 authors + related | < 30 seconds |
| Large | 100 authors + related | < 60 seconds |
| XLarge | 500 authors + related | < 180 seconds |

**Pass Criteria**: Verification completes within time limit

**Priority**: Medium  
**Automated**: Yes

---

### TC-PF-003: Population Performance

**Objective**: Test data population speed

**Test Command**:
```bash
time python populate_test_data.py 100 --env local
```

**Expected Performance**:
- ~100 records per second
- 100 authors + related data: < 30 seconds

**Priority**: Low  
**Automated**: Yes

---

## Negative Tests

### TC-NEG-001: Invalid Connection String

**Objective**: Verify graceful handling of invalid connection

**Test Steps**:
1. Use invalid server address
2. Run any script

**Expected Results**:
```
ERROR: Failed to connect to database
  Error: [08001] [Microsoft][ODBC Driver 18 for SQL Server]
  Named Pipes Provider: Could not open connection to SQL Server
```

**Pass Criteria**:
- Clear error message
- No crash
- Exit code non-zero

**Priority**: Medium  
**Automated**: Yes

---

### TC-NEG-002: Missing Baseline File

**Objective**: Handle missing baseline gracefully

**Test Command**:
```bash
python verify_migration.py --env target --baseline nonexistent.json
```

**Expected Results**:
```
ERROR: Baseline file not found: nonexistent.json
Please create baseline first using create_baseline.py
```

**Pass Criteria**:
- Helpful error message
- Suggests corrective action

**Priority**: Medium  
**Automated**: Yes

---

### TC-NEG-003: Corrupted Baseline File

**Objective**: Handle corrupted JSON baseline

**Test Steps**:
1. Create baseline file
2. Corrupt JSON (remove closing bracket)
3. Run verification

**Expected Results**:
```
ERROR: Failed to load baseline file
  Invalid JSON format
  Please recreate baseline using create_baseline.py
```

**Priority**: Low  
**Automated**: Yes

---

### TC-NEG-004: Missing Database Table

**Objective**: Handle missing table scenario

**Test Steps**:
1. Create baseline
2. Drop a table (e.g., Genres)
3. Run verification

**Expected Results**:
```
✗ Genres: Table not found in current database
  Expected table 'Genres' is missing
  Status: CRITICAL FAILURE
```

**Priority**: High  
**Automated**: Partial

---

### TC-NEG-005: Schema Mismatch Detected

**Objective**: Detect and report schema changes

**Test Steps**:
1. Create baseline
2. Add new column to table
3. Run verification

**Expected Results**:
```
⚠ Books: Schema mismatch detected
  New column found: 'Publisher' (nvarchar, NULL=YES)
  Status: WARNING
```

**Priority**: High  
**Automated**: Yes

---

## Edge Case Tests

### TC-EDGE-001: Empty Database

**Objective**: Verify scripts handle empty database

**Test Steps**:
1. Clear all tables
2. Create baseline
3. Verify against empty database

**Expected Results**:
```
Baseline Created:
  Authors: 0 records
  Books: 0 records
  ...

Verification:
  ✓ All tables: Row counts match (0 records)
  Status: PASSED
```

**Pass Criteria**: Handles gracefully

**Priority**: Low  
**Automated**: Yes

---

### TC-EDGE-002: NULL Value Handling

**Objective**: Verify NULL values handled in checksums

**Test Steps**:
1. Populate data with NULL optional fields (Bio, Nationality)
2. Create baseline
3. Verify

**Expected Results**:
```
✓ Authors: Data checksum matched
  (NULL values handled correctly)
```

**Priority**: Medium  
**Automated**: Yes

---

### TC-EDGE-003: Special Characters in Data

**Objective**: Test special character handling

**Test Data**:
- Author names with: O'Brien, José García, 中文
- Book titles with: "Quotes", <HTML>, 'Single'

**Expected Results**:
- All data stored correctly
- Checksums match
- No encoding issues

**Priority**: Medium  
**Automated**: Partial

---

### TC-EDGE-004: Maximum Field Length

**Objective**: Test data at field length boundaries

**Test Data**:
- Author Bio: Max length (2000 chars)
- Book Title: Max length (500 chars)

**Expected Results**:
- No truncation
- Data integrity maintained

**Priority**: Low  
**Automated**: Partial

---

### TC-EDGE-005: Concurrent Access

**Objective**: Test baseline creation during active transactions

**Test Steps**:
1. Start long-running transaction
2. Create baseline (should see consistent snapshot)
3. Commit transaction

**Expected Results**:
- Baseline captures consistent state
- No locking issues

**Priority**: Low  
**Automated**: No (manual test)

---

## Test Execution Summary

### Test Coverage Matrix

| Category | Total Tests | Critical | High | Medium | Low |
|----------|-------------|----------|------|--------|-----|
| Schema Validation | 6 | 5 | 1 | 0 | 0 |
| Data Integrity | 10 | 10 | 0 | 0 | 0 |
| Migration Verification | 5 | 3 | 2 | 0 | 0 |
| Referential Integrity | 6 | 5 | 1 | 0 | 0 |
| Test Data Population | 6 | 3 | 3 | 0 | 0 |
| Performance | 3 | 0 | 0 | 3 | 0 |
| Negative Tests | 5 | 0 | 2 | 2 | 1 |
| Edge Cases | 5 | 0 | 0 | 2 | 3 |
| **TOTAL** | **42** | **26** | **9** | **7** | **4** |

### Automation Status

| Status | Count | Percentage |
|--------|-------|------------|
| Fully Automated | 36 | 85.7% |
| Partially Automated | 4 | 9.5% |
| Manual Only | 2 | 4.8% |

---

## Test Execution Instructions

### Full Test Suite Execution

```bash
# 1. Setup test environment
cd BookServiceDataTesting/BookServiceTestDataIntegrity

# 2. Run schema validation
python check_schema.py > test_results/schema_validation.log

# 3. Test data population (small dataset for speed)
python populate_test_data.py 25 --env local

# 4. Create baseline
python create_baseline.py --env local --output test_results/baseline_test.json

# 5. Verify migration (no actual migration, should pass all checks)
python verify_migration.py --env local --baseline test_results/baseline_test.json

# 6. Review results
cat verification_*.log
```

### Smoke Test (Quick Validation)

```bash
# Quick 10-record test
python populate_test_data.py 10 --env local
python create_baseline.py --env local
python verify_migration.py --env local
```

### Regression Test (Comprehensive)

```bash
# Large dataset comprehensive test
python populate_test_data.py 100 --env source
python create_baseline.py --env source --output baselines/regression_baseline.json
# Perform migration
python verify_migration.py --env target --baseline baselines/regression_baseline.json
```

---

## Test Results Tracking

### Success Criteria

**All Critical Tests (26)**: Must pass 100%  
**High Priority Tests (9)**: Must pass ≥ 95%  
**Medium Priority Tests (7)**: Must pass ≥ 90%  
**Low Priority Tests (4)**: Best effort

### Test Report Template

```
Test Execution Report
=====================
Date: YYYY-MM-DD
Tester: [Name]
Environment: [local/source/target]
Data Size: [10/50/100/500] authors

Results:
  Total Tests: 42
  Passed: __
  Failed: __
  Warnings: __
  Skipped: __
  
Critical Issues: [None/List]
Recommendations: [Actions needed]

Status: PASS/FAIL
```

---

## Maintenance and Updates

### When to Update Test Cases

- New database tables added
- Schema changes implemented
- New validation requirements
- Performance benchmarks change
- Bug fixes requiring new test coverage

### Test Case Review Schedule

- Monthly: Review failed/flaky tests
- Quarterly: Update expected values and benchmarks
- After major releases: Full test case review

---

## References

- [README.md](README.md) - Module setup and usage guide
- [migration_testcase.md](migration_testcase.md) - Migration-specific test procedures
- Database schema documentation
- Python testing best practices

---

## Appendix: Test Data Patterns

### Authors Test Data Pattern
```
Name: "Author_{timestamp}_{index}"
Bio: "Bio for Author {name}"
Nationality: Random from [American, British, Indian, Chinese, German, French, Spanish, Japanese]
```

### Books Test Data Pattern
```
Title: "Book {index} by {author_name}"
ISBN: "978-{random_10_digits}"
Price: Random decimal 10.00 - 50.00
Rating: Random decimal 1.0 - 5.0
PublishedDate: Random date within last 10 years
```

### Customers Test Data Pattern
```
Name: "Customer_{timestamp}_{index}"
Email: "customer_{timestamp}_{index}@bookstore.com"
Phone: "+1-555-{random_7_digits}"
RegistrationDate: Random date within last 2 years
```

### Stocks Test Data Pattern
```
BookId: Reference to Books
BranchName: Alternating ["Main Branch", "North Branch"]
Quantity: 3 (3 copies per book per branch)
IsAvailable: Based on rental status
```

### Rentals Test Data Pattern
```
Status: Random ["Rented", "Returned"] (50/50 split)
RentalDate: Random within last 90 days
ReturnDate: NULL for "Rented", date for "Returned"
```

---

**Document Version**: 1.0  
**Last Updated**: January 10, 2026  
**Next Review**: April 10, 2026
