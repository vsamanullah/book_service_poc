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
# Check target environment (default)
python check_schema.py --env target

# Check source environment
python check_schema.py --env source

# Check local environment
python check_schema.py --env local

# Using custom config file
python check_schema.py --env target --config /path/to/db_config.json
```

**Output Example:**
```
======================================================================
Checking Schema - Environment: TARGET
Database: BookStore-Master
Server: 10.134.77.68,1433
======================================================================

=== Authors Table Structure ===
  Column Name                    Data Type       Nullable   Max Length
  ------------------------------ --------------- ---------- ----------
  Id                             int             NO         N/A
  Name                           nvarchar        NO         -1

=== Books Table Structure ===
  Column Name                    Data Type       Nullable   Max Length
  ------------------------------ --------------- ---------- ----------
  Id                             int             NO         N/A
  Title                          nvarchar        NO         -1
  Year                           int             NO         N/A
  Price                          decimal         NO         N/A
  Genre                          nvarchar        YES        -1
  AuthorId                       int             NO         N/A

=== Customers Table Structure ===
  Column Name                    Data Type       Nullable   Max Length
  ------------------------------ --------------- ---------- ----------
  CustomerId                     int             NO         N/A
  FirstName                      nvarchar        YES        -1
  LastName                       nvarchar        YES        -1
  Email                          nvarchar        YES        -1
  Country                        nvarchar        YES        -1

=== Countries Table Structure ===
  Column Name                    Data Type       Nullable   Max Length
  ------------------------------ --------------- ---------- ----------
  CountryId                      int             NO         N/A
  CountryName                    nvarchar        YES        -1
```
### 2. Populate Test Data

**Purpose**: Create controlled test datasets for testing

```bash
# Populate target environment with 10 records (default)
python populate_test_data.py --count 10 --env target

# Populate source environment with 25 records
python populate_test_data.py --count 25 --env source

# Populate local environment with 100 records
python populate_test_data.py --count 100 --env local

# Using custom config file
python populate_test_data.py --count 50 --env target --config /path/to/db_config.json
```

**Data Generation Pattern (for N records with --count N):**
- **N Authors** with unique names
- **2N Books** (2 books per author) with titles, years, prices, genres, and author references
- **N Customers** with first names, last names, email addresses, and countries

**Important Notes:**
- ⚠ **This script DELETES all existing records** before populating
- All generated records have unique timestamp-based identifiers
- Maintains referential integrity with proper foreign key relationships

**Generated Files:**
- `populate_YYYYMMDD_HHMMSS.log`: Execution log with record counts

### 3. Create Baseline (Pre-Migration)

**Purpose**: Capture complete database state before migration

```bash
# Create baseline for source environment (recommended for pre-migration)
python create_baseline.py --env source

# Create baseline for target environment
python create_baseline.py --env target

# Create baseline for local environment
python create_baseline.py --env local

# Specify custom output filename
python create_baseline.py --env source --output my_baseline.json

# Using custom config file
python create_baseline.py --env source --config /path/to/db_config.json
```

**Generated Files:**
- `baseline_<env>_YYYYMMDD_HHMMSS.json`: Complete database snapshot (e.g., `baseline_source_20260110_165255.json`)
- `baseline_YYYYMMDD_HHMMSS.log`: Detailed execution log

**Baseline Contents:**
- Row counts for all tables
- Data checksums (MD5) for data integrity verification
- Complete schema definitions (columns, types, constraints)
- Foreign key relationships
- Index definitions
- Timestamp and database connection info



### 4. Verify Migration (Post-Migration)

**Purpose**: Compare post-migration state against baseline

```bash
# Verify target environment (auto-detects most recent baseline)
python verify_migration.py --env target

# Verify source environment
python verify_migration.py --env source

# Using specific baseline file
python verify_migration.py --env target --baseline baseline_source_20260110_165255.json

