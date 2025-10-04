"""Document embedding utilities for RAG implementation with lazy loading and caching."""

import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import logging

from utils.cache_manager import get_cache_manager

logger = logging.getLogger(__name__)


class DocumentEmbedder:
    """Generate embeddings for documents and queries with lazy loading and caching."""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', lazy_load: bool = True):
        """
        Initialize document embedder with lazy loading.

        Args:
            model_name: Name of the sentence transformer model to use
            lazy_load: If True, delay model loading until first use
        """
        self.model_name = model_name
        self.lazy_load = lazy_load
        self.model = None
        self.embedding_dimension = 384  # Default for all-MiniLM-L6-v2
        self.cache_manager = get_cache_manager()
        
        if not lazy_load:
            self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        if self.model is not None:
            return  # Already loaded
        
        try:
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Loaded embedding model: {self.model_name} (dimension: {self.embedding_dimension})")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text with caching.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as numpy array
        """
        # Lazy load model if needed
        if self.model is None:
            self._load_model()
        
        if not text or not text.strip():
            return np.zeros(self.embedding_dimension)

        # Check cache
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"embed_{text_hash}"
        cached_embedding = self.cache_manager.get(cache_key, memory_only=True)
        if cached_embedding is not None:
            return cached_embedding

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            # Cache the result
            self.cache_manager.set(cache_key, embedding, memory_only=True)
            return embedding
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            return np.zeros(self.embedding_dimension)

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for encoding

        Returns:
            Array of embeddings
        """
        # Lazy load model if needed
        if self.model is None:
            self._load_model()
        
        if not texts:
            return np.array([])

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 100
            )
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to embed texts: {e}")
            return np.array([])

    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Embed text chunks and add embeddings to metadata.

        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata' keys

        Returns:
            Chunks with added 'embedding' key
        """
        if not chunks:
            return []

        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embed_texts(texts)

        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding

        return chunks

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self.embedding_dimension
