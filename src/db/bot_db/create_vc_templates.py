# src\db\bot_db\create_vc_templates.py
# Create VC Templates table operations

PRINT_PREFIX = "BOT DB - VC TEMPLATES"

# Local import
from .schema import DB_FILE_NAME
from .helpers import serialize_json, deserialize_json
from ..connections import connect_db

def _connect(read_only: bool = False):
    return connect_db(DB_FILE_NAME, read_only=read_only)

def add_vc_template(master_vc_id: int, name_prefix: str, permission_overrides: dict,
                    manager_roles: list[int], apply_global_blacklists: bool,
                    apply_owner_permissions: bool, apply_whitelisted_users: bool) -> None:
    """Add a new VC template entry to the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO create_vc_templates (master_vc_id, name_prefix, permission_overrides,
                                         manager_roles, apply_global_blacklists,
                                         apply_owner_permissions, apply_whitelisted_users)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (master_vc_id, name_prefix, serialize_json(permission_overrides),
          serialize_json(manager_roles), int(apply_global_blacklists),
          int(apply_owner_permissions), int(apply_whitelisted_users)))
    conn.commit()
    conn.close()
    print(f"[INFO] [{PRINT_PREFIX}] Added VC template with master_vc_id {master_vc_id}")

def modify_vc_template(master_vc_id: int, name_prefix: str | None = None,
                       permission_overrides: dict | None = None,
                       manager_roles: list[int] | None = None,
                       apply_global_blacklists: bool | None = None,
                       apply_owner_permissions: bool | None = None,
                       apply_whitelisted_users: bool | None = None) -> None:
    """Modify an existing VC template entry in the database."""
    conn = _connect()
    cursor = conn.cursor()
    
    fields = []
    values = []
    
    if name_prefix is not None:
        fields.append("name_prefix = ?")
        values.append(name_prefix)
    if permission_overrides is not None:
        fields.append("permission_overrides = ?")
        values.append(serialize_json(permission_overrides))
    if manager_roles is not None:
        fields.append("manager_roles = ?")
        values.append(serialize_json(manager_roles))
    if apply_global_blacklists is not None:
        fields.append("apply_global_blacklists = ?")
        values.append(int(apply_global_blacklists))
    if apply_owner_permissions is not None:
        fields.append("apply_owner_permissions = ?")
        values.append(int(apply_owner_permissions))
    if apply_whitelisted_users is not None:
        fields.append("apply_whitelisted_users = ?")
        values.append(int(apply_whitelisted_users))
    
    values.append(master_vc_id)
    
    cursor.execute(f"""
        UPDATE create_vc_templates
        SET {', '.join(fields)}
        WHERE master_vc_id = ?;
    """, tuple(values))
    
    conn.commit()
    conn.close()
    print(f"[INFO] [{PRINT_PREFIX}] Modified VC template with master_vc_id {master_vc_id}")

def get_vc_template(master_vc_id: int) -> dict | None:
    """Retrieve a VC template entry from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT master_vc_id, name_prefix, permission_overrides, manager_roles,
               apply_global_blacklists, apply_owner_permissions, apply_whitelisted_users
        FROM create_vc_templates
        WHERE master_vc_id = ?;
    """, (master_vc_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "master_vc_id": result[0],
            "name_prefix": result[1],
            "permission_overrides": deserialize_json(result[2], default={}),
            "manager_roles": deserialize_json(result[3], default=[]),
            "apply_global_blacklists": bool(result[4]),
            "apply_owner_permissions": bool(result[5]),
            "apply_whitelisted_users": bool(result[6])
        }
    print(f"[INFO] [{PRINT_PREFIX}] No VC template found with master_vc_id {master_vc_id}")
    return None

def remove_vc_template(master_vc_id: int) -> None:
    """Remove a VC template entry from the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM create_vc_templates WHERE master_vc_id = ?;
    """, (master_vc_id,))
    conn.commit()
    conn.close()
    print(f"[INFO] [{PRINT_PREFIX}] Removed VC template with master_vc_id {master_vc_id}")

def get_all_vc_templates() -> list[dict]:
    """Retrieve all VC template entries from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT master_vc_id, name_prefix, permission_overrides, manager_roles,
               apply_global_blacklists, apply_owner_permissions, apply_whitelisted_users
        FROM create_vc_templates;
    """)
    results = cursor.fetchall()
    conn.close()
    
    vc_templates = []
    for result in results:
        vc_templates.append({
            "master_vc_id": result[0],
            "name_prefix": result[1],
            "permission_overrides": deserialize_json(result[2], default={}),
            "manager_roles": deserialize_json(result[3], default=[]),
            "apply_global_blacklists": bool(result[4]),
            "apply_owner_permissions": bool(result[5]),
            "apply_whitelisted_users": bool(result[6])
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved all VC templates: {len(vc_templates)} entries found")
    return vc_templates