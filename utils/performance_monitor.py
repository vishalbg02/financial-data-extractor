"""
Performance monitoring utilities for tracking resource usage and execution time.
"""
import time
import psutil
import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor performance and resource usage"""
    
    def __init__(self):
        self.metrics = {}
        self.process = psutil.Process()
    
    @contextmanager
    def measure(self, operation_name: str):
        """Context manager to measure operation performance"""
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        logger.info(f"Starting: {operation_name}")
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            
            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            
            self.metrics[operation_name] = {
                'duration': duration,
                'start_time': datetime.fromtimestamp(start_time),
                'end_time': datetime.fromtimestamp(end_time),
                'memory_delta_mb': memory_delta,
                'peak_memory_mb': end_memory
            }
            
            logger.info(
                f"Completed: {operation_name} "
                f"(Duration: {duration:.2f}s, Memory: {memory_delta:+.1f}MB)"
            )
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / 1024 / 1024,
                'memory_total_mb': memory.total / 1024 / 1024,
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / 1024 / 1024 / 1024
            }
        except Exception as e:
            logger.warning(f"Could not get system stats: {e}")
            return {}
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all measured metrics"""
        total_duration = sum(m['duration'] for m in self.metrics.values())
        total_memory = sum(m['memory_delta_mb'] for m in self.metrics.values())
        
        return {
            'operations': len(self.metrics),
            'total_duration': total_duration,
            'total_memory_delta_mb': total_memory,
            'operations_detail': self.metrics,
            'system_stats': self.get_system_stats()
        }
    
    def reset(self):
        """Reset metrics"""
        self.metrics.clear()
    
    def check_resources(self, min_memory_mb: float = 500) -> Dict[str, Any]:
        """Check if system has enough resources"""
        stats = self.get_system_stats()
        
        warnings = []
        if stats.get('memory_available_mb', 0) < min_memory_mb:
            warnings.append(f"Low memory: {stats['memory_available_mb']:.0f}MB available")
        
        if stats.get('cpu_percent', 0) > 90:
            warnings.append(f"High CPU usage: {stats['cpu_percent']:.0f}%")
        
        if stats.get('disk_percent', 0) > 90:
            warnings.append(f"Low disk space: {stats['disk_percent']:.0f}% used")
        
        return {
            'has_sufficient_resources': len(warnings) == 0,
            'warnings': warnings,
            'stats': stats
        }


# Global performance monitor
_global_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor
