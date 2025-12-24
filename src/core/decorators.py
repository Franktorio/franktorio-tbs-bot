# src\core\decorators.py
# Core decorators to automatically offload work to workers with master bot fallback

# Standard library imports
import asyncio
from functools import wraps

# Local imports
from src.workers import WORKER_QUEUE
from src.bot import bot as master_bot

def offload_fallback(print_prefix: str):
    """
    Decorator to offload a function to an available worker.
    If no worker is available or offloading fails, falls back to executing
    the function using the master bot.

    Args:
        print_prefix (str): Prefix for logging.
    Returns:
        callable: Decorated function.
    """
    def decorator(func: callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get an available worker
            worker = WORKER_QUEUE.get_available_worker()
            loop = asyncio.get_running_loop()

            success = False
            
            # Extract task_timeout from kwargs to pass to execute_task
            task_timeout = kwargs.pop('task_timeout', None)

            if worker:
                try:
                    # Offload the task to the worker
                    success = await loop.run_in_executor(
                        None,
                        worker.execute_task,
                        func,
                        *args,
                        task_timeout=task_timeout,  # Pass task_timeout as keyword arg
                        **kwargs
                    )
                except Exception as e:
                    print(f"[ERROR] [{print_prefix}] Offloading to worker failed: {e}")

            if not success:
                print(f"[WARNING] [{print_prefix}] Offloading to worker failed or no worker available. Falling back to master bot.")
                await func(master_bot, *args, **kwargs)
                success = True
            
            return success
        return wrapper
    return decorator

def offload_fallback_return(print_prefix: str):
    """
    Decorator to offload a function to an available worker and return its result.
    If no worker is available or offloading fails, falls back to executing
    the function using the master bot.

    Args:
        print_prefix (str): Prefix for logging.
    Returns:
        callable: Decorated function.
    """
    def decorator(func: callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get an available worker
            worker = WORKER_QUEUE.get_available_worker()
            loop = asyncio.get_running_loop()

            result = None
            
            # Extract task_timeout from kwargs to pass to execute_task_return
            task_timeout = kwargs.pop('task_timeout', None)

            if worker:
                try:
                    # Offload the task to the worker
                    result = await loop.run_in_executor(
                        None,
                        worker.execute_task_return,
                        func,
                        *args,
                        task_timeout=task_timeout,  # Pass task_timeout as keyword arg
                        **kwargs
                    )
                except Exception as e:
                    print(f"[ERROR] [{print_prefix}] Offloading to worker failed: {e}")

            if result is None:
                print(f"[WARNING] [{print_prefix}] Offloading to worker failed or no worker available. Falling back to master bot.")
                result = await func(master_bot, *args, **kwargs)
            
            return result
        return wrapper
    return decorator