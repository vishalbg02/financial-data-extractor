# Quick Start Guide - RAG Q&A Feature

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- FAISS for vector similarity search
- SentenceTransformers for embeddings
- All existing dependencies

### 2. Verify Installation

```bash
python example_rag.py
```

This will run a simple example demonstrating the Q&A functionality.

## Using the Streamlit UI

### 1. Launch the Application

```bash
streamlit run app.py
```

### 2. Navigate to Q&A Tab

The application has two tabs:
- **📊 Data Extraction & Analysis** - Original functionality
- **💬 Ask Questions** - New RAG Q&A feature

Click on the "💬 Ask Questions" tab.

### 3. Upload Documents

1. Click on "Upload documents for Q&A"
2. Select one or more PDF or Excel files
3. Click "Add to Knowledge Base"
4. Wait for processing to complete

### 4. Ask Questions

1. Enter your question in the text input field
   - Example: "What is the total revenue?"
   
2. Adjust retrieval parameters (optional):
   - **Number of sources:** How many document chunks to retrieve (1-10)
   - **Min similarity:** Minimum similarity threshold (0-1)

3. Click "Get Answer"

4. View the results:
   - **Answer:** Generated answer based on document content
   - **Confidence:** Similarity score of best matching source
   - **Sources:** Relevant document chunks with similarity scores

### 5. Example Questions

Try these example questions (click the buttons):
- "What is the total revenue?"
- "What are the operating expenses?"
- "What is the net income for the year?"
- "What are the total assets?"
- "What is the debt-to-equity ratio?"
- "Show me the cash flow information"

## Using the Python API

### Basic Usage

```python
from api.qa_routes import QAService

# Initialize service
qa_service = QAService()

# Add a document
result = qa_service.add_document_from_file('path/to/financial_report.pdf')
print(result)

# Ask a question
answer = qa_service.answer_question("What is the total revenue?")
print(answer['answer'])
print(f"Confidence: {answer['confidence']:.2%}")

# View sources
for source in answer['sources']:
    print(f"- {source['text'][:100]}...")
```

### Advanced Usage

```python
# Add multiple documents
import glob

pdf_files = glob.glob('data/*.pdf')
for pdf_file in pdf_files:
    qa_service.add_document_from_file(pdf_file)

# Ask questions with custom parameters
answer = qa_service.answer_question(
    question="What were the operating expenses in Q4?",
    k=10,  # Retrieve more sources
    min_similarity=0.4  # Higher similarity threshold
)

# Get knowledge base statistics
stats = qa_service.get_knowledge_base_stats()
print(f"Total chunks: {stats['total_chunks']}")
print(f"Index size: {stats['index_size']}")

# Clear knowledge base
qa_service.clear_knowledge_base()
```

## Tips for Best Results

### 1. Document Quality
- Use clear, well-formatted documents
- Ensure text is extractable (not pure images)
- For scanned PDFs, OCR will be used automatically

### 2. Question Formulation
- Be specific in your questions
- Use financial terminology present in documents
- Ask one thing at a time

### 3. Parameter Tuning
- **k (number of sources):**
  - Lower (1-3): Faster, more focused
  - Higher (5-10): More context, better for complex questions
  
- **min_similarity:**
  - Lower (0.2-0.3): More permissive, finds more sources
  - Higher (0.4-0.6): More strict, higher quality sources

### 4. Knowledge Base Management
- Add all related documents before asking questions
- Clear and rebuild if documents change significantly
- Monitor knowledge base size for performance

## Supported Document Types

### PDF Files
- **Text-based PDFs:** Direct text extraction
- **Scanned PDFs:** OCR using EasyOCR
- **Tables:** Extracted and included in text
- **Images:** Processed via OCR

### Excel Files
- **Formats:** .xlsx, .xls, .csv
- **Multiple sheets:** All sheets processed
- **Tables:** Row-by-row text conversion
- **Headers:** Column names included

## Troubleshooting

### Issue: Slow Processing
**Symptoms:** Documents take long to add
**Solutions:**
- Check document size (keep under 50MB)
- Ensure sufficient RAM (1GB+ recommended)
- Process fewer documents at once

### Issue: Poor Answers
**Symptoms:** Answers don't match questions
**Solutions:**
- Add more relevant documents
- Lower similarity threshold
- Increase number of sources (k)
- Verify document content is related to question

### Issue: No Sources Found
**Symptoms:** "Could not find relevant information"
**Solutions:**
- Check if documents were added successfully
- Lower similarity threshold to 0.2
- Verify question uses terms from documents
- Add more documents to knowledge base

### Issue: Memory Errors
**Symptoms:** Out of memory crashes
**Solutions:**
- Clear knowledge base and start fresh
- Process smaller documents
- Reduce chunk size in configuration
- Restart the application

## Example Workflow

### Scenario: Analyzing Annual Report

1. **Upload Document**
   ```python
   qa_service.add_document_from_file('annual_report_2023.pdf')
   ```

2. **Explore Content**
   ```python
   # General overview
   qa_service.answer_question("What are the key financial highlights?")
   
   # Specific metrics
   qa_service.answer_question("What is the revenue growth rate?")
   
   # Detailed information
   qa_service.answer_question("What were the major expenses?")
   ```

3. **Cross-Reference**
   - Use Data Extraction tab for exact metrics
   - Use Q&A tab for contextual information
   - Compare structured data with narrative explanations

## Next Steps

1. **Explore Documentation:**
   - Read `docs/RAG_README.md` for technical details
   - Review `docs/INTEGRATION_GUIDE.md` for architecture

2. **Run Tests:**
   ```bash
   python -m unittest tests.test_rag
   ```

3. **Experiment:**
   - Try different document types
   - Test various question formats
   - Adjust retrieval parameters

4. **Integrate:**
   - Combine with existing data extraction
   - Build custom workflows
   - Create automated reports

## Support

- **Documentation:** See `docs/` folder
- **Examples:** Run `example_rag.py`
- **Tests:** Check `tests/test_rag.py`
- **Issues:** Open GitHub issue

## Advanced Topics

### Custom Embeddings
```python
from models.embeddings import DocumentEmbedder

# Use different model
embedder = DocumentEmbedder('paraphrase-MiniLM-L6-v2')
```

### Persistent Storage
```python
# Save knowledge base
qa_service.qa_system.save_knowledge_base('my_kb.faiss')

# Load knowledge base
qa_service.qa_system.load_knowledge_base('my_kb.faiss')
```

### Batch Processing
```python
documents = [
    {'text': doc1_text, 'metadata': {'source': 'doc1.pdf'}},
    {'text': doc2_text, 'metadata': {'source': 'doc2.pdf'}},
]
qa_service.qa_system.add_documents(documents)
```

---

**Happy Querying! 🚀**
