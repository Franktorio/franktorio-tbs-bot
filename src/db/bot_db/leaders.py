# src\db\bot_db\leaders.py
# Leaders table operations

PRINT_PREFIX = "BOT DB - LEADERS"

# Standard library imports
import datetime

# Local imports
from .schema import DB_FILE_NAME
from ._helpers import serialize_json, deserialize_json
from . import connect_bot_db

def _connect(read_only: bool = False):
    return connect_bot_db(DB_FILE_NAME, read_only=read_only)

def add_leader(user_id: int, highest_leader_role: str | None = None) -> bool:
    """Add a new leader entry to the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leaders (user_id, highest_leader_role)
        VALUES (?, ?);
    """, (user_id, highest_leader_role))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added leader with user_id {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add leader with user_id {user_id}")
    return success

def get_leader(user_id: int) -> dict | None:
    """Retrieve a leader entry from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, leader_roles, highest_leader_role, wins, last_win_at,
               last_host_at, inactivity_demotion_in, winless_demotion_in
        FROM leaders
        WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "user_id": result[0],
            "leader_roles": deserialize_json(result[1], default=[]),
            "highest_leader_role": result[2],
            "wins": deserialize_json(result[3], default={}),
            "last_win_at": result[4],
            "last_host_at": result[5],
            "inactivity_demotion_in": result[6],
            "winless_demotion_in": result[7]
        }
    print(f"[INFO] [{PRINT_PREFIX}] No leader found with user_id {user_id}")
    return None

def modify_leader(user_id: int, highest_leader_role: str | None = None,
                  last_win_at: int | None = None, last_host_at: int | None = None,
                  inactivity_demotion_in: int | None = None,
                  winless_demotion_in: int | None = None) -> bool:
    """Modify an existing leader entry in the database."""
    conn = _connect()
    cursor = conn.cursor()
    
    fields = []
    values = []
    
    if highest_leader_role is not None:
        fields.append("highest_leader_role = ?")
        values.append(highest_leader_role)
    if last_win_at is not None:
        fields.append("last_win_at = ?")
        values.append(last_win_at)
    if last_host_at is not None:
        fields.append("last_host_at = ?")
        values.append(last_host_at)
    if inactivity_demotion_in is not None:
        fields.append("inactivity_demotion_in = ?")
        values.append(inactivity_demotion_in)
    if winless_demotion_in is not None:
        fields.append("winless_demotion_in = ?")
        values.append(winless_demotion_in)
    
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

def add_leader_role(user_id: int, role: str) -> bool:
    """Add a role to a leader's leader_roles list."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT leader_roles FROM leaders WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        print(f"[WARN] [{PRINT_PREFIX}] No leader found with user_id {user_id}")
        return False
    
    leader_roles = deserialize_json(result[0], default=[])
    if role not in leader_roles:
        leader_roles.append(role)
    
    cursor.execute("""
        UPDATE leaders SET leader_roles = ? WHERE user_id = ?;
    """, (serialize_json(leader_roles), user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added role '{role}' to leader {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add role to leader {user_id}")
    return success

def remove_leader_role(user_id: int, role: str) -> bool:
    """Remove a role from a leader's leader_roles list."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT leader_roles FROM leaders WHERE user_id = ?;
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        print(f"[WARN] [{PRINT_PREFIX}] No leader found with user_id {user_id}")
        return False
    
    leader_roles = deserialize_json(result[0], default=[])
    if role in leader_roles:
        leader_roles.remove(role)
    
    cursor.execute("""
        UPDATE leaders SET leader_roles = ? WHERE user_id = ?;
    """, (serialize_json(leader_roles), user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed role '{role}' from leader {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove role from leader {user_id}")
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
    """Retrieve all leader entries from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, leader_roles, highest_leader_role, wins, last_win_at,
               last_host_at, inactivity_demotion_in, winless_demotion_in
        FROM leaders;
    """)
    results = cursor.fetchall()
    conn.close()
    
    leaders = []
    for result in results:
        leaders.append({
            "user_id": result[0],
            "leader_roles": deserialize_json(result[1], default=[]),
            "highest_leader_role": result[2],
            "wins": deserialize_json(result[3], default={}),
            "last_win_at": result[4],
            "last_host_at": result[5],
            "inactivity_demotion_in": result[6],
            "winless_demotion_in": result[7]
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved all leaders: {len(leaders)} entries found")
    return leaders