# src\db\connections.py
# Handles database connections, initialization, and migrations.

PRINT_PREFIX = "DATABASE INIT"

# Standard library imports
import os
import sqlite3
from typing import Dict

# Local imports
from . import DATABASES, DB_DIR

def connect_db(db_file_name: str, read_only: bool = False) -> sqlite3.Connection:
    """
    Connect to a database and return the connection.
    Automatically creates the database directory and file if they don't exist.
    
    Args:
        db_file_name: Name of the database file
        read_only: If True, open database in read-only mode
        
    Returns:
        sqlite3.Connection: Database connection
    """
    try:
        db_path = os.path.join(DB_DIR, db_file_name)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        if read_only:
            conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        else:
            conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to connect to database '{db_file_name}': {e}")
        raise e


def _init_tables_from_schema(schema: Dict[str, str], db_file_name: str) -> None:
    """
    Initialize database tables from schema dictionary.
    
    Args:
        schema: Dictionary mapping table names to CREATE TABLE statements
        db_file_name: Name of the database file
    """
    conn = connect_db(db_file_name)
    cursor = conn.cursor()
    
    for table_name, create_statement in schema.items():
        cursor.execute(create_statement)
        print(f"[DEBUG] [{PRINT_PREFIX}] Created/verified table '{table_name}' in '{db_file_name}'")
    
    conn.commit()
    conn.close()
    print(f"[INFO] [{PRINT_PREFIX}] Initialized tables in '{db_file_name}'")


def init_databases() -> None:
    """
    Initialize all database files and tables.
    This should be called once at startup.
    """
    # Import here to avoid circular imports
    from .bot_db import schema as bot_db_schema
    
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Initialize bot database
    _init_tables_from_schema(bot_db_schema.SCHEMA, bot_db_schema.DB_FILE_NAME)
    DATABASES[bot_db_schema.DB_FILE_NAME] = bot_db_schema
    print(f"[INFO] [{PRINT_PREFIX}] Bot database initialized")
    
    print(f"[INFO] [{PRINT_PREFIX}] All databases initialized successfully")


def migrate_db(db_file_name: str) -> None:
    """
    Creates a new database with the desired schema and copies over matching data.
    
    Args:
        db_file_name: Name of the database file to migrate
    """
    PRINT_PREFIX = "DATABASE MIGRATION"
    
    if db_file_name not in DATABASES:
        print(f"[ERROR] [{PRINT_PREFIX}] Migration failed: Unknown database file '{db_file_name}'")
        raise ValueError(f"Unknown database file: {db_file_name}")

    print(f"[INFO]  [{PRINT_PREFIX}] Starting migration for database '{db_file_name}'")
    desired_schema = DATABASES[db_file_name].SCHEMA
    old_db_path = os.path.join(DB_DIR, db_file_name)

    temp_db_path = os.path.join(DB_DIR, f"temp_{db_file_name}")
    temp_conn = sqlite3.connect(temp_db_path)
    temp_cursor = temp_conn.cursor()
    print(f"[INFO]  [{PRINT_PREFIX}] Created temporary database for migration")

    # Initialize desired schema onto the new temp database
    for ddl in desired_schema.values():
        temp_cursor.execute(ddl)
    print(f"[INFO]  [{PRINT_PREFIX}] Applied new schema to temporary database")

    # Load old database into the connection
    temp_cursor.execute(f"ATTACH DATABASE '{old_db_path}' AS olddb")

    # For each table in the desired schema, copy data from old to new if columns match
    for table_name in desired_schema.keys():
        # Get columns from old table
        temp_cursor.execute(f"PRAGMA olddb.table_info({table_name})")
        old_columns_info = temp_cursor.fetchall()
        old_columns = {col[1] for col in old_columns_info}

        # Get columns from new table
        temp_cursor.execute(f"PRAGMA table_info({table_name})")
        new_columns_info = temp_cursor.fetchall()
        new_columns = {col[1] for col in new_columns_info}

        # Determine common columns
        common_columns = old_columns.intersection(new_columns)
        if not common_columns:
            print(f"[WARN]  [{PRINT_PREFIX}] No common columns found for table '{table_name}', skipping data copy")
            continue  # No common columns to copy
        else:
            print(f"[INFO]  [{PRINT_PREFIX}] Found {len(common_columns)} common columns for table '{table_name}'")

        columns_str = ", ".join(common_columns)

        # Copy data from old to new table
        temp_cursor.execute(f"""
            INSERT INTO {table_name} ({columns_str})
            SELECT {columns_str} FROM olddb.{table_name}
        """)
        print(f"[INFO]  [{PRINT_PREFIX}] Migrated data for table '{table_name}' ({len(common_columns)} columns)")

    # Cleanup
    temp_conn.commit()
    temp_conn.close()
    os.replace(temp_db_path, old_db_path)
    print(f"[INFO] [{PRINT_PREFIX}] Migration completed successfully for database '{db_file_name}'")


