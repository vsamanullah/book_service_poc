# Database Migration Data Integrity Test Cases

## Overview
This document outlines the comprehensive test cases for verifying data integrity during database migration. The tests are automated using the `verify_migration.py` script which compares a baseline snapshot (pre-migration) against the current database state (post-migration).

---

## Test Environment

### Prerequisites
- **Baseline File**: Created using `create_baseline.py` before migration
- **Database Access**: Connection to both source and target databases
- **Tools**: Python 3.x, pyodbc, SQL Server

### Test Data Setup
```bash
# Populate test data
python populate_test_data.py 25

# Create baseline before migration
python create_baseline.py

# Run migration
# (Your migration process here)

# Verify migration
python verify_migration.py baseline_YYYYMMDD_HHMMSS.json
```

---

## Test Suite Categories

### 1. Table Existence Verification

#### TC-001: Verify All Tables Are Preserved
**Objective**: Ensure no tables are dropped during migration  
**Priority**: Critical  
**Test Steps**:
1. Compare table list in baseline vs. current database
2. Identify any removed tables
3. Identify any new tables added

**Expected Results**:
- All baseline tables exist in current database
- Warning if new tables are added
- Fail if any baseline tables are missing

**Verification Method**: Table count comparison
```sql
SELECT TABLE_SCHEMA, TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
```

---

### 2. Row Count Verification

#### TC-002: Verify No Data Loss in Authors Table
**Objective**: Ensure all author records are preserved  
**Priority**: Critical  
**Test Steps**:
1. Get row count from baseline for `dbo.Authors`
2. Get current row count for `dbo.Authors`
3. Compare counts

**Expected Results**:
- ✅ Pass: Row count unchanged (before = after)
- ⚠️ Warning: Row count increased (before < after)
- ❌ Fail: Row count decreased (DATA LOSS)

**Verification SQL**:
```sql
SELECT COUNT(*) FROM [dbo].[Authors]
```

#### TC-003: Verify No Data Loss in Books Table
**Objective**: Ensure all book records are preserved  
**Priority**: Critical  
**Test Steps**:
1. Get row count from baseline for `dbo.Books`
2. Get current row count for `dbo.Books`
3. Compare counts

**Expected Results**:
- Pass: Row count unchanged
- Warning: Row count increased
- Fail: Row count decreased (DATA LOSS)

#### TC-004: Verify Row Counts for All Tables
**Objective**: Comprehensive row count validation across all tables  
**Priority**: High  
**Test Steps**:
1. Iterate through all tables in baseline
2. Compare row counts for each table
3. Report discrepancies

**Expected Results**: Row integrity maintained across all tables

---

### 3. Data Integrity Checksums

#### TC-005: Verify Authors Data Integrity
**Objective**: Ensure author data remains unchanged during migration  
**Priority**: Critical  
**Test Steps**:
1. Calculate SHA256 checksum of all `Authors` records (baseline)
2. Calculate SHA256 checksum of all `Authors` records (current)
3. Compare checksums

**Expected Results**:
- Pass: Checksums match (data unchanged)
- Warning: Checksums differ but row count changed (acceptable data modification)
- Warning: Checksums differ with same row count (data values modified)

**Checksum Calculation**: SHA256 hash of sorted JSON representation of all rows

#### TC-006: Verify Books Data Integrity
**Objective**: Ensure book data remains unchanged during migration  
**Priority**: Critical  
**Test Steps**:
1. Calculate SHA256 checksum of all `Books` records (baseline)
2. Calculate SHA256 checksum of all `Books` records (current)
3. Compare checksums

**Expected Results**: Same as TC-005

#### TC-007: Verify Data Integrity for All Tables
**Objective**: Comprehensive checksum validation across all tables  
**Priority**: High  
**Test Steps**:
1. Iterate through all tables
2. Calculate and compare checksums
3. Identify data modifications

**Expected Results**: Data integrity maintained or modifications documented

---

### 4. Schema Verification

#### TC-008: Verify Authors Table Schema
**Objective**: Ensure Authors table structure is preserved  
**Priority**: High  
**Test Steps**:
1. Get column definitions from baseline (name, type, length, nullable, default)
2. Get current column definitions
3. Compare schemas

