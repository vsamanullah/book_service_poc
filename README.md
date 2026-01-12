# Book Service Test Automation Suite

Comprehensive test automation framework for the Book Service application, supporting functional, performance, and data integrity testing across multiple environments.

## 🚀 Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd book_service_poc
   ```

2. **Configure Environments**
   - Copy and update `db_config.json` for database connections
   - Copy and update `api_config.json` for API endpoints

3. **Choose Your Testing Approach**
   - [Functional Tests](#functional-tests) - API and UI testing
   - [Performance Tests](#performance-tests) - Load and stress testing  
   - [Data Testing](#data-testing) - Database integrity and migration verification

---

## 📁 Project Structure

```
book_service_poc/
├── api_config.json                 # API endpoint configurations
├── db_config.json                  # Database connection configurations
├── requirements.txt                # Python dependencies
├── functional_tests/               # Playwright-based functional testing
│   ├── package.json               # Node.js dependencies
│   ├── playwright.config.ts       # Playwright configuration
│   ├── readme.md                  # Functional tests documentation
│   ├── testcases/                 # Test case specifications
│   ├── tests/                     # Test implementations
│   └── utils/                     # Test utilities
├── peformance_tests/              # JMeter and Python performance testing
│   ├── *.jmx                      # JMeter test plans (10 files)
│   ├── *.csv                      # Test data files
│   ├── *.py                       # Python testing scripts
│   ├── README.md                  # Performance testing guide
│   └── results/                   # Test execution results
├── data_testing/                  # Database integrity and performance testing
│   ├── query_db_tables.py         # Database query utility
│   ├── data_integrity_tests/      # Migration and integrity verification
│   │   ├── create_baseline.py     # Pre-migration baseline creation
│   │   ├── verify_migration.py    # Post-migration verification
│   │   └── README.md              # Data integrity testing guide
│   └── database_performance_tests/ # Database performance testing
│       ├── run_and_monitor_db_test.py # Performance test runner
│       ├── JMeter_DB_Mixed_Operations.jmx # JMeter DB test plan
│       └── README.md              # Database performance guide
└── test_data/                     # Test data management utilities
    ├── check_schema.py            # Database schema inspector
    └── populate_test_data.py      # Test data generator
```

---

## 🎯 Testing Modules

### Functional Tests
**Location:** `functional_tests/`  
**Technology:** Playwright, TypeScript, Node.js  
**Purpose:** End-to-end UI testing and API validation

**Key Features:**
- Cross-browser testing (Chrome, Firefox, Safari)
- API endpoint testing (CRUD operations)
- UI workflow automation
- Database integration testing

**Quick Commands:**
```bash
cd functional_tests
npm install
npx playwright test                    # Run all tests
npx playwright test --ui              # Interactive mode
npx playwright test --headed          # Visible browser mode
```

📖 **[Complete Functional Testing Guide →](functional_tests/readme.md)**

---

### Performance Tests  
**Location:** `peformance_tests/`  
**Technology:** JMeter, Python, Apache JMeter  
**Purpose:** Load testing, stress testing, and performance monitoring

**Key Features:**
- 10 pre-built JMeter test plans (Authors + Books CRUD)
- Python-based quick testing scripts
- API discovery and documentation
- System resource monitoring during tests
- Environment-based configuration

**Quick Commands:**
```bash
# Quick API endpoint testing
python peformance_tests/test_endpoints.py --env target

# JMeter performance test with monitoring
python peformance_tests/run_with_profiling.py 01_Authors_GET_All.jmx --env target

# API discovery
python peformance_tests/discover_apis.py --env target
```

📖 **[Complete Performance Testing Guide →](peformance_tests/README.md)**

---

### Data Testing
**Location:** `data_testing/`  
**Technology:** Python, pyodbc, SQL Server  
**Purpose:** Database integrity, migration verification, and data consistency testing

#### Data Integrity Tests
**Sub-location:** `data_testing/data_integrity_tests/`

**Key Features:**
- Pre-migration baseline creation
- Post-migration verification and comparison
- Schema validation and data integrity checks
- Automated test data generation

**Quick Commands:**
```bash
# Create baseline before migration
python data_testing/data_integrity_tests/create_baseline.py --env source

# Verify after migration
python data_testing/data_integrity_tests/verify_migration.py --env target

# Quick schema check
python test_data/check_schema.py --env target
```

#### Database Performance Tests
**Sub-location:** `data_testing/database_performance_tests/`

**Key Features:**
- Database load testing (Python + JMeter)
- System performance monitoring during DB operations
- Automated database seeding and cleanup
- Real-time metrics collection

**Quick Commands:**
```bash
# Python-based DB performance test
python data_testing/database_performance_tests/run_and_monitor_db_test.py --env target

