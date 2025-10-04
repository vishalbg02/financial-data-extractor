"""Question Answering module using RAG (Retrieval Augmented Generation)."""

import logging
from typing import List, Dict, Any, Optional
from models.embeddings import DocumentEmbedder
from models.vector_store import VectorStore
from utils.text_chunker import TextChunker

logger = logging.getLogger(__name__)


class RAGQuestionAnswerer:
    """RAG-based question answering system."""

    def __init__(self, embedder: Optional[DocumentEmbedder] = None,
                 vector_store: Optional[VectorStore] = None):
        """
        Initialize RAG QA system.

        Args:
            embedder: Document embedder (creates new if not provided)
            vector_store: Vector store (creates new if not provided)
        """
        self.embedder = embedder or DocumentEmbedder()
        self.vector_store = vector_store or VectorStore(
            embedding_dimension=self.embedder.get_embedding_dimension()
        )
        self.chunker = TextChunker(chunk_size=500, chunk_overlap=50)
        logger.info("Initialized RAG Question Answerer")

    def add_document(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a document to the knowledge base.

        Args:
            text: Document text
            metadata: Optional metadata (source, file_name, etc.)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided")
            return

        # Chunk the document
        chunks = self.chunker.chunk_with_overlap(text, metadata)
        
        if not chunks:
            logger.warning("No chunks created from document")
            return

        # Generate embeddings
        chunks_with_embeddings = self.embedder.embed_chunks(chunks)

        # Add to vector store
        self.vector_store.add_chunks(chunks_with_embeddings)
        
        logger.info(f"Added document with {len(chunks)} chunks to knowledge base")

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add multiple documents to the knowledge base.

        Args:
            documents: List of documents with 'text' and optional 'metadata' keys
        """
        for doc in documents:
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})
            self.add_document(text, metadata)

    def answer_question(self, question: str, k: int = 5, 
                       min_similarity: float = 0.3) -> Dict[str, Any]:
        """
        Answer a question using RAG.

        Args:
            question: Question to answer
            k: Number of context chunks to retrieve
            min_similarity: Minimum similarity threshold

        Returns:
            Dictionary with answer, sources, and metadata
        """
        if not question or not question.strip():
            return {
                'answer': 'Please provide a valid question.',
                'sources': [],
                'confidence': 0.0
            }

        # Generate question embedding
        question_embedding = self.embedder.embed_text(question)

        # Retrieve relevant chunks
        results = self.vector_store.search_with_score(
            question_embedding, 
            k=k,
            threshold=min_similarity
        )

        if not results:
            return {
                'answer': 'I could not find relevant information to answer this question.',
                'sources': [],
                'confidence': 0.0
            }

        # Extract contexts and sources
        contexts = []
        sources = []
        for chunk, similarity in results:
            contexts.append(chunk['text'])
            sources.append({
                'text': chunk['text'],
                'similarity': similarity,
                'metadata': chunk.get('metadata', {})
            })

        # Generate answer based on context
        answer = self._generate_answer(question, contexts, sources)

        return {
            'answer': answer,
            'sources': sources,
            'confidence': sources[0]['similarity'] if sources else 0.0,
            'num_sources': len(sources)
        }

    def _generate_answer(self, question: str, contexts: List[str], 
                        sources: List[Dict[str, Any]]) -> str:
        """
        Generate answer from retrieved contexts.

        Note: This is a simple implementation. For production, integrate with LLM API.

        Args:
            question: The question
            contexts: Retrieved context chunks
            sources: Source information

        Returns:
            Generated answer
        """
        # Simple rule-based answer generation
        # In production, this would call an LLM API (OpenAI, Anthropic, etc.)
        
        question_lower = question.lower()
        
        # Check if asking for specific financial metrics
        financial_keywords = {
            'revenue': ['revenue', 'sales', 'income'],
            'profit': ['profit', 'earnings', 'net income'],
            'assets': ['assets', 'total assets'],
            'liabilities': ['liabilities', 'debt'],
            'equity': ['equity', 'shareholders equity'],
            'cash flow': ['cash flow', 'operating cash'],
            'margin': ['margin', 'profit margin'],
            'ratio': ['ratio', 'current ratio', 'debt ratio']
        }

        # Try to extract numerical answers
        import re
        numbers_found = []
        for context in contexts:
            # Find numbers with context
            number_patterns = re.findall(r'[\$€]?\s*[\d,]+\.?\d*\s*[KMBkmb]?', context)
            for num in number_patterns:
                numbers_found.append((num, context))

        # Build answer
        answer_parts = []
        
        # Add direct context information
        if numbers_found:
            answer_parts.append("Based on the documents:")
            for num, ctx in numbers_found[:3]:  # Top 3 numbers
                # Extract surrounding context
                num_pos = ctx.find(num)
                start = max(0, num_pos - 50)
                end = min(len(ctx), num_pos + len(num) + 50)
                snippet = ctx[start:end].strip()
                answer_parts.append(f"• {snippet}")
        else:
            answer_parts.append("Based on the available information:")
            # Add most relevant context
            for i, context in enumerate(contexts[:2]):
                sentences = context.split('.')[:2]  # First 2 sentences
                answer_parts.append(f"• {'. '.join(sentences).strip()}.")

        answer = '\n'.join(answer_parts)
        
        # Add note about sources
        if sources:
            file_names = set()
            for source in sources:
                metadata = source.get('metadata', {})
                if 'file_name' in metadata:
                    file_names.add(metadata['file_name'])
            
            if file_names:
                answer += f"\n\nSources: {', '.join(file_names)}"

        return answer

    def clear_knowledge_base(self):
        """Clear all documents from the knowledge base."""
        self.vector_store.clear()
        logger.info("Cleared knowledge base")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        return self.vector_store.get_stats()

    def save_knowledge_base(self, path: str):
        """Save knowledge base to disk."""
        self.vector_store.save(path)
        logger.info(f"Saved knowledge base to {path}")

    def load_knowledge_base(self, path: str):
        """Load knowledge base from disk."""
        self.vector_store.load(path)
        logger.info(f"Loaded knowledge base from {path}")
