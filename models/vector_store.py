"""Vector store implementation using FAISS for similarity search."""

import numpy as np
import faiss
from typing import List, Dict, Any, Optional, Tuple
import logging
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for efficient similarity search."""

    def __init__(self, embedding_dimension: int = 384):
        """
        Initialize vector store.

        Args:
            embedding_dimension: Dimension of embeddings
        """
        self.embedding_dimension = embedding_dimension
        self.index = None
        self.chunks = []
        self._initialize_index()

    def _initialize_index(self):
        """Initialize FAISS index."""
        # Use L2 distance (can also use Inner Product)
        self.index = faiss.IndexFlatL2(self.embedding_dimension)
        logger.info(f"Initialized FAISS index with dimension {self.embedding_dimension}")

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Add chunks with embeddings to the vector store.

        Args:
            chunks: List of chunks with 'text', 'metadata', and 'embedding' keys
        """
        if not chunks:
            logger.warning("No chunks to add")
            return

        # Extract embeddings
        embeddings = np.array([chunk['embedding'] for chunk in chunks])
        
        # Ensure correct dtype and shape
        embeddings = embeddings.astype('float32')
        
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store chunks (without embeddings to save memory)
        for chunk in chunks:
            chunk_copy = {
                'text': chunk['text'],
                'metadata': chunk.get('metadata', {})
            }
            self.chunks.append(chunk_copy)

        logger.info(f"Added {len(chunks)} chunks to vector store. Total: {len(self.chunks)}")

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search for similar chunks.

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return

        Returns:
            List of (chunk, distance) tuples
        """
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []

        # Ensure correct shape and dtype
        query_embedding = query_embedding.astype('float32')
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Search
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, k)

        # Prepare results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(dist)))

        logger.info(f"Found {len(results)} results for query")
        return results

    def search_with_score(self, query_embedding: np.ndarray, k: int = 5, 
                          threshold: Optional[float] = None) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search for similar chunks with similarity score (0-1).

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of (chunk, similarity_score) tuples
        """
        results = self.search(query_embedding, k)
        
        # Convert L2 distance to similarity score (0-1)
        # Using exponential decay: similarity = exp(-distance)
        scored_results = []
        for chunk, distance in results:
            similarity = np.exp(-distance)
            if threshold is None or similarity >= threshold:
                scored_results.append((chunk, similarity))

        return scored_results

    def clear(self):
        """Clear all data from vector store."""
        self._initialize_index()
        self.chunks = []
        logger.info("Vector store cleared")

    def save(self, path: str):
        """
        Save vector store to disk.

        Args:
            path: Path to save the vector store
        """
        try:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Save FAISS index
            index_path = str(path.with_suffix('.index'))
            faiss.write_index(self.index, index_path)

            # Save chunks
            chunks_path = str(path.with_suffix('.chunks'))
            with open(chunks_path, 'wb') as f:
                pickle.dump(self.chunks, f)

            logger.info(f"Saved vector store to {path}")
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")
            raise

    def load(self, path: str):
        """
        Load vector store from disk.

        Args:
            path: Path to load the vector store from
        """
        try:
            path = Path(path)

            # Load FAISS index
            index_path = str(path.with_suffix('.index'))
            self.index = faiss.read_index(index_path)

            # Load chunks
            chunks_path = str(path.with_suffix('.chunks'))
            with open(chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)

            logger.info(f"Loaded vector store from {path} with {len(self.chunks)} chunks")
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            'total_chunks': len(self.chunks),
            'embedding_dimension': self.embedding_dimension,
            'index_size': self.index.ntotal if self.index else 0
        }
