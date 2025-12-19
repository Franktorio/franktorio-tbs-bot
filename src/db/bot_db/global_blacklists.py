# src\db\bot_db\global_blacklists.py
# Global Blacklists table operations

PRINT_PREFIX = "BOT DB - GLOBAL BLACKLISTS"

# Standard library imports
import datetime

# Local imports
from .schema import DB_FILE_NAME
from ._helpers import serialize_json, deserialize_json
from . import connect_bot_db

def _connect(read_only: bool = False):
    return connect_bot_db(DB_FILE_NAME, read_only=read_only)

def add_global_blacklist(user_id: int, enforced_by: int, reason: str, duration: int) -> bool:
    """Add a new global blacklist entry to the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO global_blacklists (user_id, enforced_by, reason, duration)
        VALUES (?, ?, ?, ?);
    """, (user_id, enforced_by, reason, duration))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added global blacklist for user_id {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add global blacklist for user_id {user_id}")
    return success

def modify_global_blacklist(blacklist_id: int, reason: str | None = None, duration: int | None = None, is_expired: bool | None = None) -> bool:
    """
    Modify an existing global blacklist entry in the database.
    
    Allows to change reason, duration, and expiration status.
    Args:
        blacklist_id: ID of the blacklist entry to modify
        reason: New reason for the blacklist (optional)
        duration: New duration for the blacklist (optional)
        is_expired: New expiration status (optional)
    """
    conn = _connect()
    cursor = conn.cursor()
    
    # Get current blacklist and store state
    cursor.execute("""
        SELECT * FROM global_blacklists WHERE blacklist_id = ?;
    """, (blacklist_id,))
    row = cursor.fetchone()
    if not row:
        print(f"[WARN] [{PRINT_PREFIX}] No global blacklist found with blacklist_id {blacklist_id}")
        conn.close()
        return False
    
    now = int(datetime.datetime.now().timestamp())

    old_blacklist = {
        "blacklist_id": row[0],
        "user_id": row[1],
        "enforced_by": row[2],
        "reason": row[3],
        "duration": row[4],
        "applied_at": row[5],
        "modifications": deserialize_json(row[6], default=[]),
        "is_expired": bool(row[7]),
        "modified_at": now
    }

    # Apply modifications
    fields = []
    values = []

    if reason is not None:
        fields.append("reason = ?")
        values.append(reason)
    if duration is not None:
        fields.append("duration = ?")
        values.append(duration)
    if is_expired is not None:
        fields.append("is_expired = ?")
        values.append(int(is_expired))

    if fields:
        fields.append("modifications = ?")
        old_modifications = old_blacklist["modifications"]
        old_modifications.append(old_blacklist)
        values.append(serialize_json(old_modifications))
    
    values.append(blacklist_id)

    cursor.execute(f"""
        UPDATE global_blacklists
        SET {', '.join(fields)}
        WHERE blacklist_id = ?;
    """, tuple(values))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Modified global blacklist with blacklist_id {blacklist_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to modify global blacklist with blacklist_id {blacklist_id}")
    return success

def get_blacklists_by_user(user_id: int) -> list[dict]:
    """Retrieve all global blacklist entries for a specific user."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT blacklist_id, user_id, enforced_by, reason, duration,
               applied_at, modifications, is_expired
        FROM global_blacklists
        WHERE user_id = ?;
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    blacklists = []
    for result in results:
        blacklists.append({
            "blacklist_id": result[0],
            "user_id": result[1],
            "enforced_by": result[2],
            "reason": result[3],
            "duration": result[4],
            "applied_at": result[5],
            "modifications": deserialize_json(result[6], default=[]),
            "is_expired": bool(result[7])
        })
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved global blacklists for user_id {user_id}: {len(blacklists)} entries found")
    return blacklists

def blacklists_by_blacklister(enforced_by: int) -> list[dict]:
    """Retrieve all global blacklist entries enforced by a specific user."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT blacklist_id, user_id, enforced_by, reason, duration,
               applied_at, modifications, is_expired
        FROM global_blacklists
        WHERE enforced_by = ?;
    """, (enforced_by,))
    results = cursor.fetchall()
    conn.close()
    blacklists = []
    for result in results:
        blacklists.append({
            "blacklist_id": result[0],
            "user_id": result[1],
            "enforced_by": result[2],
            "reason": result[3],
            "duration": result[4],
            "applied_at": result[5],
            "modifications": deserialize_json(result[6], default=[]),
            "is_expired": bool(result[7])
        })
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved global blacklists enforced by user_id {enforced_by}: {len(blacklists)} entries found")
    return blacklists

def get_global_blacklist(blacklist_id: int) -> dict | None:
    """Retrieve a global blacklist entry from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT blacklist_id, user_id, enforced_by, reason, duration,
               applied_at, modifications, is_expired
        FROM global_blacklists
        WHERE blacklist_id = ?;
    """, (blacklist_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "blacklist_id": result[0],
            "user_id": result[1],
            "enforced_by": result[2],
            "reason": result[3],
            "duration": result[4],
            "applied_at": result[5],
            "modifications": deserialize_json(result[6], default=[]),
            "is_expired": bool(result[7])
        }
    print(f"[INFO] [{PRINT_PREFIX}] No global blacklist found with blacklist_id {blacklist_id}")
    return None

def get_all_global_blacklists(include_expired: bool = False) -> list[dict]:
    """Retrieve all global blacklist entries from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()

    
    if include_expired:
        cursor.execute("""
            SELECT blacklist_id, user_id, enforced_by, reason, duration,
                   applied_at, modifications, is_expired
            FROM global_blacklists;
        """)
    else:
        cursor.execute("""
            SELECT blacklist_id, user_id, enforced_by, reason, duration,
                   applied_at, modifications, is_expired
            FROM global_blacklists
            WHERE is_expired = 0;
        """)

    results = cursor.fetchall()
    conn.close()

    blacklists = []
    for result in results:
        blacklists.append({
            "blacklist_id": result[0],
            "user_id": result[1],
            "enforced_by": result[2],
            "reason": result[3],
            "duration": result[4],
            "applied_at": result[5],
            "modifications": deserialize_json(result[6], default=[]),
            "is_expired": bool(result[7])
        })
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved all global blacklists: {len(blacklists)} entries found")
    return blacklists

# Helper functions to modify blacklists

def expire_global_blacklist(blacklist_id: int) -> bool:
    """Mark a global blacklist entry as expired."""
    return modify_global_blacklist(blacklist_id, is_expired=True)

def extend_global_blacklist_duration(blacklist_id: int, additional_duration: int) -> bool:
    """Extend the duration of a global blacklist entry."""
    # Get current blacklist to calculate new duration
    blacklist = get_global_blacklist(blacklist_id)
    if not blacklist:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to extend duration: blacklist_id {blacklist_id} not found")
        return False
    
    new_duration = blacklist["duration"] + additional_duration
    success = modify_global_blacklist(blacklist_id, duration=new_duration)
    
    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Extended duration of global blacklist with blacklist_id {blacklist_id} by {additional_duration} seconds")
    return success

def decrease_global_blacklist_duration(blacklist_id: int, reduction_duration: int) -> bool:
    """Decrease the duration of a global blacklist entry."""
    # Get current blacklist to calculate new duration
    blacklist = get_global_blacklist(blacklist_id)
    if not blacklist:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to decrease duration: blacklist_id {blacklist_id} not found")
        return False
    
    new_duration = max(0, blacklist["duration"] - reduction_duration)
    success = modify_global_blacklist(blacklist_id, duration=new_duration)
    
    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Decreased duration of global blacklist with blacklist_id {blacklist_id} by {reduction_duration} seconds")
    return success

def edit_blacklist_reason(blacklist_id: int, new_reason: str) -> bool:
    """Edit the reason for a global blacklist entry."""
    return modify_global_blacklist(blacklist_id, reason=new_reason)