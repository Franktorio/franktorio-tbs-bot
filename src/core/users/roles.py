# src\core\users\roles.py
# User roles related core functionalities (add, remove, edit, etc)

PRINT_PREFIX = "CORE - USERS - ROLES"

# Third-party imports
import discord

# Local imports
from config.env_vars import HOME_GUILD_ID
from src.core.decorators import offload_fallback
from src.core.fetching import get_guild_or_fetch, get_member_or_fetch, get_role_or_fetch

@offload_fallback(PRINT_PREFIX)
async def add_role_to_user(bot, /, user_id: int, role_id: int, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Adds a role to a user.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        user_id (int): The ID of the user to add the role to.
        role_id (int): The ID of the role to add.
        reason (str): Reason for adding the role.
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

    role = await get_role_or_fetch(guild, role_id)
    if role is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Role with ID {role_id} not found in guild {HOME_GUILD_ID}.")
        return False

    try:
        await member.add_roles(role, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Added role {role_id} to user {user_id} in guild {HOME_GUILD_ID}.")
        return True
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to add role {role_id} to user {user_id} in guild {HOME_GUILD_ID}: {e}")
        return False

@offload_fallback(PRINT_PREFIX)
async def remove_role_from_user(bot, /, user_id: int, role_id: int, reason: str = "No reason provided", task_timeout: int = 10) -> bool:
    """
    Removes a role from a user.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        user_id (int): The ID of the user to remove the role from.
        role_id (int): The ID of the role to remove.
        reason (str): Reason for removing the role.
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

    role = await get_role_or_fetch(guild, role_id)
    if role is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Role with ID {role_id} not found in guild {HOME_GUILD_ID}.")
        return False

    try:
        await member.remove_roles(role, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Removed role {role_id} from user {user_id} in guild {HOME_GUILD_ID}.")
        return True
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove role {role_id} from user {user_id} in guild {HOME_GUILD_ID}: {e}")
        return False

@offload_fallback(PRINT_PREFIX)
async def edit_user_roles(bot, /, user_id: int, new_roles: list[discord.Role], reason: str = "No reason provided", task_timeout: int = 15) -> bool:
    """
    Edits a user's roles to match the provided list of roles.
    
    Args:
        bot: The bot instance to use. (auto offloaded to worker or master bot, don't pass manually)
        user_id (int): The ID of the user to edit roles for.
        new_roles (list[discord.Role]): List of roles to set for the user.
        reason (str): Reason for editing the roles.
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
        await member.edit(roles=new_roles, reason=reason)
        print(f"[INFO] [{PRINT_PREFIX}] Edited roles for user {user_id} in guild {HOME_GUILD_ID}.")
        return True
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Failed to edit roles for user {user_id} in guild {HOME_GUILD_ID}: {e}")
        return False
    
