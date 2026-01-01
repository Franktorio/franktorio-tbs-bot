# src\tasks\build_user_db.py
# Builds or updates the user database.

PRINT_PREFIX = "TASKS - BUILD USER DB"

# Local imports
from src.db.bot_db.users import add_if_not_exists
from src.bot import bot
from config.env_vars import HOME_GUILD_ID


def build_user_db():
    """Builds or updates the user database."""
    print(f"[INFO] [{PRINT_PREFIX}] Building user database.")
    guild = bot.get_guild(HOME_GUILD_ID)
    if guild is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Home guild with ID {HOME_GUILD_ID} not found.")
        return
    members = guild.members
    total_members = len(members)
    new_added = 0
    print(f"[INFO] [{PRINT_PREFIX}] Found {total_members} members in home guild '{guild.name}' (ID: {HOME_GUILD_ID}).")
    for index, member in enumerate(members, start=1):
        user_id = member.id
        added = add_if_not_exists(user_id)
        if added:
            new_added += 1
            print(f"[DEBUG] [{PRINT_PREFIX}] Added user {user_id} to database ({index}/{total_members}).")
        else:
            print(f"[DEBUG] [{PRINT_PREFIX}] User {user_id} already exists in database ({index}/{total_members}).")
    print(f"[INFO] [{PRINT_PREFIX}] User database build/update completed. Total new users added: {new_added}.")







