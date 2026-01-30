# src\core\helpers.py
# Core helper functions for various utilities

PRINT_PREFIX = "CORE - HELPERS"

# Third-party imports
import discord
from typing import Literal

# Local imports
from config.env_vars import HOME_GUILD_ID
from src.core import fetching
from src.bot import bot
from src.db import context_json
import src.core.embeds as embeds


async def log_to_leader_logs(title: Literal["Demotion", "Promotion", "Role Added", "Role Removed", "Blacklist"], description: str, enforcer: discord.User | None = None) -> None:
    """
    Sends an embed log to the leader logs channel.
    Args:
        title (Literal): The log title to display.
        description (str): The log message to display.
        enforcer (discord.User | None): The user who enforced the action, if applicable.
    Returns:
        None
    """

    channel_id = context_json.get_channel_entry("leader_logs_channel", None)
    if channel_id is None:
        print(f"[WARNING] [{PRINT_PREFIX}] Leader logs channel not configured.")
        return
    
    guild = await fetching.get_guild_or_fetch(bot, HOME_GUILD_ID)
    if guild is None:
        print(f"[WARNING] [{PRINT_PREFIX}] Could not fetch home guild for leader logs.")
        return
    
    channel = await fetching.get_channel_or_fetch(guild, channel_id)
    if channel is None or not isinstance(channel, discord.TextChannel):
        print(f"[WARNING] [{PRINT_PREFIX}] Could not fetch leader logs channel with ID {channel_id}.")
        return

    embed = embeds.create_leader_log_embed(title, description, enforcer)

    await channel.send(embed=embed)
    