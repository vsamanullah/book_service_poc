# Database Performance Testing Suite - Test Cases Documentation

## Overview

This document describes the test cases for the **BookServiceContext Database Performance Testing Tool**. The tool is a **JMeter wrapper** that automates database performance testing using Apache JMeter with JDBC, including optional system performance profiling.

### Testing Approach

**JMeter JDBC Load Testing**
- Industry-standard performance testing via Apache JMeter
- Direct JDBC connection to SQL Server
- System-level performance profiling (CPU, Memory, Disk, Network) via Windows typeperf
- Automated database cleanup and seeding
- 50 threads per table group, 10-minute test duration, 2-second pacing
- Auto-generated HTML reports with detailed statistics and charts
- Ideal for: Enterprise-grade benchmarking, stakeholder reporting, repeatable tests

### Command Examples
```bash
# Basic test with profiling
python run_and_monitor_db_test.py --env target

# Test without system profiling (faster)
python run_and_monitor_db_test.py --env target --no-profiling

# Cleanup database before test
python run_and_monitor_db_test.py --env target --cleanup

# Skip database seeding (use existing data)
python run_and_monitor_db_test.py --env target --no-seed
```

### Tables Under Test
- **Authors** - Author information with full biographical data
- **Books** - Book catalog with pricing and ratings
- **Genres** - Book genre categories
- **Customers** - Customer records with registration details
- **Rentals** - Rental transactions and status tracking
- **Stocks** - Book inventory and availability management

## What Are We Testing?

### Primary Objectives

1. **Database Performance Under Load**
   - Measure response times for CRUD operations across all tables
   - Identify performance bottlenecks in multi-table scenarios
   - Evaluate scalability with concurrent connections
   - Monitor resource utilization (CPU, Memory, I/O)

2. **Concurrent Connection Handling**
   - Test database behavior with multiple simultaneous connections
   - Detect deadlocks and lock contention across related tables
   - Validate connection pooling efficiency
   - Assess transaction throughput with foreign key constraints

3. **Operation-Specific Performance**
   - SELECT query performance (single table and JOINs)
   - INSERT operation throughput with FK validation
   - UPDATE statement efficiency across multiple tables
   - DELETE operation handling with referential integrity

4. **Multi-Table Transaction Testing**
   - Cross-table operations (Rentals → Customers/Stocks)
   - Foreign key constraint performance
   - Complex JOIN queries
   - Transaction isolation under load

4. **System Health Monitoring**
   - SQL Server CPU utilization
   - Memory consumption patterns
   - Active connection tracking
   - Transaction rate monitoring
   - Lock wait and deadlock detection

---

## Test Environment

### Database Schema
```
Database: BookStore-Master

Tables:
1. Authors (Parent Table)
   - ID (INT, PRIMARY KEY, IDENTITY)
   - AuthorId (UNIQUEIDENTIFIER)
   - FirstName (NVARCHAR)
   - LastName (NVARCHAR)
   - BirthDate (DATETIME)
   - Nationality (NVARCHAR)
   - Bio (NVARCHAR)
   - Email (NVARCHAR)
   - Affiliation (NVARCHAR)

2. Genres (Lookup Table)
   - ID (INT, PRIMARY KEY, IDENTITY)
   - Name (NVARCHAR)

3. Books (Parent Table)
   - ID (INT, PRIMARY KEY, IDENTITY)
   - Title (NVARCHAR)
   - AuthorId (INT, FOREIGN KEY → Authors.ID)
   - Year (INT)
   - Price (DECIMAL)
   - Description (NVARCHAR)
   - GenreId (INT, FOREIGN KEY → Genres.ID)
   - IssueDate (DATETIME)
   - Rating (TINYINT)
   - Image (NVARCHAR, NULLABLE)
   - TrailURI (NVARCHAR, NULLABLE)

4. Customers (Parent Table)
   - ID (INT, PRIMARY KEY, IDENTITY)
   - FirstName (NVARCHAR)
   - LastName (NVARCHAR)
   - Email (NVARCHAR)
   - IdentityCard (NVARCHAR)
   - UniqueKey (UNIQUEIDENTIFIER)
   - DateOfBirth (DATETIME)
   - Mobile (NVARCHAR, NULLABLE)
   - RegistrationDate (DATETIME)

5. Stocks (Child Table)
   - ID (INT, PRIMARY KEY, IDENTITY)
   - BookId (INT, FOREIGN KEY → Books.ID)
   - UniqueKey (UNIQUEIDENTIFIER)
   - IsAvailable (BIT)

6. Rentals (Transaction Table)
   - ID (INT, PRIMARY KEY, IDENTITY)
   - CustomerId (INT, FOREIGN KEY → Customers.ID)
   - StockId (INT, FOREIGN KEY → Stocks.ID)
   - RentalDate (DATETIME)
   - ReturnedDate (DATETIME, NULLABLE)
   - Status (NVARCHAR)

Foreign Key Relationships:
- Books → Authors (BookId)
- Books → Genres (GenreId)
- Stocks → Books (BookId)
- Rentals → Customers (CustomerId)
- Rentals → Stocks (StockId)
```

### Test Data
- **Genres**: 2 genres (ID=10: "General", ID=11: "Fiction") - auto-seeded
- **Authors**: 20 pre-seeded records with full biographical data
- **Books**: Generated dynamically during tests with FK to Authors (GenreId=10)
- **Customers**: 20 pre-seeded customer records
- **Stocks**: ~30 stock items (generated when books exist) - auto-seeded
- **Rentals**: 0 initial records (table is empty at start)
- **Test Records**: All marked with timestamp-based unique identifiers or "Test*" prefixes

### JMeter Test Configuration
```
Test Duration: 600 seconds (10 minutes)
Threads per Group: 50
Ramp-up Time: 10 seconds
Constant Timer: 2000ms (2-second pacing between requests)
JDBC Pool: 50 connections, 10s timeout

Thread Groups:
1. Authors Operations (25% of load) - Full CRUD with Create-Delete pattern
2. Books Operations (35% of load) - Full CRUD with Create-Delete pattern  
3. Customers Operations (20% of load) - Read-only (SELECT queries)
4. Stocks Operations (10% of load) - Read-only (SELECT queries)
5. Rentals Operations (5% of load) - Read-only (SELECT queries)
6. Genres Operations (5% of load) - Read-only (SELECT queries)
```

---

## Test Cases

### TC-001: Database Cleanup and Initialization

**Objective**: Verify database can be properly cleaned and initialized for testing

**Pre-conditions**:
- Database exists and is accessible
- User has DELETE permissions on all tables

