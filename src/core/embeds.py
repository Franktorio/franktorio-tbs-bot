# src\core\embeds.py
# Core embed functionalities, such as creating and modifying embeds.

PRINT_PREFIX = "CORE - EMBEDS"

# Third-party imports
from dis import disco
import dis
from typing import Literal
import discord

# Local imports
from config.env_vars import BOT_NAME
from src.bot import bot
from src.db.bot_db.wins import get_wins_by_user

def _get_base_embed(title: str, module: str, color: str) -> discord.Embed:
    """
    Creates a base embed with standard formatting.

    Args:
        title (str): The title of the embed.
        module (str): The module name for footer context.
        color (str): The color of the embed in hex format.
    
    Returns:
        discord.Embed: The base embed object.
    """
    embed = discord.Embed(
        title=title,
        color=discord.Color.from_str(color),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"{BOT_NAME} - {module}", icon_url=bot.user.display_avatar.url)
    print(f"[DEBUG] [{PRINT_PREFIX}] Created base embed with title '{title}' for module '{module}'")
    return embed

def create_leader_log_embed(title: Literal["Demotion", "Promotion", "Role Added", "Role Removed", "Blacklist"], description: str, enforcer: discord.User | None = None) -> discord.Embed:
    """
    Creates a leader log embed with a specific color scheme.
    Autocapitalizes each word in the title.

    Args:
        title (Literal): The log title to display.
        description (str): The log message to display.
        enforcer (discord.User | None): The user who enforced the action, if applicable.
    Returns:
        discord.Embed: The leader log embed object.
    """

    color_map = {
        "Demotion": "#B92323",
        "Promotion": "#2196C4",
        "Role Added": "#21C447",
        "Role Removed": "#B92323",
        "Blacklist": "#111111"
    }
    color = color_map.get(title, "#111111")

    embed = discord.Embed(
        title=f"📝 {' '.join(word.capitalize() for word in title.split())}",
        description=description,
        color=discord.Color.from_str(color),
        timestamp=discord.utils.utcnow()
    )
    if enforcer:
        embed.set_author(
            name=f"Enforced by {enforcer.display_name}",
            icon_url=enforcer.display_avatar.url if enforcer.display_avatar else discord.Embed.Empty
        )
    embed.set_footer(text=f"{BOT_NAME} - Leaders", icon_url=bot.user.display_avatar.url)
    print(f"[DEBUG] [{PRINT_PREFIX}] Created leader log embed with title '{title}' and description '{description}'")
    return embed

def create_success_embed(title: str, description: str) -> discord.Embed:
    """
    Creates a success embed with a green color scheme.
    Prepends a checkmark to the title.
    Autocapitalizes each word in the title.

    Args:
        title (str): The success title to display.
        description (str): The success message to display.
    
    Returns:
        discord.Embed: The success embed object.
    """
    embed = discord.Embed(
        title=f"✅ {' '.join(word.capitalize() for word in title.split())}",
        description=description,
        color=discord.Color.from_str("#21C447"),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"{BOT_NAME}", icon_url=bot.user.display_avatar.url)
    print(f"[DEBUG] [{PRINT_PREFIX}] Created success embed with title '{title}' and description '{description}'")
    return embed

def create_error_embed(title: str, description: str) -> discord.Embed:
    """
    Creates an error embed with a red color scheme.
    Prepends a cross mark to the title.
    Autocapitalizes each word in the title.

    Args:
        title (str): The error title to display.
        description (str): The error message to display.
    
    Returns:
        discord.Embed: The error embed object.
    """
    embed = discord.Embed(
        title=f"❌ {' '.join(word.capitalize() for word in title.split())}",
        description=description,
        color=discord.Color.from_str("#B92323"),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"{BOT_NAME}", icon_url=bot.user.display_avatar.url)
    print(f"[DEBUG] [{PRINT_PREFIX}] Created error embed with title '{title}' and description '{description}'")
    return embed

def create_leader_info_embed(user: discord.User, leader_data: dict, user_wins: list[dict], role: discord.Role) -> discord.Embed:
    """
    Creates an embed displaying leader information for a user.
    Args:
        user (discord.User): The Discord user whose leader info is being
        leader_data (dict): A dictionary containing leader-related data for the user.
        {
            "leader_tier": str,
            "last_win_at": int,
            "last_host_at": int,
            "promoted_at": int,
            "on_break_since": int 
        }
        user_wins (list[dict]): A list of dictionaries representing the user's wins.
        role (discord.Role): The Discord role associated with the user's leader tier.
    """
    DEFAULT_COLOR = "#111111"
    embed_color = hex(role.color.value) if role else DEFAULT_COLOR
    
    if embed_color == DEFAULT_COLOR:
        print(f"[WARNING] [{PRINT_PREFIX}] Role color not found or default for user_id {leader_data.get('user_id', 'N/A')}. Role ID: {role.id if role else 'N/A'} Role Name: {role.name if role else 'N/A'}")
    
    embed = _get_base_embed(
        title="👤 Leader Profile",
        module="Leaders",
        color=str(embed_color)
    )

    embed.set_author(
        name=user.display_name + "'s Leader Info" + f" (ID: {user.id})",
        icon_url=user.display_avatar.url if user.display_avatar else discord.Embed.Empty
    )

    last_win = leader_data.get("last_win_at")
    last_win = None if last_win == 0 else last_win

    last_host = leader_data.get("last_host_at")
    last_host = None if last_host == 0 else last_host

    promoted_at = leader_data.get("promoted_at")

    embed.add_field(
        name="⭐ Leader Tier",
        value=leader_data.get("leader_tier", "N/A").capitalize(),
        inline=True
    )
    
    embed.add_field(
        name="🏅 Wins",
        value=str(len(user_wins)),
        inline=True
    )

    # Build activity value
    activity_lines = [
        f"**Last Win:** {f'<t:{int(last_win)}:R>' if last_win else 'N/A'}",
        f"**Last Host:** {f'<t:{int(last_host)}:R>' if last_host else 'N/A'}",
        f"**Last Tier Adjustment:** <t:{int(promoted_at)}:R>" if promoted_at else "N/A",
    ]
    
    embed.add_field(
        name="⏱️ Last Activity",
        value="\n".join(activity_lines),
        inline=False
    )

    print(f"[DEBUG] [{PRINT_PREFIX}] Created leader info embed for user_id {leader_data.get('user_id', 'N/A')}")
    return embed
