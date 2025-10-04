from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Abstract base class for data extractors"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.raw_data = None
        self.extracted_data = {}

    @abstractmethod
    def extract(self) -> Dict[str, Any]:
        """Extract data from the file"""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate extracted data"""
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Get file metadata"""
        import os
        from datetime import datetime

        stat = os.stat(self.file_path)
        return {
            "file_name": os.path.basename(self.file_path),
            "file_size": stat.st_size,
            "created_time": datetime.fromtimestamp(stat.st_ctime),
            "modified_time": datetime.fromtimestamp(stat.st_mtime),
        }


