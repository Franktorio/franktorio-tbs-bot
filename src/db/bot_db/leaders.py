# src\db\bot_db\leaders.py
# Leaders table operations

PRINT_PREFIX = "BOT DB - LEADERS"

# Standard library imports
import datetime

# Local imports
from .schema import DB_FILE_NAME
from . import connect_bot_db

def _connect(read_only: bool = False):
    return connect_bot_db(DB_FILE_NAME, read_only=read_only)

def add_leader(user_id: int, leader_tier: str | None = None) -> bool:
    """Overwrite a new leader entry to the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leaders (user_id, leader_tier, on_break_since, promoted_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            leader_tier = excluded.leader_tier,
            on_break_since = excluded.on_break_since,
            promoted_at = excluded.promoted_at;
    """, (user_id, leader_tier, 0, int(datetime.datetime.now().timestamp())))
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
            "on_break_since": int,
            "promoted_at": int,
            "last_win_at": int,
            "last_host_at": int
        }
    """
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, leader_tier, on_break_since, promoted_at,
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
            "on_break_since": result[2],
            "promoted_at": result[3],
            "last_win_at": result[4],
            "last_host_at": result[5]
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

def put_leader_on_break(user_id: int) -> bool:
    """Put a leader on break by recording the current timestamp."""
    conn = _connect()
    cursor = conn.cursor()
    timestamp = int(datetime.datetime.now().timestamp())
    cursor.execute("""
        UPDATE leaders SET on_break_since = ? WHERE user_id = ?;
    """, (timestamp, user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Set leader {user_id} on break at timestamp {timestamp}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to set leader {user_id} on break")
    return success

def remove_leader_from_break(user_id: int) -> bool:
    """Remove a leader from break by setting on_break_since to 0."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE leaders SET on_break_since = 0 WHERE user_id = ?;
    """, (user_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed leader {user_id} from break")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove leader {user_id} from break")
    return success

def is_leader_on_break(user_id: int) -> bool:
    """Check if a leader is currently on break."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT on_break_since FROM leaders WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        on_break = result[0] > 0
        print(f"[INFO] [{PRINT_PREFIX}] Leader {user_id} on break status: {on_break}")
        return on_break
    print(f"[INFO] [{PRINT_PREFIX}] No leader found with user_id {user_id}")
    return False

def get_all_leaders() -> list[dict]:
    """Retrieve all leader entries from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, leader_tier, on_break_since,
               last_win_at, last_host_at
        FROM leaders;
    """)
    results = cursor.fetchall()
    conn.close()
    
    leaders = []
    for result in results:
        leaders.append({
            "user_id": result[0],
            "leader_tier": result[1],
            "on_break_since": result[2],
            "last_win_at": result[3],
            "last_host_at": result[4]
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved all leaders: {len(leaders)} entries found")
    return leaders

def get_active_leaders() -> list[dict]:
    """Retrieve all leaders who are not currently on break."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, leader_tier, on_break_since,
               last_win_at, last_host_at
        FROM leaders
        WHERE on_break_since = 0;
    """)
    results = cursor.fetchall()
    conn.close()
    
    leaders = []
    for result in results:
        leaders.append({
            "user_id": result[0],
            "leader_tier": result[1],
            "on_break_since": result[2],
            "last_win_at": result[3],
            "last_host_at": result[4]
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved active leaders: {len(leaders)} entries found")
    return leaders

def get_leaders_on_break() -> list[dict]:
    """Retrieve all leaders currently on break."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, leader_tier, on_break_since,
               last_win_at, last_host_at
        FROM leaders
        WHERE on_break_since > 0;
    """)
    results = cursor.fetchall()
    conn.close()
    
    leaders = []
    for result in results:
        leaders.append({
            "user_id": result[0],
            "leader_tier": result[1],
            "on_break_since": result[2],
            "last_win_at": result[3],
            "last_host_at": result[4]
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved leaders on break: {len(leaders)} entries found")
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