# Compare two baseline files directly (source vs target)
python verify_migration.py --source-baseline baseline_source_20260110_165255.json --target-baseline baseline_target_20260110_165305.json

# Using custom config file
python verify_migration.py --env target --config /path/to/db_config.json
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
======================================================================
✓ MIGRATION VERIFICATION PASSED
======================================================================
Environment: TARGET
No critical issues found. Migration integrity verified!
======================================================================
```

**Detailed Log Output:**
```
✓ Authors: Row count matched (25 records)
✓ Authors: Data checksum matched
✓ Books: Row count matched (22 records)
✓ Books: Data checksum matched
✓ Schema: All columns match baseline
✓ Foreign Keys: All relationships preserved
⚠ Indexes: New index found on Books.Title (non-critical)
```

---

## Typical Workflows

### Workflow 1: Database Migration Testing

```bash
# Step 1: Populate source database with test data
python populate_test_data.py --count 50 --env source

# Step 2: Create source baseline snapshot
python create_baseline.py --env source

# Step 3: Perform your database migration
# (External migration process - e.g., SSIS, Azure Data Factory, custom scripts)

# Step 4: Create target baseline snapshot
python create_baseline.py --env target

# Step 5: Compare source and target baselines
python verify_migration.py --source-baseline baseline_source_20260110_165255.json --target-baseline baseline_target_20260110_165305.json

# Alternative Step 5: Verify target against live database
python verify_migration.py --env target --baseline baseline_source_20260110_165255.json

# Step 6: Review results
# Check verification_YYYYMMDD_HHMMSS.log for detailed results
```

### Workflow 2: Schema Validation

```bash
# Step 1: Inspect current schema
python check_schema.py --env local

# Step 2: Create schema baseline
python create_baseline.py --env local

# Step 3: Make schema changes (e.g., add columns, modify types)
# (External schema modification)

# Step 4: Verify schema changes
python verify_migration.py --env local
```

### Workflow 3: Continuous Integration Testing

```bash
# CI/CD Pipeline Example

# 1. Reset test database to known state
python populate_test_data.py --count 20 --env target

# 2. Create baseline
python create_baseline.py --env target

# 3. Run application integration tests
# (Your application tests)

# 4. Verify data integrity after tests
python verify_migration.py --env target

# 5. Exit with appropriate code (0 = pass, 1 = fail)
```

### Workflow 4: Multi-Environment Comparison

```bash
# Compare production with staging
python create_baseline.py --env source    # Production
python create_baseline.py --env target    # Staging
python verify_migration.py --source-baseline baseline_source_*.json --target-baseline baseline_target_*.json
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
| `baseline_<env>_YYYYMMDD_HHMMSS.json` | create_baseline.py | Database snapshot with environment name |
| `baseline_YYYYMMDD_HHMMSS.log` | create_baseline.py | Baseline creation execution log |
| `populate_YYYYMMDD_HHMMSS.log` | populate_test_data.py | Data population execution log |
| `verification_YYYYMMDD_HHMMSS.log` | verify_migration.py | Verification test results |

**File Name Examples:**
- `baseline_source_20260110_165255.json` - Source environment baseline
- `baseline_target_20260110_165305.json` - Target environment baseline
- `baseline_local_20260110_120000.json` - Local environment baseline

---

## Command Reference Summary

### Quick Command Reference

```bash
# Schema inspection
python check_schema.py --env <source|target|local>

# Create baseline
python create_baseline.py --env <source|target|local> [--output filename.json]

# Populate test data
python populate_test_data.py --count N --env <source|target|local>

# Verify migration
python verify_migration.py --env <source|target|local> [--baseline filename.json]

# Compare two baselines
python verify_migration.py --source-baseline source.json --target-baseline target.json
```

### Common Parameter Options

All scripts support these common parameters:
- `--env {source,target,local}` - Environment from config file
- `--config /path/to/db_config.json` - Custom config file path

---
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
