# src\core\embeds.py
# Core embed functionalities, such as creating and modifying embeds.

PRINT_PREFIX = "CORE - EMBEDS"

# Third-party imports
from dis import disco
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

def create_success_embed(title: str, description: str) -> discord.Embed:
    """
    Creates a success embed with a green color scheme.
    Prepends a checkmark to the title.

    Args:
        title (str): The success title to display.
        description (str): The success message to display.
    
    Returns:
        discord.Embed: The success embed object.
    """
    embed = discord.Embed(
        title=f"✅ {title}",
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

    Args:
        title (str): The error title to display.
        description (str): The error message to display.
    
    Returns:
        discord.Embed: The error embed object.
    """
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=discord.Color.from_str("#B92323"),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"{BOT_NAME}", icon_url=bot.user.display_avatar.url)
    print(f"[DEBUG] [{PRINT_PREFIX}] Created error embed with title '{title}' and description '{description}'")
    return embed

def create_leader_info_embed(user: discord.User, leader_data: dict, user_wins: list[dict]) -> discord.Embed:
    # Leader role colors
    LEADER_ROLE_COLORS = {
        "trial": "#a6d7ff",
        "official": "#3fa5ff",
        "experienced": "#2881cf",
        "leaderboard": "#1566ad",
        "master": "#0f497c"
    }

    ON_BREAK_COLOR = "#e74c3c"
    DEFAULT_LEADER_COLOR = "#3fa5ff"  # official

    # Determine embed color based on on_break_since status or leader_tier
    on_break_since = leader_data.get("on_break_since", 0)
    if on_break_since != 0:
        embed_color = ON_BREAK_COLOR
    else:
        leader_tier = leader_data.get("leader_tier", "").lower()
        embed_color = LEADER_ROLE_COLORS.get(leader_tier, DEFAULT_LEADER_COLOR)
    
    embed = _get_base_embed(
        title="👤 Leader Profile",
        module="Leaders",
        color=embed_color
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
    on_break_since = leader_data.get("on_break_since", 0)

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

    # Build activity value with on break status if applicable
    activity_lines = [
        f"**Last Win:** {f'<t:{int(last_win)}:R>' if last_win else 'N/A'}",
        f"**Last Host:** {f'<t:{int(last_host)}:R>' if last_host else 'N/A'}",
        f"**Promoted At:** <t:{int(promoted_at)}:R>" if promoted_at else "N/A",
    ]
    if on_break_since != 0:
        activity_lines.append(f"**On Break Since:** <t:{int(on_break_since)}:R>")
    
    embed.add_field(
        name="⏱️ Last Activity",
        value="\n".join(activity_lines),
        inline=True
    )

    print(f"[DEBUG] [{PRINT_PREFIX}] Created leader info embed for user_id {leader_data.get('user_id', 'N/A')}")
    return embed
