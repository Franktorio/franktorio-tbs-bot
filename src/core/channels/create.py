# src\core\channels\create.py
# Channel creation related core functionalities (create text/voice channels, categories, stages, forums, etc)

PRINT_PREFIX = "CORE - CHANNELS - CREATE"

# Third-party imports
import discord

# Local imports
from config.env_vars import HOME_GUILD_ID
from src.core.decorators import offload_fallback_return
from core.helpers import get_guild_or_fetch, get_channel_or_fetch

@offload_fallback_return(PRINT_PREFIX)
async def create_text_channel(bot, /, channel_name: str, category_id: int = None, overwrites: dict = None, reason: str = "No reason provided", task_timeout: int = 10) -> discord.TextChannel | None:
    """
    Creates a text channel in the home guild.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        channel_name (str): The name of the text channel to create.
        category_id (int): The ID of the category to create the channel in (optional).
        overwrites (dict): A dict of permission overwrites {role/member: PermissionOverwrite} (optional).
        reason (str): Reason for creating the channel.
        task_timeout (int): Timeout for the task execution:
            None: Will wait indefinitely.
            0: Will not wait at all, fire-and-forget.
            >0: Will wait up to N seconds.
    
    Returns:
        discord.TextChannel | None: The created text channel, or None if creation failed.
    """
    guild = await get_guild_or_fetch(bot, HOME_GUILD_ID)
    if guild is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Guild with ID {HOME_GUILD_ID} not found.")
        return None

    category = None
    if category_id is not None:
        category = await get_channel_or_fetch(guild, category_id)
        if category is None or not isinstance(category, discord.CategoryChannel):
            print(f"[ERROR] [{PRINT_PREFIX}] Category with ID {category_id} not found or is not a category channel.")
            return None
    
    try:
        channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Created text channel '{channel_name}' in guild {HOME_GUILD_ID}.")
        return channel
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to create text channel '{channel_name}' in guild {HOME_GUILD_ID}: {e}")
        return None

