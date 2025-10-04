"""
RAG (Retrieval-Augmented Generation) Processor for Document Q&A
"""
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Handle document chunking for RAG"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunks with metadata
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > self.chunk_size // 2:  # Only break if we're past halfway
                    chunk_text = chunk_text[:break_point + 1]
                    end = start + break_point + 1
            
            chunk_data = {
                'text': chunk_text.strip(),
                'start': start,
                'end': end,
            }
            
            if metadata:
                chunk_data['metadata'] = metadata
            
            chunks.append(chunk_data)
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap if end < len(text) else len(text)
        
        return chunks
    
    def chunk_dataframe(self, df: pd.DataFrame, text_column: str = 'text') -> List[Dict]:
        """
        Chunk text from a DataFrame
        
        Args:
            df: DataFrame containing text
            text_column: Name of column containing text
            
        Returns:
            List of chunks with metadata
        """
        all_chunks = []
        
        for idx, row in df.iterrows():
            if text_column in row and pd.notna(row[text_column]):
                metadata = {k: v for k, v in row.items() if k != text_column}
                metadata['row_index'] = idx
                
                chunks = self.chunk_text(str(row[text_column]), metadata)
                all_chunks.extend(chunks)
        
        return all_chunks


class ConversationMemory:
    """Manage conversation history for context"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history: List[Dict] = []
    
    def add_exchange(self, question: str, answer: str, sources: Optional[List[Dict]] = None):
        """Add a question-answer exchange to history"""
        exchange = {
            'question': question,
            'answer': answer,
            'sources': sources or []
        }
        
        self.history.append(exchange)
        
        # Keep only recent history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_context(self, num_exchanges: int = 3) -> str:
        """Get recent conversation context as formatted string"""
        if not self.history:
            return ""
        
        recent = self.history[-num_exchanges:]
        context_parts = []
        
        for exchange in recent:
            context_parts.append(f"Q: {exchange['question']}")
            context_parts.append(f"A: {exchange['answer']}")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear conversation history"""
        self.history = []
    
    def get_all_exchanges(self) -> List[Dict]:
        """Get all conversation exchanges"""
        return self.history.copy()


class RAGProcessor:
    """
    RAG Processor for document-based question answering
    Uses semantic search to retrieve relevant context and generate answers
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        self.chunker = DocumentChunker(chunk_size, chunk_overlap)
        self.memory = ConversationMemory()
        
        # Document storage
        self.documents: List[Dict] = []
        self.chunks: List[Dict] = []
        self.embeddings_model = None
        
        # Initialize embeddings model
        self._init_embeddings()
    
    def _init_embeddings(self):
        """Initialize the embeddings model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded embeddings model successfully")
        except Exception as e:
            logger.error(f"Failed to load embeddings model: {e}")
            raise
    
    def add_document(self, text: str, metadata: Optional[Dict] = None) -> int:
        """
        Add a document to the RAG system
        
        Args:
            text: Document text
            metadata: Optional metadata (filename, type, etc.)
            
        Returns:
            Number of chunks created
        """
        doc_id = len(self.documents)
        
        # Store original document
        doc_metadata = metadata or {}
        doc_metadata['doc_id'] = doc_id
        
        self.documents.append({
            'text': text,
            'metadata': doc_metadata
        })
        
        # Chunk the document
        chunks = self.chunker.chunk_text(text, doc_metadata)
        
        # Generate embeddings for chunks
        for chunk in chunks:
            chunk['chunk_id'] = len(self.chunks)
            chunk['embedding'] = self._get_embedding(chunk['text'])
            self.chunks.append(chunk)
        
        logger.info(f"Added document {doc_id} with {len(chunks)} chunks")
        return len(chunks)
    
    def _get_embedding(self, text: str):
        """Generate embedding for text"""
        if self.embeddings_model is None:
            raise RuntimeError("Embeddings model not initialized")
        
        return self.embeddings_model.encode(text)
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Search for relevant chunks based on query
        
        Args:
            query: Search query
            top_k: Number of results to return (uses default if None)
            
        Returns:
            List of relevant chunks with similarity scores
        """
        if not self.chunks:
            logger.warning("No documents indexed for search")
            return []
        
        k = top_k or self.top_k
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Calculate similarities
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        chunk_embeddings = np.array([chunk['embedding'] for chunk in self.chunks])
        similarities = cosine_similarity([query_embedding], chunk_embeddings)[0]
        
        # Get top k results above threshold
        results = []
        for idx, score in enumerate(similarities):
            if score >= self.similarity_threshold:
                result = self.chunks[idx].copy()
                result['similarity_score'] = float(score)
                results.append(result)
        
        # Sort by similarity and take top k
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:k]
    
    def query(
        self,
        question: str,
        use_context: bool = True,
        return_sources: bool = True
    ) -> Dict:
        """
        Query the RAG system with a question
        
        Args:
            question: Question to answer
            use_context: Whether to use conversation history
            return_sources: Whether to return source chunks
            
        Returns:
            Dict with answer, sources, and metadata
        """
        # Build context if enabled
        context = ""
        if use_context:
            context = self.memory.get_context()
        
        # Search for relevant chunks
        relevant_chunks = self.search(question)
        
        if not relevant_chunks:
            answer = "I couldn't find relevant information in the documents to answer this question."
            sources = []
        else:
            # Build answer from chunks
            answer_parts = []
            sources = []
            
            for chunk in relevant_chunks:
                source_info = {
                    'text': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text'],
                    'score': chunk['similarity_score'],
                    'metadata': chunk.get('metadata', {})
                }
                sources.append(source_info)
            
            # Create answer based on most relevant chunk
            answer = f"Based on the documents, here's what I found:\n\n"
            answer += relevant_chunks[0]['text']
            
            # Add source attribution
            if 'metadata' in relevant_chunks[0] and 'filename' in relevant_chunks[0]['metadata']:
                answer += f"\n\n(Source: {relevant_chunks[0]['metadata']['filename']})"
        
        # Add to conversation memory
        self.memory.add_exchange(question, answer, sources if return_sources else None)
        
        result = {
            'question': question,
            'answer': answer,
            'num_sources': len(sources),
            'confidence': sources[0]['score'] if sources else 0.0
        }
        
        if return_sources:
            result['sources'] = sources
        
        return result
    
    def clear_documents(self):
        """Clear all documents and chunks"""
        self.documents = []
        self.chunks = []
        logger.info("Cleared all documents")
    
    def get_stats(self) -> Dict:
        """Get statistics about indexed documents"""
        return {
            'num_documents': len(self.documents),
            'num_chunks': len(self.chunks),
            'avg_chunk_size': sum(len(c['text']) for c in self.chunks) / len(self.chunks) if self.chunks else 0,
            'conversation_history': len(self.memory.history)
        }
