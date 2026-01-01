# src\db\bot_db\under_review.py
# Under Review table operations

PRINT_PREFIX = "BOT DB - UNDER REVIEW"

# Local imports
from .schema import DB_FILE_NAME
from . import connect_bot_db

def _connect(read_only: bool = False):
    return connect_bot_db(DB_FILE_NAME, read_only=read_only)

def add_under_review(user_id: int, reason: str) -> bool:
    """Add a new under review entry to the database."""
    conn = _connect()
    cursor = conn.cursor()
    
    # Check if the user is already under review without a removed_at timestamp
    cursor.execute("""
        SELECT COUNT(*) FROM under_review
        WHERE user_id = ? AND removed_at IS NULL;
    """, (user_id,))
    result = cursor.fetchone()
    if result[0] > 0:
        print(f"[WARNING] [{PRINT_PREFIX}] User_id {user_id} is already under review.")
        conn.close()
        return False
    
    cursor.execute("""
        INSERT INTO under_review (user_id, reason)
        VALUES (?, ?);
    """, (user_id, reason))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added under review entry for user_id {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add under review entry for user_id {user_id}")
    return success

def get_under_review(case_id: int) -> dict | None:
    """Retrieve an under review entry from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT case_id, user_id, reason, given_at, removed_at
        FROM under_review
        WHERE case_id = ?;
    """, (case_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "case_id": result[0],
            "user_id": result[1],
            "reason": result[2],
            "given_at": result[3],
            "removed_at": result[4]
        }
    print(f"[INFO] [{PRINT_PREFIX}] No under review entry found with case_id {case_id}")
    return None

def get_under_review_by_user(user_id: int) -> list[dict]:
    """Retrieve all under review entries for a specific user."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT case_id, user_id, reason, given_at, removed_at
        FROM under_review
        WHERE user_id = ?;
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    
    cases = []
    for result in results:
        cases.append({
            "case_id": result[0],
            "user_id": result[1],
            "reason": result[2],
            "given_at": result[3],
            "removed_at": result[4]
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved under review entries for user_id {user_id}: {len(cases)} entries found")
    return cases

def modify_under_review(case_id: int, reason: str | None = None, removed_at: int | None = None) -> bool:
    """Modify an existing under review entry in the database."""
    conn = _connect()
    cursor = conn.cursor()
    
    fields = []
    values = []
    
    if reason is not None:
        fields.append("reason = ?")
        values.append(reason)
    if removed_at is not None:
        fields.append("removed_at = ?")
        values.append(removed_at)
    
    if not fields:
        conn.close()
        return False
    
    values.append(case_id)
    
    cursor.execute(f"""
        UPDATE under_review
        SET {', '.join(fields)}
        WHERE case_id = ?;
    """, tuple(values))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Modified under review entry with case_id {case_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to modify under review entry with case_id {case_id}")
    return success

def remove_under_review(case_id: int) -> bool:
    """Remove an under review entry from the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM under_review WHERE case_id = ?;
    """, (case_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed under review entry with case_id {case_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove under review entry with case_id {case_id}")
    return success

def get_all_under_review() -> list[dict]:
    """Retrieve all under review entries from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT case_id, user_id, reason, given_at, removed_at
        FROM under_review;
    """)
    results = cursor.fetchall()
    conn.close()
    
    cases = []
    for result in results:
        cases.append({
            "case_id": result[0],
            "user_id": result[1],
            "reason": result[2],
            "given_at": result[3],
            "removed_at": result[4]
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved all under review entries: {len(cases)} entries found")
    return cases

def is_currently_under_review(user_id: int) -> bool:
    """Check if a user is currently under review (i.e., has an entry without removed_at)."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM under_review
        WHERE user_id = ? AND removed_at IS NULL;
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    currently_under_review = result[0] > 0
    if currently_under_review:
        print(f"[INFO] [{PRINT_PREFIX}] User_id {user_id} is currently under review")
    else:
        print(f"[INFO] [{PRINT_PREFIX}] User_id {user_id} is not currently under review")
    return currently_under_review