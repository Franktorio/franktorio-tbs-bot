# src\workers\queue.py
# Worker queue management

PRINT_PREFIX = "WORKER QUEUE"

class WorkerQueue:
    _workers = [] # List to hold worker instances, will be populated later
    _worker_index = 0

    def _get_nearest_running_worker(self) -> object | None:
        """Returns the nearest running worker in the queue."""
        start_index = self._worker_index
        while True:
            worker = self.get_worker(search=False) # Avoid infinite recursion by disabling search
            if worker.running:
                return worker
            if self._worker_index == start_index:
                print(f"[ERROR] [{PRINT_PREFIX}] No running workers available.")
                return None

    def get_worker(self, search: bool = False) -> object | None:
        """Returns the next worker in the queue using round-robin scheduling."""
        if self._worker_index >= len(self._workers):
            self._worker_index = 0
        worker = self._workers[self._worker_index]
        if not worker.running and search:
            print(f"[WARN] [{PRINT_PREFIX}] Worker {worker.index} is not running.")
            worker = self._get_nearest_running_worker()
            if worker is None:
                return None
        self._worker_index += 1
        print(f"[DEBUG] [{PRINT_PREFIX}] Assigned Worker {worker.index} to task.")
        return worker
    
    def add_worker(self, worker: object) -> int:
        """Adds a worker to the worker queue.
        Returns the index of the added worker.
        """
        self._workers.append(worker)
        print(f"[DEBUG] [{PRINT_PREFIX}] Added Worker {len(self._workers) - 1} to the queue.")
        return len(self._workers) - 1
