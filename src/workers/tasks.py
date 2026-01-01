# src\workers\tasks.py
# Worker background tasks

# Local imports
from typing import Any

# Third-party imports
import discord
from discord.ext import tasks


def start(worker: Any) -> None:
    """Initializes and starts all background tasks for the worker bot instance.
    
    Args:
        worker: The worker instance that owns this bot.
    """

    bot = worker.bot_instance
    
    @tasks.loop(seconds=10)
    async def update_tasks_performed():
        """Background task to update tasks performed count."""
        await bot.change_presence(
            activity=discord.Game(name=f"worker{worker.index}= | Tasks performed: {worker.tasks_performed}")
        )
    
    bot.update_tasks_performed = update_tasks_performed
    bot.update_tasks_performed.start()