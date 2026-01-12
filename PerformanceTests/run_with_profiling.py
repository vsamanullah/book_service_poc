#!/usr/bin/env python3
"""
Performance Test with System Profiling
This script monitors CPU, Memory, Disk, and Network while running JMeter tests
Usage: python run_with_profiling.py <test_file.jmx> [--env {source,target,local}] [--config <path>]
"""

import sys
import os
import subprocess
import time
import csv
import signal
import json
import argparse
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    GRAPHING_AVAILABLE = True
except ImportError:
    GRAPHING_AVAILABLE = False

# Color codes for console output
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_color(text, color=''):
    """Print colored text"""
    if os.name == 'nt':  # Windows
        print(text)
    else:
        print(f"{color}{text}{Colors.RESET}")

def print_header(text):
    """Print section header"""
    print_color("=" * 60, Colors.CYAN)
    print_color(text, Colors.CYAN)
    print_color("=" * 60, Colors.CYAN)
    print()

def load_api_config(config_path="../api_config.json", env_name="target"):
    """Load API configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config['environments'][env_name]
    except FileNotFoundError:
        print_color(f"Error: Configuration file not found: {config_path}", Colors.RED)
        return None
    except json.JSONDecodeError as e:
        print_color(f"Error: Invalid JSON in configuration file: {e}", Colors.RED)
        return None
    except KeyError as e:
        print_color(f"Error: Environment '{env_name}' not found in configuration", Colors.RED)
        return None

def check_application_running(base_url="http://localhost:50524"):
    """Check if the application is running"""
    try:
        import urllib.request
        response = urllib.request.urlopen(f"{base_url}/api/Authors", timeout=5)
        return response.status == 200
    except:
        return False

def reset_database(base_url="http://localhost:50524"):
    """Reset and seed the database with fresh test data"""
    import urllib.request
    import urllib.parse
    import json
    
    print()
    print_color("Database Reset and Seed", Colors.CYAN)
    print_color("=" * 40, Colors.CYAN)
    print()
    
    # Check if application is running
    print("  [1/5] Checking if application is running...")
    if not check_application_running(base_url):
        raise Exception(f"Application is not running at {base_url}")
    print(f"  [OK] Application is running on {base_url}")
    print()
    
    # Delete all Books
    print("  [2/5] Deleting all Books...")
    try:
        response = urllib.request.urlopen(f"{base_url}/api/Books")
        books = json.loads(response.read().decode())
        for book in books:
            req = urllib.request.Request(f"{base_url}/api/Books/{book['Id']}", method='DELETE')
            urllib.request.urlopen(req)
            print(f"    Deleted Book ID: {book['Id']} - {book.get('Title', 'N/A')}")
        print("  [OK] All books deleted")
    except Exception as e:
        print(f"  [WARNING] Error deleting books: {e}")
    print()
    
    # Delete all Authors
    print("  [3/5] Deleting all Authors...")
    try:
        response = urllib.request.urlopen(f"{base_url}/api/Authors")
        authors = json.loads(response.read().decode())
        for author in authors:
            req = urllib.request.Request(f"{base_url}/api/Authors/{author['Id']}", method='DELETE')
            urllib.request.urlopen(req)
            print(f"    Deleted Author ID: {author['Id']} - {author.get('Name', 'N/A')}")
        print("  [OK] All authors deleted")
    except Exception as e:
        print(f"  [WARNING] Error deleting authors: {e}")
    print()
    
    # Create 5 Authors
    print("  [4/5] Creating 5 new Authors...")
    author_names = [
        "J.K. Rowling",
        "George R.R. Martin",
        "Stephen King",
        "Agatha Christie",
        "Isaac Asimov"
    ]
    
    created_authors = []
    for name in author_names:
        try:
            data = json.dumps({"Name": name}).encode('utf-8')
            req = urllib.request.Request(
                f"{base_url}/api/Authors",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            response = urllib.request.urlopen(req)
            author = json.loads(response.read().decode())
            created_authors.append(author)
            print(f"    [OK] Created Author ID: {author['Id']} - {author['Name']}")
        except Exception as e:
            print(f"    [X] Failed to create author {name}: {e}")
    print(f"  [OK] Created {len(created_authors)} authors")
    print()
    
    # Create 3 Books
    print("  [5/5] Creating 3 new Books...")
    if len(created_authors) < 3:
        print("  [WARNING] Not enough authors created, skipping book creation")
        return
    
    books_data = [
        {
            "title": "Harry Potter and the Philosopher's Stone",
            "year": 1997,
            "price": 29.99,
            "genre": "Fantasy",
            "authorId": created_authors[0]['Id']
        },
        {
            "title": "A Game of Thrones",
            "year": 1996,
            "price": 34.99,
            "genre": "Fantasy",
            "authorId": created_authors[1]['Id']
        },
        {
            "title": "The Shining",
            "year": 1977,
            "price": 24.99,
            "genre": "Horror",
            "authorId": created_authors[2]['Id']
        }
    ]
    
    created_books = []
    for book_data in books_data:
        try:
            data = json.dumps(book_data).encode('utf-8')
            req = urllib.request.Request(
                f"{base_url}/api/Books",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            response = urllib.request.urlopen(req)
            book = json.loads(response.read().decode())
            created_books.append(book)
            # Handle both lowercase and uppercase field names from API
            book_id = book.get('id', book.get('Id', 'Unknown'))
            book_title = book.get('title', book.get('Title', 'Unknown'))
            book_author = book.get('authorId', book.get('AuthorId', 'Unknown'))
            print(f"    [OK] Created Book ID: {book_id} - {book_title} (Author: {book_author})")
        except Exception as e:
            book_title = book_data.get('title', book_data.get('Title', 'Unknown'))
            print(f"    [X] Failed to create book {book_title}: {e}")
    print(f"  [OK] Created {len(created_books)} books")
    print()
    
    print_color("Database Reset Complete!", Colors.GREEN)
    print()

def start_linux_monitoring(output_file):
    """Start performance monitoring on Linux"""
    monitoring_script = """#!/usr/bin/env python3
