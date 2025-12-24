# src\workers\events.py
# Worker event listeners

PRINT_PREFIX = "WORKER EVENTS"

# Local imports
from config.env_vars import HOME_GUILD_ID
from src.core.helpers import get_guild_or_fetch


def start(worker):
    """Initializes and registers all event listeners for the worker bot instance.
    
    Args:
        worker: The worker instance that owns this bot.
    """
    from . import tasks as worker_tasks
    
    bot = worker.bot_instance
    
    @bot.event
    async def on_ready():
        print(f"[INFO] [{PRINT_PREFIX}] Worker {worker.index} logged in as {bot.user}.")
        
        # Start background tasks
        worker_tasks.start(worker)

        # Chunk guild members
        guild = await get_guild_or_fetch(bot, HOME_GUILD_ID)
        if guild:
            await guild.chunk()
            print(f"[INFO] [{PRINT_PREFIX}] Worker {worker.index} chunked members for guild {HOME_GUILD_ID}.")
        else:
            print(f"[ERROR] [{PRINT_PREFIX}] Guild with ID {HOME_GUILD_ID} not found for chunking.")
