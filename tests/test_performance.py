"""
Tests for performance optimizations and new utilities.
"""
import unittest
import sys
import tempfile
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCacheManager(unittest.TestCase):
    """Test cache manager functionality"""
    
    def setUp(self):
        from utils.cache_manager import CacheManager
        self.cache_manager = CacheManager(cache_dir=tempfile.mkdtemp())
    
    def test_memory_cache(self):
        """Test memory caching"""
        self.cache_manager.set("test_key", "test_value", memory_only=True)
        value = self.cache_manager.get("test_key", memory_only=True)
        self.assertEqual(value, "test_value")
    
    def test_disk_cache(self):
        """Test disk caching"""
        self.cache_manager.set("disk_key", {"data": "test"}, memory_only=False)
        # Clear memory cache to force disk read
        self.cache_manager.clear_memory()
        value = self.cache_manager.get("disk_key")
        self.assertEqual(value["data"], "test")
    
    def test_cache_invalidation(self):
        """Test cache invalidation"""
        self.cache_manager.set("invalid_key", "test")
        self.cache_manager.invalidate("invalid_key")
        value = self.cache_manager.get("invalid_key")
        self.assertIsNone(value)


class TestPerformanceMonitor(unittest.TestCase):
    """Test performance monitoring"""
    
    def setUp(self):
        from utils.performance_monitor import PerformanceMonitor
        self.monitor = PerformanceMonitor()
    
    def test_measure_context(self):
        """Test performance measurement context manager"""
        with self.monitor.measure("test_operation"):
            # Simulate some work
            import time
            time.sleep(0.1)
        
        self.assertIn("test_operation", self.monitor.metrics)
        self.assertGreater(self.monitor.metrics["test_operation"]["duration"], 0.09)
    
    def test_system_stats(self):
        """Test system statistics retrieval"""
        stats = self.monitor.get_system_stats()
        
        self.assertIn("cpu_percent", stats)
        self.assertIn("memory_percent", stats)
        self.assertIn("memory_available_mb", stats)
    
    def test_resource_check(self):
        """Test resource availability check"""
        result = self.monitor.check_resources(min_memory_mb=1)
        
        self.assertIn("has_sufficient_resources", result)
        self.assertIn("warnings", result)
        self.assertIsInstance(result["warnings"], list)


class TestOptimizedOCR(unittest.TestCase):
    """Test optimized OCR functionality"""
    
    def setUp(self):
        from utils.optimized_ocr import OptimizedOCR
        self.ocr = OptimizedOCR(use_gpu=False, enable_cache=True)
    
    def test_initialization(self):
        """Test OCR engine initialization"""
        stats = self.ocr.get_stats()
        
        self.assertIn("cache_enabled", stats)
        self.assertTrue(stats["cache_enabled"])
        # At least one OCR engine should be available
        self.assertTrue(
            stats["easyocr_available"] or stats["tesseract_available"]
        )
    
    def test_image_preprocessing(self):
        """Test image preprocessing"""
        # Create a simple test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        processed = self.ocr.preprocess_image(test_image)
        
        # Processed image should be grayscale (2D)
        self.assertEqual(len(processed.shape), 2)
    
    def test_extract_text_single(self):
        """Test single image text extraction"""
        # Create a simple white image
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        # This should not crash
        text = self.ocr.extract_text_single(test_image, preprocess=False)
        self.assertIsInstance(text, str)


class TestErrorRecovery(unittest.TestCase):
    """Test error recovery utilities"""
    
    def setUp(self):
        from utils.error_recovery import ErrorRecovery
        self.recovery = ErrorRecovery()
    
    def test_analyze_ocr_error(self):
        """Test OCR error analysis"""
        error = Exception("EasyOCR failed to read text")
        analysis = self.recovery.analyze_error(error)
        
        self.assertEqual(analysis["category"], "OCR")
        self.assertIn("suggestions", analysis)
        self.assertGreater(len(analysis["suggestions"]), 0)
    
    def test_analyze_memory_error(self):
        """Test memory error analysis"""
        error = MemoryError("Out of memory")
        analysis = self.recovery.analyze_error(error)
        
        self.assertEqual(analysis["category"], "Memory")
        self.assertEqual(analysis["severity"], "critical")
    
    def test_format_error_message(self):
        """Test error message formatting"""
        error = Exception("Test error")
        analysis = self.recovery.analyze_error(error)
        formatted = self.recovery.format_error_message(analysis)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("Error", formatted)
        self.assertIn("Suggestions", formatted)


