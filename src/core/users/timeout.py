# src\core\users\timeout.py
# User timeout related core functionalities

PRINT_PREFIX = "CORE - USERS - TIMEOUT"

# Standard library imports
from datetime import timedelta

# Local imports
from config.env_vars import HOME_GUILD_ID
from src.core.decorators import offload_fallback
from src.core.fetching import get_guild_or_fetch, get_member_or_fetch

@offload_fallback(PRINT_PREFIX)
async def timeout_user(bot, /, user_id: int, duration: int, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Timeouts a user for a specified duration in seconds.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        user_id (int): The ID of the user to timeout.
        duration (int): Duration in seconds for the timeout.
        reason (str): Reason for the timeout.
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
        timeout_duration = timedelta(seconds=duration)
        await member.edit(timeout_duration=timeout_duration, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Timed out user {user_id} in guild {HOME_GUILD_ID} for {duration} seconds.")
        return True
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to timeout user {user_id} in guild {HOME_GUILD_ID}: {e}")
        return False

@offload_fallback(PRINT_PREFIX)
async def remove_timeout_user(bot, /, user_id: int, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Removes timeout from a user.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        user_id (int): The ID of the user to remove timeout from.
        reason (str): Reason for removing the timeout.
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
        await member.edit(timeout_duration=None, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Removed timeout from user {user_id} in guild {HOME_GUILD_ID}.")
        return True
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove timeout from user {user_id} in guild {HOME_GUILD_ID}: {e}")
        return False