**Test Steps**:
1. Execute `python run_and_monitor_db_test.py --env target --cleanup`
2. Verify all records are deleted from Rentals table (FK child)
3. Verify all records are deleted from Stocks table (FK child)
4. Verify all records are deleted from Books table
5. Verify all records are deleted from Authors table
6. Verify all records are deleted from Customers table
7. Verify identity seeds are reset (if permissions allow)

**Expected Results**:
- Rentals table: 0 records
- Stocks table: 0 records
- Books table: 0 records
- Authors table: 0 records
- Customers table: 0 records
- Genres table: Preserved (not deleted)
- Deletion respects foreign key constraints (correct order)
- No errors during cleanup
- Success message displayed

**Success Criteria**:   All tables are empty, identity reset successful

---

### TC-002: Database Seeding

**Objective**: Verify database can be seeded with initial test data (Genres, Authors, Books, Customers, Stocks)

**Pre-conditions**:
- Database is clean (TC-001 completed)
- User has INSERT permissions on all tables

**Test Steps**:
1. Run seeding process (automatic during test execution unless --no-seed specified)
2. Verify 2 genres are present (ID=10: "General", ID=11: "Fiction")
3. Verify 20 author records are inserted with complete biographical data
4. Verify 20 books are created with FK to authors and GenreId=10
5. Verify 20 customer records are inserted with registration details
6. Verify 30 stocks are created (linked to books)

**Expected Results**:
- Genres table: 2 records (General, Fiction) with IDs 10 and 11
- Authors table: 20 records with complete data (FirstName, LastName, BirthDate, Nationality, Bio, Email, Affiliation)
- Books table: 20 records with valid AuthorId and GenreId=10
- Customers table: 20 records with unique emails and identity cards
- Stocks table: 30 records linked to books
- All GUIDs properly generated
- No duplicate records
- All foreign key relationships valid

**Success Criteria**:
-   All tables seeded successfully
-   Foreign keys properly linked (Books→Authors, Books→Genres, Stocks→Books)
-   No constraint violations
-   Genre IDs are 10 and 11 (not 1)

---

### TC-003: Basic Load Test - Default Configuration

**Objective**: Execute a basic load test with default settings

**Test Configuration**:
```
Connections: 20
Operations per Connection: 100
Test Type: Mixed
Duration: 120 seconds
Total Operations: 2000
```

**Test Steps**:
1. Execute: `python run_and_monitor_db_test.py`
2. Monitor console output for progress
3. Wait for completion
4. Review generated CSV and summary files

**Expected Results**:
- All 2000 operations complete successfully
- Success rate > 95%
- Average response time < 100ms
- No deadlocks detected
- Results saved to `database_test_results/` directory

**Success Criteria**: 
-   >95% success rate
-   Response time within acceptable range
-   All files generated correctly

---

### TC-004: High Concurrency Load Test

**Objective**: Test database behavior under high concurrent load

**Test Configuration**:
```
Connections: 100
Operations per Connection: 500
Test Type: Mixed
Duration: 300 seconds
Total Operations: 50,000
```

**Test Steps**:
1. Execute: `python run_and_monitor_db_test.py -c 100 -o 500 -d 300`
2. Monitor system resources
3. Track error rates and response times
4. Analyze results

**Expected Results**:
- System handles high concurrency without crashes
- Degradation in response time is gradual and predictable
- Lock waits may increase but remain manageable
- CPU and memory stay within acceptable bounds

**Success Criteria**:
-   >90% success rate maintained
-   No critical errors or crashes
-   Response time P95 < 500ms

---

### TC-005: Read-Only Load Test

**Objective**: Measure SELECT query performance

**Test Configuration**:
```
Connections: 30
Operations per Connection: 200
Test Type: Read
Duration: 120 seconds
```

**Test Steps**:
1. Execute: `python run_and_monitor_db_test.py -c 30 -o 200 -t Read`
2. Monitor query execution times
3. Analyze different SELECT patterns:
   - SELECT TOP 100
   - SELECT by ID
   - SELECT with JOIN
   - SELECT COUNT(*)

**Expected Results**:
- Fastest response times among all test types
- Minimal lock contention
- High throughput (operations/second)
- Low CPU utilization

**Success Criteria**:
-   Average response time < 50ms
-   >99% success rate
-   Throughput > 100 ops/sec

---

### TC-006: Write-Intensive Load Test

**Objective**: Test INSERT operation performance and throughput

**Test Configuration**:
```
Connections: 20
Operations per Connection: 300
Test Type: Write
Duration: 150 seconds
```

**Test Steps**:
1. Execute: `python run_and_monitor_db_test.py -c 20 -o 300 -t Write`
2. Monitor INSERT performance
3. Track transaction log growth
4. Verify data integrity

**Expected Results**:
- All INSERTs complete successfully
- Higher response times than reads (expected)
- Increased page writes and transaction counts
- No constraint violations

**Success Criteria**:
-   >95% success rate
-   Average response time < 150ms
-   All inserted records are valid

---

### TC-007: Update Operations Test

**Objective**: Validate UPDATE statement performance

**Test Configuration**:
```
Connections: 15
Operations per Connection: 200
Test Type: UPDATE
Duration: 120 seconds
```

**Test Steps**:
1. Seed database with test data
2. Execute: `python run_and_monitor_db_test.py -c 15 -o 200 -t UPDATE`
3. Monitor lock waits and blocking
4. Verify updated values

**Expected Results**:
- UPDATEs complete without excessive locking
- Moderate response times
- Lock waits tracked and logged
- Data consistency maintained

**Success Criteria**:
-   >95% success rate
-   Lock wait count < 100
-   No deadlocks

---

### TC-008: Delete Operations Test

**Objective**: Test DELETE operation performance

**Test Configuration**:
```
Connections: 10
Operations per Connection: 100
Test Type: DELETE
Duration: 120 seconds
```

**Test Steps**:
1. Pre-populate database with test records
2. Execute: `python run_and_monitor_db_test.py -c 10 -o 100 -t DELETE`
3. Verify only test records are deleted
4. Check foreign key constraint handling

**Expected Results**:
- Only "Performance Test Book" records are deleted
- No errors from constraint violations
- Consistent performance
- Transaction log properly managed

**Success Criteria**:
-   >95% success rate
-   Only test data deleted
-   No constraint errors

---

### TC-009: Mixed Workload Test (Realistic Scenario)

**Objective**: Simulate real-world mixed operations

**Test Configuration**:
```
Connections: 50
Operations per Connection: 300
Test Type: Mixed
Duration: 240 seconds

Operation Distribution:
- 60% SELECT queries
- 20% INSERT operations
- 10% UPDATE operations
- 10% DELETE operations
```

