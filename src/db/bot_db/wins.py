# src\db\bot_db\wins.py
# Wins table operations

PRINT_PREFIX = "BOT DB - WINS"

# Local imports
from .schema import DB_FILE_NAME
from . import connect_bot_db

def _connect(read_only: bool = False):
    return connect_bot_db(DB_FILE_NAME, read_only=read_only)

def add_win(win_message_id: int, win_message_link: str, user_id: int) -> bool:
    """Add a new win entry to the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO wins (win_message_id, win_message_link, user_id)
        VALUES (?, ?, ?);
    """, (win_message_id, win_message_link, user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Added win for user_id {user_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add win for user_id {user_id}")
    return success

def get_win(win_message_id: int) -> dict | None:
    """Retrieve a win entry from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT win_message_id, win_message_link, user_id, won_at
        FROM wins
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
    print(f"[INFO] [{PRINT_PREFIX}] No win found with win_message_id {win_message_id}")
    return None

def get_wins_by_user(user_id: int) -> list[dict]:
    """Retrieve all win entries for a specific user."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT win_message_id, win_message_link, user_id, won_at
        FROM wins
        WHERE user_id = ?;
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    
    wins = []
    for result in results:
        wins.append({
            "win_message_id": result[0],
            "win_message_link": result[1],
            "user_id": result[2],
            "won_at": result[3]
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved wins for user_id {user_id}: {len(wins)} entries found")
    return wins

def remove_win(win_message_id: int) -> bool:
    """Remove a win entry from the database."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM wins WHERE win_message_id = ?;
    """, (win_message_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if success:
        print(f"[INFO] [{PRINT_PREFIX}] Removed win with win_message_id {win_message_id}")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove win with win_message_id {win_message_id}")
    return success

def get_all_wins() -> list[dict]:
    """Retrieve all win entries from the database."""
    conn = _connect(read_only=True)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT win_message_id, win_message_link, user_id, won_at
        FROM wins;
    """)
    results = cursor.fetchall()
    conn.close()
    
    wins = []
    for result in results:
        wins.append({
            "win_message_id": result[0],
            "win_message_link": result[1],
            "user_id": result[2],
            "won_at": result[3]
        })
    
    print(f"[INFO] [{PRINT_PREFIX}] Retrieved all wins: {len(wins)} entries found")
    return wins

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