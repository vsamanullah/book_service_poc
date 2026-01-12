"""
BookService Database Test Data Populator

This script:
1. Deletes all existing records from the database
2. Populates tables with N test records (N specified via command line)
3. Creates unique records using timestamps for uniqueness
"""

import pyodbc
import sys
from datetime import datetime, timedelta
import logging
import random
import argparse
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'populate_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from: {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        sys.exit(1)


def build_connection_string(env_config: dict) -> str:
    """Build connection string from environment configuration"""
    server = env_config.get('server', '')
    port = env_config.get('port', '')
    server_str = f"{server},{port}" if port else server
    
    return (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server_str};"
        f"DATABASE={env_config['database']};"
        f"UID={env_config.get('username', '')};"
        f"PWD={env_config.get('password', '')};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes"
    )


def get_connection_from_config(env_name: str, config_path: str = "../db_config.json") -> str:
    """Get connection string for specified environment from config file"""
    config = load_config(config_path)
    
    if env_name not in config['environments']:
        logger.error(f"Environment '{env_name}' not found in configuration")
        logger.info(f"Available environments: {', '.join(config['environments'].keys())}")
        sys.exit(1)
    
    env_config = config['environments'][env_name]
    conn_str = build_connection_string(env_config)
    logger.info(f"Using environment: {env_name}")
    
    return conn_str


