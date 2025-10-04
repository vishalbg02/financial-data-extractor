# RAG Integration Guide

## Overview

This guide explains how the RAG (Retrieval Augmented Generation) system integrates with the existing financial data extraction system.

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Financial Data Extractor                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Original System │         │   RAG System     │          │
│  ├──────────────────┤         ├──────────────────┤          │
│  │                  │         │                  │          │
│  │ • PDF Extractor  │────────▶│ • Text Chunker  │          │
│  │ • Excel Extract. │         │ • Embeddings    │          │
│  │ • Data Normaliz. │         │ • Vector Store  │          │
│  │ • Financial Calc.│         │ • QA Model      │          │
│  │ • Visualization  │         │ • API Service   │          │
│  │                  │         │                  │          │
│  └──────────────────┘         └──────────────────┘          │
│           │                            │                     │
│           └────────────┬───────────────┘                     │
│                        │                                     │
│                 ┌──────▼──────┐                              │
│                 │ Streamlit UI │                             │
│                 │  (Two Tabs)  │                             │
│                 └──────────────┘                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Component Integration

### 1. Extractor Integration

The existing PDF and Excel extractors have been **minimally extended** with a new method:

**File:** `extractors/base_extractor.py`
```python
def extract_full_text(self) -> str:
    """Extract full text content for RAG/QA purposes."""
    return ""
```

**File:** `extractors/pdf_extractor.py`
```python
def extract_full_text(self) -> str:
    """Extract full text from PDF including tables."""
    # Uses existing text_content and tables attributes
    # No changes to core extraction logic
```

**File:** `extractors/excel_extractor.py`
```python
def extract_full_text(self) -> str:
    """Extract full text from Excel sheets."""
    # Uses existing sheets attribute
    # No changes to core extraction logic
```

**Key Points:**
- ✅ No changes to existing `extract()` method
- ✅ No changes to financial variable extraction
- ✅ Reuses existing internal attributes
- ✅ Backward compatible

### 2. Model Integration

The RAG system **reuses** the existing embedding infrastructure:

**Existing:** `models/ai_model.py`
- Already uses SentenceTransformer for semantic matching
- Model: 'all-MiniLM-L6-v2'

**New:** `models/embeddings.py`
- Uses the **same model** for consistency
- Dedicated to document embedding (vs. variable matching)
- Separate class for RAG-specific functionality

**Benefits:**
- Single model loaded in memory
- Consistent semantic understanding
- No redundant downloads

### 3. UI Integration

The Streamlit UI now has **two independent tabs**:

**Tab 1: Data Extraction & Analysis** (Original)
- All existing functionality preserved
- No changes to data extraction workflow
- Same metrics and visualizations

**Tab 2: Ask Questions** (New)
- RAG-based Q&A interface
- Document upload for knowledge base
- Question input and answer display
- Source citation viewer

**Implementation:**
```python
tab1, tab2 = st.tabs(["📊 Data Extraction & Analysis", "💬 Ask Questions"])

with tab1:
    handle_extraction_tab()  # Original functionality

with tab2:
    handle_qa_tab()  # New RAG functionality
```

### 4. API Layer

A new API service provides high-level access:

**File:** `api/qa_routes.py`

**Class:** `QAService`

**Methods:**
- `add_document_from_file()` - Add documents to knowledge base
- `answer_question()` - Ask questions
- `get_knowledge_base_stats()` - Get statistics
- `clear_knowledge_base()` - Reset knowledge base

**Integration:**
- Standalone service (no impact on existing code)
- Uses extractors via composition
- Manages its own vector store

## Data Flow

### Original Flow (Unchanged)

```
Upload File → Extractor → Financial Variables → Normalizer → 
Calculator → Metrics → Visualization
```

### New RAG Flow

```
Upload File → Extractor → Full Text → Chunker → Embeddings → 
Vector Store → Question → Context Retrieval → Answer
```

### Combined Flow

