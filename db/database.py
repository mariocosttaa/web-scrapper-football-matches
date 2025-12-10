"""
Database Management
===================
Handles SQLite database operations for storing match data.
Refactored to use a relational schema (Leagues, Teams, Matches).
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
    if os.path.exists(DB_PATH) and os.path.isdir(DB_PATH):
        print(f"⚠️  Warning: {DB_PATH} exists as a directory. This may be a Docker volume mount issue.")
        raise OSError(f"{DB_PATH} is a directory, not a file. Check Docker volume mounts.")
    
    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


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
    
    # Enable Foreign Keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create Leagues Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leagues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT,
            flag_class TEXT,
            logo_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, country)
        )
    """)
    
    # Check if logo_url column exists in leagues (for migration)
    cursor.execute("PRAGMA table_info(leagues)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'logo_url' not in columns:
        print("⚠️  Migrating 'leagues' table: Adding 'logo_url' column...")
        cursor.execute("ALTER TABLE leagues ADD COLUMN logo_url TEXT")
    
    # Create Teams Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            logo_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create Matches Table
    # Note: We are dropping the old table if it exists to enforce the new schema
    # In a production env, we would migrate, but for this refactor we reset.
    
    # Check if old matches table exists and has the old schema (check for missing columns)
    cursor.execute("PRAGMA table_info(matches)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'matches' in columns and 'league_id' not in columns:
        print("⚠️  Detected old schema. Dropping 'matches' table to apply new relational schema...")
        cursor.execute("DROP TABLE IF EXISTS matches")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT UNIQUE NOT NULL,
            match_url TEXT,
            
            league_id INTEGER,
            home_team_id INTEGER,
            away_team_id INTEGER,
            
            match_time TEXT,
            match_date DATE,
            scheduled_datetime TEXT,
            
            home_score INTEGER,
            away_score INTEGER,
            
            home_red_cards INTEGER DEFAULT 0,
            away_red_cards INTEGER DEFAULT 0,
            
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
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (league_id) REFERENCES leagues (id),
            FOREIGN KEY (home_team_id) REFERENCES teams (id),
            FOREIGN KEY (away_team_id) REFERENCES teams (id)
        )
    """)
    
    # Check if red card columns exist (for migration)
    cursor.execute("PRAGMA table_info(matches)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'home_red_cards' not in columns:
        print("⚠️  Migrating 'matches' table: Adding 'home_red_cards' column...")
        cursor.execute("ALTER TABLE matches ADD COLUMN home_red_cards INTEGER DEFAULT 0")
    if 'away_red_cards' not in columns:
        print("⚠️  Migrating 'matches' table: Adding 'away_red_cards' column...")
        cursor.execute("ALTER TABLE matches ADD COLUMN away_red_cards INTEGER DEFAULT 0")
    
    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_match_id ON matches(match_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_match_status ON matches(match_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_datetime ON matches(scheduled_datetime)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_match_date ON matches(match_date)")
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized with Relational Schema: {DB_PATH}")


def get_or_create_league(cursor, name, country, flag_class, logo_url=None):
    """Helper to get or create a league."""
    if not name:
        return None
        
    cursor.execute("SELECT id, logo_url FROM leagues WHERE name = ? AND country = ?", (name, country))
    result = cursor.fetchone()
    if result:
        # Update logo_url if provided and different
        if logo_url and result['logo_url'] != logo_url:
            cursor.execute('UPDATE leagues SET logo_url = ? WHERE id = ?', (logo_url, result['id']))
        return result['id']
    else:
        cursor.execute('''
            INSERT INTO leagues (name, country, flag_class, logo_url)
            VALUES (?, ?, ?, ?)
        ''', (name, country, flag_class, logo_url))
        return cursor.lastrowid


def get_or_create_team(cursor, name, logo_url):
    """Helper to get or create a team."""
    if not name:
        return None
        
    cursor.execute("SELECT id, logo_url FROM teams WHERE name = ?", (name,))
    result = cursor.fetchone()
    if result:
        # Update logo_url if provided and different
        if logo_url and result['logo_url'] != logo_url:
            cursor.execute('UPDATE teams SET logo_url = ? WHERE id = ?', (logo_url, result['id']))
        return result['id']
    else:
        cursor.execute('INSERT INTO teams (name, logo_url) VALUES (?, ?)', (name, logo_url))
        return cursor.lastrowid


def insert_or_update_match(match_data: Dict[str, Any]) -> bool:
    """
    Insert a new match or update an existing one using the relational schema.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Handle Relations
        league_id = get_or_create_league(
            cursor, 
            match_data.get('league_name'), 
            match_data.get('league_country'),
            match_data.get('league_flag_class'),
            match_data.get('league_logo_url')
        )
        
        home_team_id = get_or_create_team(
            cursor,
            match_data.get('home_team_name'),
            match_data.get('home_team_logo_url')
        )
        
        away_team_id = get_or_create_team(
            cursor,
            match_data.get('away_team_name'),
            match_data.get('away_team_logo_url')
        )
        
        # Calculate match_date from scheduled_datetime
        scheduled_dt = match_data.get('scheduled_datetime')
        match_date = None
        if scheduled_dt:
            try:
                match_date = datetime.fromisoformat(scheduled_dt).date().isoformat()
            except ValueError:
                pass
        
        # 2. Insert/Update Match
        cursor.execute("SELECT id FROM matches WHERE match_id = ?", (match_data.get('match_id'),))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE matches SET
                    match_url = ?,
                    league_id = ?,
                    home_team_id = ?,
                    away_team_id = ?,
                    match_time = ?,
                    match_date = ?,
                    scheduled_datetime = ?,
                    home_score = ?,
                    away_score = ?,
                    home_red_cards = ?,
                    away_red_cards = ?,
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
                league_id,
                home_team_id,
                away_team_id,
                match_data.get('match_time'),
                match_date,
                scheduled_dt,
                match_data.get('home_score'),
                match_data.get('away_score'),
                match_data.get('home_red_cards', 0),
                match_data.get('away_red_cards', 0),
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
            cursor.execute("""
                INSERT INTO matches (
                    match_id, match_url, league_id, home_team_id, away_team_id,
                    match_time, match_date, scheduled_datetime, home_score, away_score,
                    home_red_cards, away_red_cards,
                    match_status, match_stage, is_live, is_scheduled, is_finished,
                    is_canceled, is_postponed, has_tv_icon, has_audio_icon, has_info_icon,
                    half_time, current_minute
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_data.get('match_id'),
                match_data.get('match_url'),
                league_id,
                home_team_id,
                away_team_id,
                match_data.get('match_time'),
                match_date,
                scheduled_dt,
                match_data.get('home_score'),
                match_data.get('away_score'),
                match_data.get('home_red_cards', 0),
                match_data.get('away_red_cards', 0),
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
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_all_matches() -> List[Dict[str, Any]]:
    """
    Get all matches with joined league and team data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            m.*,
            l.name as league_name, l.country as league_country, l.flag_class as league_flag_class, l.logo_url as league_logo_url,
            ht.name as home_team_name, ht.logo_url as home_team_logo_url,
            at.name as away_team_name, at.logo_url as away_team_logo_url
        FROM matches m
        LEFT JOIN leagues l ON m.league_id = l.id
        LEFT JOIN teams ht ON m.home_team_id = ht.id
        LEFT JOIN teams at ON m.away_team_id = at.id
        ORDER BY 
            m.is_live DESC,
            CASE WHEN m.match_date IS NULL THEN 1 ELSE 0 END,
            m.match_date ASC, 
            m.match_time ASC
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    matches = [dict(row) for row in rows]
    conn.close()
    return matches


def get_matches_by_status(status: str) -> List[Dict[str, Any]]:
    """
    Get matches filtered by status with joined data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            m.*,
            l.name as league_name, l.country as league_country, l.flag_class as league_flag_class, l.logo_url as league_logo_url,
            ht.name as home_team_name, ht.logo_url as home_team_logo_url,
            at.name as away_team_name, at.logo_url as away_team_logo_url
        FROM matches m
        LEFT JOIN leagues l ON m.league_id = l.id
        LEFT JOIN teams ht ON m.home_team_id = ht.id
        LEFT JOIN teams at ON m.away_team_id = at.id
        WHERE m.match_status = ?
        ORDER BY m.scheduled_datetime DESC
    """
    
    cursor.execute(query, (status,))
    rows = cursor.fetchall()
    matches = [dict(row) for row in rows]
    conn.close()
    return matches


def count_matches() -> int:
    """Get the total number of matches."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM matches")
    count = cursor.fetchone()[0]
    conn.close()
    return count
