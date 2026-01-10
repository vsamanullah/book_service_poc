# BookService Test Data Integrity Module

## Overview
The **BookServiceTestDataIntegrity** module provides comprehensive automated testing tools for verifying database integrity, schema validation, and data consistency. This module is essential for:

- **Database Migration Verification**: Ensure zero data loss during database migrations
- **Schema Validation**: Verify database structure matches expected design
- **Data Integrity Testing**: Validate referential integrity, constraints, and data consistency
- **Test Data Management**: Create reproducible test datasets for various testing scenarios

---

## Module Components

### Core Scripts

| Script | Purpose | Key Features |
|--------|---------|--------------|
| **check_schema.py** | Quick schema inspection | Display table structures, columns, data types, and nullable constraints |
| **create_baseline.py** | Pre-migration baseline creation | Capture complete database state including schema, data, indexes, and foreign keys |
| **verify_migration.py** | Post-migration verification | Compare current state against baseline and generate detailed report |
| **populate_test_data.py** | Test data generation | Create N test records with realistic relationships and timestamps |

### Documentation

- **README.md** (this file): Setup guide and usage instructions
- **TEST_CASES.md**: Comprehensive test case documentation with pass/fail criteria
- **migration_testcase.md**: Detailed migration test scenarios and procedures

---

## Quick Start

### Prerequisites

**Required Software:**
- Python 3.8 or higher
- SQL Server ODBC Driver 17 or 18
- pyodbc library (`pip install pyodbc`)

**Database Access:**
- Valid SQL Server credentials (SQL or Windows Authentication)
- Appropriate permissions (SELECT, INSERT, DELETE for testing)

### Installation

```bash
# Navigate to module directory
cd BookServiceDataTesting\BookServiceTestDataIntegrity

# Install Python dependencies (if not already installed)
pip install pyodbc
```

### Configuration

The module uses `../db_config.json` for database connections. Ensure this file exists with your environment configurations:

```json
{
  "environments": {
    "source": {
      "server": "your-server:port",
      "database": "BookStore-Source",
      "username": "user",
      "password": "password",
      "driver": "ODBC Driver 18 for SQL Server",
      "encrypt": true,
      "trust_certificate": true
    },
    "target": {
      "server": "your-server:port",
      "database": "BookStore-Target",
      "username": "user",
      "password": "password",
      "driver": "ODBC Driver 18 for SQL Server",
      "encrypt": true,
      "trust_certificate": true
    },
    "local": {
      "server": "(localdb)\\MSSQLLocalDB",
      "database": "BookServiceContext",
      "driver": "ODBC Driver 17 for SQL Server",
      "trusted_connection": true
    }
  }
}
```

---

## Usage Guide

### 1. Schema Inspection

**Purpose**: Quickly view database table structures

```bash
python check_schema.py
```

**Output Example:**
```
=== Authors Table Structure ===
  Id                   int             NULL=NO
  Name                 nvarchar        NULL=NO
  Bio                  nvarchar        NULL=YES
  Nationality          nvarchar        NULL=YES

=== Books Table Structure ===
  Id                   int             NULL=NO
  Title                nvarchar        NULL=NO
  AuthorId             int             NULL=NO
  ISBN                 nvarchar        NULL=NO
  Price                decimal         NULL=NO
```

### 2. Create Baseline (Pre-Migration)

**Purpose**: Capture complete database state before migration

```bash
# Using environment configuration (recommended)
python create_baseline.py --env source

# Using direct connection string
python create_baseline.py --conn "DRIVER={ODBC Driver 18 for SQL Server};SERVER=server;DATABASE=db;UID=user;PWD=pass;..."

# Specify custom output file
python create_baseline.py --env source --output my_baseline.json
```

**Generated Files:**
- `baseline_YYYYMMDD_HHMMSS.json`: Complete database snapshot
- `baseline_YYYYMMDD_HHMMSS.log`: Detailed execution log

**Baseline Contents:**
- Row counts for all tables
- Data checksums (MD5) for data integrity verification
- Complete schema definitions (columns, types, constraints)
- Foreign key relationships
- Index definitions
- Timestamp and database connection info

### 3. Populate Test Data

**Purpose**: Create controlled test datasets for testing

```bash
# Create 25 authors with related data
python populate_test_data.py 25 --env source

# Create 100 authors with related data
python populate_test_data.py 100 --env local

# Using direct connection string
python populate_test_data.py 50 --conn "DRIVER={...};SERVER=...;..."
```

**Data Generation Pattern (for N authors):**
- **N Authors** with unique names, bios, and nationalities
- **2N Books** (2 books per author) with ISBNs, prices, ratings
- **N Customers** with email addresses and registration dates
- **6N Stocks** (3 copies per book, 2 branches)
- **~3N Rentals** (approximately 50% of stocks rented)
- **5 Genres** (Fiction, Non-Fiction, Science, History, Biography)

