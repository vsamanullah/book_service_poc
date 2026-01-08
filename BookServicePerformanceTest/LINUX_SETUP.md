# Running Performance Tests on Linux

## Prerequisites

### 1. Install Python 3 and Required Packages
```bash
# Update package list
sudo apt-get update

# Install Python 3 and pip
sudo apt-get install python3 python3-pip

# Install required Python packages
pip3 install pandas matplotlib psutil
```

### 2. Install JMeter
```bash
# Install Java (required for JMeter)
sudo apt-get install default-jdk

# Download and install JMeter
wget https://dlcdn.apache.org//jmeter/binaries/apache-jmeter-5.6.3.tgz
tar -xzf apache-jmeter-5.6.3.tgz
sudo mv apache-jmeter-5.6.3 /opt/jmeter

# Add JMeter to PATH
echo 'export PATH=$PATH:/opt/jmeter/bin' >> ~/.bashrc
source ~/.bashrc
```

### 3. Install .NET Runtime (if testing .NET applications)
```bash
# Add Microsoft package repository
wget https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb

# Install .NET SDK
sudo apt-get update
sudo apt-get install -y dotnet-sdk-8.0

# Or install just the runtime
sudo apt-get install -y aspnetcore-runtime-8.0
```

## Running the Tests

### 1. Make Scripts Executable
```bash
chmod +x run_with_profiling.py
chmod +x create_profiling_graphs.py
```

### 2. Run Performance Test
```bash
# Basic usage
python3 run_with_profiling.py 01_Authors_GET_All.jmx

# Or for any JMX test file
python3 run_with_profiling.py <your-test-file.jmx>
```

### 3. View Results
```bash
# Open HTML report
xdg-open results/01_Authors_GET_All_report/index.html

# View performance graph
xdg-open results/profiling/graphs/performance_report.png
```

## Key Differences from Windows

### Performance Monitoring
- **Windows**: Uses `typeperf` to collect system metrics
- **Linux**: Uses `psutil` Python library to collect metrics
  - CPU usage via `/proc/stat`
  - Memory via `/proc/meminfo`
  - Disk I/O via `/proc/diskstats`
  - Network via `/proc/net/dev`

### Process Names
- **Windows**: Looks for `dotnet` process
- **Linux**: Same - looks for `dotnet` process

### File Paths
- Both use forward slashes `/` in the Python scripts
- Results structure is identical on both platforms

## Troubleshooting

### JMeter Command Not Found
```bash
# Verify JMeter is in PATH
which jmeter

# If not found, add manually
export PATH=$PATH:/opt/jmeter/bin
```

### Permission Denied
```bash
# Make scripts executable
chmod +x *.py

# Or run with python3 explicitly
python3 run_with_profiling.py <test-file.jmx>
```

### Missing Python Packages
```bash
# Install all required packages
pip3 install pandas matplotlib psutil

# Or using requirements.txt
pip3 install -r requirements.txt
```

### .NET Process Not Found
If the monitoring script can't find the dotnet process, ensure:
1. Your .NET application is running
2. The process is named `dotnet` (check with `ps aux | grep dotnet`)
3. You have permission to read process information

## Output Files

All platforms generate the same output structure:
```
results/
├── <test_name>_results.jtl          # JMeter raw results
├── <test_name>_jmeter.log           # JMeter log
├── <test_name>_report/              # HTML report
│   └── index.html
└── profiling/
    ├── performance_<timestamp>.csv       # Raw monitoring data
    ├── performance_<timestamp>_clean.csv # Cleaned data
    └── graphs/
        ├── performance_report.png        # Combined graphs
        └── performance_summary.txt       # Statistics
```

## Notes

- The Linux monitoring script automatically detects the dotnet process
- If multiple dotnet processes are running, it monitors the first one found
- All graphs use the same format on both Windows and Linux
- Timestamps are shown in HH:MM:SS format on the x-axis
