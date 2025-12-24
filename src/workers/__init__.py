# src\workers\__init__.py

from .queue import WorkerQueue
    
WORKER_QUEUE = WorkerQueue() # Global worker queue instance