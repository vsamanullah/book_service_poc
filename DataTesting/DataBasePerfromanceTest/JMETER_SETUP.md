# JMeter Database Performance Testing Setup

## Overview
This setup enables direct database performance testing using JMeter's JDBC samplers to test SQL Server database operations across all tables (Books, Authors, Customers, Rentals, Stocks).

## Prerequisites

### 1. Install JMeter
Download and install Apache JMeter from: https://jmeter.apache.org/download_jmeter.cgi

**Windows:**
```powershell
# Download JMeter 5.6.3
# Extract to C:\Tools\apache-jmeter-5.6.3
# Add to PATH
$env:PATH += ";C:\Tools\apache-jmeter-5.6.3\bin"
```

### 2. Download SQL Server JDBC Driver

**Required:** Microsoft JDBC Driver for SQL Server

Download from: https://learn.microsoft.com/en-us/sql/connect/jdbc/download-microsoft-jdbc-driver-for-sql-server

**Installation Steps:**
1. Download `mssql-jdbc-12.6.1.jre11.jar` (or latest version)
2. Place the JAR file in JMeter's `lib` directory:
   - Windows: `C:\Tools\apache-jmeter-5.6.3\lib\`
   - Linux: `/opt/apache-jmeter-5.6.3/lib/`

**Quick Download:**
```powershell
# Create lib directory if not exists
New-Item -ItemType Directory -Force -Path "C:\Tools\apache-jmeter-5.6.3\lib"

# Download JDBC driver
Invoke-WebRequest -Uri "https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.6.1.jre11/mssql-jdbc-12.6.1.jre11.jar" -OutFile "C:\Tools\apache-jmeter-5.6.3\lib\mssql-jdbc-12.6.1.jre11.jar"
```

### 3. Verify Installation
```powershell
jmeter --version
```

## Test Files

### JMeter Test Plan
- **JMeter_DB_Mixed_Operations.jmx** - Mixed operations across all tables with weighted distribution

### Configuration
Database connection settings are configured in the test plan:
- **Server:** 10.134.77.68:1433
- **Database:** BookStore-Master
- **Username:** testuser
- **Password:** TestDb@26#!
- **Driver:** com.microsoft.sqlserver.jdbc.SQLServerDriver

These values match the `db_config.json` "target" environment.

## Test Plan Structure

### Thread Groups (Weighted Distribution)
1. **Books Operations (40%)** - 10 threads × 20 loops = 200 operations
   - SELECT TOP 100, SELECT by ID, SELECT with JOIN, COUNT
   - INSERT, UPDATE, DELETE

2. **Customers Operations (25%)** - 10 threads × 15 loops = 150 operations
   - SELECT All, SELECT by ID, SELECT by Email, COUNT
   - INSERT, UPDATE, DELETE

3. **Rentals Operations (20%)** - 10 threads × 10 loops = 100 operations
   - SELECT All, SELECT by Customer, SELECT Active, COUNT
   - UPDATE (Return Book)

4. **Stocks Operations (15%)** - 10 threads × 8 loops = 80 operations
   - SELECT All, SELECT by Book, SELECT Available, COUNT
   - UPDATE Availability

**Total Operations:** 530

### JDBC Connection Pool
- **Pool Size:** 10 connections
- **Timeout:** 10 seconds
- **Connection Properties:** encrypt=true;trustServerCertificate=true

## Running Tests

### GUI Mode (Testing/Debugging)
```powershell
jmeter -t JMeter_DB_Mixed_Operations.jmx
```

### Command Line Mode (Performance Testing)
```powershell
# Create results directory
New-Item -ItemType Directory -Force -Path "jmeter_results"

# Run test
jmeter -n -t JMeter_DB_Mixed_Operations.jmx `
  -l jmeter_results/results.jtl `
  -j jmeter_results/jmeter.log `
  -e -o jmeter_results/html_report
```

