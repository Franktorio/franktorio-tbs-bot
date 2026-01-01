# src\db\bot_db\minor_wins.py
# Minor Wins table operations

PRINT_PREFIX = "BOT DB - MINOR WINS"

# Local imports
from .schema import DB_FILE_NAME
from . import connect_bot_db

def _connect(read_only: bool = False):
    return connect_bot_db(DB_FILE_NAME, read_only=read_only)

def add_minor_win(win_message_id: int, win_message_link: str, user_id: int) -> bool:
    """Add a new minor win entry to the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO minor_wins (win_message_id, win_message_link, user_id)
        VALUES (?, ?, ?);
    """, (win_message_id, win_message_link, user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added minor win for user_id {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add minor win for user_id {user_id}")
    return success

def get_minor_win(win_message_id: int) -> dict | None:
    """Retrieve a minor win entry from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT win_message_id, win_message_link, user_id, won_at
        FROM minor_wins
        WHERE win_message_id = ?;
    """, (win_message_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "win_message_id": result[0],
            "win_message_link": result[1],
            "user_id": result[2],
            "won_at": result[3]
        }
    print(f"[INFO] [{PRINT_PREFIX}] No minor win found with win_message_id {win_message_id}")
    return None

def get_minor_wins_by_user(user_id: int) -> list[dict]:
    """Retrieve all minor win entries for a specific user."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT win_message_id, win_message_link, user_id, won_at
        FROM minor_wins
        WHERE user_id = ?;
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    
    minor_wins = []
    for result in results:
        minor_wins.append({
            "win_message_id": result[0],
            "win_message_link": result[1],
            "user_id": result[2],
            "won_at": result[3]
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved minor wins for user_id {user_id}: {len(minor_wins)} entries found")
    return minor_wins

def remove_minor_win(win_message_id: int) -> bool:
    """Remove a minor win entry from the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM minor_wins WHERE win_message_id = ?;
    """, (win_message_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed minor win with win_message_id {win_message_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove minor win with win_message_id {win_message_id}")
    return success

def get_all_minor_wins() -> list[dict]:
    """Retrieve all minor win entries from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT win_message_id, win_message_link, user_id, won_at
        FROM minor_wins;
    """)
    results = cursor.fetchall()
    conn.close()
    
    minor_wins = []
    for result in results:
        minor_wins.append({
            "win_message_id": result[0],
            "win_message_link": result[1],
            "user_id": result[2],
            "won_at": result[3]
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved all minor wins: {len(minor_wins)} entries found")
    return minor_wins

def get_sorted_top_winners(limit: int = 10) -> list[tuple[int, int]]:
    """
    Retrieve top winners sorted by number of wins, returns a list of tuples (user_id, win_count) in descending order (most wins to least).
    """
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, COUNT(*) as win_count
        FROM wins
        GROUP BY user_id
        ORDER BY win_count DESC
        LIMIT ?;
    """, (limit,))
    results = cursor.fetchall()
    conn.close()
    
    top_winners = [(result[0], result[1]) for result in results]
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved top {limit} winners")
    return top_winners