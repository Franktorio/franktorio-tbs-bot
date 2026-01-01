# src\core\users\removals.py
# User removals related core functionalities (kick, ban, unban, etc)

PRINT_PREFIX = "CORE - USERS - REMOVALS"

# Third-party imports
import discord

# Local imports
from config.env_vars import HOME_GUILD_ID
from src.core.decorators import offload_fallback
from src.core.fetching import get_guild_or_fetch, get_member_or_fetch

@offload_fallback(PRINT_PREFIX)
async def kick_user(bot, /, user_id: int, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Kicks a user from the guild.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        user_id (int): The ID of the user to kick.
        reason (str): Reason for the kick.
        task_timeout (int): Timeout for the task execution:
            None: Will wait indefinitely.
            0: Will not wait at all, fire-and-forget.
            >0: Will wait up to N seconds.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    guild = await get_guild_or_fetch(bot, HOME_GUILD_ID)
    if guild is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Guild with ID {HOME_GUILD_ID} not found.")
        return False

    member = await get_member_or_fetch(guild, user_id)
    if member is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Member with ID {user_id} not found in guild {HOME_GUILD_ID}.")
        return False

    try:
        await member.kick(reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Kicked user {user_id} from guild {HOME_GUILD_ID}.")
        return True
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to kick user {user_id} from guild {HOME_GUILD_ID}: {e}")
        return False
    
@offload_fallback(PRINT_PREFIX)
async def ban_user(bot, /, user_id: int, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Bans a user from the guild, even if they are not currently in the guild.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        user_id (int): The ID of the user to ban.
        reason (str): Reason for the ban.
        task_timeout (int): Timeout for the task execution:
            None: Will wait indefinitely.
            0: Will not wait at all, fire-and-forget.
            >0: Will wait up to N seconds.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    guild = await get_guild_or_fetch(bot, HOME_GUILD_ID)
    if guild is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Guild with ID {HOME_GUILD_ID} not found.")
        return False

    try:
        member = guild.get_member(user_id)
        if member:
            await member.ban(reason=reason)
        else:
            await guild.ban(discord.Object(id=user_id), reason=reason)
        
        print(f"[INFO] [{PRINT_PREFIX}] Banned user {user_id} from guild {HOME_GUILD_ID}.")
        return True

    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to ban user {user_id} from guild {HOME_GUILD_ID}: {e}")
        return False

@offload_fallback(PRINT_PREFIX)
async def unban_user(bot, /, user_id: int, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Unbans a user from the guild.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        user_id (int): The ID of the user to unban.
        reason (str): Reason for the unban.
        task_timeout (int): Timeout for the task execution:
            None: Will wait indefinitely.
            0: Will not wait at all, fire-and-forget.
            >0: Will wait up to N seconds.
    Returns:
        bool: True if successful, False otherwise.
    """

    guild = await get_guild_or_fetch(bot, HOME_GUILD_ID)
    if guild is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Guild with ID {HOME_GUILD_ID} not found.")
        return False

    try:
        banned_users = await guild.bans()
        user = discord.Object(id=user_id) # Create a user object with the given ID
        for ban_entry in banned_users:
            if ban_entry.user.id == user_id:
                await guild.unban(user, reason=reason)
                print(f"[INFO] [{PRINT_PREFIX}] Unbanned user {user_id} from guild {HOME_GUILD_ID}.")
                return True

        print(f"[WARNING] [{PRINT_PREFIX}] User {user_id} is not banned in guild {HOME_GUILD_ID}.")
        return False

    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to unban user {user_id} from guild {HOME_GUILD_ID}: {e}")
        return False