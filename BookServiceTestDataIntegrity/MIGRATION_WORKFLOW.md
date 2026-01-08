# Database Migration Testing - 2-Part Workflow

Simple and clean 2-step process for database migration verification.

## 📋 Quick Start

### Part 1: Create Baseline (Before Migration)
```powershell
python create_baseline.py
```
This creates a snapshot file: `baseline_YYYYMMDD_HHMMSS.json`

### Part 2: Verify Migration (After Migration)
```powershell
python verify_migration.py baseline_YYYYMMDD_HHMMSS.json
```
This compares current state with baseline and reports any issues.

---

## 🔄 Complete Workflow

### Step 1: Create Baseline
**Run BEFORE making any database changes**

```powershell
python create_baseline.py
```

**Output:**
- ✓ Creates `baseline_20251230_143520.json`
- ✓ Captures all table data, schemas, foreign keys, indexes
- ✓ Generates checksums for data integrity validation

**What it captures:**
- Row counts for all tables
- Complete data snapshots with SHA-256 checksums
- Table schemas (columns, types, constraints)
- Foreign key relationships
- Index definitions

---

### Step 2: Run Your Migration
```powershell
# Run your migration script
.\RunMigrations.ps1

# OR execute SQL changes
# OR run Entity Framework migrations
```

---

### Step 3: Verify Migration
**Run AFTER migration to verify integrity**

```powershell
python verify_migration.py baseline_20251230_143520.json
```

Or just run without parameters - it will find the most recent baseline:
```powershell
python verify_migration.py
```

**What it verifies:**
- ✓ No data loss (row counts match or increase)
- ✓ Data integrity (checksums validate data unchanged)
- ✓ Schema consistency (columns preserved correctly)
- ✓ Foreign keys intact (relationships maintained)
- ✓ No orphaned records (referential integrity)
- ✓ Indexes preserved

---

## 📊 Example Output

### Creating Baseline
```
╔══════════════════════════════════════════════════════════════════╗
║   Database Baseline Creator - Part 1                            ║
║   Create a baseline snapshot BEFORE migration                   ║
╚══════════════════════════════════════════════════════════════════╝

✓ Connected to database successfully

======================================================================
CREATING DATABASE BASELINE SNAPSHOT
======================================================================
Found 3 user tables to baseline

📊 Processing dbo.__MigrationHistory...
   Rows: 2
   Checksum: a3f5c2d8e1b9...
   Columns: 3

📊 Processing dbo.Authors...
   Rows: 25
   Checksum: 7d2e9f1a4c8b...
   Columns: 2
   Indexes: 1

📊 Processing dbo.Books...
   Rows: 48
   Checksum: 9b5e3a7f2d1c...
   Columns: 6
   Foreign Keys: 1
   Indexes: 2

======================================================================
✓ Baseline snapshot created successfully
======================================================================

📁 Baseline saved to: baseline_20251230_143520.json

📋 Next Steps:
   1. Run your database migration
   2. Execute: python verify_migration.py
   3. Use baseline file: baseline_20251230_143520.json
```

### Verifying Migration
```
╔══════════════════════════════════════════════════════════════════╗
║   Database Migration Verifier - Part 2                          ║
║   Verify migration against baseline                             ║
╚══════════════════════════════════════════════════════════════════╝

Found baseline file: baseline_20251230_143520.json
✓ Loaded baseline from: baseline_20251230_143520.json

======================================================================
MIGRATION VERIFICATION - COMPARING BASELINE VS CURRENT
======================================================================

──────────────────────────────────────────────────────────────────────
TABLE EXISTENCE VERIFICATION
──────────────────────────────────────────────────────────────────────
✓ Table Existence: PASSED - All tables preserved

──────────────────────────────────────────────────────────────────────
ROW COUNT VERIFICATION
──────────────────────────────────────────────────────────────────────
✓ Row Count - dbo.__MigrationHistory: PASSED - 2 rows (unchanged)
✓ Row Count - dbo.Authors: PASSED - 25 rows (unchanged)
✓ Row Count - dbo.Books: PASSED - 48 rows (unchanged)

──────────────────────────────────────────────────────────────────────
DATA INTEGRITY CHECKSUMS
──────────────────────────────────────────────────────────────────────
✓ Checksum - dbo.__MigrationHistory: PASSED - Data unchanged
✓ Checksum - dbo.Authors: PASSED - Data unchanged
✓ Checksum - dbo.Books: PASSED - Data unchanged

──────────────────────────────────────────────────────────────────────
REFERENTIAL INTEGRITY VERIFICATION
──────────────────────────────────────────────────────────────────────
✓ FK Integrity - dbo.Books.AuthorId: PASSED - No orphaned records

======================================================================
MIGRATION VERIFICATION REPORT
======================================================================
Total Tests:  15
✓ Passed:     15
⚠ Warnings:   0
✗ Failed:     0
======================================================================

🎯 Success Rate: 100.0%

======================================================================
✅ MIGRATION VERIFICATION PASSED
======================================================================
No critical issues found. Migration integrity verified!
```

