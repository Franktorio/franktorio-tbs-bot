# src\core\__init__.py
# Core module initialization


# This module contains centralized core functionalities for the application.
# The purpose of this is to streamline imports and provide a single access point
# for core components used across different parts of the application.

# It wraps core discord actions like timeouts, message handling, voice channel handling, etc in for use with both 
# the master and worker bots.

# Basically handles the backend logic that the user doesn't see, allowing the master bot to only focus on user interaction.
# (avoid rate limits by offloading tasks to worker bots)
# Example:

# worker.execute_task will automatically pass down the bot instance to the function being executed as the first argument.
# additionally, by default the task will timeout (and return false) after 5 seconds but it can be changed by passing a kwarg "timeout" to execute_task
# (e.g. worker.execute_task(func, arg1, arg2, timeout=10) to set timeout to 10 seconds)
# If 0 is passed, it will be a fire-and-forget task and will not wait for any result, meaning no success/failure feedback.
# If None is passed, it will wait indefinitely for the task to complete.

# This allows the same function to be used with both the worker bot and the master bot seamlessly.
# WORKER_QUEUE.get_worker() will return a worker bot in round robin fashion to distribute the load evenly, does not guarantee
# that the worker isn't busy though, rate limits may still occur if all workers are busy.

from . import channels # channel related core functionalities (channel perms, voice channel handling, message deleting, etc)
from . import users # user related core functionalities (timeouts, bans, mutes, deafens, etc)