**Generated Files:**
- `populate_YYYYMMDD_HHMMSS.log`: Execution log with record counts

### 4. Verify Migration (Post-Migration)

**Purpose**: Compare post-migration state against baseline

```bash
# Using environment configuration
python verify_migration.py --env target

# Using direct connection string with specific baseline
python verify_migration.py --conn "DRIVER={...};..." --baseline baseline_20260110_143022.json

# Generate detailed report
python verify_migration.py --env target --report migration_report.json
```

**Verification Checks:**
- ✅ Row count comparison (no data loss)
- ✅ Data checksum verification (data integrity)
- ✅ Schema structure validation (columns, types, nullability)
- ✅ Foreign key relationship preservation
- ✅ Index definition consistency
- ✅ Referential integrity validation

**Generated Files:**
- `verification_YYYYMMDD_HHMMSS.log`: Test execution log
- `verification_report_YYYYMMDD_HHMMSS.json`: Detailed test results

**Sample Output:**
```
========================================
VERIFICATION SUMMARY
========================================
 Tests Passed: 32
 Tests Failed: 0
 Warnings: 2
 Overall Status: PASSED WITH WARNINGS

✓ Authors: Row count matched (100 records)
✓ Authors: Data checksum matched
✓ Books: Row count matched (200 records)
✓ Books: Data checksum matched
⚠ Indexes: New index found on Books.ISBN (non-critical)
```

---

## Typical Workflows

### Workflow 1: Database Migration Testing

```bash
# Step 1: Populate source database with test data
python populate_test_data.py 50 --env source

# Step 2: Create baseline snapshot
python create_baseline.py --env source --output pre_migration_baseline.json

# Step 3: Perform your database migration
# (External migration process)

# Step 4: Verify migration integrity
python verify_migration.py --env target --baseline pre_migration_baseline.json

# Step 5: Review results
# Check verification_YYYYMMDD_HHMMSS.log for detailed results
```

### Workflow 2: Schema Validation

```bash
# Step 1: Inspect current schema
python check_schema.py

# Step 2: Create schema baseline
python create_baseline.py --env local

# (Make schema changes)

# Step 3: Verify schema changes
python verify_migration.py --env local --baseline baseline_YYYYMMDD_HHMMSS.json
```

### Workflow 3: Data Integrity Continuous Testing

```bash
# Daily baseline creation
python create_baseline.py --env production --output baselines/daily_$(date +%Y%m%d).json

# Compare against previous day
python verify_migration.py --env production --baseline baselines/daily_20260109.json
```

---

## Testing Scenarios Covered

### 1. **Row Count Verification**
- **Test**: Compare record counts in all tables
- **Pass Criteria**: Exact match between baseline and current
- **Tables**: Authors, Books, Genres, Customers, Rentals, Stocks

### 2. **Data Checksum Validation**
- **Test**: MD5 checksum of sorted data for each table
- **Pass Criteria**: Checksums match (proves no data corruption)
- **Sensitivity**: Detects any change in data content

### 3. **Schema Structure Validation**
- **Test**: Compare column definitions, data types, nullability
- **Pass Criteria**: All columns match baseline definition
- **Detects**: Missing columns, type changes, constraint changes

### 4. **Foreign Key Integrity**
- **Test**: Validate all foreign key relationships
- **Pass Criteria**: All FK relationships preserved
- **Relationships Tested**:
  - Books → Authors (AuthorId)
  - Books → Genres (GenreId)
  - Stocks → Books (BookId)
  - Rentals → Customers (CustomerId)
  - Rentals → Stocks (StockId)

### 5. **Index Validation**
- **Test**: Compare index definitions
- **Pass Criteria**: Critical indexes present
- **Note**: New indexes generate warnings, not failures

### 6. **Referential Integrity**
- **Test**: Validate no orphaned records
- **Pass Criteria**: All foreign key references valid
- **Critical For**: Data consistency and application stability

---

## Database Schema

### Main Business Tables

| Table | Primary Key | Foreign Keys | Description |
|-------|-------------|--------------|-------------|
| **Authors** | Id (int) | None | Author master data |
| **Books** | Id (int) | AuthorId → Authors<br>GenreId → Genres | Book catalog |
| **Genres** | Id (int) | None | Book genre categories |
| **Customers** | Id (int) | None | Customer records |
| **Stocks** | Id (int) | BookId → Books | Book inventory |
| **Rentals** | Id (int) | CustomerId → Customers<br>StockId → Stocks | Rental transactions |

### Supporting Tables

- **Users**: Application user accounts
- **Roles**: User role definitions  
- **UserRoles**: User-role assignments
- **Errors**: Application error logs
- **__MigrationHistory**: EF migration tracking

---

## Troubleshooting

### Common Issues

#### 1. **Connection Failures**

