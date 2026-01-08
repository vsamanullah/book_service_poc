# Running Performance Tests on Windows

## Prerequisites

### 1. Install Python 3
```powershell
# Download Python from official website
# https://www.python.org/downloads/

# Or using winget (Windows Package Manager)
winget install Python.Python.3.12

# Verify installation
python --version

# Install required Python packages
pip install pandas matplotlib psutil
```

### 2. Install JMeter
```powershell
# Download JMeter from official website
# https://jmeter.apache.org/download_jmeter.cgi

# Extract to a folder (e.g., C:\apache-jmeter-5.6.3)

# Add JMeter to PATH (System Environment Variables)
# 1. Press Win + X, select "System"
# 2. Click "Advanced system settings"
# 3. Click "Environment Variables"
# 4. Under "System variables", find and edit "Path"
# 5. Add: C:\apache-jmeter-5.6.3\bin

# Or using PowerShell (as Administrator)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\apache-jmeter-5.6.3\bin", "Machine")

# Verify installation
jmeter -v
```

### 3. Install .NET SDK/Runtime
```powershell
# Download from official website
# https://dotnet.microsoft.com/download

# Or using winget
winget install Microsoft.DotNet.SDK.8

# Verify installation
dotnet --version
```

### 4. Verify Required Windows Tools
```powershell
# Performance monitoring uses typeperf (built into Windows)
typeperf -q | Select-String "Processor"

# Should show processor counters - no installation needed
```

## Running the Tests

### 1. Open PowerShell
```powershell
# Navigate to the test directory
cd "D:\WORK\HCL\HCL_FROM_ACHMEA\hcl\UniCredit\POC\POC-DOT_NET\BookServicePerformanceTest"
```

### 2. Ensure Your Application is Running
```powershell
# Start your .NET application first (in a separate terminal)
cd path\to\your\dotnet\app
dotnet run

# Or if using IIS/Kestrel, ensure the service is running
# The script expects the app at http://localhost:50524 by default
```

### 3. Run Performance Test
```powershell
# Basic usage
python run_with_profiling.py 01_Authors_GET_All.jmx

# Run other tests
python run_with_profiling.py 06_Books_GET_All.jmx
python run_with_profiling.py 03_Authors_POST_Create.jmx

# Or for any JMX test file
python run_with_profiling.py <your-test-file.jmx>
```

### 4. View Results
```powershell
# Open HTML report
start results\01_Authors_GET_All_report\index.html

# View performance graph
start results\profiling\graphs\performance_report.png

# View performance summary
type results\profiling\graphs\performance_summary.txt
```

## Available Test Files

The workspace includes several test scenarios:

### Author Tests
- `01_Authors_GET_All.jmx` - Get all authors
- `02_Authors_GET_ById.jmx` - Get author by ID
- `03_Authors_POST_Create.jmx` - Create new authors
- `04_Authors_PUT_Update.jmx` - Update existing authors
- `05_Authors_DELETE.jmx` - Delete authors

### Book Tests
- `06_Books_GET_All.jmx` - Get all books
- `07_Books_GET_ById.jmx` - Get book by ID
- `08_Books_POST_Create.jmx` - Create new books
- `09_Books_PUT_Update.jmx` - Update existing books
- `10_Books_DELETE.jmx` - Delete books

## What the Script Does

### 1. Database Reset (Step 0/7)
- Connects to your application API
- Deletes all existing books and authors
- Creates 5 fresh authors
- Creates 3 fresh books
- Ensures consistent test data

### 2. Cleanup (Step 1/7)
- Removes previous test results
- Clears old JMeter logs
- Deletes old HTML reports

### 3. Performance Monitoring (Step 2/7)
Uses Windows `typeperf` to collect:
- **CPU Usage**: Total system and .NET process
- **Memory**: Available MB and usage percentage
- **Disk I/O**: Reads/sec and Writes/sec
- **Network**: Bytes Total/sec for all network interfaces
- **Process Memory**: .NET working set private

### 4. JMeter Test (Step 3/7)
- Runs the specified JMX test file
- Generates results in JTL format
- Creates HTML report automatically

### 5. Stop Monitoring (Step 4/7)
- Stops the typeperf process
- Saves all collected metrics

### 6. Process Data (Step 5/7)
- Cleans the raw CSV data
- Converts Windows typeperf format to standard CSV
- Handles multiple network interfaces dynamically

### 7. Generate Graphs (Step 6-7/7)
- Creates comprehensive performance graphs
- Shows CPU, Memory, Disk, Network over time
- Displays metrics with actual timestamps (HH:MM:SS)
- Generates summary statistics

## Output Files

After running a test, you'll find:

