# Quick Start Guide - Performance Optimizations

## For Developers

### Using the Cache System

```python
from utils.cache_manager import get_cache_manager

# Get cache manager instance
cache = get_cache_manager()

# Store data
cache.set("my_key", {"data": "value"})

# Retrieve data
data = cache.get("my_key")

# Clear cache
cache.clear_all()
```

### Using the Performance Monitor

```python
from utils.performance_monitor import get_performance_monitor

monitor = get_performance_monitor()

# Measure operation performance
with monitor.measure("my_operation"):
    # Your code here
    process_data()

# Get metrics
summary = monitor.get_metrics_summary()
print(f"Operation took: {summary['total_duration']}s")

# Check system resources
stats = monitor.get_system_stats()
print(f"CPU: {stats['cpu_percent']}%")
print(f"Memory: {stats['memory_percent']}%")
```

### Using Optimized OCR

```python
from utils.optimized_ocr import OptimizedOCR
import numpy as np

# Initialize (with caching and fallback)
ocr = OptimizedOCR(use_gpu=False, enable_cache=True, max_workers=4)

# Process single image
text = ocr.extract_text_single(image_array)

# Process multiple images in parallel
images = [img1, img2, img3]
texts = ocr.extract_text_batch(images, progress_callback=my_callback)

# With automatic retry
text = ocr.extract_with_retry(image, max_retries=3)
```

### Using Async Tasks

```python
from utils.async_tasks import get_task_manager

# Get task manager
manager = get_task_manager()

# Submit background task
def long_running_task(file_path):
    # Your processing code
    return result

task = manager.submit_task("process_pdf", long_running_task, "file.pdf")

# Check progress
print(f"Status: {task.status}")
print(f"Progress: {task.progress}/{task.total}")

# Cancel if needed
manager.cancel_task("process_pdf")

# Get result when complete
if task.status == "completed":
    result = task.result
```

### Using Error Recovery

```python
from utils.error_recovery import ErrorRecovery, handle_extraction_error

try:
    # Your code that might fail
    extract_data(file)
except Exception as e:
    # Get recovery suggestions
    analysis = ErrorRecovery.analyze_error(e)
    
    print(f"Error Category: {analysis['category']}")
    print(f"Severity: {analysis['severity']}")
    
    for suggestion in analysis['suggestions']:
        print(f"  - {suggestion}")
    
    # For file processing specifically
    error_info = handle_extraction_error(e, "myfile.pdf")
    if error_info['can_retry']:
        # Retry the operation
        pass
```

### Using Lazy Loading

```python
from models.ai_model import AIExtractor
from models.embeddings import DocumentEmbedder

# Models won't load until first use
extractor = AIExtractor(lazy_load=True)
embedder = DocumentEmbedder(lazy_load=True)

# First use triggers loading
result = extractor.find_best_match("query", ["candidate1", "candidate2"])
embedding = embedder.embed_text("some text")
```

### Adding Progress Callbacks

```python
from extractors.pdf_extractor import PDFExtractor

def my_progress_callback(operation, current, total):
    print(f"{operation}: {current}/{total}")

extractor = PDFExtractor("file.pdf")
extractor.set_progress_callback(my_progress_callback)
data = extractor.extract()
```

## For Users

### Running the Demo

```bash
python demo_performance.py
```

This will show all optimization features in action.

### Clearing Cache

**Via UI:**
1. Open the app
2. Go to sidebar → Performance Settings
3. Click "Clear Cache"

**Via Command Line:**
```bash
rm -rf data/cache/*
```

### Monitoring Resources

Check the sidebar in the UI under "System Resources" to see:
- CPU usage
- Memory usage
- Available memory
- Resource warnings

### Troubleshooting

**Out of Memory:**
1. Clear cache
2. Process one file at a time
3. Close other applications
4. Check "System Resources" in sidebar

**Slow Processing:**
1. Enable caching (Settings → Performance Settings)
2. Enable parallel processing
3. Check system resources
4. Reduce number of simultaneous files

**OCR Not Working:**
1. Install Tesseract: `sudo apt-get install tesseract-ocr` (Linux)
2. Or EasyOCR: `pip install easyocr`
3. Check error messages for specific issues

## Testing

Run all performance tests:
```bash
python -m unittest tests.test_performance
```

Run specific test:
```bash
python -m unittest tests.test_performance.TestCacheManager
```

## Configuration

### Environment Variables

```bash
# Set cache directory
export CACHE_DIR=/path/to/cache

# Set max workers for parallel processing
export MAX_WORKERS=4
```

### In Code

```python
# Configure cache manager
cache = CacheManager(cache_dir="custom/cache/path")

# Configure OCR
ocr = OptimizedOCR(
    use_gpu=False,
    enable_cache=True,
    max_workers=4
)

# Configure task manager
manager = AsyncTaskManager(max_workers=2)
```

## Best Practices

1. **Always enable caching** for production use
2. **Monitor system resources** when processing large files
3. **Use progress callbacks** for better UX
4. **Handle errors gracefully** with error recovery
5. **Clear cache periodically** to free up disk space
6. **Use lazy loading** for faster startup
7. **Process in batches** for multiple files
8. **Set appropriate worker counts** based on CPU cores

## Performance Tips

1. **For Large PDFs (>50 pages):**
   - Enable caching
   - Use parallel processing
   - Monitor memory usage

2. **For Multiple Files:**
   - Process in batches
   - Use background tasks
   - Monitor progress

3. **For Repeated Processing:**
   - Keep cache enabled
   - Don't clear cache unnecessarily
   - Use same file names

4. **For Limited Resources:**
   - Reduce worker count
   - Disable parallel processing
   - Process one file at a time

## Documentation

- Full documentation: `docs/PERFORMANCE_OPTIMIZATION.md`
- API reference: See docstrings in source files
- Examples: `demo_performance.py`
- Tests: `tests/test_performance.py`

## Support

For issues or questions:
1. Check error messages and recovery suggestions
2. Review logs for detailed information
3. Run demo script to verify installation
4. Check system resources
5. Refer to full documentation