**Expected Schema** (Example):
```sql
- Id (int, NOT NULL, Identity)
- Name (nvarchar(100), NOT NULL)
- Country (nvarchar(50), NULL)
- BirthDate (datetime2(7), NULL)
```

**Expected Results**:
- Pass: Schema unchanged
- Warning: Column count changed
- Warning: Column properties modified

#### TC-009: Verify Books Table Schema
**Objective**: Ensure Books table structure is preserved  
**Priority**: High  
**Test Steps**: Same as TC-008

**Expected Schema** (Example):
```sql
- Id (int, NOT NULL, Identity)
- Title (nvarchar(200), NOT NULL)
- AuthorId (int, NOT NULL, FK)
- PublishedDate (datetime2(7), NULL)
- ISBN (nvarchar(20), NULL)
- Price (decimal(18,2), NULL)
```

#### TC-010: Verify Schema for All Tables
**Objective**: Comprehensive schema validation  
**Priority**: High  
**Test Steps**:
1. Compare column count for each table
2. Compare data types and properties
3. Identify schema changes

**Verification SQL**:
```sql
SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, 
       IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
ORDER BY ORDINAL_POSITION
```

---

### 5. Foreign Key Verification

#### TC-011: Verify Foreign Key Relationships
**Objective**: Ensure all foreign key constraints are maintained  
**Priority**: High  
**Test Steps**:
1. List all foreign keys from baseline
2. List all current foreign keys
3. Compare FK definitions

**Expected Foreign Keys** (Example):
```
Books.AuthorId → Authors.Id
```

**Expected Results**:
- Pass: All FKs unchanged
- Warning: FKs removed
- Warning: New FKs added

**Verification SQL**:
```sql
SELECT fk.name, tp.name, cp.name, tr.name, cr.name
FROM sys.foreign_keys AS fk
INNER JOIN sys.foreign_key_columns AS fkc 
  ON fk.object_id = fkc.constraint_object_id
-- ... (full query in verify_migration.py)
```

#### TC-012: Verify FK Constraints Are Enforced
**Objective**: Ensure FK constraints are active and enforced  
**Priority**: High  
**Test Steps**:
1. Verify FK exists in sys.foreign_keys
2. Check is_disabled flag
3. Validate constraint is active

**Expected Results**: All FKs are enabled and enforced

---

### 6. Index Verification

#### TC-013: Verify Primary Key Indexes
**Objective**: Ensure all primary keys are maintained  
**Priority**: Critical  
**Test Steps**:
1. List all primary key indexes from baseline
2. List current primary key indexes
3. Compare definitions

**Expected Results**:
- Pass: All PKs unchanged
- Fail: PKs removed or modified

#### TC-014: Verify Non-Clustered Indexes
**Objective**: Ensure all performance indexes are maintained  
**Priority**: Medium  
**Test Steps**:
1. List all non-clustered indexes from baseline
2. List current non-clustered indexes
3. Compare index definitions (columns, uniqueness)

**Expected Results**:
- Pass: All indexes unchanged
- Warning: Indexes removed
- Warning: New indexes added

**Verification SQL**:
```sql
SELECT i.name, i.type_desc, i.is_unique, i.is_primary_key,
       COL_NAME(ic.object_id, ic.column_id)
FROM sys.indexes AS i
INNER JOIN sys.index_columns AS ic 
  ON i.object_id = ic.object_id AND i.index_id = ic.index_id
-- ... (full query in verify_migration.py)
```

#### TC-015: Verify Index Performance
**Objective**: Ensure indexes are properly optimized  
**Priority**: Low  
**Test Steps**:
1. Check index fragmentation levels
2. Verify index usage statistics
3. Identify unused indexes

---

### 7. Referential Integrity Verification

#### TC-016: Verify No Orphaned Books Records
**Objective**: Ensure all books have valid author references  
**Priority**: Critical  
**Test Steps**:
1. Execute LEFT JOIN query to find orphaned records
2. Count records where FK reference is invalid

