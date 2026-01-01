# src\events\on_member_join.py
# Event Handler - Handles actions when a member joins a guild

PRINT_PREFIX = "EVENTS - MEMBER JOIN"

# Local imports
from bot import bot
from src.db.bot_db import users

@bot.event
async def on_member_join(member):
    """
    Event handler for when a member joins a guild.
    
    Adds the member to the users database if they do not already exist.
    """

    user_id = str(member.id)
    
    user = users.get_user(user_id)
    if user is None:
        users.add_user(user_id)
        print(f"[INFO] [{PRINT_PREFIX}] Added new user with ID {user_id} to the database.")
        return
    else:
        print(f"[DEBUG] [{PRINT_PREFIX}] User with ID {user_id} already exists in the database.")
