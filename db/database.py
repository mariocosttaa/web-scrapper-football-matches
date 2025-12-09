"""
Database Management
===================
Handles SQLite database operations for storing match data.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


# Database file path - in db/ directory
DB_PATH = "db/matches.db"


def get_db_connection():
    """Get a connection to the SQLite database."""
    # Ensure db/ directory exists
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    # Ensure DB_PATH is a file, not a directory
    # If DB_PATH exists as a directory, warn but don't remove (might be a volume mount issue)
    if os.path.exists(DB_PATH) and os.path.isdir(DB_PATH):
        print(f"⚠️  Warning: {DB_PATH} exists as a directory. This may be a Docker volume mount issue.")
        print(f"   Please check docker-compose.yml and ensure {DB_PATH} is mounted as a file, not a directory.")
        raise OSError(f"{DB_PATH} is a directory, not a file. Check Docker volume mounts.")
    
    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def migrate_database_schema(cursor):
    """
    Migrate existing database schema if needed.
    This handles schema changes for existing databases.
    """
    try:
        # Check if we need to migrate (check if old NOT NULL constraint exists)
        cursor.execute("PRAGMA table_info(matches)")
        columns = cursor.fetchall()
        
        # Find home_team_name and away_team_name columns
        home_team_col = next((col for col in columns if col[1] == 'home_team_name'), None)
        away_team_col = next((col for col in columns if col[1] == 'away_team_name'), None)
        
        # If columns exist and have NOT NULL constraint, we need to migrate
        # SQLite doesn't support ALTER COLUMN, so we'll recreate the table
        if home_team_col and home_team_col[3] == 1:  # notnull flag is 1
            print("⚠️  Migrating database schema (removing NOT NULL constraints)...")
            
            # Create backup table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches_backup AS 
                SELECT * FROM matches
            """)
            
            # Drop old table
            cursor.execute("DROP TABLE IF EXISTS matches")
            
            # Recreate with new schema (without NOT NULL)
            cursor.execute("""
                CREATE TABLE matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id TEXT UNIQUE NOT NULL,
                    match_url TEXT,
                    league_name TEXT,
                    league_country TEXT,
                    league_flag_class TEXT,
                    match_time TEXT,
                    scheduled_datetime TEXT,
                    home_team_name TEXT,
                    home_team_logo_url TEXT,
                    away_team_name TEXT,
                    away_team_logo_url TEXT,
                    home_score INTEGER,
                    away_score INTEGER,
                    match_status TEXT,
                    match_stage TEXT,
                    is_live BOOLEAN DEFAULT 0,
                    is_scheduled BOOLEAN DEFAULT 0,
                    is_finished BOOLEAN DEFAULT 0,
                    is_canceled BOOLEAN DEFAULT 0,
                    is_postponed BOOLEAN DEFAULT 0,
                    has_tv_icon BOOLEAN DEFAULT 0,
                    has_audio_icon BOOLEAN DEFAULT 0,
                    has_info_icon BOOLEAN DEFAULT 0,
                    half_time TEXT,
                    current_minute INTEGER,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Copy data back
            cursor.execute("""
                INSERT INTO matches 
                SELECT * FROM matches_backup
            """)
            
            # Drop backup
            cursor.execute("DROP TABLE IF EXISTS matches_backup")
            
            # Recreate indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_match_id ON matches(match_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_match_status ON matches(match_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_datetime ON matches(scheduled_datetime)")
            
            print("✅ Database migration completed")
    except Exception as e:
        print(f"⚠️  Migration check failed (this is OK for new databases): {e}")


def init_database():
    """
    Initialize the database and create tables if they don't exist.
    """
    # Ensure db/ directory exists before connecting
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='matches'")
    table_exists = cursor.fetchone() is not None
    
    # Create matches table with comprehensive fields
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT UNIQUE NOT NULL,
            match_url TEXT,
            league_name TEXT,
            league_country TEXT,
            league_flag_class TEXT,
            match_time TEXT,
            scheduled_datetime TEXT,
            home_team_name TEXT,
            home_team_logo_url TEXT,
            away_team_name TEXT,
            away_team_logo_url TEXT,
            home_score INTEGER,
            away_score INTEGER,
            match_status TEXT,
            match_stage TEXT,
            is_live BOOLEAN DEFAULT 0,
            is_scheduled BOOLEAN DEFAULT 0,
            is_finished BOOLEAN DEFAULT 0,
            is_canceled BOOLEAN DEFAULT 0,
            is_postponed BOOLEAN DEFAULT 0,
            has_tv_icon BOOLEAN DEFAULT 0,
            has_audio_icon BOOLEAN DEFAULT 0,
            has_info_icon BOOLEAN DEFAULT 0,
            half_time TEXT,
            current_minute INTEGER,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index on match_id for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_match_id ON matches(match_id)
    """)
    
    # Create index on match_status for filtering
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_match_status ON matches(match_status)
    """)
    
    # Create index on scheduled_datetime for time-based queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_scheduled_datetime ON matches(scheduled_datetime)
    """)
    
    # Migrate schema if needed (for existing databases)
    if table_exists:
        migrate_database_schema(cursor)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {DB_PATH}")


