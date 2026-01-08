#!/usr/bin/env python3
"""
Combined Database Load Test Runner
Runs load test and monitoring simultaneously
Works on both Windows and Linux
"""

import argparse
import threading
import time
import pyodbc
import csv
import random
import statistics
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_CONNECTION_STRING = "Driver={ODBC Driver 17 for SQL Server};Server=(localdb)\\MSSQLLocalDB;Database=BookServiceContext;Trusted_Connection=yes;"
RESULTS_DIR = Path("database_test_results")


def create_results_directory():
    """Create results directory if it doesn't exist"""
    RESULTS_DIR.mkdir(exist_ok=True)


def get_cpu_usage(cursor):
    """Get SQL Server CPU usage"""
    query = """
    SELECT TOP 1 
        record.value('(./Record/SchedulerMonitorEvent/SystemHealth/ProcessUtilization)[1]', 'int') AS CPUUsage
    FROM ( 
        SELECT timestamp, CONVERT(xml, record) AS record 
        FROM sys.dm_os_ring_buffers 
        WHERE ring_buffer_type = N'RING_BUFFER_SCHEDULER_MONITOR' 
        AND record LIKE '%<SystemHealth>%'
    ) AS x 
    ORDER BY timestamp DESC
    """
    try:
        cursor.execute(query)
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else 0
    except:
        return 0


def get_memory_usage(cursor):
    """Get SQL Server memory usage in MB"""
    query = "SELECT (physical_memory_in_use_kb/1024) AS MemoryUsageMB FROM sys.dm_os_process_memory"
    try:
        cursor.execute(query)
        row = cursor.fetchone()
        return row[0] if row else 0
    except:
        return 0


def get_active_connections(cursor, database):
    """Get number of active connections to the database"""
    query = f"""
    SELECT COUNT(*) AS ActiveConnections
    FROM sys.dm_exec_sessions 
    WHERE is_user_process = 1 
    AND database_id = DB_ID('{database}')
    """
    try:
        cursor.execute(query)
        row = cursor.fetchone()
        return row[0] if row else 0
    except:
        return 0


def get_performance_counters(cursor):
    """Get performance counters"""
    query = """
    SELECT 
        counter_name,
        cntr_value
    FROM sys.dm_os_performance_counters
    WHERE (counter_name IN ('Batch Requests/sec', 'Page reads/sec', 'Page writes/sec', 'Transactions/sec', 'Lock Waits/sec')
        OR (counter_name = 'Number of Deadlocks/sec' AND instance_name = '_Total'))
        AND (instance_name = '' OR instance_name = '_Total')
    """
    counters = {
        'batch_requests': 0,
        'page_reads': 0,
        'page_writes': 0,
        'transactions': 0,
        'lock_waits': 0,
        'deadlocks': 0
    }
    
    try:
        cursor.execute(query)
        for row in cursor.fetchall():
            counter_name = row[0]
            value = row[1] if row[1] is not None else 0
            
            if counter_name == 'Batch Requests/sec':
                counters['batch_requests'] = value
            elif counter_name == 'Page reads/sec':
                counters['page_reads'] = value
            elif counter_name == 'Page writes/sec':
                counters['page_writes'] = value
            elif counter_name == 'Transactions/sec':
                counters['transactions'] = value
            elif counter_name == 'Lock Waits/sec':
                counters['lock_waits'] = value
            elif counter_name == 'Number of Deadlocks/sec':
                counters['deadlocks'] = value
    except:
        pass
    
    return counters


