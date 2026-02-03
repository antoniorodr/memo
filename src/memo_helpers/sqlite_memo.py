r"""
Fast read-only access to Apple Notes via SQLite.
Only for reading - all write operations should use AppleScript.

WARNING: Apple Notes SQLite schema is undocumented and may change between macOS versions.
This module attempts to detect the correct column names automatically, but may break
on future macOS updates. If it stops working, check the schema with:

    sqlite3 ~/Library/Group\ Containers/group.com.apple.notes/NoteStore.sqlite \
        "PRAGMA table_info(ZICCLOUDSYNCINGOBJECT);" | grep -i title

Known column variations:
- macOS High Sierra+ (iCloud): ZTITLE1, ZCREATIONDATE1, ZMODIFICATIONDATE1
- Older versions: ZTITLE, ZCREATIONDATE, ZMODIFICATIONDATE
- Folders always use: ZTITLE2
"""

import sqlite3
import os
from pathlib import Path

# Cache for detected schema
_schema_cache = None


def get_notes_db_path():
    """Get the path to the Notes SQLite database."""
    return Path.home() / "Library" / "Group Containers" / "group.com.apple.notes" / "NoteStore.sqlite"


def _detect_schema(cursor):
    """
    Detect which column names are used in the current database.
    Returns a dict with keys: title, created, modified, folder_title
    """
    global _schema_cache
    if _schema_cache is not None:
        return _schema_cache
    
    # Get all columns
    cursor.execute("PRAGMA table_info(ZICCLOUDSYNCINGOBJECT)")
    columns = {row[1] for row in cursor.fetchall()}
    
    # Detect title column (prefer ZTITLE1 which has more data on modern macOS)
    if "ZTITLE1" in columns:
        # Count which has more data
        cursor.execute("SELECT COUNT(*) FROM ZICCLOUDSYNCINGOBJECT WHERE ZTITLE1 IS NOT NULL")
        count1 = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM ZICCLOUDSYNCINGOBJECT WHERE ZTITLE IS NOT NULL")
        count0 = cursor.fetchone()[0]
        title_col = "ZTITLE1" if count1 >= count0 else "ZTITLE"
    else:
        title_col = "ZTITLE"
    
    # Detect date columns based on title column
    if title_col == "ZTITLE1":
        created_col = "ZCREATIONDATE1" if "ZCREATIONDATE1" in columns else "ZCREATIONDATE"
        modified_col = "ZMODIFICATIONDATE1" if "ZMODIFICATIONDATE1" in columns else "ZMODIFICATIONDATE"
    else:
        created_col = "ZCREATIONDATE"
        modified_col = "ZMODIFICATIONDATE"
    
    _schema_cache = {
        "title": title_col,
        "created": created_col,
        "modified": modified_col,
        "folder_title": "ZTITLE2",  # Folders always use ZTITLE2
    }
    
    return _schema_cache


def get_notes_fast(limit=None, folder=None, sort_by="modified", days=None):
    """
    Fetch notes using SQLite (read-only, much faster than AppleScript).
    
    Args:
        limit: Maximum number of notes to return
        folder: Filter by folder name
        sort_by: "modified" (default) or "created"
        days: Filter notes created/modified within last N days
    
    Returns: [note_map, notes_list] compatible with existing memo format
    
    Note: Schema detection is automatic but may fail on future macOS versions.
    """
    db_path = get_notes_db_path()
    
    if not db_path.exists():
        return [{}, []]
    
    # Open in read-only mode with URI
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON")
    cursor = conn.cursor()
    
    # Auto-detect schema
    schema = _detect_schema(cursor)
    title_col = schema["title"]
    created_col = schema["created"]
    modified_col = schema["modified"]
    folder_title_col = schema["folder_title"]
    
    date_field = modified_col if sort_by == "modified" else created_col
    
    query = f"""
    SELECT 
        n.Z_PK as id,
        datetime(n.{created_col} + 978307200, 'unixepoch', 'localtime') as created,
        datetime(n.{modified_col} + 978307200, 'unixepoch', 'localtime') as modified,
        COALESCE(f.{folder_title_col}, 'Notes') as folder,
        n.{title_col} as title
    FROM ZICCLOUDSYNCINGOBJECT n
    LEFT JOIN ZICCLOUDSYNCINGOBJECT f ON n.ZFOLDER = f.Z_PK
    WHERE n.{title_col} IS NOT NULL 
      AND (n.ZMARKEDFORDELETION IS NULL OR n.ZMARKEDFORDELETION = 0)
    """
    
    params = []
    
    if folder:
        query += f" AND COALESCE(f.{folder_title_col}, 'Notes') = ?"
        params.append(folder)
    
    if days and days > 0:
        query += f" AND n.{date_field} >= (strftime('%s', 'now') - 978307200 - ? * 24 * 3600)"
        params.append(days)
    
    query += f" ORDER BY n.{date_field} DESC"
    
    if limit and limit > 0:
        query += f" LIMIT {int(limit)}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Build note_map and notes_list compatible with existing format
    # note_map: {index: (note_id, "folder - title", created_date, modified_date)}
    note_map = {}
    notes_list = []
    
    for i, (note_id, created, modified, folder_name, title) in enumerate(rows, start=1):
        display_title = f"{folder_name} - {title}"
        note_map[i] = (f"x-coredata://note/{note_id}", display_title, created, modified)
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
    
    Note: Schema detection is automatic but may fail on future macOS versions.
    """
    db_path = get_notes_db_path()
    
    if not db_path.exists():
        return 0
    
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON")
    cursor = conn.cursor()
    
    # Auto-detect schema
    schema = _detect_schema(cursor)
    title_col = schema["title"]
    folder_title_col = schema["folder_title"]
    
    query = f"""
        SELECT COUNT(*) 
        FROM ZICCLOUDSYNCINGOBJECT n
        LEFT JOIN ZICCLOUDSYNCINGOBJECT f ON n.ZFOLDER = f.Z_PK
        WHERE n.{title_col} IS NOT NULL 
          AND (n.ZMARKEDFORDELETION IS NULL OR n.ZMARKEDFORDELETION = 0)
    """
    
    params = []
    if folder:
        query = query.replace("WHERE", f"WHERE COALESCE(f.{folder_title_col}, 'Notes') = ? AND")
        params.append(folder)
    
    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    conn.close()
    
    return count
