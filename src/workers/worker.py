# src\workers\worker.py
# Worker object

PRINT_PREFIX = "WORKER"

# Standard library imports
import threading
import asyncio

# Third-party imports
import concurrent
import time
import discord
from discord.ext import commands

from . import WORKER_QUEUE
from . import events as worker_events

class Worker:
    def __init__(self, token):
        self.token = token
        self.ptoken =  "..." + token[-5:]  # Partial token for logging
        self.bot_instance = None  # Placeholder for bot instance
        self.thread = None # Placeholder for worker thread
        self.index = None # Will be set when added to WORKER_QUEUE
        self.running = False

        self.tasks_performed = 0

    def __str__(self):
        return f"Worker#{self.index}: token={self.ptoken}, running={self.running}"

    def _get_bot_instance(self) -> None:
        """Creates and sets up the bot instance for this worker."""
        # Create intents with ALL intents enabled
        intents = discord.Intents.all()

        bot = commands.Bot(
            command_prefix=f"worker{self.index}=",  # Default prefix, can be changed later
            intents=intents
        )
        self.bot_instance = bot

    def _run(self):
        """Main worker loop."""
        self._get_bot_instance()
        worker_events.start(self)
        self.running = True
        self.bot_instance.run(self.token)

    def start(self):
        """Starts the worker thread."""
        self.index = WORKER_QUEUE.add_worker(self)
        if self.thread is None:
            self.thread = threading.Thread(target=self._run)
            self.thread.start()
            print(f"[INFO] [{PRINT_PREFIX}] Worker {self.index} with token {self.ptoken} started.")

    def execute_task(self, task_function: callable, task_timeout: int | None = 5, *args, **kwargs) -> bool:
        """
        Executes a task function using this worker's bot instance.
        Passes the bot instance as the first argument to the task function.

        Args:
            task_function (callable): The coroutine function to execute, must be an async function.
            task_timeout (int | None = 5):
                None: Wait indefinitely for task completion.
                0: Do not wait for task completion, return immediately. (fire-and-forget)
                >0: Wait up to N seconds for task completion.
            *args: Positional arguments to pass to the task function.
            **kwargs: Keyword arguments to pass to the task function.

        Returns:
            bool: True if the task completed successfully or if task_timeout was set to 0, False if it timed out or raised an exception.
        """
        if not self.running:
            print(f"[ERROR] [{PRINT_PREFIX}] Worker {self.index} is not running. Cannot execute task.")
            return False
        new_args = (self.bot_instance, ) + args # Prepend bot_instance to args
        result = asyncio.run_coroutine_threadsafe(task_function(*new_args, **kwargs), self.bot_instance.loop)
        print(f"[DEBUG] [{PRINT_PREFIX}] Worker {self.index} executing task {task_function.__name__}.")
        try:
            if task_timeout == 0:
                self.tasks_performed += 1
                return True
            result.result(timeout=task_timeout)
            print(f"[DEBUG] [{PRINT_PREFIX}] Worker {self.index} completed task {task_function.__name__}.")
            self.tasks_performed += 1
            return True
        except concurrent.futures.TimeoutError:
            print(f"[ERROR] [{PRINT_PREFIX}] Worker {self.index} task {task_function.__name__} timed out.")
            return False
        except Exception as e:
            print(f"[ERROR] [{PRINT_PREFIX}] Worker {self.index} task {task_function.__name__} raised an exception: {e}")
            return False
        
    def execute_task_return(self, task_function: callable, task_timeout: int | None = 5, *args, **kwargs) -> any:
        """
        Executes a task function using this worker's bot instance and returns the result.
        Passes the bot instance as the first argument to the task function.

        Args:
            task_function (callable): The coroutine function to execute, must be an async function.
            task_timeout (int | None = 5):
                None: Wait indefinitely for task completion.
                0: Do not wait for task completion, return immediately. (fire-and-forget)
                >0: Wait up to N seconds for task completion.
            *args: Positional arguments to pass to the task function.
            **kwargs: Keyword arguments to pass to the task function.

        Returns:
            any: The result of the task function if completed successfully, None if it timed out or raised an exception.
        """
        if not self.running:
            print(f"[ERROR] [{PRINT_PREFIX}] Worker {self.index} is not running. Cannot execute task.")
            return None
        new_args = (self.bot_instance, ) + args # Prepend bot_instance to args
        result = asyncio.run_coroutine_threadsafe(task_function(*new_args, **kwargs), self.bot_instance.loop)
        print(f"[DEBUG] [{PRINT_PREFIX}] Worker {self.index} executing task {task_function.__name__}.")
        try:
            if task_timeout == 0:
                self.tasks_performed += 1
                return None
            res = result.result(timeout=task_timeout)
            print(f"[DEBUG] [{PRINT_PREFIX}] Worker {self.index} completed task {task_function.__name__}.")
            self.tasks_performed += 1
            return res
        except concurrent.futures.TimeoutError:
            print(f"[ERROR] [{PRINT_PREFIX}] Worker {self.index} task {task_function.__name__} timed out.")
            return None
        except Exception as e:
            print(f"[ERROR] [{PRINT_PREFIX}] Worker {self.index} task {task_function.__name__} raised an exception: {e}")
            return None

def start_workers(worker_tokens: list[str]) -> None:
    """Starts all workers in the global WORKER_QUEUE."""
    for token in worker_tokens:
        worker = Worker(token)
        worker.start()
        
        # Artificial small delay to stagger worker startups
        time.sleep(0.5)
    print(f"[INFO] [{PRINT_PREFIX}] All workers started.")