### With Custom Parameters
```powershell
# Override database settings
jmeter -n -t JMeter_DB_Mixed_Operations.jmx `
  -JDB_SERVER=10.134.77.68 `
  -JDB_PORT=1433 `
  -JDB_NAME=BookStore-Master `
  -JDB_USER=testuser `
  -JDB_PASSWORD="TestDb@26#!" `
  -l jmeter_results/results.jtl `
  -e -o jmeter_results/html_report
```

## Using Python Script

Run the automated script that prepares the database and executes JMeter:

```powershell
python run_jmeter_db_test.py
```

Options:
```powershell
# Specify environment
python run_jmeter_db_test.py --env target

# Custom thread count
python run_jmeter_db_test.py --threads 20

# Custom loop count
python run_jmeter_db_test.py --loops 50

# Skip cleanup
python run_jmeter_db_test.py --no-cleanup
```

## Test Operations

### Books Table Operations
- **SELECT TOP 100:** Retrieve first 100 books
- **SELECT by ID:** Find book by random ID (1-1000)
- **SELECT with JOIN:** Books with author information
- **COUNT:** Total books in database
- **INSERT:** Add new performance test book
- **UPDATE:** Modify book price
- **DELETE:** Remove performance test books

### Customers Table Operations
- **SELECT All:** Top 50 customers
- **SELECT by ID:** Find customer by ID
- **SELECT by Email:** Search customers by email pattern
- **COUNT:** Total customers
- **INSERT:** Add new test customer with GUID
- **UPDATE:** Modify customer email and mobile
- **DELETE:** Remove test customers

### Rentals Table Operations
- **SELECT All:** Recent 50 rentals
- **SELECT by Customer:** Rentals for specific customer
- **SELECT Active:** Currently active rentals
- **COUNT:** Total rentals
- **UPDATE:** Mark rental as returned

### Stocks Table Operations
- **SELECT All:** Top 50 stock items
- **SELECT by Book:** Stock for specific book
- **SELECT Available:** Available stock items
- **COUNT:** Total stock items
- **UPDATE:** Change availability status

## Viewing Results

### HTML Report
After test completes, open:
```
jmeter_results/html_report/index.html
```

### JTL File Analysis
Use JMeter GUI to analyze:
```powershell
jmeter -g jmeter_results/results.jtl -o jmeter_results/analysis_report
```

## Key Metrics

Monitor these metrics in the reports:
- **Throughput:** Operations per second
- **Response Time:** Average, Median, 90th, 95th, 99th percentile
- **Error Rate:** Percentage of failed operations
- **Concurrent Users:** Thread count
- **Connection Pool:** Utilization

## Troubleshooting

### Error: Cannot load JDBC driver
**Solution:** Ensure `mssql-jdbc-*.jar` is in JMeter's `lib` directory

### Error: Login failed for user
**Solution:** Verify credentials in test plan match `db_config.json`

### Error: Cannot open database
**Solution:** Check database name and server connectivity

### Low Performance
**Solution:** 
- Increase connection pool size
- Reduce thread count or loop count
- Check network latency
- Monitor server resources

## Comparison with Python Script

| Feature | JMeter | Python (run_and_monitor_db_test.py) |
|---------|--------|--------------------------------------|
| Thread Count | 10 per group (40 total) | Configurable (default 10) |
| Total Operations | 530 | Configurable (default 500) |
| Distribution | 40/25/20/15% | 40/25/20/15% |
| Monitoring | Via listeners | Real-time DB metrics |
| Reporting | HTML dashboard | CSV + text summary |
| Setup Complexity | Medium (JDBC driver) | Low (Python packages) |
| Execution | JMeter CLI | Python script |

## Best Practices

1. **Always seed the database** before running tests
2. **Run in non-GUI mode** for performance testing
3. **Monitor server resources** during test execution
4. **Use connection pooling** to simulate realistic load
5. **Cleanup test data** after completion
6. **Compare results** with baseline metrics

## Next Steps

1. Install JMeter and JDBC driver
2. Run test in GUI mode to verify connectivity
3. Execute full test in CLI mode
4. Analyze HTML report
5. Compare with Python script results
6. Tune parameters for your requirements