**Verification SQL**:
```sql
SELECT COUNT(*) 
FROM [dbo].[Books] b
LEFT JOIN [dbo].[Authors] a ON b.AuthorId = a.Id
WHERE b.AuthorId IS NOT NULL AND a.Id IS NULL
```

**Expected Results**:
- Pass: 0 orphaned records
- Fail: Any orphaned records found (CRITICAL)

#### TC-017: Verify All Foreign Key Relationships
**Objective**: Comprehensive referential integrity check  
**Priority**: Critical  
**Test Steps**:
1. Iterate through all foreign key relationships
2. Check for orphaned records in each relationship
3. Report any violations

**Expected Results**: No orphaned records in any table

---

### 8. Data Content Validation

#### TC-018: Verify Sample Author Records
**Objective**: Spot-check specific author records for data accuracy  
**Priority**: Medium  
**Test Steps**:
1. Select sample author records from baseline
2. Retrieve same records from current database
3. Compare all field values

**Sample Test Data**:
```
Author ID: 1
Expected Name: "Test Author 1"
Expected Country: "USA"
```

**Expected Results**: All field values match exactly

#### TC-019: Verify Sample Book Records
**Objective**: Spot-check specific book records for data accuracy  
**Priority**: Medium  
**Test Steps**:
1. Select sample book records from baseline
2. Retrieve same records from current database
3. Compare all field values including foreign keys

**Expected Results**: All field values match exactly

---

### 9. Edge Case Testing

#### TC-020: Verify NULL Value Handling
**Objective**: Ensure NULL values are preserved correctly  
**Priority**: Medium  
**Test Steps**:
1. Identify records with NULL values in baseline
2. Verify same records have NULL values in current database
3. Check NULLable columns maintain NULL capability

**Expected Results**: NULL values preserved, no unexpected NULLs or non-NULLs

#### TC-021: Verify Empty String Handling
**Objective**: Ensure empty strings are not converted to NULL  
**Priority**: Low  
**Test Steps**:
1. Identify records with empty strings in baseline
2. Verify same values in current database
3. Confirm empty strings ≠ NULL

#### TC-022: Verify Special Characters
**Objective**: Ensure special characters are preserved  
**Priority**: Medium  
**Test Steps**:
1. Test records containing: quotes, apostrophes, unicode, newlines
2. Verify character encoding is preserved
3. Check for data truncation

**Test Characters**:
```
- Single quote: O'Reilly
- Double quote: "Test"
- Unicode: 北京, Москва, العربية
- Special: &, <, >, ", ', \
```

#### TC-023: Verify Date/Time Precision
**Objective**: Ensure datetime values maintain precision  
**Priority**: Medium  
**Test Steps**:
1. Compare datetime values including milliseconds
2. Check for timezone conversion issues
3. Verify datetime2(7) precision maintained

---

### 10. Performance Validation

#### TC-024: Verify Migration Completion Time
**Objective**: Ensure migration completes within acceptable timeframe  
**Priority**: Low  
**Test Steps**:
1. Record migration start time
2. Record migration end time
3. Calculate duration

**Expected Results**: Migration completes within SLA (e.g., < 1 hour)

#### TC-025: Verify Database Size
**Objective**: Ensure database size is reasonable post-migration  
**Priority**: Low  
**Test Steps**:
1. Check baseline database size
2. Check current database size
3. Compare and analyze growth

**Expected Results**: Size increase is justified and reasonable

---

## Test Execution Results Template

### Migration Verification Summary

| **Metric** | **Count** |
|------------|-----------|
| Baseline Timestamp | YYYY-MM-DD HH:MM:SS |
| Verification Timestamp | YYYY-MM-DD HH:MM:SS |
| Total Tests Executed | X |
| Tests Passed  | X |
| Tests with Warnings  | X |
| Tests Failed  | X |
| Success Rate | XX.X% |

---

### Test Results by Category

#### Table Existence
-  All baseline tables exist
-  N new tables added
-  N tables removed

#### Row Counts
- Authors: N rows (unchanged)
- Books: N rows (unchanged)
- Summary: No data loss detected