@offload_fallback_return(PRINT_PREFIX)
async def create_voice_channel(bot, /, channel_name: str, category_id: int = None, overwrites: dict = None, reason: str = "No reason provided", task_timeout: int = 10) -> discord.VoiceChannel | None:
    """
    Creates a voice channel in the home guild.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        channel_name (str): The name of the voice channel to create.
        category_id (int): The ID of the category to create the channel in (optional).
        overwrites (dict): A dict of permission overwrites {role/member: PermissionOverwrite} (optional).
        reason (str): Reason for creating the channel.
        task_timeout (int): Timeout for the task execution:
            None: Will wait indefinitely.
            0: Will not wait at all, fire-and-forget.
            >0: Will wait up to N seconds.
    Returns:
        discord.VoiceChannel | None: The created voice channel, or None if creation failed
    """
    guild = await get_guild_or_fetch(bot, HOME_GUILD_ID)
    if guild is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Guild with ID {HOME_GUILD_ID} not found.")
        return None

    category = None
    if category_id is not None:
        category = await get_channel_or_fetch(guild, category_id)
        if category is None or not isinstance(category, discord.CategoryChannel):
            print(f"[ERROR] [{PRINT_PREFIX}] Category with ID {category_id} not found or is not a category channel.")
            return None
    
    try:
        channel = await guild.create_voice_channel(name=channel_name, category=category, overwrites=overwrites, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Created voice channel '{channel_name}' in guild {HOME_GUILD_ID}.")
        return channel
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to create voice channel '{channel_name}' in guild {HOME_GUILD_ID}: {e}")
        return None
    
@offload_fallback_return(PRINT_PREFIX)
async def create_category_channel(bot, /, category_name: str, overwrites: dict = None, reason: str = "No reason provided", task_timeout: int = 10) -> discord.CategoryChannel | None:
    """
    Creates a category channel in the home guild.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        category_name (str): The name of the category channel to create.
        overwrites (dict): A dict of permission overwrites {role/member: PermissionOverwrite} (optional).
        reason (str): Reason for creating the category.
        task_timeout (int): Timeout for the task execution:
            None: Will wait indefinitely.
            0: Will not wait at all, fire-and-forget.
            >0: Will wait up to N seconds.
    Returns:
        discord.CategoryChannel | None: The created category channel, or None if creation failed.
    """
    guild = await get_guild_or_fetch(bot, HOME_GUILD_ID)
    if guild is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Guild with ID {HOME_GUILD_ID} not found.")
        return None

    try:
        category = await guild.create_category(name=category_name, overwrites=overwrites, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Created category channel '{category_name}' in guild {HOME_GUILD_ID}.")
        return category
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to create category channel '{category_name}' in guild {HOME_GUILD_ID}: {e}")
        return None

@offload_fallback_return(PRINT_PREFIX)
async def create_forum_channel(bot, /, channel_name: str, category_id: int = None, overwrites: dict = None, reason: str = "No reason provided", task_timeout: int = 10) -> discord.ForumChannel | None:
    """
    Creates a forum channel in the home guild.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        channel_name (str): The name of the forum channel to create.
        category_id (int): The ID of the category to create the channel in (optional).
        overwrites (dict): A dict of permission overwrites {role/member: PermissionOverwrite} (optional).
        reason (str): Reason for creating the channel.
        task_timeout (int): Timeout for the task execution:
            None: Will wait indefinitely.
            0: Will not wait at all, fire-and-forget.
            >0: Will wait up to N seconds.
    Returns:
        discord.ForumChannel | None: The created forum channel, or None if creation failed.
    """
    guild = await get_guild_or_fetch(bot, HOME_GUILD_ID)
    if guild is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Guild with ID {HOME_GUILD_ID} not found.")
        return None

    category = None
    if category_id is not None:
        category = await get_channel_or_fetch(guild, category_id)
        if category is None or not isinstance(category, discord.CategoryChannel):
            print(f"[ERROR] [{PRINT_PREFIX}] Category with ID {category_id} not found or is not a category channel.")
            return None
    
    try:
        channel = await guild.create_forum(name=channel_name, category=category, overwrites=overwrites, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Created forum channel '{channel_name}' in guild {HOME_GUILD_ID}.")
        return channel
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to create forum channel '{channel_name}' in guild {HOME_GUILD_ID}: {e}")
        return None

@offload_fallback_return(PRINT_PREFIX)
async def create_stage_channel(bot, /, channel_name: str, category_id: int = None, overwrites: dict = None, reason: str = "No reason provided", task_timeout: int = 10) -> discord.StageChannel | None:
    """
    Creates a stage channel in the home guild.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        channel_name (str): The name of the stage channel to create.
        category_id (int): The ID of the category to create the channel in (optional).
        overwrites (dict): A dict of permission overwrites {role/member: PermissionOverwrite} (optional).
        reason (str): Reason for creating the channel.
        task_timeout (int): Timeout for the task execution:
            None: Will wait indefinitely.
            0: Will not wait at all, fire-and-forget.
            >0: Will wait up to N seconds.
    Returns:
        discord.StageChannel | None: The created stage channel, or None if creation failed.
    """
    guild = await get_guild_or_fetch(bot, HOME_GUILD_ID)
    if guild is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Guild with ID {HOME_GUILD_ID} not found.")
        return None

    category = None
    if category_id is not None:
        category = await get_channel_or_fetch(bot, guild, category_id)
        if category is None or not isinstance(category, discord.CategoryChannel):
            print(f"[ERROR] [{PRINT_PREFIX}] Category with ID {category_id} not found or is not a category channel.")
            return None
    
    try:
        channel = await guild.create_stage_channel(name=channel_name, category=category, overwrites=overwrites, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Created stage channel '{channel_name}' in guild {HOME_GUILD_ID}.")
        return channel
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to create stage channel '{channel_name}' in guild {HOME_GUILD_ID}: {e}")
        return None