Both flows operate **independently** and can be used together:

1. User uploads financial document
2. **Path 1 (Original):** Extract financial variables → Calculate metrics
3. **Path 2 (RAG):** Extract full text → Build knowledge base → Answer questions

## Configuration

No configuration changes required for existing functionality.

**New Configuration (Optional):**

```python
# config.py
RAG_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "embedding_model": "all-MiniLM-L6-v2",
    "vector_store_path": "data/vector_store/financial_kb",
    "default_k": 5,
    "min_similarity": 0.3
}
```

## Dependencies

**New Dependencies Added:**
- `faiss-cpu==1.7.4` - Vector similarity search
- `langchain==0.1.0` - RAG framework (future use)
- `langchain-community==0.0.10` - Community integrations
- `tiktoken==0.5.2` - Token counting utilities

**Existing Dependencies (Reused):**
- `sentence-transformers==2.2.2` - Already installed
- `numpy`, `pandas` - Already installed

## Testing

**Original Tests:** Unchanged and passing
- `tests/test_extractors.py`
- `tests/test_processors.py`

**New Tests:** Added
- `tests/test_rag.py` - Comprehensive RAG testing

**Run All Tests:**
```bash
python -m unittest discover tests/
```

## Migration Path

### For Existing Users

1. **No Action Required:** Original functionality works as before
2. **Optional:** Use new Q&A tab for questions
3. **Optional:** Install new dependencies if using RAG

### For New Users

Both features available out of the box:
- Extract financial metrics (structured data)
- Ask questions (unstructured queries)

## Use Cases

### When to Use Original System
- Extract specific financial variables
- Calculate financial ratios
- Generate structured reports
- Create visualizations
- Compare metrics across periods

### When to Use RAG System
- Ask open-ended questions
- Explore document content
- Find specific information
- Get context around numbers
- Multi-document search

### Combined Usage
1. Upload documents to both systems
2. Use original system for metrics extraction
3. Use RAG for detailed questions about context
4. Cross-reference structured data with Q&A answers

## Performance Considerations

**Original System:**
- Processing time: ~5-30 seconds per document
- Memory: ~200-500MB

**RAG System:**
- First-time setup: ~1-2 minutes (model download)
- Document indexing: ~1-5 seconds per document
- Question answering: ~0.5-2 seconds per question
- Memory: Additional ~500MB

**Combined:**
- Both can run simultaneously
- Shared embedding model reduces memory
- Independent processing pipelines

## Future Enhancements

### Planned Integrations

1. **Cross-System Features:**
   - Auto-populate Q&A knowledge base from extracted documents
   - Link Q&A answers to specific extracted metrics
   - Unified document management

2. **Advanced RAG:**
   - LLM integration (GPT-4, Claude)
   - Multi-modal support (images, charts)
   - Conversation history

3. **Analytics:**
   - Question analytics
   - Popular queries
   - Coverage analysis

## Troubleshooting

### Common Issues

**Issue:** RAG tab not showing
- **Solution:** Ensure new dependencies are installed

**Issue:** Slow question answering
- **Solution:** Reduce k parameter or check document count

**Issue:** Memory errors
- **Solution:** Process fewer documents or use smaller chunks

**Issue:** Poor answer quality
- **Solution:** Add more relevant documents or adjust similarity threshold

## Support

For questions or issues:
1. Check documentation: `docs/RAG_README.md`
2. Run example: `python example_rag.py`
3. Review tests: `tests/test_rag.py`
4. Open GitHub issue

## Summary

The RAG integration:
- ✅ **Non-invasive:** Minimal changes to existing code
- ✅ **Modular:** Separate components and APIs
- ✅ **Independent:** Original functionality unchanged
- ✅ **Efficient:** Reuses existing infrastructure
- ✅ **Extensible:** Easy to enhance and customize
- ✅ **Tested:** Comprehensive test coverage
- ✅ **Documented:** Clear documentation and examples
