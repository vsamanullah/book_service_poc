"""
Query database tables from BookService database
Enhanced version with foreign keys and primary keys display
"""
import pyodbc
import json
import argparse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path="db_config.json", env_name="target"):
    """Load database configuration from JSON file"""
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['environments'][env_name]

def build_connection_string(env_config):
    """Build ODBC connection string from environment config"""
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

def get_primary_keys(cursor, schema, table):
    """Get primary key columns for a table"""
    cursor.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + CONSTRAINT_NAME), 'IsPrimaryKey') = 1
        AND TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
    """, (schema, table))
    return [row[0] for row in cursor.fetchall()]

def get_foreign_keys(cursor, schema, table):
    """Get foreign key relationships for a table"""
    cursor.execute("""
        SELECT 
            fk.name AS FK_Name,
            cp.name AS Column_Name,
            OBJECT_SCHEMA_NAME(fk.referenced_object_id) AS Referenced_Schema,
            OBJECT_NAME(fk.referenced_object_id) AS Referenced_Table,
            cr.name AS Referenced_Column
        FROM sys.foreign_keys AS fk
        INNER JOIN sys.foreign_key_columns AS fkc 
            ON fk.object_id = fkc.constraint_object_id
        INNER JOIN sys.tables AS tp 
            ON fk.parent_object_id = tp.object_id
        INNER JOIN sys.columns AS cp 
            ON fkc.parent_object_id = cp.object_id 
            AND fkc.parent_column_id = cp.column_id
        INNER JOIN sys.columns AS cr 
            ON fkc.referenced_object_id = cr.object_id 
            AND fkc.referenced_column_id = cr.column_id
        INNER JOIN sys.schemas AS s 
            ON tp.schema_id = s.schema_id
        WHERE s.name = ? AND tp.name = ?
    """, (schema, table))
    return cursor.fetchall()

def query_tables(env_name="target", config_path="db_config.json"):
    """Query all tables from the database"""
    try:
        # Load configuration
        env_config = load_config(config_path, env_name)
        connection_string = build_connection_string(env_config)
        
        print(f"\n{'='*70}")
        print(f"Environment: {env_name.upper()}")
        print(f"Database: {env_config['database']}")
        print(f"Server: {env_config.get('server', 'N/A')}")
        print(f"{'='*70}\n")
        
        logger.info("Connecting to database...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        logger.info("Connected successfully")
        
        # Get all tables
        query = """
            SELECT 
                TABLE_SCHEMA, 
                TABLE_NAME,
                (SELECT COUNT(*) 
                 FROM INFORMATION_SCHEMA.COLUMNS c 
                 WHERE c.TABLE_SCHEMA = t.TABLE_SCHEMA 
                   AND c.TABLE_NAME = t.TABLE_NAME) as ColumnCount
            FROM INFORMATION_SCHEMA.TABLES t
            WHERE TABLE_TYPE = 'BASE TABLE'
              AND TABLE_SCHEMA NOT IN ('sys', 'INFORMATION_SCHEMA')
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        
        cursor.execute(query)
        tables = cursor.fetchall()
        
        print("\n" + "="*70)
        print(f"DATABASE: {env_config['database']}")
        print(f"SERVER: {env_config.get('server', 'N/A')}")
        print("="*70)
        print(f"\nTotal Tables Found: {len(tables)}\n")
        
        for row in tables:
            print(f"  {row.TABLE_SCHEMA}.{row.TABLE_NAME:<40} ({row.ColumnCount} columns)")
        
        print("\n" + "="*70)
        print("Getting detailed column information for each table...")
        print("="*70 + "\n")
        
        for row in tables:
            schema = row.TABLE_SCHEMA
            table = row.TABLE_NAME
            
            # Get columns for this table
            cursor.execute(f"""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE,
                    COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            
            # Get primary keys for this table
            pk_columns = get_primary_keys(cursor, schema, table)
            
            # Get foreign keys for this table
            fk_info = get_foreign_keys(cursor, schema, table)
            fk_columns = {fk[1] for fk in fk_info}
            
            print(f"\n{schema}.{table}")
            print("-" * 70)
            for col in columns:
                col_name = col.COLUMN_NAME
                data_type = col.DATA_TYPE
                max_len = f"({col.CHARACTER_MAXIMUM_LENGTH})" if col.CHARACTER_MAXIMUM_LENGTH else ""
                nullable = "NULL" if col.IS_NULLABLE == "YES" else "NOT NULL"
                default = f" DEFAULT {col.COLUMN_DEFAULT}" if col.COLUMN_DEFAULT else ""
                
                # Add markers for PK and FK
                markers = ""
                if col_name in pk_columns:
                    markers += " [PK]"
                if col_name in fk_columns:
                    markers += " [FK]"
                
                print(f"  {col_name:<30} {data_type}{max_len:<15} {nullable:<12}{markers}{default}")
            
            # Display foreign key relationships
            if fk_info:
                print(f"\n  Foreign Keys:")
                for fk in fk_info:
                    print(f"    {fk[1]} -> {fk[2]}.{fk[3]}.{fk[4]}")
            
            # Display primary key
            if pk_columns:
                print(f"\n  Primary Key: {', '.join(pk_columns)}")
        
        # Get row counts
        print("\n" + "="*70)
        print("Row Counts:")
        print("="*70 + "\n")
        
        for row in tables:
            schema = row.TABLE_SCHEMA
            table = row.TABLE_NAME
            cursor.execute(f"SELECT COUNT(*) FROM [{schema}].[{table}]")
            count = cursor.fetchone()[0]
            print(f"  {schema}.{table:<40} {count:>10} rows")
        
        conn.close()
        
        print("\n" + "="*70)
        print("✓ Query completed successfully")
        print("="*70)
        print("\nLegend:")
        print("  [PK] = Primary Key")
        print("  [FK] = Foreign Key")
        print("="*70)
        
    except pyodbc.Error as e:
        logger.error(f"Database error: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Query and display database tables with detailed schema information',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python query_db_tables.py --env source
  python query_db_tables.py --env target
  python query_db_tables.py --env local --config custom_config.json
        """
    )
    parser.add_argument('--env', type=str, default='target',
                        choices=['source', 'target', 'local'],
                        help='Environment to use (default: target)')
    parser.add_argument('--config', type=str, default='../db_config.json',
                        help='Path to config file (default: ../db_config.json)')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("        Database Tables Query Tool")
    print("="*70)
    
    query_tables(args.env, args.config)
