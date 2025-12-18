# main.py
# Entry point for the application.

import src.logging as logging # Automatically sets up logging when imported

PRINT_PREFIX = "MAIN"

# Standard library imports
import datetime

# Local imports
from config.env_vars import BOT_TOKEN
from src.bot import bot
from src.tasks import init_tasks
from src.db.connections import init_databases

print(f"[WARNING] [{PRINT_PREFIX}] Starting application. Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

@bot.event
async def on_ready():

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print startup information
    print("="*50)
    print("[INFO] [MAIN] Bot is online")
    print(f"[INFO] [MAIN] Time: {now}")
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
    
bot.run(BOT_TOKEN)