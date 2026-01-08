================================================================================
DATABASE LOAD TEST & MONITORING TOOL
================================================================================

DESCRIPTION
-----------
This tool performs comprehensive database load testing and monitoring for SQL 
Server databases. It simultaneously runs load tests with concurrent connections 
while monitoring database performance metrics in real-time.

The tool works on both Windows and Linux platforms and is specifically designed
for testing the BookServiceContext database.


FEATURES
--------
- Concurrent database load testing with configurable connections
- Real-time performance monitoring (CPU, Memory, Connections, etc.)
- Multiple test types: Read, Write, Update, Delete, Mixed operations
- Detailed CSV reports for both load test results and monitoring metrics
- Statistical analysis with percentile calculations
- Database cleanup and seeding utilities
- Automatic results directory management


REQUIREMENTS
------------
- Python 3.6 or higher
- Required Python packages:
  * pyodbc
  * (standard library: argparse, threading, time, csv, random, statistics, 
     datetime, pathlib, concurrent.futures)

- SQL Server with ODBC Driver 17 or higher
- Database: BookServiceContext
- Tables: Books, Authors (with proper schema)

Installation:
  pip install pyodbc


DATABASE SCHEMA
---------------
The tool expects the following tables:

Authors Table:
  - Id (INT, PRIMARY KEY, IDENTITY)
  - Name (NVARCHAR)

Books Table:
  - Id (INT, PRIMARY KEY, IDENTITY)
  - Title (NVARCHAR)
  - AuthorId (INT, FOREIGN KEY -> Authors.Id)
  - Price (DECIMAL)
  - Year (INT)
  - Genre (NVARCHAR)


USAGE
-----

Basic Usage:
  python run_and_monitor_db_test.py

With Custom Parameters:
  python run_and_monitor_db_test.py -c 50 -o 200 -t Mixed -d 180

Cleanup Database:
  python run_and_monitor_db_test.py --cleanup


COMMAND LINE OPTIONS
--------------------
-c, --connections <number>
    Number of concurrent database connections
    Default: 20

-o, --operations <number>
    Number of operations each connection will perform
    Default: 100

-t, --test-type <type>
    Type of test to run
    Options: Read, Write, Update, Delete, Mixed, SELECT, INSERT, UPDATE, DELETE
    Default: Mixed

-d, --duration <seconds>
    How long to run the monitoring (in seconds)
    Default: 120

-s, --connection-string <string>
    Custom database connection string
    Default: Driver={ODBC Driver 17 for SQL Server};
             Server=(localdb)\MSSQLLocalDB;
             Database=BookServiceContext;
             Trusted_Connection=yes;

--database <name>
    Database name for monitoring
    Default: BookServiceContext

--cleanup
    Clean up all records from Books and Authors tables
    Use this before or after testing to reset the database


TEST TYPES
----------
Read / SELECT:
  - Performs various SELECT queries (TOP 100, by ID, with JOIN, COUNT)

Write / INSERT:
  - Inserts new book records into the database

Update / UPDATE:
  - Updates book prices for random records

Delete / DELETE:
  - Deletes test records (only records created by the test)

Mixed:
  - Combination of all operations with weighted distribution:
    * 60% SELECT operations
    * 20% INSERT operations
    * 10% UPDATE operations
    * 10% DELETE operations


WORKFLOW
--------
The tool follows this sequence:

1. Database Cleanup
   - Removes all existing records from Books and Authors tables
   - Resets identity seeds

2. Database Seeding
   - Adds 20 author records for testing

3. Load Test Execution
   - Spawns multiple concurrent worker threads
   - Each thread performs specified number of operations
   - Records timing and success/failure for each operation

4. Performance Monitoring
   - Runs in parallel with load test
   - Samples metrics every 5 seconds
   - Tracks:
     * CPU usage percentage
     * Memory usage in MB
     * Active database connections
     * Batch requests per second
     * Page reads/writes per second
     * Transactions per second
     * Lock waits and deadlocks


OUTPUT FILES
------------
All results are saved in the 'database_test_results/' directory:

load_test_YYYYMMDD_HHMMSS.csv
  - Detailed results for each operation
  - Columns: thread_id, operation_number, operation_type, duration_ms, 
             status, timestamp, error

summary_YYYYMMDD_HHMMSS.txt
  - Statistical summary of the load test
  - Response time percentiles (95th, 99th)
  - Throughput calculations
  - Operation type breakdown

metrics_YYYYMMDD_HHMMSS.csv
  - Performance monitoring data
  - Columns: timestamp, cpu_usage, memory_usage_mb, active_connections,
             batch_requests, page_reads, page_writes, transactions,
             lock_waits, deadlocks


EXAMPLES
--------

Example 1: Quick test with default settings
  python run_and_monitor_db_test.py

Example 2: Heavy load test
  python run_and_monitor_db_test.py -c 100 -o 500 -d 300

Example 3: Read-only test
  python run_and_monitor_db_test.py -c 30 -o 200 -t Read

Example 4: Write-intensive test
  python run_and_monitor_db_test.py -c 20 -o 300 -t Write

Example 5: Cleanup database only
  python run_and_monitor_db_test.py --cleanup


PERFORMANCE METRICS EXPLAINED
------------------------------
CPU Usage:
  SQL Server CPU utilization percentage

Memory Usage:
  Physical memory used by SQL Server process in MB

Active Connections:
  Number of active user connections to the database

Batch Requests/sec:
  Number of T-SQL batches received per second

Page Reads/Writes:
  Database page I/O operations per second

Transactions/sec:
  Number of transactions started per second

Lock Waits:
  Number of times SQL Server waited for locks

Deadlocks:
  Number of deadlock incidents detected


TROUBLESHOOTING
----------------
Connection Errors:
  - Verify SQL Server is running
  - Check connection string is correct
  - Ensure ODBC Driver 17 is installed
  - Verify database exists and is accessible

Permission Errors:
  - Ensure user has appropriate database permissions
  - Need SELECT, INSERT, UPDATE, DELETE permissions on Books and Authors

Performance Issues:
  - Reduce number of concurrent connections (-c parameter)
  - Reduce operations per connection (-o parameter)
  - Check database server resources (CPU, Memory, Disk)

Import Errors:
  - Install pyodbc: pip install pyodbc
  - Ensure Python 3.6+ is installed


BEST PRACTICES
--------------
1. Always run cleanup before major tests to start with clean state
2. Start with lower connection counts and gradually increase
3. Monitor system resources during testing
4. Review both load test and monitoring results together
5. Run tests during off-peak hours for production systems
6. Keep monitoring duration longer than expected test duration
7. Document your test configuration for reproducibility


NOTES
-----
- The tool automatically creates the 'database_test_results' directory
- Test records are marked with "Performance Test Book" prefix
- DELETE operations only remove test-generated records
- Monitoring samples are taken every 5 seconds
- All timestamps are in local system time
- CSV files can be imported into Excel or other analysis tools


SUPPORT & MAINTENANCE
---------------------
For issues or questions, refer to:
- SQL Server performance documentation
- pyodbc documentation
- Database administrator


VERSION INFORMATION
-------------------
Script: run_and_monitor_db_test.py
Compatible with: SQL Server 2016+, LocalDB
Python: 3.6+
Last Updated: 2025


================================================================================
