# src\tasks\leader_updater.py
# Scheduled task to update leader roles based on their status. (demotions, promotions)

PRINT_PREFIX = "TASKS - LEADER UPDATER"

# Standar library imports
from datetime import datetime

# Third-party imports
import discord
from discord.ext import tasks

# Local imports
import src.core.fetching as fetching
import src.core.users.roles as user_roles
from src.bot import bot
from config.env_vars import HOME_GUILD_ID
import config.config_explorer as cfg_exp
import src.db.bot_db.leaders as leaders_db
import src.db.bot_db.wins as wins_db
from src.core.helpers import log_to_leader_logs


async def _remove_leader_roles(member: discord.Member) -> bool:
    """Remove all leader roles from the member.
    
    Args:
        member: The Discord member to demote
        
    Returns:
        True if successful, False otherwise
    """
    # Gather all leader-related role IDs
    all_tier_roles = cfg_exp.get_all_leader_role_ids()
    roles_to_remove = [
        *all_tier_roles.values(),
        cfg_exp.get_on_break_role_id(),
        cfg_exp.get_general_leader_role_id(),
    ]
    
    # Filter out all leader roles
    new_roles = [role for role in member.roles if role.id not in roles_to_remove]
    
    try:
        success = await user_roles.edit_user_roles(
            user_id=member.id, new_roles=new_roles, reason="Demoted from leader"
        )
        
        if success:
            print(f"[INFO] [{PRINT_PREFIX}] Removed leader roles from user {member.id}.")
        else:
            print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove leader roles from user {member.id}.")
        
        return success
        
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Exception while removing leader roles from user {member.id}: {e}")
        return False


def _due_for_demotion(leader: dict) -> bool:
    """Check if a leader is to be demoted based on their last win date."""
    user_id = leader.get("user_id")
    leader_tier = leader.get("leader_tier")
    time_threshold = leader.get("last_win_at")

    if not time_threshold:
        time_threshold = leader.get("promoted_at", 0)
    
    if leader_tier not in cfg_exp.LEADER_TIERS:
        print(f"[ERROR] [{PRINT_PREFIX}] Invalid leader tier '{leader_tier}' for user_id {user_id}")
        return True  # Demote invalid tiers
    
    wdt_days = cfg_exp.get_leader_tier_config(leader_tier).get("wdt_days")
    if not wdt_days:
        return False  # No demotion days set, cannot be demoted

    demotion_date = datetime.now().timestamp() - (wdt_days * 86400)
    if time_threshold < demotion_date:
        print(f"[INFO] [{PRINT_PREFIX}] Leader with user_id {user_id} is due for demotion.")
        return True
    return False

async def _check_for_demotion(leader: dict, member: discord.Member) -> bool:
    """Check and demote a leader if they are due for demotion."""
    to_be_demoted = _due_for_demotion(leader)

    if not to_be_demoted:
        return False
    
    # Remove all leader roles
    success = await _remove_leader_roles(member)
    if success:
        # Remove from leaders database
        leaders_db.remove_leader(leader["user_id"])
        await log_to_leader_logs(
            title="Demotion",
            description=f"User {member.mention} (ID: {member.id}) has been demoted due to inactivity.",
        )
    return success

def _find_valid_leader_exluding_ranked(leader: dict) -> str | None:
    """Find the first valid leader tier excluding ranked, admiral and master."""
    current_tier = leader.get("leader_tier")
    tier_index = cfg_exp.LEADER_TIERS.index(current_tier)

    win_amount = len(wins_db.get_wins_by_user(leader.get("user_id")))

    for i in range(tier_index - 1, -1, -1):
        tier_name = cfg_exp.LEADER_TIERS[i]
        tier_config = cfg_exp.get_leader_tier_config(tier_name)
        wins_to_reach = tier_config.get("wins_to_reach")

        if wins_to_reach is None:
            continue  # Skip tiers without win requirements

        if win_amount >= wins_to_reach:
            return tier_name
        
    return None

def _validate_leaderboard_tier(leader: dict, current_tier: str, top_10_leaders: list[dict]) -> str:
    """Check if a leader is to be promoted to ranked/admiral based on leaderboard status OR demoted from ranked/admiral."""
    for user_id, _ in top_10_leaders:
        if not user_id == leader.get("user_id"):
            continue

        if current_tier == "admiral":
            return "N/A" # Stays the same
        elif current_tier == "ranked":
            return "N/A"  # Stays the same
        
        if current_tier == "master":
            return "admiral"  # Promote to admiral
        else:
            return "ranked"  # Promote to ranked
    
    # Not in top 10, check for demotion from ranked/admiral
    if current_tier == "admiral":
        return "master"  # Demote to master
    elif current_tier == "ranked":
        valid_tier = _find_valid_leader_exluding_ranked(leader)
        return valid_tier if valid_tier else "trial"  # Demote to valid tier or trial
    
    print(f"[INFO] [{PRINT_PREFIX}] Leader with user_id {leader.get('user_id')} remains in tier '{current_tier}'.")
    return "N/A"  # Stays the same
    