---

## 🎯 What Gets Tested

### Critical Checks (Failures)
- ✗ **Data Loss** - Any reduction in row counts
- ✗ **Orphaned Records** - Foreign key violations
- ✗ **Missing Tables** - Tables deleted unexpectedly

### Warnings (Review Needed)
- ⚠ **Schema Changes** - Column additions/removals
- ⚠ **Data Modifications** - Checksum mismatches
- ⚠ **New Tables** - Tables added
- ⚠ **FK Changes** - Foreign keys modified
- ⚠ **Index Changes** - Indexes added/removed

### Success
- ✓ **Row Counts Match** - No data loss
- ✓ **Checksums Match** - Data integrity preserved
- ✓ **Schema Intact** - Structure unchanged
- ✓ **Referential Integrity** - All relationships valid

---

## 📁 Generated Files

Each run creates log files for audit trail:

**Baseline Creation:**
- `baseline_YYYYMMDD_HHMMSS.json` - Complete database snapshot
- `baseline_YYYYMMDD_HHMMSS.log` - Creation log

**Verification:**
- `verification_YYYYMMDD_HHMMSS.log` - Detailed comparison results

---

## 🔧 Configuration

### Custom Database Connection

**Option 1: Command line**
```powershell
python create_baseline.py "DRIVER={SQL Server};SERVER=myserver;DATABASE=mydb;UID=user;PWD=pass"
```

**Option 2: Edit scripts**
Edit the `connection_string` variable in both scripts:
```python
connection_string = (
    "DRIVER={SQL Server};"
    "SERVER=myserver;"
    "DATABASE=mydatabase;"
    "UID=username;"
    "PWD=password;"
)
```

### Default Connection
```python
connection_string = (
    "DRIVER={SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;"
    "DATABASE=BookServiceContext;"
    "Trusted_Connection=yes;"
)
```

---

## 💡 Use Cases

### Entity Framework Migrations
```powershell
# 1. Create baseline
python create_baseline.py

# 2. Run EF migration
Update-Database

# 3. Verify
python verify_migration.py
```

### Manual Schema Changes
```powershell
# 1. Baseline
python create_baseline.py

# 2. Execute ALTER TABLE statements
sqlcmd -S "(localdb)\MSSQLLocalDB" -d BookServiceContext -Q "ALTER TABLE..."

# 3. Verify
python verify_migration.py
```

### Data Migration Scripts
```powershell
# 1. Baseline
python create_baseline.py

# 2. Run data transformation
python migrate_data.py

# 3. Verify no data loss
python verify_migration.py
```

---

## ⚠️ Best Practices

1. **Always baseline first** - Never skip Part 1
2. **Keep baselines** - Store for audit trail and rollback reference
3. **Test migrations on copy** - Use test database before production
4. **Review warnings** - Not all warnings are problems
5. **Multiple baselines** - Create baseline before each major change

---

## 🐛 Troubleshooting

### "Cannot connect to database"
```powershell
# Verify database exists
sqlcmd -S "(localdb)\MSSQLLocalDB" -Q "SELECT name FROM sys.databases"

# Check if LocalDB is running
sqllocaldb info
sqllocaldb start MSSQLLocalDB
```

### "Baseline file not found"
Make sure you're in the correct directory and the baseline file exists:
```powershell
ls baseline_*.json
```

### "ODBC Driver not found"
Install Microsoft ODBC Driver for SQL Server:
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Permission Issues
Run PowerShell as Administrator or ensure Windows Authentication has access.

---

## 📊 Exit Codes

Scripts return appropriate exit codes for automation:
- **0** - Success (all tests passed)
- **1** - Failure (critical issues found)

Example in CI/CD:
```yaml
- name: Create Baseline
  run: python create_baseline.py

- name: Run Migration
  run: .\RunMigrations.ps1

- name: Verify Migration
  run: python verify_migration.py
```

---

## 🆚 Comparison with Old Script

| Feature | Old (Single Script) | New (2-Part) |
|---------|-------------------|--------------|
| **Workflow** | Menu-driven | Clean 2-step process |
| **Baseline** | Temporary | Persistent file |
| **Reusable** | No | Yes - compare multiple times |
| **CI/CD** | Complex | Simple automation |
| **Audit Trail** | Limited | Complete snapshots saved |
| **Clarity** | Mixed operations | Clear separation |

---

## 📞 Support

For issues:
1. Check log files for detailed errors
2. Verify database connectivity with `sqlcmd`
3. Ensure baseline file exists and is valid JSON
4. Check ODBC driver installation
