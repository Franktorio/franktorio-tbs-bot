# src\db\bot_db\active_vcs.py
# Active VCs table operations

PRINT_PREFIX = "BOT DB - ACTIVE VCS"

# Local imports
from .schema import DB_FILE_NAME
from ._helpers import serialize_json, deserialize_json
from . import connect_bot_db

def _connect(read_only: bool = False):
    return connect_bot_db(DB_FILE_NAME, read_only=read_only)

def add_active_vc(vc_id: int, owner_id: int, master_vc_id: int) -> None:
    """Add a new active VC entry to the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO active_vcs (vc_id, owner_id, master_vc_id)
        VALUES (?, ?, ?);
    """, (vc_id, owner_id, master_vc_id))
    conn.commit()
    conn.close()
    print(f"[INFO] [{PRINT_PREFIX}] Added active VC with vc_id {vc_id}")

def remove_active_vc(vc_id: int) -> None:
    """Remove an active VC entry from the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM active_vcs WHERE vc_id = ?;
    """, (vc_id,))
    conn.commit()
    conn.close()
    print(f"[INFO] [{PRINT_PREFIX}] Removed active VC with vc_id {vc_id}")

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

def add_muted_user(vc_id: int, user_id: int) -> None:
    """Add a user to the muted_users list for a specific VC."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT muted_users FROM active_vcs WHERE vc_id = ?;
    """, (vc_id,))
    result = cursor.fetchone()
    if result:
        muted_users = deserialize_json(result[0])
        if user_id not in muted_users:
            muted_users.append(user_id)
            cursor.execute("""
                UPDATE active_vcs SET muted_users = ? WHERE vc_id = ?;
            """, (serialize_json(muted_users), vc_id))
            conn.commit()
    conn.close()
    print(f"[INFO] [{PRINT_PREFIX}] Added user {user_id} to muted_users in VC {vc_id}")

def remove_muted_user(vc_id: int, user_id: int) -> None:
    """Remove a user from the muted_users list for a specific VC."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT muted_users FROM active_vcs WHERE vc_id = ?;
    """, (vc_id,))
    result = cursor.fetchone()
    if result:
        muted_users = deserialize_json(result[0])
        if user_id in muted_users:
            muted_users.remove(user_id)
            cursor.execute("""
                UPDATE active_vcs SET muted_users = ? WHERE vc_id = ?;
            """, (serialize_json(muted_users), vc_id))
            conn.commit()
    conn.close()
    print(f"[INFO] [{PRINT_PREFIX}] Removed user {user_id} from muted_users in VC {vc_id}")

def add_deafened_user(vc_id: int, user_id: int) -> None:
    """Add a user to the deafened_users list for a specific VC."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT deafened_users FROM active_vcs WHERE vc_id = ?;
    """, (vc_id,))
    result = cursor.fetchone()
    if result:
        deafened_users = deserialize_json(result[0])
        if user_id not in deafened_users:
            deafened_users.append(user_id)
            cursor.execute("""
                UPDATE active_vcs SET deafened_users = ? WHERE vc_id = ?;
            """, (serialize_json(deafened_users), vc_id))
            conn.commit()
    conn.close()
    print(f"[INFO] [{PRINT_PREFIX}] Added user {user_id} to deafened_users in VC {vc_id}")

def remove_deafened_user(vc_id: int, user_id: int) -> None:
    """Remove a user from the deafened_users list for a specific VC."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT deafened_users FROM active_vcs WHERE vc_id = ?;
    """, (vc_id,))
    result = cursor.fetchone()
    if result:
        deafened_users = deserialize_json(result[0])
        if user_id in deafened_users:
            deafened_users.remove(user_id)
            cursor.execute("""
                UPDATE active_vcs SET deafened_users = ? WHERE vc_id = ?;
            """, (serialize_json(deafened_users), vc_id))
            conn.commit()
    conn.close()
    print(f"[INFO] [{PRINT_PREFIX}] Removed user {user_id} from deafened_users in VC {vc_id}")
