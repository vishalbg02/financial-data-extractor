"""Question Answering API routes for financial data extraction."""

from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
from models.qa_model import RAGQuestionAnswerer
from models.embeddings import DocumentEmbedder
from models.vector_store import VectorStore
from extractors.pdf_extractor import PDFExtractor
from extractors.excel_extractor import ExcelExtractor

logger = logging.getLogger(__name__)


class QAService:
    """Service class for Question Answering functionality."""

    def __init__(self):
        """Initialize QA service."""
        self.embedder = DocumentEmbedder()
        self.vector_store = VectorStore(
            embedding_dimension=self.embedder.get_embedding_dimension()
        )
        self.qa_system = RAGQuestionAnswerer(
            embedder=self.embedder,
            vector_store=self.vector_store
        )
        self.knowledge_base_path = Path("data") / "vector_store" / "financial_kb"
        self.knowledge_base_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to load existing knowledge base
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Load existing knowledge base if available."""
        index_path = self.knowledge_base_path.with_suffix('.index')
        if index_path.exists():
            try:
                self.qa_system.load_knowledge_base(str(self.knowledge_base_path))
                logger.info("Loaded existing knowledge base")
            except Exception as e:
                logger.warning(f"Could not load knowledge base: {e}")

    def add_document_from_file(self, file_path: str, file_type: str = None) -> Dict[str, Any]:
        """
        Add a document to the knowledge base.

        Args:
            file_path: Path to the file
            file_type: Type of file ('pdf', 'excel', or auto-detect from extension)

        Returns:
            Status dictionary
        """
        try:
            path = Path(file_path)
            
            # Auto-detect file type if not provided
            if file_type is None:
                ext = path.suffix.lower()
                if ext == '.pdf':
                    file_type = 'pdf'
                elif ext in ['.xlsx', '.xls', '.xlsm', '.csv']:
                    file_type = 'excel'
                else:
                    return {
                        'success': False,
                        'error': f'Unsupported file type: {ext}'
                    }

            # Extract text based on file type
            if file_type == 'pdf':
                extractor = PDFExtractor(file_path)
                extractor.extract()  # Populate text_content
                full_text = extractor.extract_full_text()
            elif file_type == 'excel':
                extractor = ExcelExtractor(file_path)
                extractor.extract()  # Populate sheets
                full_text = extractor.extract_full_text()
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_type}'
                }

            if not full_text:
                return {
                    'success': False,
                    'error': 'No text could be extracted from the file'
                }

            # Get metadata
            metadata = extractor.get_metadata()
            metadata['file_type'] = file_type

            # Add to knowledge base
            self.qa_system.add_document(full_text, metadata)

            # Save knowledge base
            self.qa_system.save_knowledge_base(str(self.knowledge_base_path))

            stats = self.qa_system.get_stats()
            
            return {
                'success': True,
                'file_name': path.name,
                'chunks_added': stats.get('total_chunks', 0),
                'message': f'Successfully added {path.name} to knowledge base'
            }

        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def answer_question(self, question: str, k: int = 5, 
                       min_similarity: float = 0.3) -> Dict[str, Any]:
        """
        Answer a question using the RAG system.

        Args:
            question: Question to answer
            k: Number of context chunks to retrieve
            min_similarity: Minimum similarity threshold

        Returns:
            Answer dictionary with sources
        """
        try:
            result = self.qa_system.answer_question(
                question=question,
                k=k,
                min_similarity=min_similarity
            )
            
            return {
                'success': True,
                **result
            }

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'success': False,
                'error': str(e),
                'answer': 'An error occurred while processing your question.',
                'sources': []
            }

    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        try:
            stats = self.qa_system.get_stats()
            return {
                'success': True,
                **stats
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def clear_knowledge_base(self) -> Dict[str, Any]:
        """Clear all documents from the knowledge base."""
        try:
            self.qa_system.clear_knowledge_base()
            return {
                'success': True,
                'message': 'Knowledge base cleared successfully'
            }
        except Exception as e:
            logger.error(f"Error clearing knowledge base: {e}")
            return {
                'success': False,
                'error': str(e)
            }
