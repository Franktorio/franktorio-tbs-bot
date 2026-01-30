# src\db\bot_db\leaders.py
# Leaders table operations

PRINT_PREFIX = "BOT DB - LEADERS"

# Standard library imports
import datetime

# Local imports
from config.config_explorer import LEADER_TIERS
from .schema import DB_FILE_NAME
from . import connect_bot_db

def _connect(read_only: bool = False):
    return connect_bot_db(DB_FILE_NAME, read_only=read_only)

def add_leader(user_id: int, leader_tier: str | None = None) -> bool:
    """Overwrite a new leader entry to the database."""
    if leader_tier not in LEADER_TIERS:
        print(f"[ERROR] [{PRINT_PREFIX}] Invalid leader tier '{leader_tier}' for user_id {user_id}")
        return False
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leaders (user_id, leader_tier, promoted_at)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            leader_tier = excluded.leader_tier,
            promoted_at = excluded.promoted_at;
    """, (user_id, leader_tier, int(datetime.datetime.now().timestamp())))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added leader with user_id {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add leader with user_id {user_id}")
    return success

def get_leader(user_id: int) -> dict | None:
    """
    Retrieve a leader entry from the database.
    Args:
        user_id (int): The Discord user ID.
    Returns:
        dict | None: The leader entry as a dictionary, or None if not found.
        {
            "user_id": int,
            "leader_tier": str,
            "promoted_at": int,
            "last_win_at": int,
            "last_host_at": int
        }
    """
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, leader_tier, promoted_at,
               last_win_at, last_host_at
        FROM leaders
        WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "user_id": result[0],
            "leader_tier": result[1],
            "promoted_at": result[2],
            "last_win_at": result[3],
            "last_host_at": result[4]
        }
    print(f"[INFO] [{PRINT_PREFIX}] No leader found with user_id {user_id}")
    return None

def modify_leader(user_id: int, last_win_at: int | None = None, last_host_at: int | None = None) -> bool:
    """Modify an existing leader entry in the database."""
    conn = _connect()
    cursor = conn.cursor()
    
    fields = []
    values = []
    
    if last_win_at is not None:
        fields.append("last_win_at = ?")
        values.append(last_win_at)
    if last_host_at is not None:
        fields.append("last_host_at = ?")
        values.append(last_host_at)
    
    if not fields:
        conn.close()
        return False
    
    values.append(user_id)
    
    cursor.execute(f"""
        UPDATE leaders
        SET {', '.join(fields)}
        WHERE user_id = ?;
    """, tuple(values))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Modified leader with user_id {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to modify leader with user_id {user_id}")
    return success

def remove_leader(user_id: int) -> bool:
    """Remove a leader entry from the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM leaders WHERE user_id = ?;
    """, (user_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed leader with user_id {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove leader with user_id {user_id}")
    return success

def get_all_leaders() -> list[dict]:
    """
    Retrieve all leader entries from the database.
    
    Returns:
        list[dict]: A list of leader entries as dictionaries.
        Each dictionary contains:
        {
            "user_id": int,
            "leader_tier": str,
            "last_win_at": int,
            "last_host_at": int,
            "promoted_at": int
        }
    """
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, leader_tier,
               last_win_at, last_host_at, promoted_at
        FROM leaders;
    """)
    results = cursor.fetchall()
    conn.close()
    
    leaders = []
    for result in results:
        leaders.append({
            "user_id": result[0],
            "leader_tier": result[1],
            "last_win_at": result[2],
            "last_host_at": result[3],
            "promoted_at": result[4]
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved all leaders: {len(leaders)} entries found")
    return leaders

def refresh_last_win(user_id: int) -> bool:
    """Update the last_win_at timestamp for a leader to the current time."""
    conn = _connect()
    cursor = conn.cursor()
    timestamp = int(datetime.datetime.now().timestamp())
    cursor.execute("""
        UPDATE leaders SET last_win_at = ? WHERE user_id = ?;
    """, (timestamp, user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Refreshed last_win_at for leader {user_id} to {timestamp}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to refresh last_win_at for leader {user_id}")
    return success

def refresh_last_host(user_id: int) -> bool:
    """Update the last_host_at timestamp for a leader to the current time."""
    conn = _connect()
    cursor = conn.cursor()
    timestamp = int(datetime.datetime.now().timestamp())
    cursor.execute("""
        UPDATE leaders SET last_host_at = ? WHERE user_id = ?;
    """, (timestamp, user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Refreshed last_host_at for leader {user_id} to {timestamp}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to refresh last_host_at for leader {user_id}")
    return success

