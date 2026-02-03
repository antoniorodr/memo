"""
Fast read-only access to Apple Notes via SQLite.
Only for reading - all write operations should use AppleScript.
"""

import sqlite3
import os
from pathlib import Path


def get_notes_db_path():
    """Get the path to the Notes SQLite database."""
    return Path.home() / "Library" / "Group Containers" / "group.com.apple.notes" / "NoteStore.sqlite"


def get_notes_fast(limit=None, folder=None):
    """
    Fetch notes using SQLite (read-only, much faster than AppleScript).
    
    Returns: [note_map, notes_list] compatible with existing memo format
    """
    db_path = get_notes_db_path()
    
    if not db_path.exists():
        return [{}, []]
    
    # Open in read-only mode with URI
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON")
    cursor = conn.cursor()
    
    query = """
    SELECT 
        n.Z_PK as id,
        datetime(n.ZMODIFICATIONDATE + 978307200, 'unixepoch', 'localtime') as modified,
        COALESCE(f.ZTITLE2, 'Notes') as folder,
        n.ZTITLE as title
    FROM ZICCLOUDSYNCINGOBJECT n
    LEFT JOIN ZICCLOUDSYNCINGOBJECT f ON n.ZFOLDER = f.Z_PK
    WHERE n.ZTITLE IS NOT NULL 
      AND (n.ZMARKEDFORDELETION IS NULL OR n.ZMARKEDFORDELETION = 0)
    """
    
    params = []
    
    if folder:
        query += " AND COALESCE(f.ZTITLE2, 'Notes') = ?"
        params.append(folder)
    
    query += " ORDER BY n.ZMODIFICATIONDATE DESC"
    
    if limit and limit > 0:
        query += f" LIMIT {int(limit)}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Build note_map and notes_list compatible with existing format
    # note_map: {index: (note_id, "folder - title", modification_date)}
    note_map = {}
    notes_list = []
    
    for i, (note_id, mod_date, folder_name, title) in enumerate(rows, start=1):
        display_title = f"{folder_name} - {title}"
        note_map[i] = (f"x-coredata://note/{note_id}", display_title, mod_date)
        notes_list.append(display_title)
    
    return [note_map, notes_list]


def get_folders_fast():
    """
    Fetch folder list using SQLite (read-only).
    
    Returns: string with folder names (one per line)
    """
    db_path = get_notes_db_path()
    
    if not db_path.exists():
        return ""
    
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ZTITLE2 
        FROM ZICCLOUDSYNCINGOBJECT 
        WHERE ZFOLDERTYPE IS NOT NULL 
          AND ZTITLE2 IS NOT NULL
        ORDER BY ZTITLE2
    """)
    
    folders = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return "\n".join(folders)


def count_notes_fast(folder=None):
    """
    Count notes using SQLite (read-only).
    
    Returns: int count
    """
    db_path = get_notes_db_path()
    
    if not db_path.exists():
        return 0
    
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON")
    cursor = conn.cursor()
    
    query = """
        SELECT COUNT(*) 
        FROM ZICCLOUDSYNCINGOBJECT n
        LEFT JOIN ZICCLOUDSYNCINGOBJECT f ON n.ZFOLDER = f.Z_PK
        WHERE n.ZTITLE IS NOT NULL 
          AND (n.ZMARKEDFORDELETION IS NULL OR n.ZMARKEDFORDELETION = 0)
    """
    
    params = []
    if folder:
        query = query.replace("WHERE", "WHERE COALESCE(f.ZTITLE2, 'Notes') = ? AND")
        params.append(folder)
    
    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    conn.close()
    
    return count