import psutil
import time
import csv
from datetime import datetime

# Find dotnet process
dotnet_proc = None
for proc in psutil.process_iter(['pid', 'name']):
    if proc.info['name'] == 'dotnet':
        dotnet_proc = psutil.Process(proc.info['pid'])
        break

# Create CSV file
with open('{}', 'w', newline='') as f:
    writer = csv.writer(f)
    # Write header (mimicking Windows typeperf format)
    writer.writerow(['Timestamp', 'CPU_Total_Percent', 'Memory_Available_MB', 'Memory_Used_Percent', 
                     'Disk_Reads_PerSec', 'Disk_Writes_PerSec', 'Network1_Bytes_PerSec', 
                     'DotNet_CPU_Percent', 'DotNet_Memory_MB'])
    
    # Initialize counters
    prev_disk_io = psutil.disk_io_counters()
    prev_net_io = psutil.net_io_counters()
    prev_time = time.time()
    
    while True:
        try:
            timestamp = datetime.now().strftime('%m/%d/%Y %H:%M:%S.%f')[:-3]
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory
            mem = psutil.virtual_memory()
            mem_available_mb = mem.available / (1024 * 1024)
            mem_used_percent = mem.percent
            
            # Disk I/O
            curr_disk_io = psutil.disk_io_counters()
            curr_time = time.time()
            time_delta = curr_time - prev_time
            
            disk_reads_per_sec = (curr_disk_io.read_count - prev_disk_io.read_count) / time_delta if time_delta > 0 else 0
            disk_writes_per_sec = (curr_disk_io.write_count - prev_disk_io.write_count) / time_delta if time_delta > 0 else 0
            
            # Network
            curr_net_io = psutil.net_io_counters()
            net_bytes_per_sec = ((curr_net_io.bytes_sent + curr_net_io.bytes_recv) - 
                                (prev_net_io.bytes_sent + prev_net_io.bytes_recv)) / time_delta if time_delta > 0 else 0
            
            # .NET Process
            dotnet_cpu = 0
            dotnet_mem = 0
            if dotnet_proc and dotnet_proc.is_running():
                try:
                    dotnet_cpu = dotnet_proc.cpu_percent(interval=0.1)
                    dotnet_mem = dotnet_proc.memory_info().rss
                except:
                    pass
            
            # Write row
            writer.writerow([timestamp, cpu_percent, mem_available_mb, mem_used_percent,
                           disk_reads_per_sec, disk_writes_per_sec, net_bytes_per_sec,
                           dotnet_cpu, dotnet_mem])
            f.flush()
            
            # Update previous values
            prev_disk_io = curr_disk_io
            prev_net_io = curr_net_io
            prev_time = curr_time
            
            time.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Monitoring error: {{e}}")
            time.sleep(1)
