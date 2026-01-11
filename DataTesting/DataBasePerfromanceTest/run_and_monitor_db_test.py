#!/usr/bin/env python3
"""
JMeter Database Performance Test Runner with System Profiling
Prepares database and executes JMeter test plan while monitoring system performance
Usage: python run_and_monitor_db_test.py [options]
"""

import argparse
import subprocess
import sys
import json
import os
import signal
import time
import csv
import pyodbc
from pathlib import Path
from datetime import datetime

# Optional imports for graphing
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    GRAPHING_AVAILABLE = True
except ImportError:
    GRAPHING_AVAILABLE = False

# Configuration
JMETER_TEST_PLAN = Path("JMeter_DB_Mixed_Operations.jmx")
CONFIG_FILE = Path("../../db_config.json")
JMETER_RESULTS_DIR = Path("jmeter_results")

# Auto-detect best available ODBC driver
try:
    import pyodbc as _pyodbc_test
    available_drivers = _pyodbc_test.drivers()
    if "ODBC Driver 18 for SQL Server" in available_drivers:
        DEFAULT_DRIVER = "ODBC Driver 18 for SQL Server"
    elif "ODBC Driver 17 for SQL Server" in available_drivers:
        DEFAULT_DRIVER = "ODBC Driver 17 for SQL Server"
    else:
        DEFAULT_DRIVER = "SQL Server"
except:
    DEFAULT_DRIVER = "ODBC Driver 17 for SQL Server"

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
    print_color("=" * 70, Colors.CYAN)
    print_color(text, Colors.CYAN)
    print_color("=" * 70, Colors.CYAN)
    print()


def check_jmeter():
    """Check if JMeter is installed and accessible"""
    try:
        # On Windows, need to use jmeter.bat
        jmeter_cmd = 'jmeter.bat' if os.name == 'nt' else 'jmeter'
        result = subprocess.run([jmeter_cmd, '--version'], 
                              capture_output=True, text=True, timeout=10, shell=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0] if result.stdout else "JMeter"
            if "APACHE JMETER" in version_line:
                version_line = [line for line in result.stdout.split('\n') if 'JMETER' in line][0]
            print_color(f"  ✓ JMeter found: {version_line.strip()}", Colors.GREEN)
            return True
        else:
            print_color("  ✗ JMeter not found or not accessible", Colors.RED)
            return False
    except FileNotFoundError:
        print_color("  ✗ JMeter not found in PATH", Colors.RED)
        print()
        print("Please install JMeter and add it to your PATH")
        print("  Windows: $env:PATH += ';C:\\Tools\\apache-jmeter-5.6.3\\bin'")
        print("  Download from: https://jmeter.apache.org/download_jmeter.cgi")
        print()
        print("See JMETER_SETUP.md for detailed installation instructions")
        return False
    except Exception as e:
        print_color(f"  Error checking JMeter: {e}", Colors.RED)
        return False


