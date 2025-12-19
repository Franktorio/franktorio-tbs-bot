# src\db\bot_db\users.py
# Users table operations

PRINT_PREFIX = "BOT DB - USERS"

# Local imports
from .schema import DB_FILE_NAME
from ._helpers import serialize_json, deserialize_json
from . import connect_bot_db

def _connect(read_only: bool = False):
    return connect_bot_db(DB_FILE_NAME, read_only=read_only)

def add_user(user_id: int, roblox_user_id: int | None = None) -> bool:
    """Add a new user entry to the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, roblox_user_id)
        VALUES (?, ?);
    """, (user_id, roblox_user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added user with user_id {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add user with user_id {user_id}")
    return success

def get_user(user_id: int) -> dict | None:
    """Retrieve a user entry from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, roblox_user_id, is_banned, warnings, notes,
               personal_blacklists, personal_whitelists
        FROM users
        WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "user_id": result[0],
            "roblox_user_id": result[1],
            "is_banned": bool(result[2]),
            "warnings": deserialize_json(result[3], default={}),
            "notes": deserialize_json(result[4], default={}),
            "personal_blacklists": deserialize_json(result[5], default=[]),
            "personal_whitelists": deserialize_json(result[6], default=[])
        }
    print(f"[INFO] [{PRINT_PREFIX}] No user found with user_id {user_id}")
    return None

def modify_user(user_id: int, roblox_user_id: int | None = None, 
                is_banned: bool | None = None) -> bool:
    """Modify an existing user entry in the database."""
    conn = _connect()
    cursor = conn.cursor()
    
    fields = []
    values = []
    
    if roblox_user_id is not None:
        fields.append("roblox_user_id = ?")
        values.append(roblox_user_id)
    if is_banned is not None:
        fields.append("is_banned = ?")
        values.append(int(is_banned))
    
    if not fields:
        conn.close()
        return False
    
    values.append(user_id)
    
    cursor.execute(f"""
        UPDATE users
        SET {', '.join(fields)}
        WHERE user_id = ?;
    """, tuple(values))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Modified user with user_id {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to modify user with user_id {user_id}")
    return success

def add_warning(user_id: int, reason: str, severity: str, enforcer_id: int) -> str | None:
    """Add a warning to a user's warnings with an auto-generated ID.
    
    Args:
        user_id: The user to warn
        reason: The reason for the warning
        severity: Either 'severe' or 'nonsevere'
        enforcer_id: User ID of who issued the warning
    
    Returns:
        The generated warning_id if successful, None otherwise
    """
    import datetime
    from datetime import timezone
    import random
    
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT warnings FROM users WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        print(f"[WARN] [{PRINT_PREFIX}] No user found with user_id {user_id}")
        return None
    
    warnings = deserialize_json(result[0], default={})
    
    # Auto-generate unique warning ID
    timestamp = int(datetime.datetime.now(timezone.utc).timestamp() * 1000)
    random_suffix = random.randint(1000, 9999)
    warning_id = f"warn_{timestamp}_{random_suffix}"
    
    # Ensure uniqueness (extremely unlikely to collide, but just in case)
    while warning_id in warnings:
        random_suffix = random.randint(1000, 9999)
        warning_id = f"warn_{timestamp}_{random_suffix}"
    
    warning = {
        "reason": reason,
        "severity": severity,
        "timestamp": datetime.datetime.now(timezone.utc).timestamp(),
        "enforcer": str(enforcer_id)
    }
    warnings[warning_id] = warning
    
    cursor.execute("""
        UPDATE users SET warnings = ? WHERE user_id = ?;
    """, (serialize_json(warnings), user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added {severity} warning to user {user_id} with ID {warning_id}")
        return warning_id
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add warning to user {user_id}")
        return None

def get_warnings(user_id: int, severity_filter: str | None = None) -> dict:
    """Get warnings for a user, optionally filtered by severity.
    
    Args:
        user_id: The user to get warnings for
        severity_filter: Optional filter - 'severe', 'nonsevere', or None for all
    
    Returns:
        Dictionary of warnings (warning_id -> warning_object)
    """
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT warnings FROM users WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print(f"[WARN] [{PRINT_PREFIX}] No user found with user_id {user_id}")
        return {}
    
    all_warnings = deserialize_json(result[0], default={})
    
    if severity_filter is None:
        print(f"[INFO] [{PRINT_PREFIX}] Retrieved all warnings for user {user_id}: {len(all_warnings)} warnings")
        return all_warnings
    
    filtered_warnings = {
        wid: wdata for wid, wdata in all_warnings.items()
        if wdata.get("severity") == severity_filter
    }
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved {severity_filter} warnings for user {user_id}: {len(filtered_warnings)} warnings")
    return filtered_warnings

def get_severe_warnings(user_id: int) -> dict:
    """Get only severe warnings for a user."""
    return get_warnings(user_id, severity_filter="severe")

def get_nonsevere_warnings(user_id: int) -> dict:
    """Get only nonsevere warnings for a user."""
    return get_warnings(user_id, severity_filter="nonsevere")

def get_all_warnings(user_id: int) -> dict:
    """Get all warnings for a user."""
    return get_warnings(user_id, severity_filter=None)

def remove_warning(user_id: int, warning_id: str) -> bool:
    """Remove a warning from a user's warnings."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT warnings FROM users WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        print(f"[WARN] [{PRINT_PREFIX}] No user found with user_id {user_id}")
        return False
    
    warnings = deserialize_json(result[0], default={})
    if warning_id in warnings:
        del warnings[warning_id]
    
    cursor.execute("""
        UPDATE users SET warnings = ? WHERE user_id = ?;
    """, (serialize_json(warnings), user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed warning from user {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove warning from user {user_id}")
    return success

def add_note(user_id: int, note_id: str, note_text: str) -> bool:
    """Add a note to a user's notes."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT notes FROM users WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        print(f"[WARN] [{PRINT_PREFIX}] No user found with user_id {user_id}")
        return False
    
    notes = deserialize_json(result[0], default={})
    notes[note_id] = note_text
    
    cursor.execute("""
        UPDATE users SET notes = ? WHERE user_id = ?;
    """, (serialize_json(notes), user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added note to user {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add note to user {user_id}")
    return success

def remove_note(user_id: int, note_id: str) -> bool:
    """Remove a note from a user's notes."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT notes FROM users WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        print(f"[WARN] [{PRINT_PREFIX}] No user found with user_id {user_id}")
        return False
    
    notes = deserialize_json(result[0], default={})
    if note_id in notes:
        del notes[note_id]
    
    cursor.execute("""
        UPDATE users SET notes = ? WHERE user_id = ?;
    """, (serialize_json(notes), user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed note from user {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove note from user {user_id}")
    return success

def add_personal_blacklist(user_id: int, blacklisted_user_id: int) -> bool:
    """Add a user to another user's personal blacklist."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT personal_blacklists FROM users WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        print(f"[WARN] [{PRINT_PREFIX}] No user found with user_id {user_id}")
        return False
    
    blacklists = deserialize_json(result[0], default=[])
    if blacklisted_user_id not in blacklists:
        blacklists.append(blacklisted_user_id)
    
    cursor.execute("""
        UPDATE users SET personal_blacklists = ? WHERE user_id = ?;
    """, (serialize_json(blacklists), user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added {blacklisted_user_id} to user {user_id}'s personal blacklist")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add to personal blacklist for user {user_id}")
    return success

def remove_personal_blacklist(user_id: int, blacklisted_user_id: int) -> bool:
    """Remove a user from another user's personal blacklist."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT personal_blacklists FROM users WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        print(f"[WARN] [{PRINT_PREFIX}] No user found with user_id {user_id}")
        return False
    
    blacklists = deserialize_json(result[0], default=[])
    if blacklisted_user_id in blacklists:
        blacklists.remove(blacklisted_user_id)
    
    cursor.execute("""
        UPDATE users SET personal_blacklists = ? WHERE user_id = ?;
    """, (serialize_json(blacklists), user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed {blacklisted_user_id} from user {user_id}'s personal blacklist")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove from personal blacklist for user {user_id}")
    return success

def add_personal_whitelist(user_id: int, whitelisted_user_id: int) -> bool:
    """Add a user to another user's personal whitelist."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT personal_whitelists FROM users WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        print(f"[WARN] [{PRINT_PREFIX}] No user found with user_id {user_id}")
        return False
    
    whitelists = deserialize_json(result[0], default=[])
    if whitelisted_user_id not in whitelists:
        whitelists.append(whitelisted_user_id)
    
    cursor.execute("""
        UPDATE users SET personal_whitelists = ? WHERE user_id = ?;
    """, (serialize_json(whitelists), user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added {whitelisted_user_id} to user {user_id}'s personal whitelist")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add to personal whitelist for user {user_id}")
    return success

def remove_personal_whitelist(user_id: int, whitelisted_user_id: int) -> bool:
    """Remove a user from another user's personal whitelist."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT personal_whitelists FROM users WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        print(f"[WARN] [{PRINT_PREFIX}] No user found with user_id {user_id}")
        return False
    
    whitelists = deserialize_json(result[0], default=[])
    if whitelisted_user_id in whitelists:
        whitelists.remove(whitelisted_user_id)
    
    cursor.execute("""
        UPDATE users SET personal_whitelists = ? WHERE user_id = ?;
    """, (serialize_json(whitelists), user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed {whitelisted_user_id} from user {user_id}'s personal whitelist")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove from personal whitelist for user {user_id}")
    return success

def get_all_users() -> list[dict]:
    """Retrieve all user entries from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, roblox_user_id, is_banned, warnings, notes,
               personal_blacklists, personal_whitelists
        FROM users;
    """)
    results = cursor.fetchall()
    conn.close()
    
    users = []
    for result in results:
        users.append({
            "user_id": result[0],
            "roblox_user_id": result[1],
            "is_banned": bool(result[2]),
            "warnings": deserialize_json(result[3], default={}),
            "notes": deserialize_json(result[4], default={}),
            "personal_blacklists": deserialize_json(result[5], default=[]),
            "personal_whitelists": deserialize_json(result[6], default=[])
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved all users: {len(users)} entries found")
    return users