""".format(output_file)
    
    # Write monitoring script to temp file
    script_path = f"results/profiling/monitor_{os.getpid()}.py"
    with open(script_path, 'w') as f:
        f.write(monitoring_script)
    
    # Make it executable and start it
    os.chmod(script_path, 0o755)
    
    try:
        process = subprocess.Popen(
            ['python3', script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return process
    except Exception as e:
        print(f"Error starting monitoring: {e}")
        return None

def generate_performance_graphs(clean_file, output_dir='results/profiling/graphs'):
    """Generate performance graphs from clean CSV file"""
    if not GRAPHING_AVAILABLE:
        print("[WARNING] pandas/matplotlib not installed. Install with: pip install pandas matplotlib")
        return False
    
    if not os.path.exists(clean_file):
        print(f"[ERROR] Clean file not found: {clean_file}")
        return False
    
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Load data
        print(f"  Loading data from: {clean_file}")
        df = pd.read_csv(clean_file)
        
        # Convert timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Calculate elapsed time
        df['Elapsed_Seconds'] = (df['Timestamp'] - df['Timestamp'].min()).dt.total_seconds()
        
        # Sum all network interface columns
        network_cols = [col for col in df.columns if col.startswith('Network') and col.endswith('_Bytes_PerSec')]
        if network_cols:
            for col in network_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            df['Network_Bytes_PerSec'] = df[network_cols].sum(axis=1)
        else:
            df['Network_Bytes_PerSec'] = 0
        
        # Convert other numeric columns
        numeric_cols = ['CPU_Total_Percent', 'Memory_Available_MB', 'Memory_Used_Percent', 
                       'Disk_Reads_PerSec', 'Disk_Writes_PerSec', 'DotNet_CPU_Percent', 'DotNet_Memory_MB']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        print(f"  [OK] Loaded {len(df)} data points ({df['Elapsed_Seconds'].max():.1f} seconds)")
        
        # Create graphs
        plt.style.use('seaborn-v0_8-darkgrid')
        dotnet_mem_mb = df['DotNet_Memory_MB'] / (1024 * 1024)
        
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(16, 20))
        
        # Graph 1: CPU Usage
        ax1.plot(df['Timestamp'], df['CPU_Total_Percent'], color='#e74c3c', linewidth=2, label='Total CPU', alpha=0.8)
        ax1.plot(df['Timestamp'], df['DotNet_CPU_Percent'], color='#3498db', linewidth=2, label='.NET Process CPU', alpha=0.8)
        ax1.fill_between(df['Timestamp'], df['CPU_Total_Percent'], alpha=0.2, color='#e74c3c')
        ax1.fill_between(df['Timestamp'], df['DotNet_CPU_Percent'], alpha=0.2, color='#3498db')
        ax1.axhline(y=df['CPU_Total_Percent'].mean(), color='#e74c3c', linestyle='--', alpha=0.5, linewidth=1)
        ax1.axhline(y=df['DotNet_CPU_Percent'].mean(), color='#3498db', linestyle='--', alpha=0.5, linewidth=1)
        ax1.set_ylabel('CPU Usage (%)', fontsize=12)
        ax1.set_xlabel('Time', fontsize=12)
        ax1.set_title('CPU Usage Over Time', fontsize=14, fontweight='bold', pad=15)
        ax1.legend(loc='upper right', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_ylim(0, max(100, df['CPU_Total_Percent'].max() * 1.1))
        ax1.text(0.02, 0.95, f'Avg Total: {df["CPU_Total_Percent"].mean():.1f}%\\nAvg .NET: {df["DotNet_CPU_Percent"].mean():.1f}%', 
                 transform=ax1.transAxes, fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Graph 2: Memory Usage
        ax2.plot(df['Timestamp'], df['Memory_Used_Percent'], color='#2ecc71', linewidth=2, label='System Memory Used %')
        ax2.fill_between(df['Timestamp'], df['Memory_Used_Percent'], alpha=0.3, color='#2ecc71')
        ax2.axhline(y=df['Memory_Used_Percent'].mean(), color='#2ecc71', linestyle='--', alpha=0.5, linewidth=1)
        ax2.set_ylabel('Memory Usage (%)', fontsize=12)
        ax2.set_xlabel('Time', fontsize=12)
        ax2.set_title('System Memory Usage Over Time', fontsize=14, fontweight='bold', pad=15)
        ax2.legend(loc='upper right', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_ylim(0, 100)
        ax2.text(0.02, 0.95, f'Average: {df["Memory_Used_Percent"].mean():.1f}%', 
                 transform=ax2.transAxes, fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Graph 3: .NET Process Memory
        ax3.plot(df['Timestamp'], dotnet_mem_mb, color='#f39c12', linewidth=2, label='.NET Process Memory')
        ax3.fill_between(df['Timestamp'], dotnet_mem_mb, alpha=0.3, color='#f39c12')
        ax3.axhline(y=dotnet_mem_mb.mean(), color='#f39c12', linestyle='--', alpha=0.5, linewidth=1)
        ax3.set_ylabel('Memory (MB)', fontsize=12)
        ax3.set_xlabel('Time', fontsize=12)
        ax3.set_title('.NET Process Memory Usage Over Time', fontsize=14, fontweight='bold', pad=15)
        ax3.legend(loc='upper right', fontsize=10)
        ax3.grid(True, alpha=0.3)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax3.tick_params(axis='x', rotation=45)
        ax3.text(0.02, 0.95, f'Average: {dotnet_mem_mb.mean():.1f} MB', 
                 transform=ax3.transAxes, fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Graph 4: Disk I/O and Network
        ax4_twin = ax4.twinx()
        line1 = ax4.plot(df['Timestamp'], df['Disk_Reads_PerSec'], color='#1abc9c', linewidth=2, label='Disk Reads/sec', alpha=0.8)
        line2 = ax4.plot(df['Timestamp'], df['Disk_Writes_PerSec'], color='#e67e22', linewidth=2, label='Disk Writes/sec', alpha=0.8)
        line3 = ax4_twin.plot(df['Timestamp'], df['Network_Bytes_PerSec'] / 1024, color='#9b59b6', linewidth=2, label='Network (KB/sec)', alpha=0.6, linestyle='--')
        ax4.set_xlabel('Time', fontsize=12)
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax4.tick_params(axis='x', rotation=45)
        ax4.set_ylabel('Disk Operations per Second', fontsize=12, color='#1abc9c')
        ax4_twin.set_ylabel('Network KB/sec', fontsize=12, color='#9b59b6')
        ax4.set_title('Disk I/O and Network Over Time', fontsize=14, fontweight='bold', pad=15)
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax4.legend(lines, labels, loc='upper right', fontsize=10)
        ax4.grid(True, alpha=0.3)
        ax4.tick_params(axis='y', labelcolor='#1abc9c')
        ax4_twin.tick_params(axis='y', labelcolor='#9b59b6')
        
        plt.tight_layout()
        
        # Save graph
        output_file = os.path.join(output_dir, 'performance_report.png')
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  [OK] Saved graph: {output_file}")
        
        # Create summary text file
        summary_file = os.path.join(output_dir, 'performance_summary.txt')
        with open(summary_file, 'w') as f:
            f.write("PERFORMANCE SUMMARY\\n")
            f.write("=" * 60 + "\\n\\n")
            f.write(f"Test Duration: {df['Elapsed_Seconds'].max():.1f} seconds\\n")
            f.write(f"Start Time: {df['Timestamp'].min()}\\n")
            f.write(f"End Time: {df['Timestamp'].max()}\\n")
            f.write(f"Data Points: {len(df)}\\n\\n")
            f.write("CPU USAGE\\n")
            f.write("-" * 60 + "\\n")
            f.write(f"Total CPU Average:    {df['CPU_Total_Percent'].mean():.2f}%\\n")
            f.write(f"Total CPU Peak:       {df['CPU_Total_Percent'].max():.2f}%\\n")
            f.write(f".NET CPU Average:     {df['DotNet_CPU_Percent'].mean():.2f}%\\n")
            f.write(f".NET CPU Peak:        {df['DotNet_CPU_Percent'].max():.2f}%\\n\\n")
            f.write("MEMORY USAGE\\n")
            f.write("-" * 60 + "\\n")
            f.write(f"System Memory Avg:    {df['Memory_Used_Percent'].mean():.2f}%\\n")
            f.write(f"System Memory Peak:   {df['Memory_Used_Percent'].max():.2f}%\\n")
            f.write(f".NET Memory Avg:      {dotnet_mem_mb.mean():.2f} MB\\n")
            f.write(f".NET Memory Peak:     {dotnet_mem_mb.max():.2f} MB\\n\\n")
            f.write("DISK I/O\\n")
            f.write("-" * 60 + "\\n")
            f.write(f"Disk Reads Average:   {df['Disk_Reads_PerSec'].mean():.2f} /sec\\n")
            f.write(f"Disk Reads Peak:      {df['Disk_Reads_PerSec'].max():.2f} /sec\\n")
            f.write(f"Disk Writes Average:  {df['Disk_Writes_PerSec'].mean():.2f} /sec\\n")
            f.write(f"Disk Writes Peak:     {df['Disk_Writes_PerSec'].max():.2f} /sec\\n\\n")
            f.write("NETWORK\\n")
            f.write("-" * 60 + "\\n")
            f.write(f"Network Average:      {df['Network_Bytes_PerSec'].mean():.2f} bytes/sec\\n")
            f.write(f"Network Peak:         {df['Network_Bytes_PerSec'].max():.2f} bytes/sec\\n\\n")
        print(f"  [OK] Saved summary: {summary_file}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Graph generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description='Performance Test with System Profiling',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Test with target environment (default)
  python run_with_profiling.py 01_Authors_GET_All.jmx
  
  # Test with source environment
  python run_with_profiling.py 01_Authors_GET_All.jmx --env source
  
  # Test with local environment
  python run_with_profiling.py 06_Books_GET_All.jmx --env local
  
  # Use custom config file
  python run_with_profiling.py 01_Authors_GET_All.jmx --env target --config ../custom_api_config.json
        """
    )
    
    parser.add_argument(
        'test_file',
        help='JMeter test file (.jmx)'
    )
    
    parser.add_argument(
        '--env',
        choices=['source', 'target', 'local'],
        default='target',
        help='Environment to test (default: target)'
    )
    
    parser.add_argument(
        '--config',
        default='../api_config.json',
        help='Path to API config file (default: ../api_config.json)'
    )
    
    parser.add_argument(
        '--profile',
        action='store_true',
        help='Enable system profiling (CPU, Memory, Disk, Network monitoring)'
    )
    
    args = parser.parse_args()
    
    test_file = args.test_file
    test_name = Path(test_file).stem
    
    # Check if file exists
    if not os.path.exists(test_file):
        print_color(f"ERROR: Test file not found: {test_file}", Colors.RED)
        print()
        print("Make sure the file exists in the current directory.")
        sys.exit(1)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Load API configuration
    env_config = load_api_config(args.config, args.env)
    
    if not env_config:
        print_color("\nFailed to load configuration. Exiting.", Colors.RED)
        sys.exit(1)
    
    base_url = env_config['base_url']
    
    print_header("Performance Test with System Profiling")
    print(f"Test File: {test_file}")
    print(f"Test Name: {test_name}")
    print(f"Environment: {env_config.get('description', args.env)}")
    print(f"Base URL: {base_url}")
    print(f"Profiling: {'Enabled' if args.profile else 'Disabled'}")
    print(f"Timestamp: {timestamp}")
    print()
    
    # Run database reset and seed script (only for local environment)
    if args.env == 'local':
        print_color("[0/7] Resetting and seeding database...", Colors.YELLOW)
        
        try:
            reset_database(base_url=base_url)
            print_color("[OK] Database reset and seeded successfully", Colors.GREEN)
        except Exception as e:
            print_color(f"[WARNING] Database reset failed: {e}", Colors.YELLOW)
        print()
    else:
        print_color("[0/7] Skipping database reset (only available for local environment)", Colors.YELLOW)
        print()
    
    # Create directories
    os.makedirs("results", exist_ok=True)
    os.makedirs("results/profiling", exist_ok=True)
    os.makedirs("results/profiling/graphs", exist_ok=True)
    
    # Clean up old results
    print_color("[1/7] Cleaning up old results...", Colors.YELLOW)
    cleanup_files = [
        f"results/{test_name}_results.jtl",
        f"results/{test_name}_jmeter.log"
    ]
    for file in cleanup_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"  Deleted: {file}")
    
    # Remove old report directory
    import shutil
    report_dir = f"results/{test_name}_report"
    if os.path.exists(report_dir):
        shutil.rmtree(report_dir)
        print(f"  Deleted directory: {report_dir}")
    
    print_color("[OK] Cleanup complete", Colors.GREEN)
    print()
    
    # Start Performance Monitoring
    perf_process = None
    perf_file = None
    clean_file = None
    
    if args.profile:
        print_color("[2/7] Starting performance monitoring...", Colors.YELLOW)
        perf_file = f"results/profiling/performance_{timestamp}.csv"
        
        if os.name == 'nt':  # Windows
            # Start typeperf for Windows
            perf_cmd = [
                'typeperf',
                r'\Processor(_Total)\% Processor Time',
                r'\Memory\Available MBytes',
                r'\Memory\% Committed Bytes In Use',
                r'\PhysicalDisk(_Total)\Disk Reads/sec',
                r'\PhysicalDisk(_Total)\Disk Writes/sec',
                r'\Network Interface(*)\Bytes Total/sec',
                r'\Process(dotnet)\% Processor Time',
                r'\Process(dotnet)\Working Set - Private',
                '-si', '1',
                '-o', perf_file
            ]
            
            perf_process = subprocess.Popen(
                perf_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            print_color(f"[OK] Performance monitoring started (PID: {perf_process.pid})", Colors.GREEN)
        else:
            # For Linux/Mac - Start custom monitoring script
            perf_process = start_linux_monitoring(perf_file)
            if perf_process:
                print_color(f"[OK] Performance monitoring started (PID: {perf_process.pid})", Colors.GREEN)
            else:
                print_color("[WARNING] Performance monitoring could not be started", Colors.YELLOW)
        
        print(f"    Output file: {perf_file}")
        print("    Collecting: CPU, Memory, Disk, Network metrics")
        print()
        
        # Wait for monitoring to stabilize
        time.sleep(2)
    else:
        print_color("[2/7] Profiling disabled (use --profile to enable)", Colors.YELLOW)
        print()
    
    # Run JMeter Test
    print_color("[3/7] Running JMeter performance test...", Colors.YELLOW)
    print(f"    Test File: {test_file}")

    # Extract config for JMeter
    jmeter_host = env_config.get('host', 'localhost')
    jmeter_port = env_config.get('port', 80)
    jmeter_protocol = env_config.get('protocol', 'http')
    
    print(f"    Target: {jmeter_protocol}://{jmeter_host}:{jmeter_port}")
    print()
    
    jmeter_params = f"-JBASE_URL={jmeter_host} -JPORT={jmeter_port} -JPROTOCOL={jmeter_protocol}"
    jmeter_cmd = f'jmeter -n -t {test_file} {jmeter_params} -l results/{test_name}_results.jtl -j results/{test_name}_jmeter.log -e -o results/{test_name}_report'
    
    jmeter_result = subprocess.run(jmeter_cmd, shell=True)
    
    print()
    if jmeter_result.returncode == 0:
        print_color("[OK] JMeter test completed successfully", Colors.GREEN)
    else:
        print_color(f"[WARNING] JMeter test completed with errors (Exit Code: {jmeter_result.returncode})", Colors.YELLOW)
    print()
    
    # Wait to capture post-test metrics
    if args.profile:
        time.sleep(2)
    
    # Stop Performance Monitoring
    if args.profile and perf_process:
        print_color("[4/7] Stopping performance monitoring...", Colors.YELLOW)
        if os.name == 'nt':
            # Windows - terminate typeperf
            subprocess.run(['taskkill', '/F', '/PID', str(perf_process.pid)], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Linux/Mac - terminate process
            perf_process.terminate()
            try:
                perf_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                perf_process.kill()
        time.sleep(1)
        print_color("[OK] Performance monitoring stopped", Colors.GREEN)
        print()
    elif args.profile:
        print_color("[4/7] No performance monitoring to stop", Colors.YELLOW)
        print()
    else:
        print_color("[4/7] Profiling was disabled - skipping", Colors.YELLOW)
        print()
    
    # Clean and process CSV
    if args.profile:
        print_color("[5/7] Processing performance data...", Colors.YELLOW)
        clean_file = f"results/profiling/performance_{timestamp}_clean.csv"
        
        try:
            if os.path.exists(perf_file):
                clean_csv(perf_file, clean_file)
                print_color("[OK] Performance data cleaned and formatted", Colors.GREEN)
            else:
                print_color("[WARNING] Performance file not found", Colors.YELLOW)
        except Exception as e:
            print_color(f"[ERROR] Failed to clean CSV: {e}", Colors.RED)
        print()
    else:
        print_color("[5/7] Profiling was disabled - skipping data processing", Colors.YELLOW)
        print()
    
    # Generate Performance Summary and Graphs
    if args.profile:
        print_color("[6/7] Generating performance summary and graphs...", Colors.YELLOW)
        try:
            generate_summary(clean_file)
            
            # Generate graphs directly using embedded function
            print("  Generating graphs...")
            if generate_performance_graphs(clean_file, "results/profiling/graphs"):
                print_color("[OK] Summary and graphs generated successfully", Colors.GREEN)
            else:
                print_color("[WARNING] Graph generation had issues", Colors.YELLOW)
        except Exception as e:
            print_color(f"[ERROR] Summary generation failed: {e}", Colors.RED)
        print()
    else:
        print_color("[6/7] Profiling was disabled - skipping summary generation", Colors.YELLOW)
        print()
    
    # Final report consolidation
    print_color("[7/7] Consolidating results...", Colors.YELLOW)
    # Verify all output files exist
    files_exist = {
        "JMeter Results": os.path.exists(f"results/{test_name}_results.jtl"),
        "JMeter Log": os.path.exists(f"results/{test_name}_jmeter.log"),
        "HTML Report": os.path.exists(f"results/{test_name}_report/index.html")
    }
    
    if args.profile:
        files_exist["Performance CSV"] = os.path.exists(clean_file) if clean_file else False
        files_exist["Performance Graph"] = os.path.exists("results/profiling/graphs/performance_report.png")
    
    all_present = all(files_exist.values())
    if all_present:
        print_color("[OK] All result files generated successfully", Colors.GREEN)
    else:
        print_color("[WARNING] Some result files are missing:", Colors.YELLOW)
        for name, exists in files_exist.items():
            status = "[OK]" if exists else "[MISSING]"
            print(f"  {status} {name}")
    print()
    
    # Final Summary
    print_header("Test Execution Complete!")
    print("Results Location:")
    print(f"  - JMeter Results:     results/{test_name}_results.jtl")
    print(f"  - JMeter Log:         results/{test_name}_jmeter.log")
    print(f"  - HTML Report:        results/{test_name}_report/index.html")
    
    if args.profile:
        print(f"  - Performance (Raw):  {perf_file}")
        print(f"  - Performance (Clean): {clean_file}")
        print(f"  - Performance Graphs: results/profiling/graphs/performance_report.png")
    
    print()
    print("To view HTML report, run:")
    print(f"  start results/{test_name}_report/index.html")
    print()

def clean_csv(input_file, output_file):
    """Clean the CSV file by removing PDH header and renaming columns"""
    # Try different encodings
    encodings = ['utf-8', 'utf-16-le', 'utf-16', 'utf-16-be']
    lines = None
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as infile:
                lines = infile.readlines()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if lines is None:
        raise Exception("Could not decode CSV file with any supported encoding")
    
    # Check if this is Windows typeperf format (has PDH header) or Linux format (already clean)
    header_line = lines[0]
    
    if 'PDH-CSV' in header_line or 'Network Interface' in header_line:
        # Windows typeperf format - needs cleaning
        network_count = header_line.count('Network Interface')
        
        # Skip first line (PDH header)
        data_lines = lines[1:]
        
        # Create new header with clean names
        if network_count > 0:
            network_headers = ','.join([f'Network{i+1}_Bytes_PerSec' for i in range(network_count)])
            new_header = f'Timestamp,CPU_Total_Percent,Memory_Available_MB,Memory_Used_Percent,Disk_Reads_PerSec,Disk_Writes_PerSec,{network_headers},DotNet_CPU_Percent,DotNet_Memory_MB\n'
        else:
            new_header = 'Timestamp,CPU_Total_Percent,Memory_Available_MB,Memory_Used_Percent,Disk_Reads_PerSec,Disk_Writes_PerSec,DotNet_CPU_Percent,DotNet_Memory_MB\n'
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(new_header)
            outfile.writelines(data_lines)
    else:
        # Linux format - already has clean headers, just copy
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.writelines(lines)

def generate_summary(clean_file):
    """Generate summary statistics from clean CSV"""
    if not os.path.exists(clean_file):
        return
    
    try:
        import pandas as pd
        
        df = pd.read_csv(clean_file)
        
        # Calculate statistics
        cpu_avg = df['CPU_Total_Percent'].mean()
        mem_used_avg = df['Memory_Used_Percent'].mean()
        mem_avail_avg = df['Memory_Available_MB'].mean()
        dotnet_cpu_avg = df['DotNet_CPU_Percent'].mean()
        dotnet_mem_avg = df['DotNet_Memory_MB'].mean() / (1024 * 1024)  # Convert to MB
        
        print()
        print_color("System Performance Summary:", Colors.CYAN)
        print_color("=" * 40, Colors.CYAN)
        print_color(f"CPU Total Average: {cpu_avg:.2f}%", Colors.YELLOW)
        print_color(f"Memory Available Average: {mem_avail_avg:.2f} MB", Colors.YELLOW)
        print_color(f"Memory Used Average: {mem_used_avg:.2f}%", Colors.YELLOW)
        print_color(f"DotNet CPU Average: {dotnet_cpu_avg:.2f}%", Colors.GREEN)
        print_color(f"DotNet Memory Average: {dotnet_mem_avg:.2f} MB", Colors.GREEN)
        print()
    except ImportError:
        print_color("[INFO] Install pandas for detailed statistics: pip install pandas", Colors.YELLOW)
    except Exception as e:
        print_color(f"[WARNING] Could not generate summary: {e}", Colors.YELLOW)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("Test interrupted by user", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print()
        print_color(f"ERROR: {e}", Colors.RED)
        sys.exit(1)