**Test Steps**:
1. Execute: `python run_and_monitor_db_test.py -c 50 -o 300 -t Mixed -d 240`
2. Monitor all metrics simultaneously
3. Analyze operation type breakdown
4. Compare performance across operation types

**Expected Results**:
- Balanced workload distribution
- Different response times per operation type
- System handles mixed load efficiently
- No significant blocking or deadlocks

**Success Criteria**:
-   >95% overall success rate
-   Operation distribution matches expected ratios (±5%)
-   P95 response time < 200ms

---

### TC-010: Performance Monitoring Verification

**Objective**: Validate monitoring metrics are captured correctly

**Test Steps**:
1. Run any load test
2. Verify metrics_*.csv file is generated
3. Check all metric columns are populated:
   - timestamp
   - cpu_usage
   - memory_usage_mb
   - active_connections
   - batch_requests
   - page_reads
   - page_writes
   - transactions
   - lock_waits
   - deadlocks

**Expected Results**:
- Metrics collected every 5 seconds
- All values are numeric (except timestamp)
- No missing data points
- Summary statistics displayed at end

**Success Criteria**:
-   All metrics captured
-   No data gaps
-   Statistics calculated correctly

---

### TC-011: Stress Test - Maximum Connections

**Objective**: Find breaking point and maximum capacity

**Test Configuration**:
```
Connections: 200
Operations per Connection: 1000
Test Type: Mixed
Duration: 600 seconds
Total Operations: 200,000
```

**Test Steps**:
1. Execute: `python run_and_monitor_db_test.py -c 200 -o 1000 -d 600`
2. Monitor for failures and errors
3. Track resource exhaustion
4. Document degradation patterns

**Expected Results**:
- System may show degraded performance
- Error rate may increase
- Resource utilization near maximum
- System remains stable (no crashes)

**Success Criteria**:
-   >80% success rate maintained
-   System recovers after test
-   No data corruption

---

### TC-012: Results File Generation

**Objective**: Verify all output files are created correctly

**Test Steps**:
1. Run complete test cycle
2. Check `database_test_results/` directory
3. Verify file creation:
   - load_test_YYYYMMDD_HHMMSS.csv
   - summary_YYYYMMDD_HHMMSS.txt
   - metrics_YYYYMMDD_HHMMSS.csv

**Expected Results**:
- All three file types created
- Files contain valid data
- CSV files importable to Excel
- Summary file readable and formatted

**Success Criteria**:
-   All files present
-   No empty or corrupt files
-   Timestamps match test execution time

---

### TC-012a: Multi-Table Operation Distribution

**Objective**: Verify operations are distributed across all 4 main tables (Books, Customers, Rentals, Stocks)

**Test Configuration**:
```
Connections: 20
Operations per Connection: 100
Test Type: Mixed
Total Operations: 2000
```

**Test Steps**:
1. Execute: `python run_and_monitor_db_test.py --env target -c 20 -o 100 -t Mixed`
2. Review summary report for operation distribution
3. Verify operations across all tables:
   - Books operations (40% - SELECT, INSERT, UPDATE, DELETE)
   - Customer operations (25% - SELECT, INSERT, UPDATE, DELETE)
   - Rental operations (20% - SELECT, INSERT, UPDATE)
   - Stock operations (15% - SELECT, INSERT, UPDATE)

**Expected Results**:
- Operations distributed across all 4 table types
- Each table type shows multiple operation types
- Proper weighting: Books > Customers > Rentals > Stocks
- Foreign key operations succeed (Rentals referencing Customers/Stocks)

**Success Criteria**:
-   All 4 table types have operations
-   Operation distribution roughly matches weights (±10%)
-   >75% success rate across all table types
-   No orphaned FK records

---

### TC-012b: Customer Operations Performance

**Objective**: Test Customer table CRUD operations under load

**Test Configuration**:
```
Connections: 15
Operations per Connection: 150
Focus: Customer operations (INSERT, SELECT, UPDATE, DELETE)
```

**Test Steps**:
1. Seed customers (20 records)
2. Execute mixed operations
3. Monitor operations:
   - CUSTOMER_INSERT: New customer registrations
   - CUSTOMER_SELECT_BY_ID: Customer lookup
   - CUSTOMER_SELECT_BY_EMAIL: Email-based search
   - CUSTOMER_SELECT_ALL: List all customers
   - CUSTOMER_COUNT: Count operations
   - CUSTOMER_UPDATE: Modify customer details
   - CUSTOMER_DELETE: Remove customers (if no rentals)

**Expected Results**:
- All customer operations complete successfully
- Email uniqueness maintained
- UniqueKey (GUID) properly generated
- SELECT operations faster than INSERT/UPDATE

**Success Criteria**:
-   >90% success rate for SELECT operations
-   >80% success rate for INSERT operations
-   Average SELECT response < 10ms
-   Average INSERT response < 50ms

---

### TC-012c: Rental Transaction Performance

**Objective**: Test Rental transaction operations with FK constraints

**Test Configuration**:
```
Connections: 10
Operations per Connection: 100
Focus: Rental operations with FK validation
```

**Test Steps**:
1. Seed customers and stocks
2. Execute rental operations:
   - RENTAL_INSERT: Create new rentals (requires valid CustomerId and StockId)
   - RENTAL_SELECT_ACTIVE: Query active rentals
   - RENTAL_SELECT_BY_CUSTOMER: Customer rental history
   - RENTAL_UPDATE: Update rental status (Active → Returned)
   - RENTAL_COUNT: Count operations

**Expected Results**:
- Rental INSERTs validate FK constraints
- Cannot create rental with invalid CustomerId
- Cannot create rental with invalid StockId
- Status updates work correctly
- ReturnedDate set properly when status = 'Returned'

**Success Criteria**:
-   >85% success rate (some failures expected for invalid FKs)
-   All successful rentals have valid FK references
-   No orphaned rental records
-   Average response time < 100ms

---

### TC-012d: Stock Inventory Operations

**Objective**: Test Stock inventory management operations

**Test Configuration**:
```
Connections: 12
Operations per Connection: 120
Focus: Stock availability tracking
```

**Test Steps**:
1. Seed books and stocks (3 copies per book)
2. Execute stock operations:
   - STOCK_INSERT: Add new stock items
   - STOCK_SELECT_AVAILABLE: Find available books
   - STOCK_SELECT_BY_BOOK: Get all copies of a book
   - STOCK_UPDATE: Toggle availability
   - STOCK_COUNT: Count operations

**Expected Results**:
- Stock items properly linked to Books via BookId
- IsAvailable bit field works correctly
- UniqueKey (GUID) properly generated
- Multiple copies per book tracked correctly

