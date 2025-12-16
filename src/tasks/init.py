# src\tasks\init.py
# Sets up and starts scheduled tasks for the bot.

PRINT_PREFIX = "TASKS"


def init_tasks():
    print(f"[INFO] [{PRINT_PREFIX}] Initializing scheduled tasks.")
    tasks = [] # List of tuples (task_function, name)

    for task in tasks:
        task_function, name = task
        print(f"[INFO] [{PRINT_PREFIX}] Starting task: {name}")
        task_function.start()

    print(f"[INFO] [{PRINT_PREFIX}] Scheduled tasks initialized.")