# src\tasks\init.py
# Sets up and starts scheduled tasks for the bot.

PRINT_PREFIX = "TASKS"

from src.tasks.build_user_db import build_user_db

def init_tasks():
    print(f"[INFO] [{PRINT_PREFIX}] Initializing scheduled tasks.")
    tasks: list[tuple[callable, str]] = []
    startup_tasks: list[tuple[callable, str]] = [
        (build_user_db, "Build User Database"),
    ]

    for task in tasks:
        task_function, name = task
        print(f"[INFO] [{PRINT_PREFIX}] Starting task: {name}")
        task_function.start()
        
    for task in startup_tasks:
        task_function, name = task
        print(f"[INFO] [{PRINT_PREFIX}] Running startup task: {name}")
        task_function()

    print(f"[INFO] [{PRINT_PREFIX}] Scheduled tasks initialized.")