**Success Criteria**:
-   >90% success rate
-   All stock items have valid BookId references
-   IsAvailable toggles work correctly
-   Average response time < 20ms

---

### TC-012e: Foreign Key Constraint Validation

**Objective**: Verify FK constraints are enforced under load

**Test Steps**:
1. Attempt to create Books with invalid AuthorId → Should fail
2. Attempt to create Rentals with invalid CustomerId → Should fail
3. Attempt to create Rentals with invalid StockId → Should fail
4. Attempt to create Stocks with invalid BookId → Should fail
5. Verify error messages are proper FK violations

**Expected Results**:
- All FK violations caught by database
- Proper error messages returned
- No orphaned records created
- Database maintains referential integrity

**Success Criteria**:
-   100% FK validation enforcement
-   No orphaned records after test
-   Clear error messages for violations

---

### TC-013: Error Handling and Recovery

**Objective**: Verify system handles errors gracefully

**Test Scenarios**:
1. **Invalid connection string**
   - Expected: Clear error message, graceful exit
   
2. **Database not found**
   - Expected: Connection error reported, no crash
   
3. **Insufficient permissions**
   - Expected: Permission error logged, partial results saved
   
4. **Interrupted test (Ctrl+C)**
   - Expected: Monitoring stops cleanly, partial results saved

**Success Criteria**:
-   No unhandled exceptions
-   Meaningful error messages
-   Partial results preserved

---

### TC-014: Statistical Accuracy

**Objective**: Validate statistical calculations are correct

**Test Steps**:
1. Run load test
2. Export results to Excel
3. Manually calculate:
   - Average response time
   - Median response time
   - 95th percentile
   - 99th percentile
   - Throughput
4. Compare with tool output

**Expected Results**:
- Manual calculations match tool output (±0.5%)
- Percentiles correctly calculated
- Throughput formula accurate

**Success Criteria**:
-   <1% variance from manual calculations
-   All statistics present in summary

---

## JMeter Test Cases

### TC-015: JMeter Basic Execution Test

**Objective**: Verify JMeter test plan executes successfully with 50 threads per group

**Pre-conditions**:
- JMeter installed and in PATH (jmeter.bat for Windows)
- SQL Server JDBC driver in JMeter lib folder (mssql-jdbc-12.6.1.jre11.jar)
- Database is accessible
- Database is seeded with test data

**Test Steps**:
1. Execute: `python run_and_monitor_db_test.py --env target --no-profiling`
2. Verify JMeter starts without errors
3. Monitor console for test progress
4. Wait for 10-minute test completion
5. Review generated files in jmeter_results/ directory

**Expected Results**:
- JMeter test runs for 600 seconds (10 minutes)
- 50 threads per group execute operations in parallel
- HTML report generated successfully
- No JDBC connection errors
- Summary statistics displayed

**Success Criteria**:
-   JMeter executes without errors
-   All output files created (JTL, HTML report, log)
-   >95% success rate in summary
-   Test runs for full 10 minutes

---

### TC-016: JMeter Test with System Profiling

**Objective**: Validate system performance monitoring during JMeter test execution

**Test Configuration**:
```
Tool: JMeter
Profiling: Enabled (Windows typeperf)
Duration: 600 seconds
Thread Groups: 6 (Authors, Books, Customers, Stocks, Rentals, Genres)
Threads per Group: 50
```

**Test Steps**:
1. Execute: `python run_and_monitor_db_test.py --env target`
2. Verify typeperf starts monitoring system metrics
3. Wait for 10-minute test completion
4. Verify performance data collection
5. Check performance graph generation

**Expected Results**:
- Performance monitoring starts before JMeter test
- Metrics collected every 1 second (CPU, Memory, Disk I/O, Network)
- Monitoring stops after test completion
- CSV file cleaned and processed (PDH headers removed)
- 4 performance graphs generated as PNG file

**Success Criteria**:
-   Performance data captured successfully for full test duration
-   Graphs generated without errors
-   All 4 metrics visible in 2x2 subplot layout
-   Clean CSV file created without PDH headers
-   Graphs show correlation with test load

---

### TC-017: JMeter Authors Thread Group - Full CRUD Performance

**Objective**: Validate Authors table full CRUD operations via JDBC (25% of total load)

**Test Configuration**:
```
Threads: 50
Duration: 600 seconds  
Ramp-up: 10 seconds
Constant Timer: 2000ms
Operation Mix (randomly selected):
- SELECT All (TOP 50)
- SELECT by ID
- COUNT
- INSERT (with NEWID, random data)
- UPDATE (Bio and Email)
- Create-Delete Transaction (INSERT followed by immediate DELETE)
```

**Test Steps**:
1. Review JMeter test plan Authors Thread Group
2. Execute JMeter test
3. Analyze HTML report for Authors operations
4. Check JTL file for individual request times
5. Verify data integrity after test
6. Confirm test records properly created and deleted

**Expected Results**:
- All Authors operations complete successfully
- SELECT queries fastest (<50ms average)
- INSERT creates records with unique AuthorId (GUID)
- UPDATE modifies only test records (FirstName LIKE 'TestAuthor%')
- Create-Delete transactions atomic (INSERT+DELETE as one unit)
- DELETE removes only test records (FirstName LIKE 'DeleteMe%')
- No orphaned records after test

**Success Criteria**:
-   >98% success rate for Authors operations
-   Average response time < 100ms
-   No FK constraint violations
-   Create-Delete pattern works correctly
-   Only test records affected by INSERT/UPDATE/DELETE

---

### TC-018: JMeter Books Thread Group - Full CRUD Performance

**Objective**: Validate Books table full CRUD operations via JDBC (35% of total load)

**Test Configuration**:
```
Threads: 50
Duration: 600 seconds
Ramp-up: 10 seconds
Constant Timer: 2000ms
Operation Mix (randomly selected):
- SELECT All (TOP 100)
- SELECT by ID
- SELECT with JOIN (Books + Authors)
- COUNT
- INSERT (with random AuthorId, Year, Price, Rating, GenreId=10)
- UPDATE (Price and Rating)
- Create-Delete Transaction (INSERT followed by immediate DELETE)
```

**Test Steps**:
1. Execute JMeter test
2. Focus on Books Thread Group results
3. Verify FK constraint to Authors works (SELECT TOP 1 ID FROM Authors ORDER BY NEWID())
4. Verify GenreId=10 is used (valid Genre FK)
5. Check UPDATE operations affect only test books (Title LIKE 'Test Book%')
6. Validate DELETE only removes test books (Title LIKE 'DeleteMe%')