def run_monitoring(connection_string, database, duration):
    """Run monitoring in background"""
    print("[MONITOR] Starting performance monitoring...")
    
    # Create results directory
    create_results_directory()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metrics_file = RESULTS_DIR / f"metrics_{timestamp}.csv"
    interval_seconds = 5
    
    # Initialize CSV
    with open(metrics_file, 'w', newline='') as f:
        fieldnames = ['timestamp', 'cpu_usage', 'memory_usage_mb', 'active_connections',
                     'batch_requests', 'page_reads', 'page_writes', 'transactions',
                     'lock_waits', 'deadlocks']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
    
    start_time = datetime.now()
    end_time = start_time.timestamp() + duration
    sample_count = 0
    
    # Collect metrics for stats
    all_metrics = []
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        while time.time() < end_time:
            sample_count += 1
            current_time = datetime.now()
            
            try:
                # Collect all metrics
                cpu_usage = get_cpu_usage(cursor)
                memory_usage = get_memory_usage(cursor)
                active_conns = get_active_connections(cursor, database)
                perf_counters = get_performance_counters(cursor)
                
                metrics = {
                    'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'cpu_usage': cpu_usage,
                    'memory_usage_mb': memory_usage,
                    'active_connections': active_conns,
                    'batch_requests': perf_counters['batch_requests'],
                    'page_reads': perf_counters['page_reads'],
                    'page_writes': perf_counters['page_writes'],
                    'transactions': perf_counters['transactions'],
                    'lock_waits': perf_counters['lock_waits'],
                    'deadlocks': perf_counters['deadlocks']
                }
                
                # Write to CSV
                with open(metrics_file, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=metrics.keys())
                    writer.writerow(metrics)
                
                all_metrics.append(metrics)
                
                # Display current metrics
                print(f"[MONITOR Sample {sample_count}] {current_time.strftime('%H:%M:%S')}")
                print(f"  CPU: {cpu_usage}% | Memory: {memory_usage} MB | Connections: {active_conns}")
                print(f"  Batch Req/sec: {perf_counters['batch_requests']} | Transactions/sec: {perf_counters['transactions']}")
                print(f"  Lock Waits: {perf_counters['lock_waits']} | Deadlocks: {perf_counters['deadlocks']}")
                
            except Exception as e:
                print(f"  [MONITOR] Error collecting metrics: {str(e)}")
            
            # Wait for next sample
            remaining_time = end_time - time.time()
            if remaining_time > 0:
                sleep_time = min(interval_seconds, remaining_time)
                time.sleep(sleep_time)
        
        cursor.close()
        conn.close()
        
    except KeyboardInterrupt:
        print("\n[MONITOR] Monitoring stopped by user")
    except Exception as e:
        print(f"\n[MONITOR] Monitoring error: {str(e)}")
    
    print(f"\n[MONITOR] Monitoring completed! Samples: {sample_count}")
    print(f"[MONITOR] Results saved to: {metrics_file}")
    
    # Generate summary statistics
    if all_metrics:
        cpu_values = [m['cpu_usage'] for m in all_metrics]
        mem_values = [m['memory_usage_mb'] for m in all_metrics]
        conn_values = [m['active_connections'] for m in all_metrics]
        
        if cpu_values:
            print(f"[MONITOR] CPU Avg: {round(sum(cpu_values)/len(cpu_values), 2)}% | Max: {max(cpu_values)}%")
        if mem_values:
            print(f"[MONITOR] Memory Avg: {round(sum(mem_values)/len(mem_values), 2)} MB | Max: {max(mem_values)} MB")
        if conn_values:
            print(f"[MONITOR] Connections Avg: {round(sum(conn_values)/len(conn_values), 2)} | Max: {max(conn_values)}")


# ============================================================================
# LOAD TEST FUNCTIONS
# ============================================================================

def execute_select_operation(cursor):
    """Execute various SELECT operations"""
    operation_type = random.choice(['top100', 'by_id', 'with_join', 'count'])
    
    if operation_type == 'top100':
        cursor.execute("SELECT TOP 100 * FROM Books ORDER BY Id")
        cursor.fetchall()
        return "SELECT_TOP100"
    
    elif operation_type == 'by_id':
        book_id = random.randint(1, 1000)
        cursor.execute("SELECT * FROM Books WHERE Id = ?", book_id)
        cursor.fetchall()
        return "SELECT_BY_ID"
    
    elif operation_type == 'with_join':
        cursor.execute("""
            SELECT TOP 50 b.Id, b.Title, a.Name 
            FROM Books b 
            INNER JOIN Authors a ON b.AuthorId = a.Id
            ORDER BY b.Id
        """)
        cursor.fetchall()
        return "SELECT_WITH_JOIN"
    
    else:  # count
        cursor.execute("SELECT COUNT(*) FROM Books")
        cursor.fetchall()
        return "SELECT_COUNT"


def execute_insert_operation(cursor):
    """Execute INSERT operation"""
    title = f"Performance Test Book {random.randint(1, 999999)}"
    author_id = random.randint(1, 20)
    price = round(random.uniform(10.0, 100.0), 2)
    year = random.randint(1900, 2025)
    genre = random.choice(["Fiction", "Non-Fiction", "Science", "History", "Biography"])
    
    cursor.execute("""
        INSERT INTO Books (Title, AuthorId, Price, Year, Genre) 
        VALUES (?, ?, ?, ?, ?)
    """, title, author_id, price, year, genre)
    cursor.commit()
    return "INSERT"