def load_config(config_file: Path = CONFIG_FILE) -> dict:
    """Load database configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)


def build_connection_string(env_config: dict) -> str:
    """Build ODBC connection string from environment config"""
    server = env_config.get('server', '')
    port = env_config.get('port', '1433')
    database = env_config.get('database', '')
    username = env_config.get('username', '')
    password = env_config.get('password', '')
    
    connection_string = (
        f"DRIVER={{{DEFAULT_DRIVER}}};"
        f"SERVER={server},{port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )
    
    return connection_string


def get_connection_from_config(env_name: str, config_file: Path):
    """Get connection string and database name from config file"""
    try:
        config = load_config(config_file)
        
        if env_name not in config['environments']:
            print(f"Error: Environment '{env_name}' not found in configuration.")
            print(f"Available environments: {', '.join(config['environments'].keys())}")
            return None, None
        
        env_config = config['environments'][env_name]
        connection_string = build_connection_string(env_config)
        database_name = env_config.get('database', 'Unknown')
        
        print(f"Using environment: {env_name}")
        print(f"Server: {env_config.get('server')}:{env_config.get('port', '1433')}")
        print(f"Database: {database_name}")
        print()
        
        return connection_string, database_name
        
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None, None


def cleanup_database(connection_string):
    """Clean up database by deleting test records"""
    print("Cleaning up database...")
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Delete in correct order to respect FK constraints
        delete_queries = [
            ("Rentals", "DELETE FROM [dbo].[Rentals]"),
            ("Stocks", "DELETE FROM [dbo].[Stocks]"),
            ("Books", "DELETE FROM [dbo].[Books]"),
            ("Authors", "DELETE FROM [dbo].[Authors]"),
            ("Customers", "DELETE FROM [dbo].[Customers]"),
        ]
        
        for table_name, query in delete_queries:
            try:
                cursor.execute(query)
                affected = cursor.rowcount
                print(f"  ✓ Deleted {affected} records from {table_name}")
            except Exception as e:
                print(f"  Warning: Could not delete from {table_name}: {str(e)}")
        
        cursor.commit()
        print("  ✓ Database cleanup completed!")
        print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"  Error during cleanup: {str(e)}")
        print()


def seed_genres(connection_string):
    """Seed database with default genre"""
    print("Seeding Genres table...")
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if genre already exists
        cursor.execute("SELECT COUNT(*) FROM [dbo].[Genres] WHERE Name = 'Fiction'")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute("INSERT INTO [dbo].[Genres] (Name) VALUES ('Fiction')")
            cursor.commit()
            print("  ✓ Seeded 1 genre (Fiction)")
        else:
            print("  ✓ Genre already exists (Fiction)")
        print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"  Warning: Could not seed genres: {str(e)}")
        print()


def seed_database(connection_string):
    """Seed database with test data"""
    print("Seeding database with test data...")
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if authors already exist
        cursor.execute("SELECT COUNT(*) FROM [dbo].[Authors]")
        existing_count = cursor.fetchone()[0]
        
        if existing_count >= 20:
            print(f"  Authors table already has {existing_count} records. Skipping.")
            cursor.close()
            conn.close()
            seed_books(connection_string)
            seed_customers(connection_string)
            seed_stocks(connection_string)
            return
        
        # Seed 20 authors
        authors = [
            ("John", "Doe", "American", "Fiction writer", "john.doe@books.com"),
            ("Jane", "Smith", "British", "Mystery author", "jane.smith@books.com"),
            ("Robert", "Johnson", "Canadian", "Sci-Fi novelist", "robert.j@books.com"),
            ("Emily", "Brown", "Australian", "Romance writer", "emily.b@books.com"),
            ("Michael", "Davis", "American", "Thriller author", "michael.d@books.com"),
            ("Sarah", "Wilson", "British", "Historical fiction", "sarah.w@books.com"),
            ("David", "Martinez", "Spanish", "Adventure writer", "david.m@books.com"),
            ("Lisa", "Anderson", "American", "Young adult author", "lisa.a@books.com"),
            ("James", "Taylor", "Irish", "Horror writer", "james.t@books.com"),
            ("Mary", "Thomas", "American", "Fantasy author", "mary.t@books.com"),
            ("William", "Jackson", "British", "Crime novelist", "william.j@books.com"),
            ("Patricia", "White", "Canadian", "Drama writer", "patricia.w@books.com"),
            ("Richard", "Harris", "American", "Biography author", "richard.h@books.com"),
            ("Linda", "Martin", "Australian", "Cookbook writer", "linda.m@books.com"),
            ("Charles", "Thompson", "British", "Travel writer", "charles.t@books.com"),
            ("Barbara", "Garcia", "Mexican", "Poetry author", "barbara.g@books.com"),
            ("Joseph", "Martinez", "Spanish", "Philosophy writer", "joseph.m@books.com"),
            ("Susan", "Robinson", "American", "Self-help author", "susan.r@books.com"),
            ("Thomas", "Clark", "British", "Science writer", "thomas.c@books.com"),
            ("Jessica", "Rodriguez", "Argentine", "Children's author", "jessica.r@books.com"),
        ]
        
        inserted = 0
        for first, last, nationality, bio, email in authors:
            try:
                cursor.execute("""
                    INSERT INTO [dbo].[Authors] 
                    (AuthorId, FirstName, LastName, BirthDate, Nationality, Bio, Email, Affiliation)
                    VALUES (NEWID(), ?, ?, GETDATE(), ?, ?, ?, 'Independent')
                """, first, last, nationality, bio, email)
                inserted += 1
            except Exception as e:
                print(f"  Warning: Could not insert author {first} {last}: {str(e)}")
        
        cursor.commit()
        print(f"  ✓ Seeded {inserted} authors successfully!")
        print()
        
        cursor.close()
        conn.close()
        
        # Seed related data
        seed_books(connection_string)
        seed_customers(connection_string)
        seed_stocks(connection_string)
        
    except Exception as e:
        print(f"  Warning: Could not seed authors: {str(e)}")
        print()


def seed_books(connection_string):
    """Seed database with book items"""
    print("Seeding Books table...")
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if books already exist
        cursor.execute("SELECT COUNT(*) FROM [dbo].[Books]")
        existing_count = cursor.fetchone()[0]
        
        if existing_count >= 20:
            print(f"  Books table already has {existing_count} records. Skipping.")
            cursor.close()
            conn.close()
            return
        
        # Get existing author IDs and genre ID
        cursor.execute("SELECT ID FROM [dbo].[Authors]")
        author_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT ID FROM [dbo].[Genres] WHERE Name = 'Fiction'")
        genre_result = cursor.fetchone()
        genre_id = genre_result[0] if genre_result else 1
        
        if not author_ids:
            print(f"  Warning: No authors found. Cannot create books.")
            cursor.close()
            conn.close()
            return
        
        # Create 2 books per author (40 books total for 20 authors)
        book_titles = [
            "The Great Adventure", "Mystery of the Lost City",
            "Journey to the Stars", "Love in Paris",
            "The Last Stand", "Tales from History",
            "Mountain Quest", "Teen Dreams",
            "The Haunting", "Dragon's Realm",
            "Murder Mystery", "Family Drama",
            "Life Story", "Cooking Basics",
            "World Tour", "Poetic Verses",
            "Deep Thoughts", "Success Guide",
            "Science Explained", "Fairy Tales"
        ]
        
        inserted = 0
        for i, author_id in enumerate(author_ids[:10]):  # Limit to first 10 authors
            for book_num in range(2):
                try:
                    title_idx = (i * 2 + book_num) % len(book_titles)
                    cursor.execute("""
                        INSERT INTO [dbo].[Books] 
                        (Title, AuthorId, Year, Price, Description, GenreId, IssueDate, Rating)
                        VALUES (?, ?, ?, ?, ?, ?, GETDATE(), ?)
                    """, 
                    book_titles[title_idx], 
                    author_id, 
                    2020 + i, 
                    19.99 + (book_num * 5), 
                    f"Description for {book_titles[title_idx]}", 
                    genre_id,
                    4 + (i % 2))
                    inserted += 1
                except Exception as e:
                    print(f"  Warning: Could not insert book for author {author_id}: {str(e)}")
        
        cursor.commit()
        print(f"  ✓ Seeded {inserted} books successfully!")
        print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"  Warning: Could not seed books: {str(e)}")
        print()


def seed_customers(connection_string):
    """Seed database with customer records"""
    print("Seeding Customers table...")
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if customers already exist
        cursor.execute("SELECT COUNT(*) FROM [dbo].[Customers]")
        existing_count = cursor.fetchone()[0]
        
        if existing_count >= 20:
            print(f"  Customers table already has {existing_count} records. Skipping.")
            cursor.close()
            conn.close()
            return
        
        # Seed 20 customers
        customers = [
            ("Alice", "Johnson", "alice.j@email.com", "ID001", "1234567890"),
            ("Bob", "Williams", "bob.w@email.com", "ID002", "1234567891"),
            ("Carol", "Brown", "carol.b@email.com", "ID003", "1234567892"),
            ("Dan", "Jones", "dan.j@email.com", "ID004", "1234567893"),
            ("Eve", "Garcia", "eve.g@email.com", "ID005", "1234567894"),
            ("Frank", "Miller", "frank.m@email.com", "ID006", "1234567895"),
            ("Grace", "Davis", "grace.d@email.com", "ID007", "1234567896"),
            ("Henry", "Rodriguez", "henry.r@email.com", "ID008", "1234567897"),
            ("Ivy", "Martinez", "ivy.m@email.com", "ID009", "1234567898"),
            ("Jack", "Hernandez", "jack.h@email.com", "ID010", "1234567899"),
            ("Kelly", "Lopez", "kelly.l@email.com", "ID011", "1234567800"),
            ("Leo", "Gonzalez", "leo.g@email.com", "ID012", "1234567801"),
            ("Mia", "Wilson", "mia.w@email.com", "ID013", "1234567802"),
            ("Nick", "Anderson", "nick.a@email.com", "ID014", "1234567803"),
            ("Olivia", "Thomas", "olivia.t@email.com", "ID015", "1234567804"),
            ("Paul", "Taylor", "paul.t@email.com", "ID016", "1234567805"),
            ("Quinn", "Moore", "quinn.m@email.com", "ID017", "1234567806"),
            ("Rose", "Jackson", "rose.j@email.com", "ID018", "1234567807"),
            ("Sam", "Martin", "sam.m@email.com", "ID019", "1234567808"),
            ("Tina", "Lee", "tina.l@email.com", "ID020", "1234567809"),
        ]
        
        inserted = 0
        for first, last, email, id_card, mobile in customers:
            try:
                cursor.execute("""
                    INSERT INTO [dbo].[Customers] 
                    (FirstName, LastName, Email, IdentityCard, UniqueKey, DateOfBirth, Mobile, RegistrationDate)
                    VALUES (?, ?, ?, ?, NEWID(), DATEADD(year, -25, GETDATE()), ?, GETDATE())
                """, first, last, email, id_card, mobile)
                inserted += 1
            except Exception as e:
                print(f"  Warning: Could not insert customer {first} {last}: {str(e)}")
        
        cursor.commit()
        print(f"  ✓ Seeded {inserted} customers successfully!")
        print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"  Warning: Could not seed customers: {str(e)}")
        print()


def seed_stocks(connection_string):
    """Seed database with stock items"""
    print("Seeding Stocks table...")
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if stocks already exist
        cursor.execute("SELECT COUNT(*) FROM [dbo].[Stocks]")
        existing_count = cursor.fetchone()[0]
        
        if existing_count >= 30:
            print(f"  Stocks table already has {existing_count} records. Skipping.")
            cursor.close()
            conn.close()
            return
        
        # Get existing book IDs
        cursor.execute("SELECT ID FROM [dbo].[Books]")
        book_ids = [row[0] for row in cursor.fetchall()]
        
        if not book_ids:
            print(f"  Warning: No books found. Cannot create stock items.")
            cursor.close()
            conn.close()
            return
        
        # Create 3 stock items per book
        inserted = 0
        for book_id in book_ids[:10]:  # Limit to first 10 books
            for copy in range(3):
                try:
                    cursor.execute("""
                        INSERT INTO [dbo].[Stocks] 
                        (BookId, UniqueKey, IsAvailable)
                        VALUES (?, NEWID(), ?)
                    """, book_id, 1 if copy < 2 else 0)  # First 2 copies available
                    inserted += 1
                except Exception as e:
                    print(f"  Warning: Could not insert stock for book {book_id}: {str(e)}")
        
        cursor.commit()
        print(f"  ✓ Seeded {inserted} stock items successfully!")
        print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"  Warning: Could not seed stocks: {str(e)}")
        print()


def run_jmeter_test(env_config, results_dir, timeout=600):
    """Run JMeter test"""
    print_header("[Step 4/7] Running JMeter Test")
    
    # Create results directory
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamped filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    jtl_file = results_dir / f"results_{timestamp}.jtl"
    report_dir = results_dir / f"report_{timestamp}"
    log_file = results_dir / f"jmeter_{timestamp}.log"
    
    # Prepare JMeter command
    jmeter_cmd = 'jmeter.bat' if os.name == 'nt' else 'jmeter'
    cmd = [
        jmeter_cmd,
        '-n',  # Non-GUI mode
        '-t', str(JMETER_TEST_PLAN),
        '-l', str(jtl_file),
        '-e',  # Generate HTML report
        '-o', str(report_dir),
        '-j', str(log_file),
        f"-JDB_SERVER={env_config['server']}",
        f"-JDB_PORT={env_config.get('port', '1433')}",
        f"-JDB_NAME={env_config['database']}",
        f"-JDB_USER={env_config['username']}",
        f"-JDB_PASSWORD={env_config['password']}"
    ]
    
    print(f"  Test Plan: {JMETER_TEST_PLAN}")
    print(f"  Results: {jtl_file}")
    print(f"  Report: {report_dir}")
    print(f"  Timeout: {timeout} seconds")
    print()
    print_color("  Starting JMeter test...", Colors.YELLOW)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            print_color("  ✓ JMeter test completed successfully", Colors.GREEN)
            
            # Parse JMeter log for summary
            try:
                with open(log_file, 'r') as f:
                    log_content = f.read()
                    if 'summary =' in log_content:
                        summary_lines = [line for line in log_content.split('\n') if 'summary =' in line]
                        if summary_lines:
                            print()
                            print_color("  Test Summary:", Colors.CYAN)
                            for line in summary_lines[-1:]:
                                print(f"    {line.split('summary =')[1].strip()}")
            except Exception:
                pass
        else:
            print_color(f"  ✗ JMeter test failed with return code {result.returncode}", Colors.RED)
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
    
    except subprocess.TimeoutExpired:
        print_color("  ✗ JMeter test timed out", Colors.RED)
    except Exception as e:
        print_color(f"  ✗ Error running JMeter: {e}", Colors.RED)
    
    print()
    return jtl_file, report_dir


def start_performance_monitoring(perf_file):
    """Start Windows performance monitoring"""
    print_header("[Step 3/7] Starting Performance Monitoring")
    
    if os.name != 'nt':
        print_color("  ⚠ Performance monitoring only available on Windows", Colors.YELLOW)
        return None
    
    try:
        perf_cmd = ['typeperf',
            r'\Processor(_Total)\% Processor Time',
            r'\Memory\Available MBytes',
            r'\Memory\% Committed Bytes In Use',
            r'\PhysicalDisk(_Total)\Disk Reads/sec',
            r'\PhysicalDisk(_Total)\Disk Writes/sec',
            r'\Network Interface(*)\Bytes Total/sec',
            '-si', '1',
            '-o', str(perf_file)
        ]
        
        proc = subprocess.Popen(perf_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_color("  ✓ Performance monitoring started", Colors.GREEN)
        print(f"    Output file: {perf_file}")
        print(f"    Process ID: {proc.pid}")
        print()
        return proc
    except Exception as e:
        print_color(f"  ✗ Failed to start monitoring: {e}", Colors.RED)
        print()
        return None


def stop_performance_monitoring(proc):
    """Stop performance monitoring process"""
    print_header("[Step 5/7] Stopping Performance Monitoring")
    
    if proc is None:
        print_color("  ⚠ No monitoring process to stop", Colors.YELLOW)
        print()
        return
    
    try:
        # Try graceful shutdown first
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/PID', str(proc.pid)], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
        else:
            proc.send_signal(signal.SIGINT)
            proc.wait(timeout=3)
        print_color("  ✓ Performance monitoring stopped", Colors.GREEN)
    except subprocess.TimeoutExpired:
        print_color("  ⚠ Monitoring process timeout, forcing termination", Colors.YELLOW)
        try:
            proc.kill()
            proc.wait(timeout=1)
        except:
            pass
    except KeyboardInterrupt:
        print_color("  ⚠ Interrupted - forcing process termination", Colors.YELLOW)
        try:
            proc.kill()
        except:
            pass
        raise
    except Exception as e:
        print_color(f"  ⚠ Error stopping monitoring: {e}", Colors.YELLOW)
        try:
            proc.kill()
        except:
            pass
    print()


def clean_csv(file_path):
    """Clean Windows typeperf CSV output"""
    with open(file_path, 'r', encoding='utf-16') as f:
        lines = f.readlines()
    
    # Remove first line (PDH header)
    if lines and lines[0].startswith('"(PDH-CSV'):
        lines = lines[1:]
    
    clean_file = file_path.with_suffix('.clean.csv')
    with open(clean_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return clean_file


def generate_performance_graphs(perf_csv, output_file):
    """Generate performance graphs"""
    if not GRAPHING_AVAILABLE:
        print_color("  ⚠ Graphing libraries not available (install pandas and matplotlib)", Colors.YELLOW)
        return
    
    try:
        df = pd.read_csv(perf_csv)
        df.columns = df.columns.str.strip('"')
        df['Timestamp'] = pd.to_datetime(df.iloc[:, 0], format='%m/%d/%Y %H:%M:%S.%f')
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('System Performance During Test', fontsize=16)
        
        # CPU Usage
        cpu_col = [col for col in df.columns if 'Processor Time' in col][0]
        axes[0, 0].plot(df['Timestamp'], df[cpu_col], label='CPU Usage', color='blue')
        axes[0, 0].axhline(y=df[cpu_col].mean(), color='r', linestyle='--', label=f'Avg: {df[cpu_col].mean():.1f}%')
        axes[0, 0].fill_between(df['Timestamp'], df[cpu_col], alpha=0.3)
        axes[0, 0].set_ylabel('CPU %')
        axes[0, 0].set_title('CPU Usage')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Memory Usage
        mem_col = [col for col in df.columns if 'Committed Bytes In Use' in col][0]
        axes[0, 1].plot(df['Timestamp'], df[mem_col], label='Memory Usage', color='green')
        axes[0, 1].axhline(y=df[mem_col].mean(), color='r', linestyle='--', label=f'Avg: {df[mem_col].mean():.1f}%')
        axes[0, 1].fill_between(df['Timestamp'], df[mem_col], alpha=0.3)
        axes[0, 1].set_ylabel('Memory %')
        axes[0, 1].set_title('Memory Usage')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Disk I/O
        disk_read = [col for col in df.columns if 'Disk Reads' in col][0]
        disk_write = [col for col in df.columns if 'Disk Writes' in col][0]
        axes[1, 0].plot(df['Timestamp'], df[disk_read], label='Reads', color='orange')
        axes[1, 0].plot(df['Timestamp'], df[disk_write], label='Writes', color='purple')
        axes[1, 0].set_ylabel('Operations/sec')
        axes[1, 0].set_title('Disk I/O')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Network Activity
        net_cols = [col for col in df.columns if 'Bytes Total/sec' in col]
        if net_cols:
            net_data = df[net_cols].sum(axis=1) / 1024 / 1024  # Convert to MB/s
            axes[1, 1].plot(df['Timestamp'], net_data, label='Network', color='red')
            axes[1, 1].set_ylabel('MB/s')
            axes[1, 1].set_title('Network Activity')
            axes[1, 1].legend()
            axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print_color(f"  ✓ Performance graphs saved: {output_file}", Colors.GREEN)
        plt.close()
    except Exception as e:
        print_color(f"  ✗ Error generating graphs: {e}", Colors.RED)


def process_performance_data(perf_file, results_dir):
    """Process and graph performance data"""
    print_header("[Step 6/7] Processing Performance Data")
    
    if not perf_file.exists():
        print_color("  ⚠ Performance data file not found", Colors.YELLOW)
        print()
        return
    
    try:
        clean_file = clean_csv(perf_file)
        print_color(f"  ✓ Cleaned performance data: {clean_file}", Colors.GREEN)
        
        graph_file = results_dir / f"performance_graphs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        generate_performance_graphs(clean_file, graph_file)
    except Exception as e:
        print_color(f"  ✗ Error processing performance data: {e}", Colors.RED)
    print()


def consolidate_results(jtl_file, report_dir, perf_file):
    """Consolidate and display final results"""
    print_header("[Step 7/7] Test Results Summary")
    
    files_exist = []
    if jtl_file.exists():
        files_exist.append(f"  ✓ JMeter Results: {jtl_file}")
    if report_dir.exists():
        files_exist.append(f"  ✓ HTML Report: {report_dir}/index.html")
    if perf_file and perf_file.exists():
        files_exist.append(f"  ✓ Performance Data: {perf_file}")
        clean_file = perf_file.with_suffix('.clean.csv')
        if clean_file.exists():
            files_exist.append(f"  ✓ Cleaned CSV: {clean_file}")
    
    graph_files = list(JMETER_RESULTS_DIR.glob("performance_graphs_*.png"))
    if graph_files:
        files_exist.append(f"  ✓ Performance Graphs: {graph_files[-1]}")
    
    if files_exist:
        print_color("Test outputs:", Colors.GREEN)
        for line in files_exist:
            print(line)
    else:
        print_color("  ⚠ No output files found", Colors.YELLOW)
    print()


def main():
    parser = argparse.ArgumentParser(
        description='JMeter Database Performance Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run JMeter test with profiling
  python run_and_monitor_db_test.py --env target
  
  # Run without profiling (faster)
  python run_and_monitor_db_test.py --env target --no-profiling
  
  # Skip database seeding (reuse existing data)
  python run_and_monitor_db_test.py --env target --no-seed
  
  # Cleanup only
  python run_and_monitor_db_test.py --env target --cleanup
        """)
    
    parser.add_argument('--env', '--environment', type=str, dest='environment', default='target',
                       help='Database environment from config file (source, target, local)')
    parser.add_argument('--config', type=str, default='../../db_config.json',
                       help='Path to configuration file (default: ../../db_config.json)')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up all records from database tables (use before/after testing)')
    parser.add_argument('--no-profiling', action='store_true',
                       help='Skip system performance profiling')
    parser.add_argument('--no-seed', action='store_true',
                       help='Skip database seeding')
    parser.add_argument('--timeout', type=int, default=1800,
                       help='JMeter test timeout in seconds (default: 1800)')
    
    args = parser.parse_args()
    
    # Load from configuration file
    connection_string, database_name = get_connection_from_config(
        args.environment, 
        Path(args.config)
    )
    if not connection_string:
        print("\nFailed to load configuration. Exiting.")
        sys.exit(1)
    
    # Load environment config for JMeter
    config = load_config(Path(args.config))
    env_config = config['environments'][args.environment]
    
    # If cleanup flag is set, run cleanup and exit
    if args.cleanup:
        cleanup_database(connection_string)
        return
    
    # JMeter execution path
    print_header("DATABASE PERFORMANCE TEST - JMETER MODE")
    print(f"Environment: {args.environment}")
    print(f"Database: {database_name}")
    print()
    
    # Check JMeter installation
    print_header("[Step 1/7] Checking Prerequisites")
    if not check_jmeter():
        sys.exit(1)
    print()
    
    # Step 2: Cleanup
    print_header("[Step 2/7] Cleaning Database")
    cleanup_database(connection_string)
    print()
    
    # Step 3: Seeding (unless skipped)
    if not args.no_seed:
        print_header("[Step 2.5/7] Seeding Database")
        seed_genres(connection_string)
        seed_database(connection_string)
        print()
    
    # Setup directories
    JMETER_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Performance monitoring (if enabled)
    perf_proc = None
    perf_file = None
    if not args.no_profiling and os.name == 'nt':
        perf_file = JMETER_RESULTS_DIR / f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        perf_proc = start_performance_monitoring(perf_file)
        time.sleep(2)  # Let monitoring stabilize
    
    # Run JMeter test
    jtl_file, report_dir = run_jmeter_test(env_config, JMETER_RESULTS_DIR, timeout=args.timeout)
    
    # Stop monitoring
    if perf_proc:
        stop_performance_monitoring(perf_proc)
    
    # Process performance data
    if perf_file and not args.no_profiling:
        process_performance_data(perf_file, JMETER_RESULTS_DIR)
    
    # Consolidate results
    consolidate_results(jtl_file, report_dir, perf_file)
    
    print_color("\n" + "=" * 70, Colors.GREEN)
    print_color("JMETER TEST COMPLETED SUCCESSFULLY!", Colors.GREEN)
    print_color("=" * 70, Colors.GREEN)
    print()
    print(f"Results directory: {JMETER_RESULTS_DIR}")
    print(f"Open report: {report_dir}/index.html")
    print()


if __name__ == "__main__":
    main()