**Expected Results**:
- All Books operations complete successfully
- SELECT queries fastest (<50ms average)
- JOIN queries show Authors data correctly
- INSERT respects FK constraints (valid AuthorId, GenreId=10)
- No FK constraint violations for GenreId (10 exists in Genres table)
- UPDATE modifies only test records
- Create-Delete transactions atomic
- DELETE removes only test records

**Success Criteria**:
-   >98% success rate for Books operations
-   Average response time < 120ms
-   No FK constraint errors for AuthorId or GenreId
-   JOIN queries execute successfully
-   No orphaned records after test

---

### TC-019: JMeter Customers Thread Group - Read-Only Performance

**Objective**: Test Customers table read operations via JDBC (20% of load)

**Test Configuration**:
```
Threads: 50
Duration: 600 seconds
Ramp-up: 10 seconds
Constant Timer: 2000ms
Operation Mix (randomly selected, read-only):
- SELECT All (TOP 50, ordered by RegistrationDate DESC)
- SELECT by ID
- SELECT by Email (LIKE '%test%')
- COUNT
```

**Test Steps**:
1. Execute JMeter test
2. Focus on Customers Thread Group results
3. Verify all operations are read-only (no INSERT/UPDATE/DELETE)
4. Analyze SELECT by Email LIKE pattern performance
5. Confirm COUNT operations return accurate results

**Expected Results**:
- All Customer operations complete successfully
- Only SELECT and COUNT queries executed
- Email LIKE searches work correctly with wildcards
- Fast response times (read-only operations)
- No data modifications

**Success Criteria**:
-   100% success rate for Customer read operations
-   Average response time < 50ms
-   No INSERT/UPDATE/DELETE operations executed
-   Database data unchanged after test

---

### TC-020: JMeter Stocks Thread Group - Read-Only Performance

**Objective**: Test Stocks table read operations via JDBC (10% of load)

**Test Configuration**:
```
Threads: 50
Duration: 600 seconds
Ramp-up: 10 seconds
Constant Timer: 2000ms
Operation Mix (randomly selected, read-only):
- SELECT All (TOP 100)
- SELECT Available only (WHERE IsAvailable=1)
- SELECT by BookId (FK lookup)
- COUNT
```

**Test Steps**:
1. Execute JMeter test
2. Focus on Stocks Thread Group results
3. Verify all operations are read-only (no INSERT/UPDATE/DELETE)
4. Analyze availability filtering performance (IsAvailable=1)
5. Verify BookId FK lookups work correctly

**Expected Results**:
- All Stock operations complete successfully
- Only SELECT and COUNT queries executed
- IsAvailable filtering returns correct results
- BookId FK references resolve properly
- Fast response times (read-only operations)

**Success Criteria**:
-   100% success rate for Stock read operations
-   Average response time < 50ms
-   No INSERT/UPDATE/DELETE operations executed
-   Database data unchanged after test

---

### TC-021: JMeter Rentals Thread Group - Read-Only Performance

**Objective**: Test Rentals table read operations via JDBC (5% of load)

**Test Configuration**:
```
Threads: 50
Duration: 600 seconds
Ramp-up: 10 seconds
Constant Timer: 2000ms
Operation Mix (randomly selected, read-only):
- SELECT All
- SELECT Active rentals only (WHERE ReturnedDate IS NULL)
- COUNT
```

**Test Steps**:
1. Execute JMeter test
2. Focus on Rentals Thread Group results
3. Verify all operations are read-only (no INSERT/UPDATE/DELETE)
4. Analyze Active rentals filtering performance
5. Confirm COUNT operations return accurate results

**Expected Results**:
- All Rental operations complete successfully
- Only SELECT and COUNT queries executed
- Active rental filtering works correctly
- Fast response times (read-only operations)
- No data modifications

**Success Criteria**:
-   100% success rate for Rental read operations
-   Average response time < 50ms
-   No INSERT/UPDATE/DELETE operations executed
-   Database data unchanged after test

---

### TC-022: JMeter Genres Thread Group - Read-Only Performance

**Objective**: Test Genres table read operations via JDBC (5% of load)

**Test Configuration**:
```
Threads: 50
Duration: 600 seconds
Ramp-up: 10 seconds
Constant Timer: 2000ms
Operation Mix (randomly selected, read-only):
- SELECT All
- SELECT by ID (Genre 10 or 11)
- COUNT
```

**Test Steps**:
1. Execute JMeter test
2. Focus on Genres Thread Group results
3. Verify all operations are read-only (no INSERT/UPDATE/DELETE)
4. Confirm only Genre IDs 10 and 11 exist
5. Analyze simple lookup performance

**Expected Results**:
- All Genre operations complete successfully
- Only SELECT and COUNT queries executed
- SELECT by ID returns correct Genre names (10='General', 11='Fiction')
- Fast response times (read-only operations)
- No data modifications

**Success Criteria**:
-   100% success rate for Genre read operations
-   Average response time < 50ms
-   No INSERT/UPDATE/DELETE operations executed
-   Database data unchanged after test

---

### TC-023: Create-Delete Transaction Pattern Validation

**Objective**: Verify atomic Create-Delete transactions leave no orphaned records

**Test Configuration**:
```
Authors Thread Group (25% load):
- Transaction Controller: "Create and Delete Author"
  - INSERT Author with FirstName='DeleteMe${__UUID}'
  - DELETE Author WHERE FirstName LIKE 'DeleteMe%'

Books Thread Group (35% load):
- Transaction Controller: "Create and Delete Book"
  - INSERT Book with Title='DeleteMe${__UUID}', GenreId=10
  - DELETE Book WHERE Title LIKE 'DeleteMe%'
```

**Test Steps**:
1. Execute JMeter test
2. Monitor Create-Delete transactions in results
3. After test completion, query database:
   - `SELECT * FROM Authors WHERE FirstName LIKE 'DeleteMe%'`
   - `SELECT * FROM Books WHERE Title LIKE 'DeleteMe%'`
4. Verify no orphaned "DeleteMe" records exist
5. Check transaction success rates

**Expected Results**:
- Create-Delete transactions complete atomically
- No "DeleteMe" records remain in database
- Transaction success rate >95%
- If transaction fails, both operations roll back
- No partial transactions (Create without Delete)

**Success Criteria**:
-   Zero orphaned "DeleteMe" records after test
-   Transaction success rate >95%
-   Average transaction time < 200ms
-   No partial transaction artifacts

---

### TC-024: Foreign Key Constraint Validation

**Objective**: Verify FK constraints are properly enforced in Books operations