```
results/
├── 01_Authors_GET_All_results.jtl          # JMeter raw results
├── 01_Authors_GET_All_jmeter.log           # JMeter log
├── 01_Authors_GET_All_report/              # HTML report
│   ├── index.html                          # Main report (open this)
│   ├── content/                            # Report assets
│   └── statistics.json
└── profiling/
    ├── performance_20251229_180823.csv       # Raw typeperf data
    ├── performance_20251229_180823_clean.csv # Cleaned data
    └── graphs/
        ├── performance_report.png            # Combined performance graphs
        └── performance_summary.txt           # Statistics summary
```

## Troubleshooting

### Python Not Found
```powershell
# Check if Python is installed
python --version

# If not found, add Python to PATH or reinstall
# Make sure to check "Add Python to PATH" during installation
```

### JMeter Command Not Found
```powershell
# Verify JMeter is in PATH
jmeter -v

# If not found, add manually:
$env:Path += ";C:\apache-jmeter-5.6.3\bin"

# Or restart PowerShell after adding to system PATH
```

### Application Not Running Error
```
[1/5] Checking if application is running...
[ERROR] Application is not running at http://localhost:50524
```

**Solution:**
1. Start your .NET application first
2. Verify it's running on the correct port (default: 50524)
3. Update the base URL in `run_with_profiling.py` if using a different port

### Permission Denied for typeperf
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell and select "Run as Administrator"
```

### Missing Python Packages
```powershell
# Install all required packages
pip install pandas matplotlib psutil

# Or upgrade if already installed
pip install --upgrade pandas matplotlib psutil
```

### Graph Generation Fails
```powershell
# Ensure matplotlib backend is available
pip install --upgrade matplotlib pillow

# If still fails, check the clean CSV file exists
dir results\profiling\*_clean.csv
```

### Unicode/Encoding Errors
The script now uses ASCII characters ([OK], [X]) instead of Unicode symbols.
If you see encoding errors:
```powershell
# Set PowerShell encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
```

## Performance Tips

### Optimize JMeter Performance
```powershell
# Increase JMeter heap size (edit jmeter.bat or use environment variable)
$env:JVM_ARGS = "-Xms512m -Xmx2048m"
```

### Monitor Resource Usage
```powershell
# Watch real-time performance during test
# Open Task Manager (Ctrl+Shift+Esc)
# Go to Performance tab
# Watch CPU, Memory, Disk, Network
```

### Run Multiple Tests
```powershell
# Create a batch file to run multiple tests
@echo off
python run_with_profiling.py 01_Authors_GET_All.jmx
python run_with_profiling.py 02_Authors_GET_ById.jmx
python run_with_profiling.py 06_Books_GET_All.jmx
echo All tests complete!
```

## Advanced Configuration

### Change Application URL
Edit `run_with_profiling.py`:
```python
# Find and update the base_url parameter
reset_database(base_url="http://localhost:YOUR_PORT")
```

### Adjust Monitoring Interval
Edit `run_with_profiling.py`:
```python
# Change '-si', '1' to desired interval (seconds)
'-si', '2',  # Collect every 2 seconds
```

### Customize Graph Format
```powershell
# Generate graphs in different formats
python create_profiling_graphs.py results\profiling\performance_20251229_180823_clean.csv --format pdf
python create_profiling_graphs.py results\profiling\performance_20251229_180823_clean.csv --format svg
```

## Notes

- **Automatic Database Reset**: Each test run resets and seeds the database with fresh data
- **Timestamp Format**: Graphs show time in HH:MM:SS format on the x-axis
- **Multiple Network Interfaces**: The script automatically detects and aggregates all network interfaces
- **Background Monitoring**: Performance monitoring runs in the background during the entire test
- **Cross-Platform**: The same scripts work on Linux with minor differences (see LINUX_SETUP.md)

## Example Output

After a successful test run:
```
============================================================
Test Execution Complete!
============================================================

Results Location:
  - JMeter Results:     results/01_Authors_GET_All_results.jtl
  - JMeter Log:         results/01_Authors_GET_All_jmeter.log
  - HTML Report:        results/01_Authors_GET_All_report/index.html
  - Performance (Raw):  results/profiling/performance_20251229_180823.csv
  - Performance (Clean): results/profiling/performance_20251229_180823_clean.csv
  - Performance Graphs: results/profiling/graphs/performance_report.png

To view HTML report, run:
  start results/01_Authors_GET_All_report/index.html
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `python run_with_profiling.py <test.jmx>` | Run performance test |
| `start results\<test>_report\index.html` | View HTML report |
| `start results\profiling\graphs\performance_report.png` | View performance graphs |
| `python create_profiling_graphs.py <csv>` | Regenerate graphs |
| `python run_with_profiling.py --help` | Show help (if implemented) |
