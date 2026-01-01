# src\core\users\voice.py
# User voice related core functionalities (deafens, mutes, moves, disconnects, etc)

PRINT_PREFIX = "CORE - USERS - VOICE"

# Local imports
from config.env_vars import HOME_GUILD_ID
from src.core.decorators import offload_fallback
from src.core.fetching import get_guild_or_fetch, get_member_or_fetch, get_channel_or_fetch

@offload_fallback(PRINT_PREFIX)
async def disconnect_user(bot, /, user_id: int, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Disconnects a user from their current voice channel.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        user_id (int): The ID of the user to disconnect.
        reason (str): Reason for the disconnection.
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

    if member.voice is None or member.voice.channel is None:
        print(f"[WARNING] [{PRINT_PREFIX}] Member with ID {user_id} is not connected to any voice channel.")
        return False

    try:
        await member.move_to(None, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Disconnected user {user_id} from voice channel in guild {HOME_GUILD_ID}.")
        return True
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to disconnect user {user_id} from voice channel in guild {HOME_GUILD_ID}: {e}")
        return False
    
@offload_fallback(PRINT_PREFIX)
async def move_user(bot, /, user_id: int, target_channel_id: int, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Moves a user to a specified voice channel.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        user_id (int): The ID of the user to move.
        target_channel_id (int): The ID of the target voice channel.
        reason (str): Reason for the move.
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

    target_channel = await get_channel_or_fetch(guild, target_channel_id)
    if target_channel is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Target channel with ID {target_channel_id} not found in guild {HOME_GUILD_ID}.")
        return False

    try:
        await member.move_to(target_channel, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Moved user {user_id} to channel {target_channel_id} in guild {HOME_GUILD_ID}.")
        return True
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to move user {user_id} to channel {target_channel_id} in guild {HOME_GUILD_ID}: {e}")
        return False

@offload_fallback(PRINT_PREFIX)
async def modify_voice_user(bot, /, user_id: int, mute: bool | None = None, deafen: bool | None = None, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Modifies a user's voice state (mute/deafen).
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        user_id (int): The ID of the user to modify.
        mute (bool | None): True to mute, False to unmute, None to leave unchanged.
        deafen (bool | None): True to deafen, False to undeafen, None to leave unchanged.
        reason (str): Reason for the modification.
        task_timeout (int): Timeout for the task execution:
            None: Will wait indefinitely.
            0: Will not wait at all, fire-and-forget.
            >0: Will wait up to N seconds.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    guild = bot.get_guild(HOME_GUILD_ID)
    if guild is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Guild with ID {HOME_GUILD_ID} not found.")
        return False

    member = guild.get_member(user_id)
    if member is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Member with ID {user_id} not found in guild {HOME_GUILD_ID}.")
        return False

    try:
        await member.edit(mute=mute, deafen=deafen, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Modified voice state for user {user_id} in guild {HOME_GUILD_ID}.")
        return True
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to modify voice state for user {user_id} in guild {HOME_GUILD_ID}: {e}")
        return False