**Error**: `Unable to connect to database`

**Solutions**:
- Verify SQL Server is running and accessible
- Check firewall settings (port 1433)
- Confirm credentials in db_config.json
- Test connectivity: `telnet server 1433`
- Verify ODBC driver installation: `odbcinst -q -d`

#### 2. **Baseline File Not Found**

**Error**: `Baseline file 'baseline_*.json' not found`

**Solutions**:
- Run `create_baseline.py` first
- Use `--baseline` flag to specify correct file path
- Check file permissions

#### 3. **Schema Mismatch Detected**

**Error**: `Schema validation failed: Column mismatch`

**Solutions**:
- This is expected if schema was intentionally changed
- Review the detailed log for specific differences
- Update baseline if changes are correct: re-run `create_baseline.py`

#### 4. **Checksum Mismatch**

**Error**: `Data checksum mismatch for table Books`

**Causes**:
- Data was modified during migration
- Timestamp fields auto-updated
- Floating-point precision issues

**Solutions**:
- Review detailed log for affected records
- Investigate data modification source
- Consider if timestamp changes are acceptable

#### 5. **Python/ODBC Issues**

**Error**: `pyodbc.Error: ('IM002', '[IM002] [Microsoft][ODBC Driver Manager] Data source name not found')`

**Solutions**:
```bash
# Windows: Install ODBC Driver 18
# Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

# Verify installed drivers
odbcinst -q -d

# Update driver name in db_config.json if needed
```

---

## Best Practices

### 1. **Always Create Baselines Before Changes**
```bash
# Before any migration or schema change
python create_baseline.py --env production --output backups/baseline_pre_release_v2.5.json
```

### 2. **Use Descriptive Baseline Names**
```bash
# Include context in filename
python create_baseline.py --env prod --output baseline_before_v3_migration.json
```

### 3. **Archive Baseline Files**
```bash
# Keep baselines for audit trail
mkdir -p baselines/2026/january
mv baseline_*.json baselines/2026/january/
```

### 4. **Review Logs Thoroughly**
- Even if verification passes, review warnings
- Check for non-critical differences (like new indexes)
- Monitor execution time for performance issues

### 5. **Test in Non-Production First**
```bash
# Test migration process on non-prod environment first
python populate_test_data.py 100 --env staging
python create_baseline.py --env staging
# (perform migration on staging)
python verify_migration.py --env staging
```

### 6. **Regular Integrity Checks**
```bash
# Schedule weekly integrity verification
# Create cron job or scheduled task
python verify_migration.py --env production --baseline baselines/weekly_baseline.json
```

---

## Output Files Reference

| File Pattern | Generated By | Purpose |
|--------------|--------------|---------|
| `baseline_YYYYMMDD_HHMMSS.json` | create_baseline.py | Database snapshot |
| `baseline_YYYYMMDD_HHMMSS.log` | create_baseline.py | Baseline creation log |
| `verification_YYYYMMDD_HHMMSS.log` | verify_migration.py | Verification results |
| `verification_report_YYYYMMDD_HHMMSS.json` | verify_migration.py | Detailed test results |
| `populate_YYYYMMDD_HHMMSS.log` | populate_test_data.py | Data population log |

---

## Performance Considerations

- **Baseline Creation**: ~5-30 seconds depending on data volume
- **Verification**: ~10-60 seconds depending on data volume
- **Data Population**: ~1-5 seconds per 100 records
- **Network Latency**: Add 2-10 seconds for remote database connections

**Optimization Tips**:
- Run during off-peak hours for large databases
- Use local database copies for faster execution
- Limit test data size for quick iterations

---

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Verify Database Migration
  run: |
    cd BookServiceDataTesting/BookServiceTestDataIntegrity
    python verify_migration.py --env staging --baseline baselines/pre_deploy.json
    if [ $? -ne 0 ]; then
      echo "Migration verification failed!"
      exit 1
    fi
```

### Azure DevOps Example
```yaml
- task: PythonScript@0
  displayName: 'Verify Migration Integrity'
  inputs:
    scriptSource: 'filePath'
    scriptPath: 'BookServiceDataTesting/BookServiceTestDataIntegrity/verify_migration.py'
    arguments: '--env $(Environment) --baseline $(BaselineFile)'
```

---

## Support and Contact

For questions, issues, or suggestions:
- Review detailed logs in generated `.log` files
- Check **TEST_CASES.md** for specific test case details
- Consult **migration_testcase.md** for migration-specific scenarios

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2026 | Initial release with core verification features |

---

## Related Documentation

- [TEST_CASES.md](TEST_CASES.md) - Comprehensive test case specifications
- [migration_testcase.md](migration_testcase.md) - Migration test procedures
- [../README.md](../README.md) - Parent module documentation

---

## License

This module is part of the BookService POC UniCredit test automation framework.
