# src\logging.py
# Overrides the built-in print function to log messages to a file with timestamps.
# Also implements automatic log rotation at midnight, keeping logs for 7 days.

import builtins
import os
import datetime
import threading
from config.env_vars import DEBUG_ENABLED

PRINT_PREFIX = "LOG MANAGER"

TO_SKIP = [
    "self._context.run(self._callback, *self._args)", # Spammy debug logs that are not useful
    "TypeError: 'NoneType' object is not callable", # Recurring error that clutters logs
    "Traceback (most recent call last):" # Recurring error that spams logs
]

# Reference to the original print function
original_print = builtins.print

os.makedirs("logs", exist_ok=True)
os.makedirs("logs/rotated_logs", exist_ok=True)

# Create and/or open the bot logs file in append mode
bot_logs = open("logs/bot_logs.log", "a")

log_queue = [] # Hold messages when logs are closed for rotation

log_lock = threading.Lock()

def logging_print(*args, **kwargs):
    """Custom print function for logging purposes."""
    global DEBUG_ENABLED
    # Skip debug prints if DEBUG_ENABLED is False
    for arg in args:
        if not DEBUG_ENABLED and "[DEBUG]" in str(arg):
            return
        for skip_str in TO_SKIP:
            if skip_str in str(arg):
                return
    
    original_print(*args, **kwargs)  # Print to console

    text_output = ""
    for arg in args:
        text_output += str(arg) + " "
    
    bot_log = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text_output}\n"
    with log_lock:
        bot_logs.write(bot_log)
        bot_logs.flush() # Force write to file
    
def _rotate_log():
    """Rotate the log file by closing the current one and opening a new one."""
    global bot_logs
    bot_logs = open("logs/bot_logs.log", "a")

def auto_rotate_log():
    """
    Automatically rotate the log file at midnight every day.
    
    Stores up to 7 days of logs by renaming old log files.
    1. bot_logs.log -> bot_logs_YYYYMMDD.log
    2. bot_logs_YYYYMMDD.log (7 days old) is deleted
    3. New bot_logs.log is created
    4. bot_logs.log is renamed to bot_logs_YYYYMMDD.log
    5. New bot_logs.log is created
    6. Repeat daily at midnight

    """
    global bot_logs

    while True:
        now = datetime.datetime.now()
        next_midnight = (now + datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Wait until midnight
        sleep_duration = (next_midnight - now).total_seconds()
        log_queue.append(f"[INFO] [{PRINT_PREFIX}] Next log rotation scheduled in {sleep_duration} seconds.")
        threading.Event().wait(sleep_duration)
        log_queue.append(f"[INFO] [{PRINT_PREFIX}] Rotating log file.")

        # Rotate the log file
        now = datetime.datetime.now()
        with log_lock:
            bot_logs.close()

            date_suffix = now.strftime("%Y%m%d")

            try:
                os.rename("logs/bot_logs.log", f"logs/rotated_logs/bot_logs_{date_suffix}.log")
                log_queue.append(f"[INFO] [{PRINT_PREFIX}] Log file rotated to bot_logs_{date_suffix}.log")
            except FileNotFoundError:
                log_queue.append(f"[WARNING] [{PRINT_PREFIX}] No log file to rotate.")
                pass

            # Delete logs older than 7 days
            old_date_suffix = (now - datetime.timedelta(days=7)).strftime("%Y%m%d")
            old_log_path = f"logs/rotated_logs/bot_logs_{old_date_suffix}.log"
            if os.path.exists(old_log_path):
                log_queue.append(f"[INFO] [{PRINT_PREFIX}] Deleting old log file: bot_logs_{old_date_suffix}.log")
                os.remove(old_log_path)
            else:
                log_queue.append(f"[DEBUG] [{PRINT_PREFIX}] No old log file to delete for date: {old_date_suffix}")
        
            # Reopen new active log
            _rotate_log()
        for log_msg in log_queue:
            print(log_msg)
        log_queue.clear()
        
        print(f"[INFO] [{PRINT_PREFIX}] Log rotation complete.")
        for _ in range(5):
            print("#"*70)


# Override the built-in print function
builtins.print = logging_print

# Start the auto log rotation in a separate daemon thread
log_rotation_thread = threading.Thread(target=auto_rotate_log, daemon=True)
log_rotation_thread.start()