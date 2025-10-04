"""Tests for RAG (Retrieval Augmented Generation) functionality."""

import unittest
import sys
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.text_chunker import TextChunker
from models.embeddings import DocumentEmbedder
from models.vector_store import VectorStore
from models.qa_model import RAGQuestionAnswerer


class TestTextChunker(unittest.TestCase):
    """Test text chunking functionality."""

    def setUp(self):
        self.chunker = TextChunker(chunk_size=100, chunk_overlap=20)

    def test_chunk_simple_text(self):
        """Test chunking simple text."""
        text = "This is a simple test. " * 10
        chunks = self.chunker.chunk_text(text)
        
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertIn('text', chunk)
            self.assertIn('metadata', chunk)

    def test_chunk_with_metadata(self):
        """Test chunking with metadata."""
        text = "Test text. " * 10
        metadata = {'source': 'test.pdf', 'page': 1}
        chunks = self.chunker.chunk_text(text, metadata)
        
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertEqual(chunk['metadata']['source'], 'test.pdf')
            self.assertEqual(chunk['metadata']['page'], 1)
            self.assertIn('chunk_index', chunk['metadata'])

    def test_chunk_with_overlap(self):
        """Test chunking with overlap."""
        text = "A" * 200
        chunks = self.chunker.chunk_with_overlap(text)
        
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk['text']), self.chunker.chunk_size + 10)

    def test_empty_text(self):
        """Test chunking empty text."""
        chunks = self.chunker.chunk_text("")
        self.assertEqual(len(chunks), 0)


class TestDocumentEmbedder(unittest.TestCase):
    """Test document embedding functionality."""

    def setUp(self):
        # Use a small model for testing
        self.embedder = DocumentEmbedder('all-MiniLM-L6-v2')

    def test_embed_single_text(self):
        """Test embedding single text."""
        text = "This is a test sentence for embedding."
        embedding = self.embedder.embed_text(text)
        
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(len(embedding.shape), 1)
        self.assertEqual(embedding.shape[0], self.embedder.get_embedding_dimension())

    def test_embed_multiple_texts(self):
        """Test embedding multiple texts."""
        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence."
        ]
        embeddings = self.embedder.embed_texts(texts)
        
        self.assertEqual(embeddings.shape[0], len(texts))
        self.assertEqual(embeddings.shape[1], self.embedder.get_embedding_dimension())

    def test_embed_chunks(self):
        """Test embedding chunks."""
        chunks = [
            {'text': 'First chunk', 'metadata': {}},
            {'text': 'Second chunk', 'metadata': {}}
        ]
        embedded_chunks = self.embedder.embed_chunks(chunks)
        
        self.assertEqual(len(embedded_chunks), 2)
        for chunk in embedded_chunks:
            self.assertIn('embedding', chunk)
            self.assertIsInstance(chunk['embedding'], np.ndarray)

    def test_empty_text(self):
        """Test embedding empty text."""
        embedding = self.embedder.embed_text("")
        self.assertEqual(len(embedding), self.embedder.get_embedding_dimension())