class TestAsyncTasks(unittest.TestCase):
    """Test async task manager"""
    
    def setUp(self):
        from utils.async_tasks import AsyncTaskManager, TaskStatus
        self.manager = AsyncTaskManager(max_workers=2)
        self.manager.start()
        self.TaskStatus = TaskStatus
    
    def tearDown(self):
        self.manager.stop()
    
    def test_submit_task(self):
        """Test task submission"""
        def simple_task():
            import time
            time.sleep(0.1)
            return "completed"
        
        task = self.manager.submit_task("test_task", simple_task)
        
        self.assertEqual(task.task_id, "test_task")
        self.assertEqual(task.status, self.TaskStatus.QUEUED)
    
    def test_task_completion(self):
        """Test task completion"""
        def simple_task():
            return "result"
        
        task = self.manager.submit_task("completion_test", simple_task)
        
        # Wait for completion
        import time
        max_wait = 5
        elapsed = 0
        while task.status not in [self.TaskStatus.COMPLETED, self.TaskStatus.FAILED] and elapsed < max_wait:
            time.sleep(0.1)
            elapsed += 0.1
        
        self.assertEqual(task.status, self.TaskStatus.COMPLETED)
        self.assertEqual(task.result, "result")
    
    def test_task_cancellation(self):
        """Test task cancellation"""
        def long_task():
            import time
            time.sleep(5)
            return "should not complete"
        
        task = self.manager.submit_task("cancel_test", long_task)
        
        # Request cancellation immediately
        self.manager.cancel_task("cancel_test")
        
        self.assertTrue(task.cancel_requested)


class TestLazyLoading(unittest.TestCase):
    """Test lazy loading of AI models"""
    
    def test_ai_model_lazy_loading(self):
        """Test AI model lazy initialization"""
        from models.ai_model import AIExtractor
        
        extractor = AIExtractor(lazy_load=True)
        
        # Model should not be loaded yet
        self.assertIsNone(extractor.model)
        self.assertIsNone(extractor.vectorizer)
        
        # Use the model - this should trigger loading
        result = extractor.find_best_match("test", ["test1", "test2"])
        
        # Now model should be loaded
        self.assertTrue(extractor.model is not None or extractor.vectorizer is not None)
    
    def test_embedder_lazy_loading(self):
        """Test embedder lazy initialization"""
        from models.embeddings import DocumentEmbedder
        
        embedder = DocumentEmbedder(lazy_load=True)
        
        # Model should not be loaded yet
        self.assertIsNone(embedder.model)
        
        # Use the embedder - this should trigger loading
        embedding = embedder.embed_text("test text")
        
        # Now model should be loaded
        self.assertIsNotNone(embedder.model)
        self.assertIsInstance(embedding, np.ndarray)


class TestCachedCalculations(unittest.TestCase):
    """Test cached financial calculations"""
    
    def test_financial_calculator_caching(self):
        """Test that financial calculations are cached"""
        import pandas as pd
        from processors.financial_calculator import FinancialCalculator
        
        # Create test data
        data = pd.DataFrame({
            'value': {
                'revenue': 100000,
                'cost_of_goods_sold': 60000,
                'net_income': 10000,
                'total_assets': 50000,
                'shareholders_equity': 30000,
                'current_assets': 25000,
                'current_liabilities': 15000
            }
        })
        
        # First calculation
        calc1 = FinancialCalculator(data)
        metrics1 = calc1.calculate_all_metrics()
        
        # Second calculation with same data - should use cache
        calc2 = FinancialCalculator(data)
        metrics2 = calc2.calculate_all_metrics()
        
        # Results should be identical
        self.assertEqual(metrics1, metrics2)
        self.assertGreater(len(metrics1), 0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
