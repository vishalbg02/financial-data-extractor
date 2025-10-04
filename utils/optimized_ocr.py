"""
Optimized OCR module with batch processing, caching, and multiple fallback options.
Supports EasyOCR (GPU/CPU) and Tesseract as fallback.
"""
import logging
import numpy as np
import pytesseract
from PIL import Image
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import cv2

from utils.cache_manager import get_cache_manager
from utils.performance_monitor import get_performance_monitor

logger = logging.getLogger(__name__)


class OptimizedOCR:
    """Optimized OCR with caching, batch processing, and fallback options"""
    
    def __init__(self, 
                 use_gpu: bool = False,
                 enable_cache: bool = True,
                 max_workers: int = 4):
        """
        Initialize OCR engine with optimizations
        
        Args:
            use_gpu: Try to use GPU for EasyOCR
            enable_cache: Enable caching of OCR results
            max_workers: Number of parallel workers for batch processing
        """
        self.enable_cache = enable_cache
        self.max_workers = max_workers
        self.cache_manager = get_cache_manager() if enable_cache else None
        self.performance_monitor = get_performance_monitor()
        
        # Try to initialize EasyOCR
        self.easyocr_reader = None
        self.use_easyocr = False
        try:
            import easyocr
            self.easyocr_reader = easyocr.Reader(['en'], gpu=use_gpu)
            self.use_easyocr = True
            logger.info(f"EasyOCR initialized (GPU: {use_gpu})")
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}. Will use Tesseract fallback.")
        
        # Check Tesseract availability
        self.tesseract_available = self._check_tesseract()
        
        if not self.use_easyocr and not self.tesseract_available:
            logger.error("No OCR engine available! Install EasyOCR or Tesseract.")
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract is available"""
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract is available")
            return True
        except Exception as e:
            logger.warning(f"Tesseract not available: {e}")
            return False
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Apply adaptive thresholding for better text detection
            processed = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(processed)
            
            return denoised
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}. Using original image.")
            return image
    
    def _get_image_cache_key(self, image: np.ndarray) -> str:
        """Generate cache key for an image"""
        import hashlib
        # Use a hash of the image data as cache key
        image_hash = hashlib.md5(image.tobytes()).hexdigest()
        return f"ocr_{image_hash}"
    
    def extract_text_single(self, 
                           image: np.ndarray,
                           preprocess: bool = True) -> str:
        """
        Extract text from a single image
        
        Args:
            image: Image as numpy array
            preprocess: Whether to preprocess the image
            
        Returns:
            Extracted text
        """
        # Check cache first
        if self.enable_cache:
            cache_key = self._get_image_cache_key(image)
            cached_result = self.cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug("Using cached OCR result")
                return cached_result
        
        # Preprocess if requested
        if preprocess:
            image = self.preprocess_image(image)
        
        # Try EasyOCR first
        text = None
        if self.use_easyocr:
            try:
                result = self.easyocr_reader.readtext(image)
                text = ' '.join([item[1] for item in result])
            except Exception as e:
                logger.warning(f"EasyOCR failed: {e}")
        
        # Fallback to Tesseract
        if text is None and self.tesseract_available:
            try:
                # Convert numpy array to PIL Image for Tesseract
                pil_image = Image.fromarray(image)
                text = pytesseract.image_to_string(pil_image)
            except Exception as e:
                logger.warning(f"Tesseract OCR failed: {e}")
                text = ""
        
        # If both failed
        if text is None:
            text = ""
        
        # Cache result
        if self.enable_cache and text:
            self.cache_manager.set(cache_key, text)
        
        return text
    
    def extract_text_batch(self,
                          images: List[np.ndarray],
                          preprocess: bool = True,
                          progress_callback: Optional[Callable[[int, int], None]] = None) -> List[str]:
        """
        Extract text from multiple images in parallel
        
        Args:
            images: List of images as numpy arrays
            preprocess: Whether to preprocess images
            progress_callback: Optional callback function(current, total)
            
        Returns:
            List of extracted texts
        """
        with self.performance_monitor.measure(f"OCR batch processing ({len(images)} images)"):
            results = [''] * len(images)
            
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_idx = {
                    executor.submit(self.extract_text_single, img, preprocess): idx
                    for idx, img in enumerate(images)
                }
                
                # Collect results as they complete
                completed = 0
                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        results[idx] = future.result()
                    except Exception as e:
                        logger.error(f"OCR failed for image {idx}: {e}")
                        results[idx] = ""
                    
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, len(images))
            
            return results
    
    def extract_with_retry(self,
                          image: np.ndarray,
                          max_retries: int = 3,
                          preprocess: bool = True) -> str:
        """
        Extract text with automatic retry on failure
        
        Args:
            image: Image as numpy array
            max_retries: Maximum number of retry attempts
            preprocess: Whether to preprocess the image
            
        Returns:
            Extracted text
        """
        for attempt in range(max_retries):
            try:
                text = self.extract_text_single(image, preprocess)
                if text and len(text.strip()) > 0:
                    return text
                
                if attempt < max_retries - 1:
                    logger.warning(f"OCR attempt {attempt + 1} returned empty text, retrying...")
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"OCR attempt {attempt + 1} failed: {e}, retrying...")
                else:
                    logger.error(f"OCR failed after {max_retries} attempts: {e}")
        
        return ""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get OCR engine statistics"""
        return {
            'easyocr_available': self.use_easyocr,
            'tesseract_available': self.tesseract_available,
            'cache_enabled': self.enable_cache,
            'max_workers': self.max_workers
        }
