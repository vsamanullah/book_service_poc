"""
Check database schema structure
"""
import pyodbc
import json
import argparse
from pathlib import Path

def load_config(config_path="../../db_config.json", env_name="target"):
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

def check_schema(env_name="target", config_path="../../db_config.json"):
    """Check database schema structure"""
    try:
        # Load configuration
        env_config = load_config(config_path, env_name)
        connection_string = build_connection_string(env_config)
        
        print(f"\n{'='*70}")
        print(f"Checking Schema - Environment: {env_name.upper()}")
        print(f"Database: {env_config['database']}")
        print(f"Server: {env_config.get('server', 'N/A')}")
        print(f"{'='*70}\n")
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        tables = ['Authors', 'Books', 'Genres', 'Customers', 'Rentals', 'Stocks']

        for table_name in tables:
            print(f"\n=== {table_name} Table Structure ===")
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)
            
            rows = cursor.fetchall()
            if rows:
                print(f"  {'Column Name':<30} {'Data Type':<15} {'Nullable':<10} {'Max Length'}")
                print(f"  {'-'*30} {'-'*15} {'-'*10} {'-'*10}")
                for row in rows:
                    col_name = row[0]
                    data_type = row[1]
                    nullable = row[2]
                    max_len = row[3] if row[3] else "N/A"
                    print(f"  {col_name:<30} {data_type:<15} {nullable:<10} {max_len}")
            else:
                print(f"  ⚠ Table '{table_name}' not found or has no columns")

        conn.close()
        
        print(f"\n{'='*70}")
        print("Schema check completed successfully")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check database schema structure')
    parser.add_argument('--env', type=str, default='target',
                        choices=['source', 'target', 'local'],
                        help='Environment to use (default: target)')
    parser.add_argument('--config', type=str, default='../../db_config.json',
                        help='Path to config file (default: ../../db_config.json)')
    
    args = parser.parse_args()
    check_schema(args.env, args.config)

