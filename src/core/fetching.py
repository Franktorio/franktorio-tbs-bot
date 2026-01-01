# src\core\_helpers.py
# Helper functions for core module to handle cache-first with fetch fallback

# Third-party imports
import discord


async def get_guild_or_fetch(bot: discord.Client, guild_id: int) -> discord.Guild | None:
    """
    Gets a guild from cache, fetches if not found.
    
    Args:
        bot: The bot instance to use.
        guild_id (int): The ID of the guild to get.
    
    Returns:
        discord.Guild | None: The guild object, or None if not found.
    """
    guild = bot.get_guild(guild_id)
    if guild is None:
        try:
            guild = await bot.fetch_guild(guild_id)
        except Exception:
            pass
    return guild


async def get_member_or_fetch(guild: discord.Guild, user_id: int) -> discord.Member | None:
    """
    Gets a member from cache, fetches if not found.
    
    Args:
        bot: The bot instance (unused but kept for consistency).
        guild (discord.Guild): The guild to get the member from.
        user_id (int): The ID of the user to get.
    
    Returns:
        discord.Member | None: The member object, or None if not found.
    """
    member = guild.get_member(user_id)
    if member is None:
        try:
            member = await guild.fetch_member(user_id)
        except Exception:
            pass
    return member


async def get_channel_or_fetch(guild: discord.Guild, channel_id: int) -> discord.abc.GuildChannel | discord.Thread | None:
    """
    Gets a channel from cache, fetches if not found.
    
    Args:
        bot: The bot instance (unused but kept for consistency).
        guild (discord.Guild): The guild to get the channel from.
        channel_id (int): The ID of the channel to get.
    
    Returns:
        discord.abc.GuildChannel | discord.Thread | None: The channel object, or None if not found.
    """
    channel = guild.get_channel(channel_id)
    if channel is None:
        try:
            channel = await guild.fetch_channel(channel_id)
        except Exception:
            pass
    return channel

async def get_role_or_fetch(guild: discord.Guild, role_id: int) -> discord.Role | None:
    """
    Gets a role from cache, fetches if not found.
    
    Args:
        bot: The bot instance (unused but kept for consistency).
        guild (discord.Guild): The guild to get the role from.
        role_id (int): The ID of the role to get.
    Returns:
        discord.Role | None: The role object, or None if not found.
    """
    role = guild.get_role(role_id)
    if role is None:
        try:
            role = await guild.fetch_role(role_id)
        except Exception:
            pass
    return role