#### Data Checksums
-  Authors: Data unchanged
-  Books: Data unchanged
- Summary: Data integrity verified

#### Schema Verification
-  Authors schema: Unchanged
- Books schema: Unchanged
- Summary: Schema preserved

#### Foreign Keys
-  N foreign keys preserved
-  N foreign keys added/removed

#### Indexes
-  N indexes preserved
-  N indexes added/removed

#### Referential Integrity
-  No orphaned records
- Summary: All FK relationships valid

---

## Critical Failure Scenarios

### Data Loss (CRITICAL)
**Trigger**: Row count decrease in any table  
**Action**:
1. STOP further migration activities
2. Investigate missing data
3. Rollback if necessary
4. Re-run migration with fixes

### Orphaned Records (CRITICAL)
**Trigger**: Foreign key violations detected  
**Action**:
1. Identify orphaned records
2. Determine root cause
3. Fix data integrity issues
4. Re-validate

### Schema Changes (HIGH)
**Trigger**: Column removed or type changed  
**Action**:
1. Verify change is intentional
2. Update baseline if expected
3. Test application compatibility

---

## Automation Commands

### Full Test Suite Execution
```bash
# Step 1: Create test data
python populate_test_data.py 25

# Step 2: Create baseline
python create_baseline.py

# Step 3: Run migration
# (Your migration process)

# Step 4: Verify migration
python verify_migration.py baseline_YYYYMMDD_HHMMSS.json

# Step 5: Review logs
# Check verification_YYYYMMDD_HHMMSS.log
```

### Quick Verification (After Migration)
```bash
python verify_migration.py  # Auto-detects latest baseline
```

---

## Success Criteria

### Migration is considered SUCCESSFUL if:
1. All baseline tables exist in target
2. Row counts are unchanged or increased (documented)
3. Data checksums match (or changes documented)
4. Schema is preserved (or changes documented)
5. Foreign keys are maintained
6. No orphaned records exist
7. All indexes are present
8. No critical test failures

### Migration requires REVIEW if:
- Warnings present but no failures
- Row counts increased (verify expected growth)
- Schema modifications detected (verify intentional)
- New tables/indexes added (verify expected)

### Migration has FAILED if:
- Any row count decreased (data loss)
- Orphaned records exist (referential integrity violation)
- Tables or primary keys missing
- Critical schema changes unexpected

---

## Rollback Procedures

### If Migration Fails:
1. **Document Failures**: Capture all failed test cases and errors
2. **Preserve State**: Do not modify current database
3. **Analyze Logs**: Review `verification_*.log` for root cause
4. **Execute Rollback**:
   ```bash
   # Restore from backup
   RESTORE DATABASE [BookStore-Master] 
   FROM DISK = 'path/to/backup.bak'
   WITH REPLACE, RECOVERY
   ```
5. **Verify Rollback**: Run verification against original baseline
6. **Fix Issues**: Address root cause before re-attempting migration

---

## Reporting

### Log Files Generated
- `baseline_YYYYMMDD_HHMMSS.json` - Pre-migration snapshot
- `baseline_YYYYMMDD_HHMMSS.log` - Baseline creation log
- `verification_YYYYMMDD_HHMMSS.log` - Verification execution log

### Report Contents
- Timestamp of baseline and verification
- Total tests executed, passed, warned, failed
- Detailed test results for each category
- List of critical failures (if any)
- Success rate percentage

---

## Maintenance

### Updating Test Cases
- Add new test cases as database schema evolves
- Update expected results when intentional changes occur
- Document exceptions and known differences

### Baseline Management
- Create new baseline after each successful migration
- Archive old baselines with migration documentation
- Label baselines clearly with version/date

### Version History
- v1.0 (2026-01-08): Initial test case documentation
- Added comprehensive coverage for all verification categories
- Includes 25 individual test cases across 10 categories

---

## Contact & Support

For issues or questions regarding migration verification:
- Review logs in `verification_*.log`
- Check baseline file integrity
- Verify database connectivity
- Consult database administrator

---

**END OF TEST CASES DOCUMENT**
