import time
import psutil
import logging
from functools import wraps
from typing import Dict, Any, Callable
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor application performance metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def record_metric(self, metric_name: str, value: float):
        """Record a performance metric"""
        with self.lock:
            self.metrics[metric_name].append({
                'value': value,
                'timestamp': time.time()
            })
    
    def get_average_metric(self, metric_name: str) -> float:
        """Get average value for a metric"""
        with self.lock:
            if metric_name not in self.metrics:
                return 0.0
            values = [m['value'] for m in self.metrics[metric_name]]
            return sum(values) / len(values) if values else 0.0
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').percent
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            'uptime': time.time() - self.start_time,
            'total_requests': len(self.metrics.get('request_time', [])),
            'avg_request_time': self.get_average_metric('request_time'),
            'avg_file_processing_time': self.get_average_metric('file_processing_time'),
            'avg_pdf_generation_time': self.get_average_metric('pdf_generation_time'),
            'system_stats': self.get_system_stats()
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(metric_name: str):
    """Decorator to monitor function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                performance_monitor.record_metric(metric_name, execution_time)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                performance_monitor.record_metric(f"{metric_name}_error", execution_time)
                raise
        return wrapper
    return decorator

def log_performance_metrics():
    """Log current performance metrics"""
    summary = performance_monitor.get_performance_summary()
    logger.info(f"Performance Summary: {summary}")

# Performance monitoring functions
def start_performance_logging(interval: int = 300):
    """Start periodic performance logging"""
    def log_periodically():
        while True:
            log_performance_metrics()
            time.sleep(interval)
    
    thread = threading.Thread(target=log_periodically, daemon=True)
    thread.start()
    return thread

def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage in MB"""
    memory = psutil.virtual_memory()
    return {
        'total_mb': memory.total / (1024 * 1024),
        'available_mb': memory.available / (1024 * 1024),
        'used_mb': memory.used / (1024 * 1024),
        'percent': memory.percent
    }

def optimize_memory():
    """Attempt to optimize memory usage"""
    import gc
    gc.collect()
    logger.info("Memory optimization completed")

if __name__ == "__main__":
    # Test performance monitoring
    logging.basicConfig(level=logging.INFO)
    
    @monitor_performance('test_function')
    def test_function():
        time.sleep(0.1)
        return "test"
    
    # Run some tests
    for i in range(5):
        test_function()
    
    # Print summary
    summary = performance_monitor.get_performance_summary()
    print(f"Performance Summary: {summary}")
