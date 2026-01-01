# src\core\channels\modifications.py
# Channel modification related core functionalities (modify text/voice channels, categories, stages, forums, etc)

PRINT_PREFIX = "CORE - CHANNELS - MODIFICATIONS"

# Third-party imports
import discord

# Local imports
from config.env_vars import HOME_GUILD_ID
from src.core.decorators import offload_fallback
from src.core.fetching import get_guild_or_fetch, get_channel_or_fetch

@offload_fallback(PRINT_PREFIX)
async def rename_channel(bot: discord.Client, /, channel_id: int, new_name: str, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Renames a channel in the home guild.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        channel_id (int): The ID of the channel to rename.
        new_name (str): The new name for the channel.
        reason (str): Reason for renaming the channel.
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

    channel = await get_channel_or_fetch(guild, channel_id)
    if channel is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Channel with ID {channel_id} not found in guild {HOME_GUILD_ID}.")
        return False

    try:
        await channel.edit(name=new_name, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Renamed channel {channel_id} to '{new_name}' in guild {HOME_GUILD_ID}.")
        return True
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to rename channel {channel_id} in guild {HOME_GUILD_ID}: {e}")
        return False

@offload_fallback(PRINT_PREFIX)
async def set_channel_permission(bot: discord.Client, /, channel_id: int, target: discord.Role | discord.Member, overwrite: discord.PermissionOverwrite | None = None, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Adds permission overwrites to a channel for a specific role or member.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        channel_id (int): The ID of the channel to modify.
        target (discord.Role | discord.Member): The role or member to set the permissions for.
        overwrite (discord.PermissionOverwrite | None): The permission overwrites to apply, or None to clear overwrite for the target.
        reason (str): Reason for modifying the permissions.
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

    channel = await get_channel_or_fetch(guild, channel_id)
    if channel is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Channel with ID {channel_id} not found in guild {HOME_GUILD_ID}.")
        return False

    try:
        await channel.set_permissions(target, overwrite=overwrite, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Set permissions for target {target} in channel {channel_id} in guild {HOME_GUILD_ID}.")
        return True
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to set permissions for target {target} in channel {channel_id} in guild {HOME_GUILD_ID}: {e}")
        return False
    
@offload_fallback(PRINT_PREFIX)
async def set_channel_status(bot: discord.Client, /, channel_id: int, new_status: str, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Sets the status of a stage channel in the home guild.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        channel_id (int): The ID of the stage channel to change the status of.
        new_status (str): The new status for the stage channel ('live' or 'ended').
        reason (str): Reason for changing the status.
        task_timeout (int): Timeout for the task execution:
            None: Will wait indefinitely.
            0: Will not wait at all, fire-and-forget.
            >0: Will wait up to N seconds.
    Returns:
        bool: True if successful, False otherwise.
    """

    guild = bot.get_guild(HOME_GUILD_ID)
    if guild is None:
        try:
            guild = await bot.fetch_guild(HOME_GUILD_ID)
        except Exception as e:
            print(f"[ERROR] [{PRINT_PREFIX}] Guild with ID {HOME_GUILD_ID} not found: {e}")
            return False

    channel = guild.get_channel(channel_id)
    if channel is None:
        try:
            channel = await guild.fetch_channel(channel_id)
        except Exception:
            pass
    if channel is None or not isinstance(channel, discord.StageChannel):
        print(f"[ERROR] [{PRINT_PREFIX}] Stage channel with ID {channel_id} not found in guild {HOME_GUILD_ID}.")
        return False

    try:
        channel.edit(status=new_status, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Changed status of stage channel {channel_id} to '{new_status}' in guild {HOME_GUILD_ID}.")
        return True
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to change status of stage channel {channel_id} in guild {HOME_GUILD_ID}: {e}")
        return False