# JMeter-based DB performance test  
python data_testing/database_performance_tests/run_and_monitor_db_test.py --tool jmeter --env target
```

📖 **[Complete Data Testing Guide →](data_testing/data_integrity_tests/README.md)**  
📖 **[Database Performance Guide →](data_testing/database_performance_tests/README.md)**

---

## ⚙️ Configuration

### Database Configuration (`db_config.json`)
```json
{
  "environments": {
    "source": {
      "server": "10.134.77.68,1433",
      "database": "BookService-Master", 
      "username": "testuser",
      "password": "TestDb@26#!",
      "driver": "ODBC Driver 18 for SQL Server",
      "encrypt": true,
      "trust_certificate": true
    },
    "target": { "...": "similar configuration" },
    "local": { "...": "local database configuration" }
  }
}
```

### API Configuration (`api_config.json`) 
```json
{
  "environments": {
    "source": {
      "description": "Source API Environment",
      "base_url": "https://10.134.77.68",
      "api_prefix": "/api", 
      "verify_ssl": false,
      "timeout": 10
    },
    "target": { "...": "similar configuration" },
    "local": { "...": "local API configuration" }
  }
}
```

---

## 🛠️ Prerequisites

### System Requirements
- **Windows 10/11** (primary development OS)
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Apache JMeter 5.6.3+** (for performance testing)
- **SQL Server** with ODBC Driver 17/18

### Python Dependencies
```bash
pip install -r requirements.txt
```

### Key Python Packages
- `requests` - HTTP API testing
- `pyodbc` - SQL Server database connectivity 
- `pandas` - Data analysis and reporting
- `matplotlib` - Performance graphs and visualization
- `psutil` - System performance monitoring

### Node.js Dependencies (Functional Tests)
```bash
cd functional_tests
npm install
```

### Key Node.js Packages
- `@playwright/test` - Browser automation and testing
- `typescript` - Type-safe test development

---

## 🚀 Common Usage Scenarios

### 1. Pre-Deployment API Validation
```bash
# Quick validation of all API endpoints
python peformance_tests/test_endpoints.py --env target

# Comprehensive endpoint testing with load
python peformance_tests/comprehensive_endpoint_test.py --env target
```

### 2. Database Migration Testing
```bash
# Step 1: Create baseline before migration  
python data_testing/data_integrity_tests/create_baseline.py --env source

# Step 2: Perform your database migration

# Step 3: Verify migration success
python data_testing/data_integrity_tests/verify_migration.py --env target
```

### 3. Full Regression Testing
```bash
# 1. Functional tests (API + UI)
cd functional_tests && npx playwright test

# 2. Performance tests  
python peformance_tests/run_with_profiling.py 01_Authors_GET_All.jmx --env target

# 3. Data integrity verification
python data_testing/data_integrity_tests/verify_migration.py --env target
```

### 4. Environment Comparison
```bash
# Compare API responses between environments
python peformance_tests/test_endpoints.py --env source
python peformance_tests/test_endpoints.py --env target

# Compare database schemas
python test_data/check_schema.py --env source  
python test_data/check_schema.py --env target
```

---

## 📊 Test Reports and Results

### Functional Test Reports
- **HTML Reports:** `functional_tests/playwright-report/`
- **Screenshots:** Auto-captured on test failures
- **Video Recordings:** Available for failed test debugging
- **Trace Files:** For detailed step-by-step debugging

### Performance Test Reports  
- **JMeter HTML Reports:** `peformance_tests/results/*/index.html`
- **System Metrics:** `peformance_tests/results/profiling/graphs/`
- **CSV Results:** `peformance_tests/results/*.jtl`

### Data Testing Reports
- **Migration Reports:** `verification_report_YYYYMMDD_HHMMSS.json`
- **Baseline Files:** `baseline_YYYYMMDD_HHMMSS.json`
- **Execution Logs:** `*_YYYYMMDD_HHMMSS.log`

---

## 🔧 Troubleshooting

### Common Issues

**Database Connection Failed**
- Verify `db_config.json` configuration
- Check SQL Server ODBC driver installation
- Confirm network connectivity and credentials

**API Endpoint Not Found**
- Verify `api_config.json` base_url and api_prefix
- Check if the application is running
- Validate SSL/TLS configuration

**JMeter Tests Failing**
- Ensure JMeter is in system PATH
- Check JDBC driver installation in JMeter lib folder
- Verify database connectivity from JMeter

**Playwright Browser Issues**
```bash
# Reinstall browsers
npx playwright install --force
```

### Getting Help

1. **Check Module Documentation:**
   - [Functional Tests README](functional_tests/readme.md)
   - [Performance Tests README](peformance_tests/README.md)  
   - [Data Integrity README](data_testing/data_integrity_tests/README.md)
   - [Database Performance README](data_testing/database_performance_tests/README.md)

2. **Check Test Cases:**
   - [Performance Test Cases](peformance_tests/test_cases.md)
   - [Data Integrity Test Cases](data_testing/data_integrity_tests/test_cases.md)
   - [Database Performance Test Cases](data_testing/database_performance_tests/test_cases.md)

3. **Review Setup Guides:**
   - [Windows Setup](peformance_tests/WINDOWS_SETUP.md)
   - [Linux Setup](peformance_tests/LINUX_SETUP.md)
   - [JMeter Setup](data_testing/database_performance_tests/JMETER_SETUP.md)

---

## 🤝 Contributing

### Development Guidelines
1. **Follow existing code structure** and naming conventions
2. **Update documentation** when adding new features
3. **Add test cases** for new functionality
4. **Use environment-based configuration** for all scripts
5. **Generate appropriate logs and reports**

### Adding New Tests
1. **Functional Tests:** Add to `functional_tests/tests/` with corresponding documentation in `functional_tests/testcases/`
2. **Performance Tests:** Add JMeter files to `peformance_tests/` and update `peformance_tests/README.md`
3. **Data Tests:** Add to appropriate subfolder in `data_testing/` with documentation updates

---

## 📋 License

This test automation suite is developed for the Book Service application testing. Please refer to your organization's licensing terms for usage and distribution guidelines.