def execute_update_operation(cursor):
    """Execute UPDATE operation"""
    book_id = random.randint(1, 1000)
    new_price = round(random.uniform(10.0, 100.0), 2)
    
    cursor.execute("""
        UPDATE Books 
        SET Price = ? 
        WHERE Id = ?
    """, new_price, book_id)
    cursor.commit()
    return "UPDATE"


def execute_delete_operation(cursor):
    """Execute DELETE operation"""
    # Only delete test records
    cursor.execute("""
        DELETE TOP (1) FROM Books 
        WHERE Title LIKE 'Performance Test Book%'
    """)
    cursor.commit()
    return "DELETE"


def worker_thread(connection_string, operations_per_thread, test_type, thread_id):
    """Worker thread that executes database operations"""
    results = []
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        for i in range(operations_per_thread):
            start_time = time.time()
            
            try:
                # Determine operation type
                if test_type in ['Mixed', 'Read']:
                    operation_weights = {
                        'SELECT': 0.6,
                        'INSERT': 0.2,
                        'UPDATE': 0.1,
                        'DELETE': 0.1
                    } if test_type == 'Mixed' else {'SELECT': 1.0}
                    
                    rand_val = random.random()
                    if rand_val < operation_weights.get('SELECT', 0):
                        operation = execute_select_operation(cursor)
                    elif rand_val < operation_weights.get('SELECT', 0) + operation_weights.get('INSERT', 0):
                        operation = execute_insert_operation(cursor)
                    elif rand_val < operation_weights.get('SELECT', 0) + operation_weights.get('INSERT', 0) + operation_weights.get('UPDATE', 0):
                        operation = execute_update_operation(cursor)
                    else:
                        operation = execute_delete_operation(cursor)
                
                elif test_type in ['Write', 'INSERT']:
                    operation = execute_insert_operation(cursor)
                
                elif test_type == 'UPDATE':
                    operation = execute_update_operation(cursor)
                
                elif test_type == 'DELETE':
                    operation = execute_delete_operation(cursor)
                
                else:  # SELECT
                    operation = execute_select_operation(cursor)
                
                duration = (time.time() - start_time) * 1000  # Convert to ms
                
                results.append({
                    'thread_id': thread_id,
                    'operation_number': i + 1,
                    'operation_type': operation,
                    'duration_ms': round(duration, 2),
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                })
                
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                results.append({
                    'thread_id': thread_id,
                    'operation_number': i + 1,
                    'operation_type': 'ERROR',
                    'duration_ms': round(duration, 2),
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                })
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[LOAD TEST] Thread {thread_id} connection error: {str(e)}")
    
    return results


