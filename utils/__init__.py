
"""
Utility functions
"""

from .file_handler import FileHandler

try:
    from .visualization import Visualizer
    __all__ = ['FileHandler', 'Visualizer']
except ImportError:
    __all__ = ['FileHandler']

# New utilities - Performance & Optimization
try:
    from .cache_manager import CacheManager, get_cache_manager
    __all__.extend(['CacheManager', 'get_cache_manager'])
except ImportError:
    pass

try:
    from .performance_monitor import PerformanceMonitor, get_performance_monitor
    __all__.extend(['PerformanceMonitor', 'get_performance_monitor'])
except ImportError:
    pass

try:
    from .optimized_ocr import OptimizedOCR
    __all__.extend(['OptimizedOCR'])
except ImportError:
    pass

try:
    from .async_tasks import AsyncTaskManager, AsyncTask, TaskStatus, get_task_manager
    __all__.extend(['AsyncTaskManager', 'AsyncTask', 'TaskStatus', 'get_task_manager'])
except ImportError:
    pass

try:
    from .error_recovery import ErrorRecovery, handle_extraction_error
    __all__.extend(['ErrorRecovery', 'handle_extraction_error'])
except ImportError:
    pass