def insert_or_update_match(match_data: Dict[str, Any]) -> bool:
    """
    Insert a new match or update an existing one.
    
    Args:
        match_data: Dictionary containing match information
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if match already exists
        cursor.execute("SELECT id FROM matches WHERE match_id = ?", (match_data.get('match_id'),))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing match
            cursor.execute("""
                UPDATE matches SET
                    match_url = ?,
                    league_name = ?,
                    league_country = ?,
                    league_flag_class = ?,
                    match_time = ?,
                    scheduled_datetime = ?,
                    home_team_name = ?,
                    home_team_logo_url = ?,
                    away_team_name = ?,
                    away_team_logo_url = ?,
                    home_score = ?,
                    away_score = ?,
                    match_status = ?,
                    match_stage = ?,
                    is_live = ?,
                    is_scheduled = ?,
                    is_finished = ?,
                    is_canceled = ?,
                    is_postponed = ?,
                    has_tv_icon = ?,
                    has_audio_icon = ?,
                    has_info_icon = ?,
                    half_time = ?,
                    current_minute = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE match_id = ?
            """, (
                match_data.get('match_url'),
                match_data.get('league_name'),
                match_data.get('league_country'),
                match_data.get('league_flag_class'),
                match_data.get('match_time'),
                match_data.get('scheduled_datetime'),
                match_data.get('home_team_name'),
                match_data.get('home_team_logo_url'),
                match_data.get('away_team_name'),
                match_data.get('away_team_logo_url'),
                match_data.get('home_score'),
                match_data.get('away_score'),
                match_data.get('match_status'),
                match_data.get('match_stage'),
                match_data.get('is_live', False),
                match_data.get('is_scheduled', False),
                match_data.get('is_finished', False),
                match_data.get('is_canceled', False),
                match_data.get('is_postponed', False),
                match_data.get('has_tv_icon', False),
                match_data.get('has_audio_icon', False),
                match_data.get('has_info_icon', False),
                match_data.get('half_time'),
                match_data.get('current_minute'),
                match_data.get('match_id')
            ))
        else:
            # Insert new match
            cursor.execute("""
                INSERT INTO matches (
                    match_id, match_url, league_name, league_country, league_flag_class,
                    match_time, scheduled_datetime, home_team_name, home_team_logo_url,
                    away_team_name, away_team_logo_url, home_score, away_score,
                    match_status, match_stage, is_live, is_scheduled, is_finished,
                    is_canceled, is_postponed, has_tv_icon, has_audio_icon, has_info_icon,
                    half_time, current_minute
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_data.get('match_id'),
                match_data.get('match_url'),
                match_data.get('league_name'),
                match_data.get('league_country'),
                match_data.get('league_flag_class'),
                match_data.get('match_time'),
                match_data.get('scheduled_datetime'),
                match_data.get('home_team_name'),
                match_data.get('home_team_logo_url'),
                match_data.get('away_team_name'),
                match_data.get('away_team_logo_url'),
                match_data.get('home_score'),
                match_data.get('away_score'),
                match_data.get('match_status'),
                match_data.get('match_stage'),
                match_data.get('is_live', False),
                match_data.get('is_scheduled', False),
                match_data.get('is_finished', False),
                match_data.get('is_canceled', False),
                match_data.get('is_postponed', False),
                match_data.get('has_tv_icon', False),
                match_data.get('has_audio_icon', False),
                match_data.get('has_info_icon', False),
                match_data.get('half_time'),
                match_data.get('current_minute')
            ))
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        match_id = match_data.get('match_id', 'unknown')
        home_team = match_data.get('home_team_name', 'None')
        away_team = match_data.get('away_team_name', 'None')
        print(f"❌ Database error for match {match_id} ({home_team} vs {away_team}): {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def get_all_matches() -> List[Dict[str, Any]]:
    """
    Get all matches from the database.
    
    Returns:
        List of dictionaries containing match data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM matches ORDER BY scheduled_datetime DESC, match_time DESC")
    rows = cursor.fetchall()
    
    matches = [dict(row) for row in rows]
    conn.close()
    
    return matches


def get_matches_by_status(status: str) -> List[Dict[str, Any]]:
    """
    Get matches filtered by status.
    
    Args:
        status: Match status ('live', 'scheduled', 'finished', 'canceled', 'postponed')
        
    Returns:
        List of dictionaries containing match data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM matches WHERE match_status = ? ORDER BY scheduled_datetime DESC", (status,))
    rows = cursor.fetchall()
    
    matches = [dict(row) for row in rows]
    conn.close()
    
    return matches


def get_match_by_id(match_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific match by its match_id.
    
    Args:
        match_id: The unique match identifier
        
    Returns:
        Dictionary containing match data, or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    return dict(row) if row else None


def count_matches() -> int:
    """Get the total number of matches in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM matches")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    return count

