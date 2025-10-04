import os
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class FileHandler:
    """Handle file operations"""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.cwd()
        self.temp_dir = self.base_dir / "data" / "temp"
        self.output_dir = self.base_dir / "data" / "output"

        # Create directories
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_uploaded_file(self, uploaded_file, filename: Optional[str] = None) -> Path:
        """Save uploaded file to temp directory"""
        if filename is None:
            filename = uploaded_file.name

        file_path = self.temp_dir / filename

        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        logger.info(f"Saved file to {file_path}")
        return file_path

    def cleanup_temp(self):
        """Clean up temporary files"""
        try:
            for file in self.temp_dir.glob('*'):
                if file.is_file():
                    file.unlink()
            logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")

    def get_file_info(self, file_path: Path) -> dict:
        """Get file information"""
        stat = file_path.stat()
        return {
            'name': file_path.name,
            'size': stat.st_size,
            'extension': file_path.suffix,
            'path': str(file_path)
        }