**Test Configuration**:
```
Books Thread Group operations:
- INSERT Book with:
  - GenreId=10 (valid FK to Genres table)
  - AuthorId from SELECT TOP 1 (valid FK to Authors table)
- SELECT with JOIN to verify FK relationships:
  - Books → Authors
  - Books → Genres
```

**Test Steps**:
1. Execute JMeter test
2. Monitor Books INSERT operations
3. Verify all INSERTs use GenreId=10 (not 1)
4. Verify AuthorId is retrieved from existing Authors
5. Check JOIN queries return correct related data
6. Confirm no FK constraint violations

**Expected Results**:
- All Books INSERTs succeed with GenreId=10
- No "FK_dbo.Books_dbo.Genres_GenreId" constraint errors
- AuthorId references valid Authors records
- JOIN queries return matching Authors and Genres
- No orphaned Books with invalid FKs

**Success Criteria**:
-   100% success rate for Books INSERT (no FK errors)
-   All Books have GenreId=10 or 11 (valid Genres)
-   All Books have valid AuthorId references
-   JOIN queries return correct related data
-   No FK constraint violation errors in results

---

### TC-025: JMeter HTML Report Validation

**Objective**: Verify JMeter HTML report is generated correctly with all required sections

**Test Steps**:
1. Execute JMeter test
2. Open report_*/index.html in browser
3. Verify all sections present:
   - Dashboard (summary statistics)
   - Charts (Response Times Over Time, Throughput)
   - Statistics table
   - Errors (if any)
   - Top 5 Errors by Sampler
4. Check graphs are populated with data
5. Verify statistics accuracy

**Expected Results**:
- HTML report opens in browser
- All dashboard widgets show data
- Charts display time-series graphs
- Statistics table has all samplers listed
- Error section shows details (if errors occurred)
- Report is self-contained (can be shared)

**Success Criteria**:
-   All report sections present and functional
-   Graphs display correctly
-   Statistics match JTL file
-   Report can be archived and shared

---

### TC-026: JMeter Performance Graph Validation

**Objective**: Verify system performance graphs are generated correctly (Windows only)

**Test Steps**:
1. Execute: `python run_and_monitor_db_test.py --env target`
2. Wait for completion (10 minutes)
3. Locate performance_graphs_*.png file in jmeter_results/
4. Open image and verify:
   - 2×2 subplot layout
   - CPU Usage graph (top-left) with average line
   - Memory Usage graph (top-right) with average line
   - Disk I/O graph (bottom-left) with Read/Write lines
   - Network Activity graph (bottom-right) in MB/s
5. Check data is realistic and not all zeros

**Expected Results**:
- PNG file created in jmeter_results/
- All 4 graphs visible and properly labeled
- CPU shows percentage (0-100%)
- Memory shows percentage
- Disk shows operations/sec
- Network shows MB/s
- Average lines displayed on CPU and Memory
- Graphs have timestamps on X-axis

**Success Criteria**:
-   PNG file generated successfully
-   All 4 graphs present with data
-   Graphs are readable and properly formatted
-   File size reasonable (< 500KB)

---

### TC-027: JMeter Test Without Seeding

**Objective**: Test JMeter execution without re-seeding database (reuse existing data)

**Test Steps**:
1. Run initial test with seeding
2. Execute: `python run_and_monitor_db_test.py --env target --no-seed`
3. Verify test uses existing data
4. Check no seeding messages appear
5. Confirm test completes successfully

**Expected Results**:
- Seeding step skipped
- Test proceeds directly to JMeter execution
- Existing data used for operations
- Test completes faster (no seeding overhead)
- No errors from missing data

**Success Criteria**:
-   Test completes successfully
-   Seeding step skipped
-   Existing data sufficient for all operations
-   Execution time reduced

---

### TC-028: JMeter Test Without Performance Profiling

**Objective**: Test JMeter execution without system profiling (faster execution)

**Test Steps**:
1. Execute: `python run_and_monitor_db_test.py --env target --no-profiling`
2. Verify test runs without typeperf
3. Confirm no performance_graphs_*.png generated
4. Check test completes faster

**Expected Results**:
- System profiling skipped
- No typeperf process started
- No performance graphs generated
- Test completes successfully
- Faster execution time

**Success Criteria**:
-   Test completes successfully
-   Profiling step skipped
-   No performance graphs in output
-   JMeter results still generated

---

## Performance Benchmarks

### JMeter Testing - Expected Performance (50 threads per group, 10 minutes)

| Thread Group | Load % | Operations | Avg Response | Success Rate |
|--------------|--------|-----------|--------------|--------------|
| Authors (Full CRUD) | 25% | ~7,500 | <80ms | >98% |
| Books (Full CRUD) | 35% | ~10,500 | <100ms | >98% |
| Customers (Read-Only) | 20% | ~6,000 | <50ms | 100% |
| Stocks (Read-Only) | 10% | ~3,000 | <50ms | 100% |
| Rentals (Read-Only) | 5% | ~1,500 | <50ms | 100% |
| Genres (Read-Only) | 5% | ~1,500 | <50ms | 100% |
| **Total** | **100%** | **~30,000** | **<70ms** | **>98%** |

**Notes**:
- 50 threads per group with 2-second pacing = ~25 operations/min per thread
- 600 seconds duration = 10 minutes
- Approximate operation counts: 50 threads × 10 mins / 2 sec pacing × load percentage
- Authors and Books include Create-Delete transactions reducing effective operations
- Read-only operations (Customers, Stocks, Rentals, Genres) have 100% success rates
- CRUD operations (Authors, Books) may have <2% failures due to concurrency

### Operation Response Time Benchmarks

| Operation Type | Average | P95 | P99 | Max Acceptable |
|---------------|---------|-----|-----|----------------|
| SELECT TOP 100 | <30ms | <50ms | <80ms | 100ms |
| SELECT BY ID | <10ms | <20ms | <40ms | 50ms |
| SELECT WITH JOIN | <40ms | <70ms | <100ms | 150ms |
| SELECT COUNT | <20ms | <40ms | <60ms | 80ms |
| INSERT | <50ms | <100ms | <150ms | 200ms |
| UPDATE | <60ms | <120ms | <180ms | 250ms |
| DELETE | <40ms | <80ms | <120ms | 150ms |
| Create-Delete Transaction | <150ms | <250ms | <350ms | 450ms |

### System Performance Thresholds (JMeter Profiling)

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| CPU Usage | <60% | 60-85% | >85% |
| Memory Committed | <70% | 70-85% | >85% |
| Disk Reads/sec | <100 | 100-200 | >200 |
| Disk Writes/sec | <50 | 50-100 | >100 |
| Network MB/sec | <10 | 10-50 | >50 |

