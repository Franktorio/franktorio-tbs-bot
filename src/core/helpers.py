# src\core\helpers.py
# Core helper functions for various utilities

PRINT_PREFIX = "CORE - HELPERS"

# Local imports
from fastapi.background import P
import config.config_explorer as config_explorer
from src.db import bot_db



def _is_on_win_leaderboard(user_id: int) -> bool:
    """
    Check if a user is currently on the leaderboard.

    Args:
        user_id (int): The Discord user ID.
    Returns:
        bool: True if the user is on the leaderboard, False otherwise.
    """
    for user, _ in bot_db.wins.get_sorted_top_winners():
        print(f"[DEBUG] [{PRINT_PREFIX}] Checking leaderboard user: {user} against user_id: {user_id}")
        if user == user_id:
            return True
    return False

        
def check_promotion_eligibility(user_id: int) -> str | None:
    """
    Check if a user is eligible for leader promotion and return the tier name if eligible or None otherwise.

    Args:
        user_id (int): The Discord user ID.

    Returns:
        str | None: The tier name if eligible, otherwise None.
    """

    user_data = bot_db.users.get_user(user_id)
    if not user_data:
        print(f"[WARN] [{PRINT_PREFIX}] User: {user_id} not found in users database when checking for promotion eligibility.")
        return None
    
    leader_data = bot_db.leaders.get_leader(user_id)
    if not leader_data:
        print(f"[WARN] [{PRINT_PREFIX}] User: {user_id} was checked for promotion but is not a leader, please investigate.")
        return None
    
    current_tier = leader_data.get("leader_tier", None)
    if not current_tier:
        print(f"[WARN] [{PRINT_PREFIX}] User: {user_id} has no leader tier assigned, cannot check promotion eligibility.")
        return None
    
    tier_config = config_explorer.get_leader_tier_config(current_tier)
    if not tier_config:
        print(f"[ERROR] [{PRINT_PREFIX}] Leader tier: {current_tier} configuration not found when checking promotion eligibility for user: {user_id}.")
        return None
    
    next_tier = tier_config.get("next_tier", None)
    if not next_tier:
        return None
    
    # Get wins requirement from current tier (wins needed to reach next tier)
    wins_to_reach = tier_config.get("wins_to_reach", None)
    
    # Get total wins for the leader
    leader_wins_total = len(bot_db.wins.get_wins_by_user(user_id))
    
    # Check win-based promotion
    if wins_to_reach is not None and leader_wins_total >= wins_to_reach:
        return next_tier
    
    # Special case: master -> admiral (requires leaderboard placemen while also being master)
    if next_tier == "admiral" and current_tier == "master":
        if _is_on_win_leaderboard(user_id):
            print(f"[INFO] [{PRINT_PREFIX}] Eligibility for admiral promotion for user: {user_id} is {next_tier}.")
            return next_tier
        else:
            print(f"[DEBUG] [{PRINT_PREFIX}] User: {user_id} not on leaderboard, cannot promote to admiral.")
            return None
        
    # Special case: any leader tier -> ranked (requires leaderboard placement)
    if next_tier == "ranked":
        if _is_on_win_leaderboard(user_id):
            print(f"[INFO] [{PRINT_PREFIX}] Eligibility for ranked promotion for user: {user_id} is {next_tier}.")
            return next_tier
        else:
            print(f"[DEBUG] [{PRINT_PREFIX}] User: {user_id} not on leaderboard, cannot promote to ranked.")
            return None

    return None
