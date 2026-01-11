# Book Service Performance Testing

This directory contains JMeter performance test scripts and Python utilities for testing the Book Service API endpoints.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Test Scripts](#test-scripts)
- [Quick Testing Scripts](#quick-testing-scripts)
- [JMeter Performance Tests](#jmeter-performance-tests)
- [Usage Examples](#usage-examples)

---

## Overview

The performance testing suite includes:
- **10 JMeter test files** - CRUD operations for Authors and Books endpoints
- **Quick test scripts** - Python scripts for rapid endpoint validation
- **API discovery tool** - Automated endpoint discovery and documentation
- **Profiling script** - System resource monitoring during JMeter tests

All scripts now support **environment-based configuration** using `api_config.json`, allowing you to easily switch between source, target, and local environments.

---

## Prerequisites

### Required Software
- **Python 3.8+** with packages:
  ```bash
  pip install requests urllib3 pandas matplotlib psutil
  ```
- **Apache JMeter** (for performance tests)
  - Download from: https://jmeter.apache.org/download_jmeter.cgi
  - Add to PATH or use full path to `jmeter` command

### Configuration File
Ensure `api_config.json` exists in the parent directory with environment definitions:

```json
{
  "environments": {
    "source": {
      "description": "Source API Environment",
      "base_url": "https://10.134.77.68",
      "api_prefix": "/api",
      "verify_ssl": false,
      "timeout": 10,
      "headers": {
        "Accept": "application/json",
        "Content-Type": "application/json"
      }
    },
    "target": {
      "description": "Target API Environment (Post-Migration)",
      "base_url": "https://10.134.77.68",
      "api_prefix": "/api",
      "verify_ssl": false,
      "timeout": 10,
      "headers": {
        "Accept": "application/json",
        "Content-Type": "application/json"
      }
    },
    "local": {
      "description": "Local Development Environment",
      "base_url": "http://localhost:50524",
      "api_prefix": "/api",
      "verify_ssl": false,
      "timeout": 10,
      "headers": {
        "Accept": "application/json",
        "Content-Type": "application/json"
      }
    }
  },
  "endpoints": {
    "authors": {
      "path": "/api/Authors",
      "methods": {
        "get_all": "/api/Authors",
        "get_by_id": "/api/Authors/{id}",
        "post": "/api/Authors",
        "put": "/api/Authors/{id}",
        "delete": "/api/Authors/{id}"
      }
    },
    "books": {
      "path": "/api/Books",
      "methods": {
        "get_all": "/api/Books",
        "get_by_id": "/api/Books/{id}",
        "post": "/api/Books",
        "put": "/api/Books/{id}",
        "delete": "/api/Books/{id}"
      }
    }
  }
}
```

---

## Test Scripts

### Quick Testing Scripts

#### 1. **discover_apis.py** - API Discovery Tool
Discovers and tests available API endpoints, checks for Swagger documentation.

```bash
# Test target environment (default)
python discover_apis.py

# Test source environment
python discover_apis.py --env source

# Test local environment
python discover_apis.py --env local

# Save results to JSON file
python discover_apis.py --env target --output api_discovery_results.json

# Use custom config file
python discover_apis.py --env target --config ../custom_api_config.json
```

**Features:**
- Tests all known endpoints (Authors, Books)
- Discovers additional endpoints
- Checks for Swagger/OpenAPI documentation
- Generates detailed summary report
- Optional JSON output for automation

---

#### 2. **test_endpoints.py** - Quick Endpoint Test
Quick validation of basic GET endpoints.

```bash
# Test target environment (default)
python test_endpoints.py

# Test source environment
python test_endpoints.py --env source

# Test local environment
python test_endpoints.py --env local

# Use custom config file
python test_endpoints.py --env target --config ../custom_api_config.json
```

**Features:**
- Tests 4 basic GET endpoints
- Fast execution (< 5 seconds)
- Response time and size metrics
- Success/failure summary

**Endpoints Tested:**
- GET /api/Authors (all authors)
- GET /api/Authors/1 (author by ID)
- GET /api/Books (all books)
- GET /api/Books/1 (book by ID)

---

#### 3. **comprehensive_endpoint_test.py** - Full CRUD Test
Comprehensive testing of all 10 JMeter test scenarios.

```bash
# Test target environment (default)
python comprehensive_endpoint_test.py

# Test source environment
python comprehensive_endpoint_test.py --env source

# Test local environment
python comprehensive_endpoint_test.py --env local

# Use custom config file
python comprehensive_endpoint_test.py --env target --config ../custom_api_config.json
```

**Features:**
- Tests all CRUD operations
- Creates test data automatically
- Validates response codes
- Detailed success/failure reporting
- Corresponds to all 10 JMeter scripts

**Tests Performed:**
1. GET /api/Authors - List all authors
2. POST /api/Authors - Create new author
3. GET /api/Authors/{id} - Get author by ID
4. PUT /api/Authors/{id} - Update author
5. DELETE /api/Authors/{id} - Delete author
6. GET /api/Books - List all books
7. POST /api/Books - Create new book
8. GET /api/Books/{id} - Get book by ID
9. PUT /api/Books/{id} - Update book
10. DELETE /api/Books/{id} - Delete book

---

#### 4. **run_with_profiling.py** - Performance Test with System Monitoring
Runs JMeter tests with system resource monitoring (CPU, Memory, Disk, Network).

```bash
# Test with target environment (default)
python run_with_profiling.py 01_Authors_GET_All.jmx

# Test with source environment
python run_with_profiling.py 01_Authors_GET_All.jmx --env source

# Test with local environment
python run_with_profiling.py 06_Books_GET_All.jmx --env local

# Use custom config file
python run_with_profiling.py 01_Authors_GET_All.jmx --env target --config ../custom_api_config.json
```

**Features:**
- Runs JMeter performance tests
- Monitors system resources in real-time
- Resets and seeds database before test
- Generates performance graphs (requires pandas/matplotlib)
- Creates HTML reports
- Saves clean CSV data

**Outputs:**
- `results/{test_name}_results.jtl` - JMeter results
- `results/{test_name}_report/` - HTML report directory
- `results/profiling/performance_*.csv` - Resource monitoring data
- `results/profiling/graphs/performance_report.png` - Performance graphs
- `results/profiling/graphs/performance_summary.txt` - Summary statistics

---

## JMeter Performance Tests

### Authors Endpoint Tests
- **01_Authors_GET_All.jmx** - Get all authors
- **02_Authors_GET_ById.jmx** - Get author by ID
- **03_Authors_POST_Create.jmx** - Create new author
- **04_Authors_PUT_Update.jmx** - Update author
- **05_Authors_DELETE.jmx** - Delete author

### Books Endpoint Tests
- **06_Books_GET_All.jmx** - Get all books
- **07_Books_GET_ById.jmx** - Get book by ID
- **08_Books_POST_Create.jmx** - Create new book
- **09_Books_PUT_Update.jmx** - Update book
- **10_Books_DELETE.jmx** - Delete book

### CSV Data Files
- `author_data.csv` - Test data for creating authors
- `author_ids.csv` - Author IDs for GET/PUT/DELETE operations
- `book_create_data.csv` - Test data for creating books
- `book_ids.csv` - Book IDs for GET/PUT/DELETE operations
- `book_update_data.csv` - Test data for updating books
- `delete_author_ids.csv` - Author IDs for DELETE operations
- `delete_book_ids.csv` - Book IDs for DELETE operations

---

## Usage Examples

### Quick Validation Workflow
```bash
# 1. Discover available APIs
python discover_apis.py --env target

# 2. Quick endpoint test
python test_endpoints.py --env target

# 3. Comprehensive CRUD test
python comprehensive_endpoint_test.py --env target
```

### Performance Testing Workflow
```bash
# 1. Test Authors GET endpoint with profiling
python run_with_profiling.py 01_Authors_GET_All.jmx --env target

# 2. View HTML report
start results/01_Authors_GET_All_report/index.html

# 3. Check performance graphs
start results/profiling/graphs/performance_report.png
```

### Manual JMeter Execution
If you need to run JMeter tests manually without profiling:

```bash
# Generate HTML report
jmeter -n -t 01_Authors_GET_All.jmx -l results/01_results.jtl -j results/01_jmeter.log -e -o results/01_report

# Run without HTML report
jmeter -n -t 01_Authors_GET_All.jmx -l results/01_results.jtl -j results/01_jmeter.log
```

---

## Environment Comparison

Test both source and target environments to compare performance:

```bash
# Test source environment
python comprehensive_endpoint_test.py --env source > results/source_test.log

# Test target environment
python comprehensive_endpoint_test.py --env target > results/target_test.log

# Compare results
diff results/source_test.log results/target_test.log
```

---

## Troubleshooting

### SSL Certificate Errors
All scripts disable SSL verification by default. If you need to enable it, update `api_config.json`:
```json
"verify_ssl": true
```

### Connection Errors
1. Verify the API is running at the configured base_url
2. Check firewall settings
3. Ensure correct port (default: 443 for HTTPS, 80 for HTTP, 50524 for local)

### JMeter Not Found
Add JMeter to PATH or use full path:
```bash
C:\apache-jmeter-5.6.3\bin\jmeter -n -t 01_Authors_GET_All.jmx ...
```

### Missing Python Packages
Install required packages:
```bash
pip install requests urllib3 pandas matplotlib psutil
```

---

## Known Issues

1. **PUT and DELETE operations return 405** on some environments
   - This is a server-side limitation, not a test issue
   - Affects tests: 04, 05, 09, 10

2. **Database reset may fail** if application is not running
   - Script will show warning but continue with tests

---

## Test Results Location

After running tests, results are saved in:
```
results/
├── {test_name}_results.jtl          # JMeter raw results
├── {test_name}_jmeter.log           # JMeter log file
├── {test_name}_report/              # HTML report directory
│   └── index.html                    # Main report page
└── profiling/
    ├── performance_*.csv             # Performance data
    └── graphs/
        ├── performance_report.png    # Performance graphs
        └── performance_summary.txt   # Summary statistics
```

---

## See Also
- [Test Cases Documentation](TEST_CASES.md)
- [Windows Setup Guide](WINDOWS_SETUP.md)
- [Linux Setup Guide](LINUX_SETUP.md)