async def _check_for_leaderboard_promotion_or_demotion(leader: dict, member: discord.Member, top_10_leaders: list[dict]) -> bool:
    """Check and promote/demote a leader based on leaderboard status."""
    current_tier = leader.get("leader_tier")
    new_tier = _validate_leaderboard_tier(leader, current_tier, top_10_leaders)

    if new_tier == "N/A" or new_tier == current_tier:
        return False  # No change

    tier_config = cfg_exp.get_leader_tier_config(new_tier)
    role_id = tier_config.get("role_id")

    if not role_id:
        print(f"[ERROR] [{PRINT_PREFIX}] No role ID found for tier '{new_tier}' for user_id {leader.get('user_id')}")
        return False

    new_role = fetching.get_role_from_guild(member.guild, role_id)
    if not new_role:
        print(f"[ERROR] [{PRINT_PREFIX}] Could not fetch role ID {role_id} for tier '{new_tier}' for user_id {leader.get('user_id')}")
        return False

    # Update roles
    new_roles = [role for role in member.roles if role.id != cfg_exp.get_all_leader_role_ids().get(current_tier)]
    new_roles.append(new_role)

    success = await user_roles.edit_user_roles(
        user_id=member.id, new_roles=new_roles, reason=f"Promoted/Demoted to {new_tier} leader"
    )

    if success:
        # Update leader tier in database
        leaders_db.update_leader_tier(leader.get("user_id"), new_tier)
        await log_to_leader_logs(
            title="Promotion" if cfg_exp.LEADER_TIERS.index(new_tier) > cfg_exp.LEADER_TIERS.index(current_tier) else "Demotion",
            description=f"User {member.mention} (ID: {member.id}) has been moved from {current_tier} to {new_tier} leader.",
        )
        print(f"[INFO] [{PRINT_PREFIX}] Updated leader tier for user_id {leader.get('user_id')} from {current_tier} to {new_tier}.")
    else:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to update leader tier for user_id {leader.get('user_id')} from {current_tier} to {new_tier}.")

@tasks.loop(minutes=5)
async def leader_updater():
    """Scheduled task to update leader roles based on their status.
    
    Flow:
    1. Fetch all leaders from the database.
    2. Validate each leader:
        - Check if the user exists in the guild.
        - Check if they are to be demoted based on last win date.
        - Check if they are to be promoted to ranked/admiral leader.
    3. Update roles accordingly.
    4. Make sure everyone with leader roles is in the leaders database:
        - If a user has leader roles but is not in the database, remove their leader roles.
    """

    print(f"[INFO] [{PRINT_PREFIX}] Starting leader update task at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    guild = await fetching.get_guild_or_fetch(bot, HOME_GUILD_ID)
    if not guild:
        print(f"[ERROR] [{PRINT_PREFIX}] Could not fetch home guild with ID {HOME_GUILD_ID}")
        return

    leaders = leaders_db.get_all_leaders()
    top_10_leaders = wins_db.get_sorted_top_winners(10)

    for leader in leaders:
        member = await fetching.get_member_or_fetch(guild, leader["user_id"])

        # Remove leader if not found in guild
        if not member:
            print(f"[WARNING] [{PRINT_PREFIX}] Leader with user_id {leader['user_id']} not found in guild. Skipping.")
            leaders_db.remove_leader(leader["user_id"])
            continue

        # Check for demotion
        demoted = await _check_for_demotion(leader, member)
        if demoted:
            continue  # Skip further checks if demoted

        # Check for promotion/demotion based on leaderboard
        await _check_for_leaderboard_promotion_or_demotion(leader, member, top_10_leaders)

    # Ensure no users have leader roles without being in the leaders database
    all_tier_role_ids = list(cfg_exp.get_all_leader_role_ids().values())
    all_tier_role_ids.append(cfg_exp.get_general_leader_role_id())
    for member in guild.members:
        has_leader_role = any(role.id in all_tier_role_ids for role in member.roles)
        is_in_leaders_db = any(leader["user_id"] == member.id for leader in leaders)

        if has_leader_role and not is_in_leaders_db:
            print(f"[INFO] [{PRINT_PREFIX}] User {member.id} has leader roles but is not in the leaders database. Removing roles.")
            await _remove_leader_roles(member)




    