class TestVectorStore(unittest.TestCase):
    """Test vector store functionality."""

    def setUp(self):
        self.vector_store = VectorStore(embedding_dimension=384)
        self.embedder = DocumentEmbedder('all-MiniLM-L6-v2')

    def test_add_chunks(self):
        """Test adding chunks to vector store."""
        chunks = [
            {
                'text': 'Revenue is $1M',
                'metadata': {'source': 'test.pdf'},
                'embedding': self.embedder.embed_text('Revenue is $1M')
            },
            {
                'text': 'Expenses are $500K',
                'metadata': {'source': 'test.pdf'},
                'embedding': self.embedder.embed_text('Expenses are $500K')
            }
        ]
        
        self.vector_store.add_chunks(chunks)
        stats = self.vector_store.get_stats()
        
        self.assertEqual(stats['total_chunks'], 2)
        self.assertEqual(stats['index_size'], 2)

    def test_search(self):
        """Test searching in vector store."""
        # Add some chunks
        chunks = [
            {
                'text': 'Revenue is $1M',
                'metadata': {'source': 'test.pdf'},
                'embedding': self.embedder.embed_text('Revenue is $1M')
            },
            {
                'text': 'Expenses are $500K',
                'metadata': {'source': 'test.pdf'},
                'embedding': self.embedder.embed_text('Expenses are $500K')
            }
        ]
        self.vector_store.add_chunks(chunks)
        
        # Search
        query_embedding = self.embedder.embed_text('What is the revenue?')
        results = self.vector_store.search(query_embedding, k=1)
        
        self.assertEqual(len(results), 1)
        self.assertIn('Revenue', results[0][0]['text'])

    def test_search_with_score(self):
        """Test searching with similarity score."""
        chunks = [
            {
                'text': 'Revenue is $1M',
                'metadata': {'source': 'test.pdf'},
                'embedding': self.embedder.embed_text('Revenue is $1M')
            }
        ]
        self.vector_store.add_chunks(chunks)
        
        query_embedding = self.embedder.embed_text('What is the revenue?')
        results = self.vector_store.search_with_score(query_embedding, k=1)
        
        self.assertEqual(len(results), 1)
        chunk, score = results[0]
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

    def test_clear(self):
        """Test clearing vector store."""
        chunks = [
            {
                'text': 'Test',
                'metadata': {},
                'embedding': self.embedder.embed_text('Test')
            }
        ]
        self.vector_store.add_chunks(chunks)
        self.vector_store.clear()
        
        stats = self.vector_store.get_stats()
        self.assertEqual(stats['total_chunks'], 0)


class TestRAGQuestionAnswerer(unittest.TestCase):
    """Test RAG question answering functionality."""

    def setUp(self):
        embedder = DocumentEmbedder('all-MiniLM-L6-v2')
        vector_store = VectorStore(embedding_dimension=embedder.get_embedding_dimension())
        self.qa_system = RAGQuestionAnswerer(embedder=embedder, vector_store=vector_store)

    def test_add_document(self):
        """Test adding a document."""
        text = "The company revenue for 2023 was $5 million. Operating expenses were $2 million."
        metadata = {'source': 'financial_report.pdf', 'year': 2023}
        
        self.qa_system.add_document(text, metadata)
        stats = self.qa_system.get_stats()
        
        self.assertGreater(stats['total_chunks'], 0)

    def test_answer_question(self):
        """Test answering a question."""
        # Add some documents
        documents = [
            {
                'text': 'The total revenue for 2023 was $10 million. Net income was $2 million.',
                'metadata': {'source': 'report1.pdf'}
            },
            {
                'text': 'Operating expenses totaled $6 million in 2023.',
                'metadata': {'source': 'report2.pdf'}
            }
        ]
        self.qa_system.add_documents(documents)
        
        # Ask a question
        result = self.qa_system.answer_question('What was the revenue?', k=3)
        
        self.assertIn('answer', result)
        self.assertIn('sources', result)
        self.assertIn('confidence', result)
        self.assertGreater(len(result['sources']), 0)

    def test_answer_empty_question(self):
        """Test answering an empty question."""
        result = self.qa_system.answer_question('')
        
        self.assertIn('answer', result)
        self.assertEqual(result['confidence'], 0.0)

    def test_answer_no_documents(self):
        """Test answering when no documents are added."""
        result = self.qa_system.answer_question('What is the revenue?')
        
        self.assertIn('answer', result)
        self.assertEqual(len(result['sources']), 0)

    def test_clear_knowledge_base(self):
        """Test clearing the knowledge base."""
        self.qa_system.add_document('Test document', {})
        self.qa_system.clear_knowledge_base()
        
        stats = self.qa_system.get_stats()
        self.assertEqual(stats['total_chunks'], 0)


if __name__ == '__main__':
    unittest.main()