def run_load_test(connections, operations, connection_string, test_type):
    """Run load test with concurrent connections"""
    print("[LOAD TEST] Starting database load test...")
    time.sleep(3)  # Give monitor time to start
    
    # Create results directory
    create_results_directory()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = RESULTS_DIR / f"load_test_{timestamp}.csv"
    summary_file = RESULTS_DIR / f"summary_{timestamp}.txt"
    
    print(f"[LOAD TEST] Running with {connections} concurrent connections")
    print(f"[LOAD TEST] Each connection will perform {operations} operations")
    print(f"[LOAD TEST] Test type: {test_type}")
    print(f"[LOAD TEST] Total operations: {connections * operations}")
    print()
    
    # Initialize CSV file
    with open(results_file, 'w', newline='') as f:
        fieldnames = ['thread_id', 'operation_number', 'operation_type', 'duration_ms', 'status', 'timestamp', 'error']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
    
    # Execute load test with thread pool
    start_time = time.time()
    all_results = []
    
    print(f"[LOAD TEST] {datetime.now().strftime('%H:%M:%S')} - Starting {connections} worker threads...")
    
    with ThreadPoolExecutor(max_workers=connections) as executor:
        futures = [
            executor.submit(worker_thread, connection_string, operations, test_type, i+1)
            for i in range(connections)
        ]
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            results = future.result()
            all_results.extend(results)
            
            # Write results to CSV
            with open(results_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['thread_id', 'operation_number', 'operation_type', 'duration_ms', 'status', 'timestamp', 'error'])
                for result in results:
                    writer.writerow({k: result.get(k, '') for k in ['thread_id', 'operation_number', 'operation_type', 'duration_ms', 'status', 'timestamp', 'error']})
            
            if completed % max(1, connections // 10) == 0 or completed == connections:
                print(f"[LOAD TEST] Progress: {completed}/{connections} threads completed ({round(completed/connections*100)}%)")
    
    total_duration = time.time() - start_time
    
    print(f"\n[LOAD TEST] All operations completed in {round(total_duration, 2)} seconds")
    
    # Calculate statistics
    successful_ops = [r for r in all_results if r['status'] == 'SUCCESS']
    failed_ops = [r for r in all_results if r['status'] == 'FAILED']
    
    if successful_ops:
        durations = [r['duration_ms'] for r in successful_ops]
        durations.sort()
        
        avg_duration = statistics.mean(durations)
        median_duration = statistics.median(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        p95_duration = durations[int(len(durations) * 0.95)] if len(durations) > 0 else 0
        p99_duration = durations[int(len(durations) * 0.99)] if len(durations) > 0 else 0
        
        throughput = len(successful_ops) / total_duration
        
        # Count operations by type
        op_counts = {}
        for result in successful_ops:
            op_type = result['operation_type']
            op_counts[op_type] = op_counts.get(op_type, 0) + 1
        
        # Generate summary
        summary = f"""
DATABASE LOAD TEST SUMMARY
{'=' * 60}

Test Configuration:
  Concurrent Connections: {connections}
  Operations per Connection: {operations}
  Test Type: {test_type}
  Total Operations: {len(all_results)}
  Test Duration: {round(total_duration, 2)} seconds

Results:
  Successful Operations: {len(successful_ops)} ({round(len(successful_ops)/len(all_results)*100, 2)}%)
  Failed Operations: {len(failed_ops)} ({round(len(failed_ops)/len(all_results)*100, 2) if all_results else 0}%)
  Throughput: {round(throughput, 2)} operations/second

Response Times (milliseconds):
  Average: {round(avg_duration, 2)} ms
  Median: {round(median_duration, 2)} ms
  Min: {round(min_duration, 2)} ms
  Max: {round(max_duration, 2)} ms
  95th Percentile: {round(p95_duration, 2)} ms
  99th Percentile: {round(p99_duration, 2)} ms

Operations by Type:
"""
        for op_type, count in sorted(op_counts.items()):
            summary += f"  {op_type}: {count} ({round(count/len(successful_ops)*100, 2)}%)\n"
        
        summary += f"\nResults saved to:\n  {results_file}\n  {summary_file}\n"
        
        # Write summary to file
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        # Print summary to console
        print(summary)
        
    else:
        print(f"[LOAD TEST] ERROR: All operations failed!")
        with open(summary_file, 'w') as f:
            f.write(f"ERROR: All {len(all_results)} operations failed!\n")
    
    print(f"[LOAD TEST] Results saved to: {results_file}")


def cleanup_database(connection_string):
    """Clean up all records from Books and Authors tables"""
    print("=" * 50)
    print("DATABASE CLEANUP")
    print("=" * 50)
    print()
    print("WARNING: This will DELETE ALL records from Books and Authors tables!")
    print()
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Get counts before deletion
        cursor.execute("SELECT COUNT(*) FROM Books")
        books_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Authors")
        authors_count = cursor.fetchone()[0]
        
        print(f"Current records:")
        print(f"  Books: {books_count}")
        print(f"  Authors: {authors_count}")
        print()
        
        if books_count == 0 and authors_count == 0:
            print("Tables are already empty. No cleanup needed.")
            cursor.close()
            conn.close()
            return
        
        print("Deleting records...")
        
        # Delete all books first (due to foreign key constraint)
        cursor.execute("DELETE FROM Books")
        deleted_books = cursor.rowcount
        print(f"  Deleted {deleted_books} books")
        
        # Delete all authors
        cursor.execute("DELETE FROM Authors")
        deleted_authors = cursor.rowcount
        print(f"  Deleted {deleted_authors} authors")
        
        # Reset identity seed for Authors table
        cursor.execute("DBCC CHECKIDENT ('Authors', RESEED, 0)")
        print(f"  Reset Authors identity to 0")
        
        # Commit the changes
        cursor.commit()
        
        print()
        print("✓ Cleanup completed successfully!")
        print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: Failed to cleanup database: {str(e)}")
        print()


def seed_database(connection_string):
    """Seed database with initial Authors data for testing"""
    print("=" * 50)
    print("DATABASE SEEDING")
    print("=" * 50)
    print()
    print("Adding seed data for Authors...")
    print()
    
    authors = [
        "William Shakespeare", "Jane Austen", "Charles Dickens", "Mark Twain",
        "Ernest Hemingway", "F. Scott Fitzgerald", "George Orwell", "J.K. Rowling",
        "Stephen King", "Agatha Christie", "Leo Tolstoy", "Fyodor Dostoevsky",
        "Virginia Woolf", "James Joyce", "Franz Kafka", "Gabriel Garcia Marquez",
        "Haruki Murakami", "Margaret Atwood", "Toni Morrison", "Chinua Achebe"
    ]
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if authors already exist
        cursor.execute("SELECT COUNT(*) FROM Authors")
        existing_count = cursor.fetchone()[0]
        
        if existing_count >= 20:
            print(f"Authors table already has {existing_count} records. Skipping seed.")
            cursor.close()
            conn.close()
            return
        
        # Insert authors
        inserted = 0
        for author_name in authors:
            try:
                cursor.execute("INSERT INTO Authors (Name) VALUES (?)", author_name)
                inserted += 1
            except Exception as e:
                print(f"  Warning: Could not insert '{author_name}': {str(e)}")
        
        cursor.commit()
        
        print(f"✓ Seeded {inserted} authors successfully!")
        print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: Failed to seed database: {str(e)}")
        print()



def main():
    parser = argparse.ArgumentParser(description='Combined Database Load & Monitoring Test')
    parser.add_argument('-c', '--connections', type=int, default=20,
                       help='Number of concurrent connections (default: 20)')
    parser.add_argument('-o', '--operations', type=int, default=100,
                       help='Operations per connection (default: 100)')
    parser.add_argument('-t', '--test-type', type=str, default='Mixed',
                       choices=['Read', 'Write', 'Update', 'Delete', 'Mixed', 'SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                       help='Type of test to run (default: Mixed)')
    parser.add_argument('-d', '--duration', type=int, default=120,
                       help='Monitoring duration in seconds (default: 120)')
    parser.add_argument('-s', '--connection-string', type=str, default=DEFAULT_CONNECTION_STRING,
                       help='Database connection string')
    parser.add_argument('--database', type=str, default='BookServiceContext',
                       help='Database name (default: BookServiceContext)')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up all records from Books and Authors tables (use before/after testing)')
    
    args = parser.parse_args()
    
    # If cleanup flag is set, run cleanup and exit
    if args.cleanup:
        cleanup_database(args.connection_string)
        return
    
    print("=" * 50)
    print("COMBINED DATABASE LOAD & MONITORING TEST")
    print("=" * 50)
    print()
    
    # Clean up database before running test
    print("Step 1: Cleaning up database...")
    cleanup_database(args.connection_string)
    
    print("Step 2: Seeding database with Authors...")
    seed_database(args.connection_string)
    
    print("Step 3: Starting performance test...")
    print()
    print("Test Configuration:")
    print(f"  Concurrent Connections: {args.connections}")
    print(f"  Operations per Connection: {args.operations}")
    print(f"  Test Type: {args.test_type}")
    print(f"  Monitoring Duration: {args.duration} seconds")
    print()
    
    # Start monitoring in background thread
    monitor_thread = threading.Thread(
        target=run_monitoring,
        args=(args.connection_string, args.database, args.duration)
    )
    monitor_thread.start()
    
    # Run load test
    run_load_test(args.connections, args.operations, args.connection_string, args.test_type)
    
    # Wait for monitoring to complete
    print()
    print("[WAITING] Waiting for monitoring to complete...")
    monitor_thread.join()
    
    print()
    print("=" * 50)
    print("COMBINED TEST COMPLETED!")
    print("=" * 50)
    print()
    print("Results saved in: database_test_results/")
    print()
    print("Next steps:")
    print("  1. Review load test results (load_test_*.csv)")
    print("  2. Review monitoring metrics (metrics_*.csv)")
    print("  3. Run performance analysis queries (Database-Performance-Analysis.sql)")
    print()


if __name__ == "__main__":
    main()
