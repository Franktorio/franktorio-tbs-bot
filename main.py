# main.py
# Entry point for the application.

import src.logging as logging # Automatically sets up logging when imported

PRINT_PREFIX = "MAIN"

# Standard library imports
import datetime
import threading

# Local imports
from config.env_vars import BOT_TOKEN, HOME_GUILD_ID, ALLOWED_GUILDS
from src.bot import bot
from src.tasks import init_tasks
from src.db.connections import init_databases
from src.api.api import run_api

print(f"[WARNING] [{PRINT_PREFIX}] Starting application. Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")

print(f"[INFO] [{PRINT_PREFIX}] Initializing databases")
init_databases()
print(f"[INFO] [{PRINT_PREFIX}] Databases initialized successfully")

api_thread = threading.Thread(target=run_api, daemon=True)
api_thread.start()
print(f"[INFO] [{PRINT_PREFIX}] Local API server started in background thread")

@bot.event
async def on_ready():

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print startup information
    print("="*50)
    print("[INFO] [MAIN] Bot is online")
    print(f"[INFO] [MAIN] Time: {now} UTC")
    print(f"[INFO] [MAIN] Logged in as: {bot.user} (ID: {bot.user.id})")
    print(f"[INFO] [MAIN] Connected to {len(bot.guilds)} guild(s)")
    print("="*50)
    
    # Start background tasks
    init_tasks()
    
    # Sync command tree
    print("[INFO] [MAIN] Syncing command tree...")
    try:
        synced = await bot.tree.sync()
        print(f"[INFO] [MAIN] Successfully synced {len(synced)} command(s)")
    except Exception as e:
        print(f"[ERROR] [MAIN] Failed to sync commands: {e}")
        print("[WARNING] [MAIN] Bot will continue running but slash commands may not be available")
    
    # Sync everything to home guild
    home_guild = bot.get_guild(HOME_GUILD_ID)
    if home_guild:
        try:
            synced = await bot.tree.sync(guild=home_guild)
            print(f"[INFO] [{PRINT_PREFIX}] Successfully synced {len(synced)} command(s) to home guild '{home_guild.name}' (ID: {HOME_GUILD_ID})")
        except Exception as e:
            print(f"[ERROR] [{PRINT_PREFIX}] Failed to sync commands to home guild: {e}")
    else:
        print(f"[WARNING] [{PRINT_PREFIX}] Home guild with ID {HOME_GUILD_ID} not found among connected guilds")
    
    # Leave guilds that are not allowed
    allowed = ALLOWED_GUILDS.append(HOME_GUILD_ID)
    for guild in bot.guilds:
        if guild.id not in allowed:
            print(f"[WARNING] [{PRINT_PREFIX}] Bot is in guild '{guild.name}' (ID: {guild.id}) which is not in allowed guilds.")
            await guild.leave()
            print(f"[INFO] [{PRINT_PREFIX}] Left guild '{guild.name}' (ID: {guild.id})")
    
bot.run(BOT_TOKEN)