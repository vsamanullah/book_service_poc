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


class TestDataPopulator:
    """Manages test data population for BookService database"""
    
    def __init__(self, connection_string: str, record_count: int):
        self.connection_string = connection_string
        self.record_count = record_count
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
            logger.info(f"✓ Connected to database successfully")
            logger.info(f"  Database Version: {version[:100]}...")
            return True
        except Exception as e:
            logger.error(f"✗ Database connection failed: {e}")
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
            
            # Disable foreign key constraints temporarily
            logger.info("⚙  Disabling foreign key constraints...")
            cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'")
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
                        logger.info(f"🗑  Deleted {count:>5} rows from {schema}.{table_name}")
                    else:
                        logger.info(f"⊘  Skipped {schema}.{table_name} (already empty)")
                        
                except Exception as e:
                    logger.warning(f"⚠  Could not delete from {schema}.{table_name}: {e}")
            
            # Re-enable foreign key constraints
            logger.info("\n⚙  Re-enabling foreign key constraints...")
            cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL'")
            conn.commit()
            
            logger.info("="*70)
            logger.info("✓ All records deleted successfully")
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
        
        logger.info(f"\n📝 Populating Authors table with {count} records...")
        
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
                      'William', 'Mary', 'James', 'Patricia', 'Charles', 'Jennifer', 'Daniel']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
                     'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson']
        
        author_ids = []
        
        for i in range(count):
            # Create unique timestamp-based identifier
            timestamp_str = (self.timestamp + timedelta(seconds=i)).strftime('%Y%m%d%H%M%S')
            microseconds = (self.timestamp + timedelta(microseconds=i*1000)).microsecond
            
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            author_name = f"{first_name} {last_name} [{timestamp_str}.{microseconds:06d}]"
            
            try:
                cursor.execute("""
                    INSERT INTO Authors (Name)
                    OUTPUT INSERTED.Id
                    VALUES (?)
                """, author_name)
                
                author_id = cursor.fetchone()[0]
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
        
        logger.info(f"\n📚 Populating Books table with {count} records...")
        
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
            
            try:
                cursor.execute("""
                    INSERT INTO Books (Title, AuthorId)
                    OUTPUT INSERTED.Id
                    VALUES (?, ?)
                """, title, author_id)
                
                book_id = cursor.fetchone()[0]
                book_ids.append(book_id)
                
                if (i + 1) % 10 == 0 or i == count - 1:
                    logger.info(f"   Created {i + 1}/{count} books...")
                    
            except Exception as e:
                logger.error(f"   Error creating book {i+1}: {e}")
                raise
        
        conn.commit()
        logger.info(f"✓ Created {len(book_ids)} books successfully")
        
        return book_ids
    
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
            
            logger.info("\n" + "="*70)
            logger.info("✓ DATABASE POPULATED SUCCESSFULLY")
            logger.info("="*70)
            logger.info(f"  Authors created: {len(author_ids)}")
            logger.info(f"  Books created:   {len(book_ids)}")
            logger.info("="*70)
            
        except Exception as e:
            logger.error(f"\n❌ Error populating database: {e}")
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
                    SUM(p.rows) AS RowCount
                FROM sys.tables t
                INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                INNER JOIN sys.partitions p ON t.object_id = p.object_id
                WHERE p.index_id IN (0, 1)
                    AND s.name NOT IN ('sys', 'INFORMATION_SCHEMA')
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
╔══════════════════════════════════════════════════════════════════╗
║   Database Test Data Populator                                  ║
║   Delete all records and populate with fresh test data          ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("❌ Error: Missing record count parameter")
        print("\nUsage:")
        print("  python populate_test_data.py <number_of_records>")
        print("\nExample:")
        print("  python populate_test_data.py 25")
        print("  This will create 25 authors and 50 books (2x ratio)")
        sys.exit(1)
    
    try:
        record_count = int(sys.argv[1])
        if record_count <= 0:
            raise ValueError("Record count must be positive")
    except ValueError as e:
        print(f"❌ Error: Invalid record count '{sys.argv[1]}'")
        print("   Record count must be a positive integer")
        sys.exit(1)
    
    # Detect best available ODBC driver
    available_driver = None
    try:
        import pyodbc
        all_drivers = pyodbc.drivers()
        
        preferred_drivers = [
            "ODBC Driver 17 for SQL Server",
            "ODBC Driver 13 for SQL Server",
            "SQL Server Native Client 11.0",
            "SQL Server"
        ]
        
        for driver in preferred_drivers:
            if driver in all_drivers:
                available_driver = driver
                print(f"Using ODBC driver: {available_driver}")
                break
                
        if not available_driver:
            available_driver = "SQL Server"
            print(f"Using default ODBC driver: {available_driver}")
    except Exception as e:
        available_driver = "SQL Server"
        print(f"Warning: Could not detect drivers, using default: {e}")
    
    connection_string = (
        f"DRIVER={{{available_driver}}};"
        "SERVER=(localdb)\\MSSQLLocalDB;"
        "DATABASE=BookServiceContext;"
        "Trusted_Connection=yes;"
    )
    
    # Allow custom connection string from environment or additional args
    if len(sys.argv) > 2:
        connection_string = sys.argv[2]
    
    # Create populator instance
    populator = TestDataPopulator(connection_string, record_count)
    
    # Test connection
    if not populator.test_connection():
        print("\n❌ Cannot connect to database. Please check connection string.")
        print(f"   Connection: {connection_string}")
        sys.exit(1)
    
    # Show summary before deletion
    print("\n" + "="*70)
    print("CURRENT DATABASE STATE (BEFORE DELETION)")
    print("="*70)
    populator.print_summary()
    
    # Ask for confirmation
    print("\n" + "="*70)
    print("⚠️  WARNING: This will DELETE ALL existing records!")
    print("="*70)
    print(f"Then populate with {record_count} new test records per table")
    print("(Authors: {}, Books: {})".format(record_count, record_count * 2))
    print("="*70)
    proceed = input("\nAre you sure you want to proceed? (yes/no): ")
    
    if proceed.lower() not in ['yes', 'y']:
        print("Cancelled.")
        sys.exit(0)
    
    try:
        # Delete all records
        populator.delete_all_records()
        
        # Populate with new data
        populator.populate_database()
        
        # Show final summary
        populator.print_summary()
        
        print("\n" + "="*70)
        print("✅ TEST DATA POPULATED SUCCESSFULLY")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"   • Deleted all existing records")
        print(f"   • Created {record_count} authors")
        print(f"   • Created {record_count * 2} books")
        print(f"   • All records have unique timestamp-based identifiers")
        print("\n📋 Next Steps:")
        print("   1. Run: python create_baseline.py")
        print("   2. Perform your migration/changes")
        print("   3. Run: python verify_migration.py")
        print("="*70)
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
