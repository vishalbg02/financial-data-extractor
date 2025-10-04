"""
Async task manager for background processing of large files in Streamlit.
"""
import threading
import logging
from typing import Callable, Any, Dict, Optional
from queue import Queue
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)


class TaskStatus:
    """Status of an async task"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AsyncTask:
    """Represents an async task"""
    
    def __init__(self, task_id: str, task_fn: Callable, *args, **kwargs):
        self.task_id = task_id
        self.task_fn = task_fn
        self.args = args
        self.kwargs = kwargs
        self.status = TaskStatus.QUEUED
        self.progress = 0
        self.total = 100
        self.message = "Waiting to start..."
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.cancel_requested = False
    
    def update_progress(self, current: int, total: int, message: str = None):
        """Update task progress"""
        self.progress = current
        self.total = total
        if message:
            self.message = message
    
    def request_cancel(self):
        """Request cancellation of this task"""
        self.cancel_requested = True
        logger.info(f"Cancellation requested for task {self.task_id}")


class AsyncTaskManager:
    """Manages background tasks for Streamlit apps"""
    
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self.tasks: Dict[str, AsyncTask] = {}
        self.task_queue = Queue()
        self.workers = []
        self.running = False
        self._lock = threading.Lock()
    
    def start(self):
        """Start the task manager"""
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"AsyncTaskManager started with {self.max_workers} workers")
    
    def stop(self):
        """Stop the task manager"""
        self.running = False
        logger.info("AsyncTaskManager stopped")
    
    def _worker(self):
        """Worker thread that processes tasks"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    continue
                
                # Check if task was cancelled before starting
                if task.cancel_requested:
                    task.status = TaskStatus.CANCELLED
                    task.end_time = datetime.now()
                    continue
                
                # Execute task
                with self._lock:
                    task.status = TaskStatus.RUNNING
                    task.start_time = datetime.now()
                
                try:
                    # Set up progress callback
                    def progress_callback(current, total, message=None):
                        task.update_progress(current, total, message)
                    
                    # Add progress callback to kwargs if task accepts it
                    if 'progress_callback' in task.kwargs or len(task.args) > 0:
                        task.kwargs['progress_callback'] = progress_callback
                    
                    # Run the task
                    result = task.task_fn(*task.args, **task.kwargs)
                    
                    # Check if cancelled during execution
                    if task.cancel_requested:
                        task.status = TaskStatus.CANCELLED
                    else:
                        task.result = result
                        task.status = TaskStatus.COMPLETED
                    
                except Exception as e:
                    logger.error(f"Task {task.task_id} failed: {str(e)}\n{traceback.format_exc()}")
                    task.error = str(e)
                    task.status = TaskStatus.FAILED
                
                finally:
                    task.end_time = datetime.now()
                    self.task_queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                continue
    
    def submit_task(self, task_id: str, task_fn: Callable, *args, **kwargs) -> AsyncTask:
        """
        Submit a new task for background processing
        
        Args:
            task_id: Unique identifier for the task
            task_fn: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        
        Returns:
            AsyncTask object for tracking progress
        """
        task = AsyncTask(task_id, task_fn, *args, **kwargs)
        
        with self._lock:
            self.tasks[task_id] = task
        
        self.task_queue.put(task)
        logger.info(f"Task {task_id} submitted")
        
        return task
    
    def get_task(self, task_id: str) -> Optional[AsyncTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Request cancellation of a task
        
        Returns:
            True if cancellation was requested, False if task not found
        """
        task = self.get_task(task_id)
        if task:
            task.request_cancel()
            return True
        return False
    
    def get_all_tasks(self) -> Dict[str, AsyncTask]:
        """Get all tasks"""
        return self.tasks.copy()
    
    def clear_completed_tasks(self):
        """Remove completed tasks from memory"""
        with self._lock:
            to_remove = [
                task_id for task_id, task in self.tasks.items()
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            ]
            for task_id in to_remove:
                del self.tasks[task_id]
        
        logger.info(f"Cleared {len(to_remove)} completed tasks")


# Global task manager instance
_global_task_manager = None


def get_task_manager() -> AsyncTaskManager:
    """Get or create global task manager"""
    global _global_task_manager
    if _global_task_manager is None:
        _global_task_manager = AsyncTaskManager()
        _global_task_manager.start()
    return _global_task_manager
