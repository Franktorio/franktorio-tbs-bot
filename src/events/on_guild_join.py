# src\events\on_guild_add.py
# Event Handler - Handles actions when the bot is added to a new guild

PRINT_PREFIX = "EVENTS - GUILD JOIN"

# Third-party imports
import discord

# Local imports
from bot import bot
from config.env_vars import HOME_GUILD_ID, ALLOWED_GUILDS

@bot.event
async def on_guild_join(guild: discord.Guild):
    """
    Event handler for when the bot joins a new guild.
    Will leave the server if it's not home guild or in the allowed guilds list.
    """

    allowed = ALLOWED_GUILDS.append(HOME_GUILD_ID)

    if guild.id not in allowed:
        print(f"[WARNING] [{PRINT_PREFIX}] Joined guild '{guild.name}' (ID: {guild.id}) which is not in allowed guilds.")
        await guild.leave()
        print(f"[INFO] [{PRINT_PREFIX}] Left guild '{guild.name}' (ID: {guild.id})")