"""
Error recovery utilities with suggestions for common errors.
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ErrorRecovery:
    """Provides error recovery suggestions and automatic fixes"""
    
    # Common error patterns and their solutions
    ERROR_SOLUTIONS = {
        "OCR": {
            "pattern": ["ocr", "easyocr", "tesseract", "readtext"],
            "suggestions": [
                "Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract",
                "Install EasyOCR: pip install easyocr",
                "Check if the PDF is a scanned image - text-based PDFs don't need OCR",
                "Try reducing PDF resolution if memory issues occur",
                "Ensure sufficient memory is available (at least 2GB free)"
            ],
            "auto_recovery": "fallback_to_text_extraction"
        },
        "Memory": {
            "pattern": ["memory", "out of memory", "memoryerror", "ram"],
            "suggestions": [
                "Close other applications to free up memory",
                "Process files one at a time instead of in batch",
                "Reduce batch size in configuration",
                "Enable memory-efficient chunking",
                "Clear cache: delete data/cache directory"
            ],
            "auto_recovery": "reduce_batch_size"
        },
        "GPU": {
            "pattern": ["cuda", "gpu", "device"],
            "suggestions": [
                "GPU not available - will use CPU mode",
                "Install CUDA toolkit if you have NVIDIA GPU",
                "System will automatically fallback to CPU processing"
            ],
            "auto_recovery": "use_cpu"
        },
        "File": {
            "pattern": ["file not found", "no such file", "permission denied"],
            "suggestions": [
                "Check if the file exists at the specified path",
                "Ensure you have read permissions for the file",
                "File might be locked by another process",
                "Try uploading the file again",
                "Check file format is supported (PDF, Excel, CSV)"
            ],
            "auto_recovery": None
        },
        "Encoding": {
            "pattern": ["encoding", "decode", "utf-8", "unicode"],
            "suggestions": [
                "File might have special characters or encoding issues",
                "Try saving the file with UTF-8 encoding",
                "Remove special characters from the file",
                "Convert file to a standard format"
            ],
            "auto_recovery": "try_different_encoding"
        },
        "Model": {
            "pattern": ["model", "transformer", "download", "huggingface"],
            "suggestions": [
                "AI model needs to be downloaded on first use",
                "Check internet connection",
                "Ensure sufficient disk space (at least 500MB)",
                "Wait for model download to complete",
                "If download fails, restart the application"
            ],
            "auto_recovery": "use_fallback_model"
        },
        "Network": {
            "pattern": ["connection", "timeout", "network", "http"],
            "suggestions": [
                "Check internet connection",
                "Retry the operation",
                "Some features may work offline after models are cached",
                "Check firewall settings"
            ],
            "auto_recovery": "retry_with_backoff"
        }
    }
    
    @staticmethod
    def analyze_error(error: Exception) -> Dict[str, Any]:
        """
        Analyze an error and provide recovery suggestions
        
        Args:
            error: The exception that occurred
        
        Returns:
            Dictionary with error analysis and suggestions
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Find matching error category
        matched_category = None
        for category, config in ErrorRecovery.ERROR_SOLUTIONS.items():
            for pattern in config["pattern"]:
                if pattern in error_str:
                    matched_category = category
                    break
            if matched_category:
                break
        
        if not matched_category:
            # Generic error handling
            return {
                "category": "Unknown",
                "error_type": error_type,
                "message": str(error),
                "suggestions": [
                    "Check the application logs for more details",
                    "Try restarting the application",
                    "Ensure all dependencies are installed",
                    "Contact support if the issue persists"
                ],
                "auto_recovery": None,
                "severity": "medium"
            }
        
        config = ErrorRecovery.ERROR_SOLUTIONS[matched_category]
        
        return {
            "category": matched_category,
            "error_type": error_type,
            "message": str(error),
            "suggestions": config["suggestions"],
            "auto_recovery": config["auto_recovery"],
            "severity": ErrorRecovery._assess_severity(matched_category)
        }
    
    @staticmethod
    def _assess_severity(category: str) -> str:
        """Assess error severity"""
        critical = ["Memory", "File"]
        high = ["OCR", "Model"]
        medium = ["GPU", "Encoding"]
        low = ["Network"]
        
        if category in critical:
            return "critical"
        elif category in high:
            return "high"
        elif category in medium:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def get_recovery_action(error_analysis: Dict[str, Any]) -> Optional[str]:
        """Get the recommended recovery action"""
        return error_analysis.get("auto_recovery")
    
    @staticmethod
    def format_error_message(error_analysis: Dict[str, Any]) -> str:
        """Format error message for display"""
        category = error_analysis["category"]
        message = error_analysis["message"]
        severity = error_analysis["severity"]
        
        # Emoji for severity
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        
        emoji = severity_emoji.get(severity, "⚠️")
        
        formatted = f"{emoji} **{category} Error** ({severity.upper()})\n\n"
        formatted += f"**Error:** {message}\n\n"
        formatted += "**Suggestions:**\n"
        
        for i, suggestion in enumerate(error_analysis["suggestions"], 1):
            formatted += f"{i}. {suggestion}\n"
        
        if error_analysis["auto_recovery"]:
            formatted += f"\n💡 **Auto-recovery:** {error_analysis['auto_recovery']}"
        
        return formatted


def handle_extraction_error(error: Exception, file_name: str) -> Dict[str, Any]:
    """
    Handle extraction errors with recovery suggestions
    
    Args:
        error: The exception that occurred
        file_name: Name of the file being processed
    
    Returns:
        Error information with recovery suggestions
    """
    analysis = ErrorRecovery.analyze_error(error)
    
    logger.error(
        f"Error processing {file_name}: {analysis['category']} - {analysis['message']}"
    )
    
    return {
        "file_name": file_name,
        "error": True,
        "analysis": analysis,
        "formatted_message": ErrorRecovery.format_error_message(analysis),
        "can_retry": analysis["category"] in ["Network", "Memory", "GPU"],
        "should_skip": analysis["category"] in ["File", "Encoding"]
    }