class TestDataPopulator:
    """Manages test data population for BookService database"""
    
    def __init__(self, connection_string: str, record_count: int, env_name: str = "target"):
        self.connection_string = connection_string
        self.record_count = record_count
        self.env_name = env_name
        self.timestamp = datetime.now()
        
    def get_connection(self):
        """Get database connection"""
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            conn.close()
            logger.info(f" Connected to database successfully")
            logger.info(f"  Database Version: {version[:100]}...")
            return True
        except Exception as e:
            logger.error(f" Database connection failed: {e}")
            return False
    
    def get_table_structure(self, conn):
        """Get database table structure to understand relationships"""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                t.TABLE_SCHEMA,
                t.TABLE_NAME,
                (SELECT COUNT(*) 
                 FROM INFORMATION_SCHEMA.COLUMNS c 
                 WHERE c.TABLE_SCHEMA = t.TABLE_SCHEMA 
                   AND c.TABLE_NAME = t.TABLE_NAME) as ColumnCount
            FROM INFORMATION_SCHEMA.TABLES t
            WHERE t.TABLE_TYPE = 'BASE TABLE'
                AND t.TABLE_SCHEMA NOT IN ('sys', 'INFORMATION_SCHEMA')
            ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME
        """)
        
        tables = []
        for row in cursor.fetchall():
            tables.append({
                'schema': row[0],
                'name': row[1],
                'columns': row[2]
            })
        return tables
    
    def get_foreign_key_order(self, conn):
        """Get tables in order for deletion (child tables first)"""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT
                s.name AS TableSchema,
                t.name AS TableName,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM sys.foreign_keys fk 
                        WHERE fk.parent_object_id = t.object_id
                    ) THEN 1
                    ELSE 0
                END AS HasForeignKeys
            FROM sys.tables t
            INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE s.name NOT IN ('sys', 'INFORMATION_SCHEMA')
                AND t.name NOT IN ('__MigrationHistory')
            ORDER BY HasForeignKeys DESC, TableName
        """)
        
        return [(row[0], row[1]) for row in cursor.fetchall()]
    
    def delete_all_records(self):
        """Delete all records from all user tables"""
        logger.info("\n" + "="*70)
        logger.info("DELETING ALL RECORDS FROM DATABASE")
        logger.info("="*70)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get tables in proper order (respecting foreign keys)
            tables = self.get_foreign_key_order(conn)
            
            logger.info(f"Found {len(tables)} tables to clear\n")
            
            # Disable foreign key constraints for specific tables only
            logger.info("⚙  Disabling foreign key constraints...")
            for schema, table_name in tables:
                try:
                    cursor.execute(f"ALTER TABLE [{schema}].[{table_name}] NOCHECK CONSTRAINT ALL")
                except Exception as e:
                    logger.warning(f"  Could not disable constraints on {schema}.{table_name}: {e}")
            conn.commit()
            
            # Delete from each table
            for schema, table_name in tables:
                full_table = f"[{schema}].[{table_name}]"
                try:
                    # Get current row count
                    cursor.execute(f"SELECT COUNT(*) FROM {full_table}")
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        # Delete all records
                        cursor.execute(f"DELETE FROM {full_table}")
                        conn.commit()
                        logger.info(f"  Deleted {count:>5} rows from {schema}.{table_name}")
                    else:
                        logger.info(f"  Skipped {schema}.{table_name} (already empty)")
                        
                except Exception as e:
                    logger.warning(f"  Could not delete from {schema}.{table_name}: {e}")
            
            # Re-enable foreign key constraints for specific tables only
            logger.info("\n⚙  Re-enabling foreign key constraints...")
            for schema, table_name in tables:
                try:
                    cursor.execute(f"ALTER TABLE [{schema}].[{table_name}] WITH CHECK CHECK CONSTRAINT ALL")
                except Exception as e:
                    logger.warning(f"  Could not re-enable constraints on {schema}.{table_name}: {e}")
            conn.commit()
            
            logger.info("="*70)
            logger.info(" All records deleted successfully")
            logger.info("="*70)
            
        except Exception as e:
            logger.error(f"Error during deletion: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def populate_authors(self, conn, count: int):
        """Populate Authors table with test data"""
        cursor = conn.cursor()
        
        logger.info(f"\n Populating Authors table with {count} records...")
        
        # Check table structure
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'Authors'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
        logger.info(f"   Table columns: {', '.join([c[0] for c in columns])}")
        
        # Generate and insert authors
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Robert', 'Lisa', 
                      'William', 'Mary', 'James', 'Patricia', 'Charles', 'Jennifer', 'Daniel',
                      'Thomas', 'Susan', 'Joseph', 'Nancy', 'Richard', 'Betty', 'Christopher']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
                     'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson',
                     'Anderson', 'Taylor', 'Thomas', 'Moore', 'Martin', 'Lee', 'White', 'Harris']
        nationalities = ['American', 'British', 'Canadian', 'Australian', 'Irish', 'German', 'French', 'Spanish',
                        'Italian', 'Japanese', 'Indian', 'Brazilian']
        
        author_ids = []
        
        for i in range(count):
            # Create unique timestamp-based identifier
            timestamp_str = (self.timestamp + timedelta(seconds=i)).strftime('%Y%m%d%H%M%S')
            microseconds = (self.timestamp + timedelta(microseconds=i*1000)).microsecond
            
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            unique_suffix = f"[{timestamp_str}.{microseconds:06d}]"
            
            # Generate author name (single Name field)
            author_name = f"{first_name} {last_name} {unique_suffix}"
            
            try:
                cursor.execute("""
                    INSERT INTO Authors (Name)
                    VALUES (?)
                """, author_name)
                
                # Get the inserted ID
                cursor.execute("SELECT @@IDENTITY")
                author_id = int(cursor.fetchone()[0])
                author_ids.append(author_id)
                
                if (i + 1) % 10 == 0 or i == count - 1:
                    logger.info(f"   Created {i + 1}/{count} authors...")
                    
            except Exception as e:
                logger.error(f"   Error creating author {i+1}: {e}")
                raise
        
        conn.commit()
        logger.info(f"✓ Created {len(author_ids)} authors successfully")
        
        return author_ids
    
    def populate_books(self, conn, author_ids: list, count: int):
        """Populate Books table with test data"""
        cursor = conn.cursor()
        
        logger.info(f"\n Populating Books table with {count} records...")
        
        # Check table structure
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'Books'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
        logger.info(f"   Table columns: {', '.join([c[0] for c in columns])}")
        
        # Book title templates
        title_templates = [
            'The Adventures of {}',
            'Guide to {}',
            'History of {}',
            'Introduction to {}',
            'Mastering {}',
            'The Complete {} Handbook',
            'Essential {} Techniques',
            'Understanding {}',
            '{} for Beginners',
            'Advanced {} Concepts',
            'The {} Chronicles',
            '{} in Modern Times'
        ]
        
        topics = ['Programming', 'Databases', 'Cloud Computing', 'AI', 'Data Science',
                 'Web Development', 'Mobile Apps', 'Security', 'DevOps', 'Testing',
                 'Architecture', 'Design Patterns', 'Algorithms', 'Networks', 'APIs']
        
        book_ids = []
        
        for i in range(count):
            # Create unique timestamp-based identifier
            timestamp_str = (self.timestamp + timedelta(seconds=i)).strftime('%Y%m%d%H%M%S')
            microseconds = (self.timestamp + timedelta(microseconds=i*1000)).microsecond
            
            template = random.choice(title_templates)
            topic = random.choice(topics)
            title = template.format(topic) + f" [TS:{timestamp_str}.{microseconds:06d}]"
            
            # Assign to random author
            author_id = random.choice(author_ids)
            year = random.randint(2000, 2026)
            price = round(random.uniform(9.99, 99.99), 2)
            genre = random.choice(['Fiction', 'Non-Fiction', 'Science', 'Technology', 'History', 'Biography', 'Mystery', 'Thriller'])
            
            try:
                cursor.execute("""
                    INSERT INTO Books (Title, Year, Price, Genre, AuthorId)
                    VALUES (?, ?, ?, ?, ?)
                """, title, year, price, genre, author_id)
                
                # Get the inserted ID
                cursor.execute("SELECT @@IDENTITY")
                book_id = int(cursor.fetchone()[0])
                book_ids.append(book_id)
                
                if (i + 1) % 10 == 0 or i == count - 1:
                    logger.info(f"   Created {i + 1}/{count} books...")
                    
            except Exception as e:
                logger.error(f"   Error creating book {i+1}: {e}")
                raise
        
        conn.commit()
        logger.info(f"✓ Created {len(book_ids)} books successfully")
        
        return book_ids
    
    def populate_customers(self, conn, count: int):
        """Populate Customers table with test data"""
        cursor = conn.cursor()
        
        logger.info(f"\n Populating Customers table with {count} records...")
        
        first_names = ['Alice', 'Bob', 'Carol', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 
                      'Ivy', 'Jack', 'Kate', 'Leo', 'Mia', 'Noah', 'Olivia', 'Paul', 'Quinn',
                      'Rachel', 'Sam', 'Tina', 'Uma', 'Victor', 'Wendy', 'Xavier', 'Yara', 'Zoe']
        last_names = ['Anderson', 'Baker', 'Carter', 'Davis', 'Evans', 'Foster', 'Green', 
                     'Harris', 'Irving', 'Jackson', 'King', 'Lewis', 'Moore', 'Nelson', 'Owen',
                     'Parker', 'Quinn', 'Reed', 'Scott', 'Turner', 'Underwood', 'Vincent']
        
        customer_ids = []
        
        for i in range(count):
            timestamp_str = (self.timestamp + timedelta(seconds=i)).strftime('%Y%m%d%H%M%S')
            microseconds = (self.timestamp + timedelta(microseconds=i*1000)).microsecond
            
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            unique_suffix = f"[{timestamp_str}.{microseconds:06d}]"
            
            email = f"{first_name.lower()}.{last_name.lower()}.{i}@customer.com"
            country = random.choice(['USA', 'UK', 'Canada', 'Australia', 'Germany', 'France', 'India', 'Japan'])
            
            try:
                cursor.execute("""
                    INSERT INTO Customers (FirstName, LastName, Email, Country)
                    VALUES (?, ?, ?, ?)
                """, first_name + " " + unique_suffix, last_name, email, country)
                
                # Get the inserted ID
                cursor.execute("SELECT @@IDENTITY")
                customer_id = int(cursor.fetchone()[0])
                customer_ids.append(customer_id)
                
                if (i + 1) % 10 == 0 or i == count - 1:
                    logger.info(f"   Created {i + 1}/{count} customers...")
                    
            except Exception as e:
                logger.error(f"   Error creating customer {i+1}: {e}")
                raise
        
        conn.commit()
        logger.info(f"✓ Created {len(customer_ids)} customers successfully")
        
        return customer_ids
    
    # Note: Stocks and Rentals tables not found in current schema - methods removed
    
    def populate_database(self):
        """Populate Stocks table with test data"""
        cursor = conn.cursor()
        
        total_stocks = len(book_ids) * copies_per_book
        logger.info(f"\n Populating Stocks table with {total_stocks} records ({copies_per_book} copies per book)...")
        
        stock_ids = []
        counter = 0
        
        for book_id in book_ids:
            for copy in range(copies_per_book):
                import uuid
                unique_key = str(uuid.uuid4())
                is_available = random.choice([True, True, True, False])  # 75% available
                
                try:
                    cursor.execute("""
                        INSERT INTO Stocks (BookId, UniqueKey, IsAvailable)
                        OUTPUT INSERTED.ID
                        VALUES (?, ?, ?)
                    """, book_id, unique_key, is_available)
                    
                    stock_id = cursor.fetchone()[0]
                    stock_ids.append(stock_id)
                    counter += 1
                    
                    if counter % 50 == 0 or counter == total_stocks:
                        logger.info(f"   Created {counter}/{total_stocks} stocks...")
                        
                except Exception as e:
                    logger.error(f"   Error creating stock for book {book_id}: {e}")
                    raise
        
        conn.commit()
        logger.info(f"✓ Created {len(stock_ids)} stocks successfully")
        
        return stock_ids
    
    def populate_rentals(self, conn, customer_ids: list, stock_ids: list, rental_count: int):
        """Populate Rentals table with test data"""
        cursor = conn.cursor()
        
        logger.info(f"\n Populating Rentals table with {rental_count} records...")
        
        rental_ids = []
        statuses = ['Rented', 'Returned', 'Returned', 'Returned', 'Overdue']  # Mixed statuses
        
        for i in range(rental_count):
            customer_id = random.choice(customer_ids)
            stock_id = random.choice(stock_ids)
            status = random.choice(statuses)
            
            rental_date = datetime.now() - timedelta(days=random.randint(1, 180))
            returned_date = rental_date + timedelta(days=random.randint(7, 30)) if status == 'Returned' else None
            
            try:
                cursor.execute("""
                    INSERT INTO Rentals (CustomerId, StockId, RentalDate, ReturnedDate, Status)
                    OUTPUT INSERTED.ID
                    VALUES (?, ?, ?, ?, ?)
                """, customer_id, stock_id, rental_date, returned_date, status)
                
                rental_id = cursor.fetchone()[0]
                rental_ids.append(rental_id)
                
                if (i + 1) % 10 == 0 or i == rental_count - 1:
                    logger.info(f"   Created {i + 1}/{rental_count} rentals...")
                    
            except Exception as e:
                logger.error(f"   Error creating rental {i+1}: {e}")
                raise
        
        conn.commit()
        logger.info(f"✓ Created {len(rental_ids)} rentals successfully")
        
        return rental_ids
    
    def populate_database(self):
        """Main method to populate database with test data"""
        logger.info("\n" + "="*70)
        logger.info("POPULATING DATABASE WITH TEST DATA")
        logger.info("="*70)
        logger.info(f"Records to create per table: {self.record_count}")
        logger.info(f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        logger.info("="*70)
        
        conn = self.get_connection()
        
        try:
            # Get table structure
            tables = self.get_table_structure(conn)
            logger.info(f"\nDatabase has {len(tables)} user tables:")
            for table in tables:
                logger.info(f"  • {table['schema']}.{table['name']} ({table['columns']} columns)")
            
            # Populate Authors first (parent table)
            author_ids = self.populate_authors(conn, self.record_count)
            
            # Populate Books (child table with FK to Authors)
            # Create more books than authors (realistic scenario)
            books_count = self.record_count * 2
            book_ids = self.populate_books(conn, author_ids, books_count)
            
            # Populate Customers (independent table)
            customer_ids = self.populate_customers(conn, self.record_count)
            
            logger.info("\n" + "="*70)
            logger.info("✓ DATABASE POPULATED SUCCESSFULLY")
            logger.info("="*70)
            logger.info(f"  Authors created:   {len(author_ids)}")
            logger.info(f"  Books created:     {len(book_ids)}")
            logger.info(f"  Customers created: {len(customer_ids)}")
            logger.info("="*70)
            
        except Exception as e:
            logger.error(f"\n Error populating database: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def print_summary(self):
        """Print summary of current database state"""
        logger.info("\n" + "="*70)
        logger.info("DATABASE SUMMARY")
        logger.info("="*70)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get all tables and row counts
            cursor.execute("""
                SELECT 
                    s.name + '.' + t.name AS TableName,
                    SUM(p.rows) AS RowCnt
                FROM sys.tables t
                INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                INNER JOIN sys.partitions p ON t.object_id = p.object_id
                WHERE p.index_id IN (0, 1)
                    AND s.name NOT IN ('sys', 'INFORMATION_SCHEMA')
                    AND t.name NOT IN ('__MigrationHistory')
                GROUP BY s.name, t.name
                ORDER BY s.name, t.name
            """)
            
            total_rows = 0
            for row in cursor.fetchall():
                table_name = row[0]
                row_count = row[1]
                total_rows += row_count
                logger.info(f"  {table_name:40} {row_count:>10} rows")
            
            logger.info("=" * 70)
            logger.info(f"  Total Rows: {total_rows}")
            logger.info("=" * 70)
            
        finally:
            conn.close()


def main():
    """Main entry point"""
    print("""  
           Database Test Data Populator 
           Delete all records and populate with fresh test data 
    """)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Populate database with test data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using environment from config file:
  python populate_test_data.py 25 --env source
  
  # Using custom config file:
  python populate_test_data.py 50 --env target --config my_config.json
  
  # Using direct connection string:
  python populate_test_data.py 100 --conn "DRIVER={...};SERVER=...;..."
  
  # Default (without config):
  python populate_test_data.py 25
        """
    )
    
    parser.add_argument('--count', type=int, default=10,
                       help='Number of records to create per table (default: 10). Use 0 to only delete all records.')
    parser.add_argument('--env', type=str, default='target',
                       choices=['source', 'target', 'local'],
                       help='Environment to populate (default: target)')
    parser.add_argument('--config', type=str, default='../db_config.json',
                       help='Path to config file (default: ../db_config.json)')
    
    args = parser.parse_args()
    
    # Validate record count
    record_count = args.count
    if record_count < 0:
        print(f"✗ Error: Invalid record count '{record_count}'")
        print("  Record count must be 0 or a positive integer (use 0 to delete all records only)")
        sys.exit(1)
    
    # Load configuration
    try:
        connection_string = get_connection_from_config(args.env, args.config)
        env_config = load_config(args.config)['environments'][args.env]
    except Exception as e:
        print(f"\n✗ Error loading configuration: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error loading configuration: {e}")
        sys.exit(1)
    
    # Create populator instance
    populator = TestDataPopulator(connection_string, record_count, args.env)
    
    # Print environment info
    print("="*70)
    print(f"Environment: {args.env.upper()}")
    print(f"Database: {env_config['database']}")
    print(f"Server: {env_config.get('server', 'N/A')}")
    print(f"Records per table: {record_count}")
    print("="*70)
    
    # Test connection
    if not populator.test_connection():
        print("\n✗ Cannot connect to database. Please check configuration.")
        sys.exit(1)
    
    # Show summary before deletion
    print("\n" + "="*70)
    print("CURRENT DATABASE STATE (BEFORE DELETION)")
    print("="*70)
    populator.print_summary()
    
    # Info about what will happen
    print("\n" + "="*70)
    if record_count == 0:
        print("⚠ WARNING: This will DELETE ALL records (NO new data will be populated)")
    else:
        print("⚠ WARNING: This will DELETE ALL records and populate with new data")
    print("="*70)
    if record_count > 0:
        print(f"Will populate with {record_count} new test records per table")
        print("(Authors: {}, Books: {}, Customers: {})".format(
            record_count, record_count * 2, record_count))
    else:
        print("All records will be DELETED. No new data will be created.")
    print("="*70 + "\n")
    
    try:
        # Delete all records
        populator.delete_all_records()
        
        if record_count > 0:
            # Populate with new data
            populator.populate_database()
            
            # Show final summary
            populator.print_summary()
            
            print("\n" + "="*70)
            print("✓ TEST DATA POPULATED SUCCESSFULLY")
            print("="*70)
            print(f"\n  Summary:")
            print(f"    • Environment: {args.env.upper()}")
            print(f"    • Deleted all existing records")
            print(f"    • Created {record_count} authors")
            print(f"    • Created {record_count * 2} books")
            print(f"    • Created {record_count} customers")
            print(f"    • All records have unique timestamp-based identifiers")
            print("="*70)
        else:
            # Show final summary after deletion only
            populator.print_summary()
            
            print("\n" + "="*70)
            print("✓ ALL RECORDS DELETED SUCCESSFULLY")
            print("="*70)
            print(f"\n  Summary:")
            print(f"    • Environment: {args.env.upper()}")
            print(f"    • All existing records have been deleted")
            print(f"    • No new data was populated")
            print(f"    • Database is now empty")
            print("="*70)
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
