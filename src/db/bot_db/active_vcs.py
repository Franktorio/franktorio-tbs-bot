# src\db\bot_db\active_vcs.py
# Active VCs table operations

PRINT_PREFIX = "BOT DB - ACTIVE VCS"

# Local imports
from .schema import DB_FILE_NAME
from ._helpers import serialize_json, deserialize_json
from . import connect_bot_db

def _connect(read_only: bool = False):
    return connect_bot_db(DB_FILE_NAME, read_only=read_only)

def add_active_vc(vc_id: int, owner_id: int, master_vc_id: int) -> bool:
    """Add a new active VC entry to the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO active_vcs (vc_id, owner_id, master_vc_id)
        VALUES (?, ?, ?);
    """, (vc_id, owner_id, master_vc_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added active VC with vc_id {vc_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add active VC with vc_id {vc_id}")
    return success

def remove_active_vc(vc_id: int) -> bool:
    """Remove an active VC entry from the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM active_vcs WHERE vc_id = ?;
    """, (vc_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed active VC with vc_id {vc_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove active VC with vc_id {vc_id}")
    return success

def get_active_vc(vc_id: int) -> dict | None:
    """Retrieve an active VC entry from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT vc_id, owner_id, master_vc_id, muted_users FROM active_vcs WHERE vc_id = ?;
    """, (vc_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        print(f"[INFO] [{PRINT_PREFIX}] Retrieved active VC with vc_id {vc_id}")
        return {
            "vc_id": result[0],
            "owner_id": result[1],
            "master_vc_id": result[2],
            "muted_users": deserialize_json(result[3], default=[])
        }
    print(f"[INFO] [{PRINT_PREFIX}] No active VC found with vc_id {vc_id}")
    return None

def get_all_active_vcs() -> list[dict]:
    """Retrieve all active VC entries from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT vc_id, owner_id, master_vc_id, muted_users FROM active_vcs;
    """)
    results = cursor.fetchall()
    conn.close()
    active_vcs = []
    for result in results:
        active_vcs.append({
            "vc_id": result[0],
            "owner_id": result[1],
            "master_vc_id": result[2],
            "muted_users": deserialize_json(result[3], default=[])
        })
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved all active VCs: {len(active_vcs)} entries found")
    return active_vcs

def add_muted_user(vc_id: int, user_id: int) -> bool:
    """Add a user to the muted_users list for a specific VC."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT muted_users FROM active_vcs WHERE vc_id = ?;
    """, (vc_id,))
    result = cursor.fetchone()
    success = False
    if result:
        muted_users = deserialize_json(result[0])
        if user_id not in muted_users:
            muted_users.append(user_id)
            cursor.execute("""
                UPDATE active_vcs SET muted_users = ? WHERE vc_id = ?;
            """, (serialize_json(muted_users), vc_id))
            success = cursor.rowcount > 0
            conn.commit()
    conn.close()
    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added user {user_id} to muted_users in VC {vc_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add user {user_id} to muted_users in VC {vc_id}")
    return success

def remove_muted_user(vc_id: int, user_id: int) -> bool:
    """Remove a user from the muted_users list for a specific VC."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT muted_users FROM active_vcs WHERE vc_id = ?;
    """, (vc_id,))
    result = cursor.fetchone()
    success = False
    if result:
        muted_users = deserialize_json(result[0])
        if user_id in muted_users:
            muted_users.remove(user_id)
            cursor.execute("""
                UPDATE active_vcs SET muted_users = ? WHERE vc_id = ?;
            """, (serialize_json(muted_users), vc_id))
            success = cursor.rowcount > 0
            conn.commit()
    conn.close()
    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed user {user_id} from muted_users in VC {vc_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove user {user_id} from muted_users in VC {vc_id}")
    return success

def add_deafened_user(vc_id: int, user_id: int) -> bool:
    """Add a user to the deafened_users list for a specific VC."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT deafened_users FROM active_vcs WHERE vc_id = ?;
    """, (vc_id,))
    result = cursor.fetchone()
    success = False
    if result:
        deafened_users = deserialize_json(result[0])
        if user_id not in deafened_users:
            deafened_users.append(user_id)
            cursor.execute("""
                UPDATE active_vcs SET deafened_users = ? WHERE vc_id = ?;
            """, (serialize_json(deafened_users), vc_id))
            success = cursor.rowcount > 0
            conn.commit()
    conn.close()
    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added user {user_id} to deafened_users in VC {vc_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add user {user_id} to deafened_users in VC {vc_id}")
    return success

def remove_deafened_user(vc_id: int, user_id: int) -> bool:
    """Remove a user from the deafened_users list for a specific VC."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT deafened_users FROM active_vcs WHERE vc_id = ?;
    """, (vc_id,))
    result = cursor.fetchone()
    success = False
    if result:
        deafened_users = deserialize_json(result[0])
        if user_id in deafened_users:
            deafened_users.remove(user_id)
            cursor.execute("""
                UPDATE active_vcs SET deafened_users = ? WHERE vc_id = ?;
            """, (serialize_json(deafened_users), vc_id))
            success = cursor.rowcount > 0
            conn.commit()
    conn.close()
    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed user {user_id} from deafened_users in VC {vc_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove user {user_id} from deafened_users in VC {vc_id}")
    return success

def get_master_vc(vc_id: int) -> int | None:
    """Retrieve the master_vc_id for a specific active VC."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT master_vc_id FROM active_vcs WHERE vc_id = ?;
    """, (vc_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        print(f"[INFO] [{PRINT_PREFIX}] Retrieved master_vc_id for VC {vc_id}")
        return result[0]
    print(f"[INFO] [{PRINT_PREFIX}] No master_vc_id found for VC {vc_id}")
    return None