### Resource Utilization Thresholds

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| CPU Usage | <50% | 50-80% | >80% |
| Memory | <2GB | 2-4GB | >4GB |
| Active Connections | <100 | 100-200 | >200 |
| Lock Waits/sec | <10 | 10-50 | >50 |
| Deadlocks | 0 | 1-5 | >5 |

---

## Test Execution Checklist

### Before Testing (Common)
- [ ] SQL Server is running (remote server: 10.134.77.68:1433)
- [ ] Database exists (BookStore-Master)
- [ ] Network connectivity to remote SQL Server
- [ ] SQL authentication credentials valid (testuser)
- [ ] Sufficient disk space for results
- [ ] Configuration file exists (../db_config.json)

### Before JMeter Testing
- [ ] Apache JMeter 5.6.3+ installed
- [ ] JMeter added to system PATH (jmeter.bat accessible)
- [ ] SQL Server JDBC driver in JMeter lib/ folder (mssql-jdbc-12.6.1.jre11.jar)
- [ ] JMeter test plan exists (JMeter_DB_Mixed_Operations.jmx)
- [ ] Windows environment (for performance profiling)
- [ ] Python 3.7+ installed
- [ ] pyodbc package installed (`pip install -r requirements.txt`)

### During Testing
- [ ] Monitor console output for errors
- [ ] Check CPU/Memory on server (if monitoring)
- [ ] Observe response time trends
- [ ] Note any warnings or failures
- [ ] Watch for JDBC connection errors (JMeter)
- [ ] Verify typeperf is running (JMeter with profiling)

### After Testing
- [ ] Review JTL file (results_*.jtl)
- [ ] Open HTML report (report_*/index.html)
- [ ] Analyze summary statistics
- [ ] Check profiling data (performance_graphs_*.png)
- [ ] Review performance graphs (if generated)
- [ ] Compare against benchmarks
- [ ] Document any anomalies
- [ ] Clean up test data (optional with --cleanup)

---

## Test Data Summary

### What Gets Created
- **Genres**: 2 genres (ID=10: "General", ID=11: "Fiction") - created on first run
- **Authors**: 20 seeded records + test records during execution
  - Seeded: FirstName format "FirstName{1-20}", persistent across tests
  - Test records: FirstName format "TestAuthor${UUID}" (CRUD operations)
  - Delete records: FirstName format "DeleteMe${UUID}" (Create-Delete transactions)
- **Books**: 20 seeded records + test records during execution
  - Seeded: 20 books with valid AuthorId and GenreId=10
  - Test records: Title format "Test Book ${UUID}", GenreId=10 (CRUD operations)
  - Delete records: Title format "DeleteMe${UUID}", GenreId=10 (Create-Delete transactions)
- **Customers**: 20 seeded records (persistent across tests)
  - Format: FirstName "Customer{1-20}", LastName "Test{1-20}"
- **Stocks**: 30 seeded records (persistent across tests)
  - 1-2 copies per Book with IsAvailable=1

### What Gets Cleaned Up
- Running with `--cleanup` removes ALL data from all tables (FK-safe order)
- DELETE operations only remove "Performance Test Book" and "TestBook" records
- Create-Delete transactions remove "DeleteMe%" records atomically
- Regular cleanup recommended after major tests

---

## Success Criteria (Overall)

| Criteria | Target | Minimum Acceptable |
|----------|--------|-------------------|
| Success Rate | >99% | >95% |
| Average Response Time | <70ms | <150ms |
| P95 Response Time | <150ms | <300ms |
| Throughput | >50 ops/sec | >30 ops/sec |
| CPU Usage (avg) | <60% | <80% |
| Memory Usage (avg) | <3GB | <5GB |
| Deadlock Count | 0 | <5 |
| Test Completion | 100% | 100% |

---

## Common Issues and Solutions

### Issue 1: High Response Times
**Symptoms**: Average >200ms, P95 >500ms
**Possible Causes**: 
- Insufficient indexing
- Lock contention
- CPU/Memory constraints
**Solution**: Add indexes, reduce concurrency, optimize queries

### Issue 2: Connection Failures
**Symptoms**: Thread connection errors
**Possible Causes**:
- Max connections exceeded
- Connection string invalid
- Server not responding
**Solution**: Check connection limits, verify credentials

### Issue 3: Lock Waits/Deadlocks
**Symptoms**: High lock_waits counter, deadlock errors
**Possible Causes**:
- Concurrent UPDATEs on same records
- Long-running transactions
**Solution**: Reduce UPDATE concurrency, implement retry logic

