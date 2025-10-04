"""Text chunking utilities for RAG implementation."""

import re
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """Chunk text for efficient embedding and retrieval."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize text chunker.

        Args:
            chunk_size: Maximum number of characters per chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Chunk text into smaller pieces with metadata.

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of chunks with metadata
        """
        if not text or not text.strip():
            return []

        # Clean text
        text = self._clean_text(text)

        # Split into paragraphs first
        paragraphs = self._split_into_paragraphs(text)

        chunks = []
        current_chunk = ""
        chunk_metadata = metadata or {}

        for para in paragraphs:
            # If paragraph is too long, split it
            if len(para) > self.chunk_size:
                # Add current chunk if not empty
                if current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "metadata": chunk_metadata.copy()
                    })
                    current_chunk = ""

                # Split long paragraph into sentences
                sentences = self._split_into_sentences(para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > self.chunk_size:
                        if current_chunk:
                            chunks.append({
                                "text": current_chunk.strip(),
                                "metadata": chunk_metadata.copy()
                            })
                        current_chunk = sentence + " "
                    else:
                        current_chunk += sentence + " "
            else:
                # Add paragraph to current chunk
                if len(current_chunk) + len(para) > self.chunk_size:
                    # Save current chunk and start new one
                    if current_chunk:
                        chunks.append({
                            "text": current_chunk.strip(),
                            "metadata": chunk_metadata.copy()
                        })
                    current_chunk = para + "\n\n"
                else:
                    current_chunk += para + "\n\n"

        # Add remaining chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": chunk_metadata.copy()
            })

        # Add chunk indices
        for idx, chunk in enumerate(chunks):
            chunk["metadata"]["chunk_index"] = idx
            chunk["metadata"]["total_chunks"] = len(chunks)

        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and normalizing."""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_with_overlap(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Chunk text with overlap for better context retrieval.

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of chunks with overlap
        """
        if not text or not text.strip():
            return []

        text = self._clean_text(text)
        chunks = []
        chunk_metadata = metadata or {}
        
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            # Try to end at a sentence boundary
            if end < text_length:
                # Look for sentence ending
                for delimiter in ['. ', '! ', '? ', '\n']:
                    last_delim = text[start:end].rfind(delimiter)
                    if last_delim != -1:
                        end = start + last_delim + len(delimiter)
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        **chunk_metadata,
                        "chunk_index": len(chunks),
                        "start_pos": start,
                        "end_pos": end
                    }
                })

            # Move to next chunk with overlap
            start = end - self.chunk_overlap

        # Update total chunks
        for chunk in chunks:
            chunk["metadata"]["total_chunks"] = len(chunks)

        logger.info(f"Created {len(chunks)} chunks with overlap from text")
        return chunks
