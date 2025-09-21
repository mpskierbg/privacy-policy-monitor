import sqlite3
import os
from log_config import setup_logger

logger = setup_logger(__name__)  # __name__ will be 'database' for this file

def get_db_connection():
    """Create and return a database connection to the SQLite database."""
    # Get the directory of this script
    logger.debug("Establishing database connection")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Create the full path to the database file
    db_path = os.path.join(base_dir, 'privacy_policies.db')

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # This allows us to access columns by name
    return conn

def init_db():
    """Initialize the database with the required tables."""
    logger.info("Initializing database")
    conn = get_db_connection()
    cursor = conn.cursor()
    logger.info("Database initialized successfully")

    # Create a table to store the monitored sites and their latest content
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitored_sites (
            id INTEGER PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            site_name TEXT,
            last_checked TEXT,
            last_content TEXT,
            requires_browser INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

def add_site(url, site_name=None):
    """Add a new site to the monitored_sites table."""
    logger.info(f"Attempting to add site: {url}.")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "Insert INTO monitored_sites (url, site_name) VALUES (?, ?)",
            (url, site_name)
        )
        conn.commit()
        conn.close()
        logger.info(f"Succesfully added {url} to monitored sites.")
    except sqlite3.IntegrityError:
        logger.info(f"{url} is already in the database. Skipping.")
    finally:
        conn.close()

def mark_site_as_requires_browser(site_id):
    """
    Mark a site as requireing browser automation in the database
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        
        check_add_column("requires_browser", "INTEGER DEFAULT 0")
        
        cursor.execute(
            "UPDATE monitored_sites SET requires_browser = 1 WHERE id = ?",
            (site_id,)
        )
        conn.commit()
        logger.info(f"Marked site ID {site_id} as requiring automation.")
    except Exception as e:
        logger.error(f"Error updating site {site_id}: {e}.")
    finally:
        conn.close()

def check_add_column(column_name, column_defintion):
    """
    Add a new column to the monitored_sites table if it doesnt exist
    
    Args:
        column_name (str): the name of the column to add
        column_definition (str): the sqlite column definition (e.g., "INTEGER DEFAULT 0")
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(monitored_sites)")
        columns = [column[1] for column in cursor.fetchall()]

        if column_name not in columns:
            cursor.execute(f"ALTER TABLE monitored_sites ADD COLUMN {column_name} {column_defintion}")
            conn.commit()
            logger.info(f"Successfully added column '{column_name}' to monitored_sites table.")
            return True
        else:
            logger.info(f"Column '{column_name}' already exists in monitored sites table.")
            return False
        
    except Exception as e:
        logger.error(f"Error updating database scheme: {e}.")
        return False
    finally:
        conn.close()

    