### Issue 4: Foreign Key Constraint Errors
**Symptoms**: "FK_dbo.Books_dbo.Genres_GenreId constraint violated"
**Possible Causes**:
- Using invalid GenreId (e.g., GenreId=1 doesn't exist)
- Books INSERT using GenreId other than 10 or 11
**Solution**: Verify GenreId=10 or 11 in all Books INSERT operations

### Issue 5: JMeter Not Found in PATH
**Symptoms**: "JMeter not found in PATH"
**Possible Causes**:
- JMeter not installed
- JMeter bin folder not in PATH
- Windows requires jmeter.bat (not jmeter)
**Solution**: Add JMeter bin folder to PATH, verify jmeter.bat executable

### Issue 6: Memory Growth
**Symptoms**: Memory usage continuously increases
**Possible Causes**:
- Connection leaks
- Large result sets
- Transaction log growth
**Solution**: Verify connections close, limit result sizes

---

## Reporting Results

### Key Metrics to Report
1. **Test Configuration** (50 threads per group, 10 minutes, 2-second pacing)
2. **Success Rate** (%)
3. **Response Times** (avg, median, P95, P99)
4. **Throughput** (operations/second)
5. **Resource Utilization** (CPU, Memory peaks)
6. **Error Summary** (if any)
7. **Recommendations** (based on findings)

### Report Template
```
Test Date: [DATE]
Configuration: 50 threads per group, 10 minutes, 2-second pacing
Duration: 600 seconds
Total Operations: ~30,000

Results:
- Success Rate: [%]
- Avg Response Time: [X]ms
- P95 Response Time: [Y]ms
- Throughput: [Z] ops/sec

Thread Group Performance:
- Authors (Full CRUD): [%] success, [X]ms avg
- Books (Full CRUD): [%] success, [X]ms avg
- Customers (Read-Only): [%] success, [X]ms avg
- Stocks (Read-Only): [%] success, [X]ms avg
- Rentals (Read-Only): [%] success, [X]ms avg
- Genres (Read-Only): [%] success, [X]ms avg

Resource Usage:
- CPU: [X]% avg, [Y]% max
- Memory: [X]% avg, [Y]% max
- Disk I/O: [X] reads/sec, [Y] writes/sec
- Network: [X] MB/sec

Observations:
[Key findings]

Recommendations:
[Actions to take]
```

---

## Conclusion

This comprehensive test suite provides JMeter-based performance testing coverage across **6 main business tables** using JDBC. By executing these test cases, you can:

- **Validate database performance** under high concurrent load (50 threads per table)
- **Benchmark with industry standards** using JMeter's JDBC-based testing
- **Profile system-level performance** (CPU, Memory, Disk, Network) on Windows
- **Generate stakeholder reports** with JMeter's HTML reports and performance graphs
- **Identify bottlenecks** in multi-table scenarios
- **Verify foreign key constraint performance** under concurrent load with correct Genre IDs
- **Test referential integrity** with complex table relationships
- **Assess scalability** with configurable thread counts and durations
- **Monitor transaction behavior** with Create-Delete atomic patterns
- **Validate data integrity** with no orphaned test records

### Test Coverage Summary
- **Authors**: Full CRUD with Create-Delete transactions (25% load)
- **Books**: Full CRUD with FK validation (GenreId=10) and Create-Delete transactions (35% load)
- **Customers**: Read-Only operations (SELECT, COUNT) (20% load)
- **Stocks**: Read-Only operations with availability filtering (10% load)
- **Rentals**: Read-Only operations with active rental filtering (5% load)
- **Genres**: Read-Only operations (5% load)
- **Total**: ~30,000 operations over 10 minutes with 50 threads per group

| Table | Operations Tested | FK Relationships | Test Cases |
|-------|------------------|------------------|------------|
| **Authors** | INSERT (seed), SELECT | Parent to Books | TC-002, TC-003, TC-012e, TC-017 |
| **Books** | SELECT, INSERT, UPDATE, DELETE | Child of Authors/Genres, Parent to Stocks | TC-003, TC-005-008, TC-012a, TC-017 |
| **Genres** | INSERT (seed), SELECT | Parent to Books | TC-002, TC-003, TC-017 |
| **Customers** | SELECT, INSERT, UPDATE, DELETE | Parent to Rentals | TC-003, TC-012a, TC-012b, TC-018 |
| **Rentals** | SELECT, INSERT, UPDATE | Child of Customers/Stocks | TC-003, TC-012a, TC-012c, TC-012e, TC-019 |
| **Stocks** | SELECT, INSERT, UPDATE | Child of Books, Parent to Rentals | TC-003, TC-012a, TC-012d, TC-012e, TC-020 |

### Testing Mode Comparison

| Aspect | Python Testing | JMeter Testing |
|--------|---------------|----------------|
| **Protocol** | pyodbc (native ODBC) | JDBC |
| **Flexibility** | High (configurable) | Fixed (530 ops) |
| **Database Metrics** | Yes (DMVs) | No |
| **System Metrics** | No | Yes (Windows typeperf) |
| **HTML Reports** | No | Yes (charts, graphs) |
| **Use Cases** | Custom load patterns, rapid iteration | Standardized benchmarking, reporting |
| **Test Cases** | TC-001 to TC-014 | TC-015 to TC-024 |

### Operation Distribution in Mixed Tests

**Python Testing (Configurable)**:
- **Books**: 40% (primary table with full CRUD)
- **Customers**: 25% (active user management)
- **Rentals**: 20% (transaction processing)
- **Stocks**: 15% (inventory management)

**JMeter Testing (Fixed - 530 Operations)**:
- **Books Thread Group**: 200 operations (40%)
- **Customers Thread Group**: 150 operations (25%)
- **Rentals Thread Group**: 100 operations (20%)
- **Stocks Thread Group**: 80 operations (15%)

### Key Performance Indicators

**Python Testing Targets**:
- SELECT operations: < 30ms average
- INSERT operations: < 50ms average  
- UPDATE operations: < 60ms average
- DELETE operations: < 40ms average
- Overall success rate: > 95% under normal load
- Database metrics: CPU < 50%, Memory stable

**JMeter Testing Targets**:
- Total duration: 60-90 seconds (530 operations)
- Average response time: < 90ms
- Overall success rate: > 90%
- System metrics: CPU < 60%, Memory < 70% committed
- HTML report: All sections populated with data

**Resource Thresholds (Both Modes)**:
- CPU utilization: < 80% sustained
- Memory usage: Stable, no leaks
- Connection count: < configured max
- Lock waits: < 5% of operations
- Deadlocks: 0 (zero tolerance)
- FK constraint validation: 100% enforcement

### Typical Test Workflow

#### Python Load Testing Workflow
```bash
# 1. Clean database
python run_and_monitor_db_test.py --env target --cleanup

# 2. Run comprehensive load test
python run_and_monitor_db_test.py --env target -c 20 -o 100 -t Mixed -d 120

# 3. Review results
# - Check database_test_results/load_test_*.csv
# - Review database_test_results/summary_*.txt
# - Analyze database_test_results/metrics_*.csv

# 4. Run specific table tests if needed
python run_and_monitor_db_test.py --env target -c 10 -o 50 -t Books
```

#### JMeter Testing Workflow
```bash
# 1. Clean database
python run_and_monitor_db_test.py --env target --cleanup

# 2. Run JMeter test with profiling (Windows)
python run_and_monitor_db_test.py --tool jmeter --env target

# 3. Review results
# - Open jmeter_results/report_*/index.html (HTML report)
# - Check jmeter_results/performance_graphs_*.png (system metrics)
# - Review jmeter_results/results_*.jtl (raw data)

# 4. Run quick test without profiling
python run_and_monitor_db_test.py --tool jmeter --env target --no-profiling
```

#### Comprehensive Testing (Both Tools)
```bash
# 1. Cleanup
python run_and_monitor_db_test.py --env target --cleanup

# 2. Python baseline test
python run_and_monitor_db_test.py --env target -c 10 -o 50 -t Mixed

# 3. JMeter standardized test
python run_and_monitor_db_test.py --tool jmeter --env target

# 4. Compare results from both tools
# - Python: Database-level metrics (DMVs)
# - JMeter: System-level metrics (CPU, Memory, Disk, Network)
```

### Version History
- **v1.0** (Initial): Basic Books testing only
- **v2.0**: Comprehensive 6-table testing with FK validation, multi-table operations, and referential integrity testing
- **v3.0** (Current): Consolidated tool with dual testing modes (Python + JMeter), system performance profiling, and HTML reporting

---

**END OF TEST CASES DOCUMENT**
- Establish performance baselines
- Monitor system health during load
- Generate data-driven performance reports

Regular execution of these tests ensures database reliability and helps maintain performance SLAs.
