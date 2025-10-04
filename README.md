# Financial Data Extractor with RAG Q&A

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Advanced AI-powered financial data extraction system with **Retrieval Augmented Generation (RAG)** for question answering.

## 🌟 Features

### Data Extraction (Original)
- 📊 **Multi-Source Support:** Extract from PDF, Excel, and CSV files
- 🔍 **Intelligent Matching:** Fuzzy matching and semantic similarity
- 📈 **Financial Metrics:** Calculate 20+ financial ratios automatically
- 🎨 **Visualizations:** Interactive charts and graphs
- 🤖 **OCR Support:** Extract from scanned documents

### Question Answering (NEW - RAG)
- 💬 **Natural Language Q&A:** Ask questions about your documents
- 🧠 **Semantic Search:** Find relevant information using AI embeddings
- 📚 **Multi-Document Support:** Query across multiple files
- 🎯 **Source Citations:** View exact document sources for answers
- ⚡ **Fast Retrieval:** Sub-second response times

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/vishalbg02/financial-data-extractor.git
cd financial-data-extractor

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Example Usage

```python
from api.qa_routes import QAService

# Initialize Q&A service
qa = QAService()

# Add a financial document
qa.add_document_from_file('annual_report.pdf')

# Ask questions
answer = qa.answer_question("What is the total revenue?")
print(answer['answer'])
print(f"Confidence: {answer['confidence']:.2%}")
```

## 📖 Documentation

- [**Quick Start Guide**](docs/QUICK_START.md) - Get started in 5 minutes
- [**RAG Documentation**](docs/RAG_README.md) - Technical details of RAG system
- [**Integration Guide**](docs/INTEGRATION_GUIDE.md) - How RAG integrates with extraction
- [**Project Structure**](PROJECT_STRUCTURE.md) - Complete file organization
- [**Implementation Summary**](IMPLEMENTATION_SUMMARY.md) - Development overview

## 🎯 Use Cases

### 1. Financial Data Extraction
- Extract revenue, expenses, assets, liabilities
- Calculate profit margins, ROI, debt ratios
- Compare metrics across periods
- Generate visualizations

### 2. Document Question Answering
- "What was the revenue growth in Q4?"
- "Show me operating expenses"
- "What is the debt-to-equity ratio?"
- "Summarize the cash flow statement"

### 3. Combined Analysis
- Extract structured metrics
- Ask contextual questions
- Cross-reference data points
- Generate comprehensive reports

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              Streamlit Web UI                   │
├─────────────────┬───────────────────────────────┤
│  Data Extract   │   Question Answering (RAG)    │
├─────────────────┼───────────────────────────────┤
│  Extractors     │   TextChunker                 │
│  Normalizer     │   DocumentEmbedder            │
│  Calculator     │   VectorStore (FAISS)         │
│  Visualizer     │   QA Model                    │
└─────────────────┴───────────────────────────────┘
```

## 📊 Supported File Types

| Type | Formats | Features |
|------|---------|----------|
| PDF | `.pdf` | Text extraction, OCR, tables |
| Excel | `.xlsx`, `.xls`, `.csv` | Multi-sheet, formulas |
| Images | Embedded in PDFs | OCR with EasyOCR |

## 🔧 Technology Stack

- **UI:** Streamlit
- **Data Processing:** Pandas, NumPy
- **PDF:** PDFPlumber, PyPDF2, pdf2image
- **OCR:** EasyOCR, Pytesseract
- **ML/AI:** SentenceTransformers, scikit-learn
- **Vector DB:** FAISS
- **Visualization:** Plotly, Matplotlib

## 📈 Performance

| Operation | Time | Memory |
|-----------|------|--------|
| PDF Extraction | 5-30s | ~200MB |
| Excel Extraction | 1-10s | ~150MB |
| Document Embedding | 1-5s | ~500MB |
| Question Answering | ~500ms | ~600MB |

## 🧪 Testing

Run all tests:
```bash
python -m unittest discover tests/
```

Run RAG-specific tests:
```bash
python -m unittest tests.test_rag -v
```

**Test Coverage:**
- ✅ 17 RAG tests (text chunking, embeddings, vector store, Q&A)
- ✅ 3 Extractor tests
- ✅ All tests passing

## 📦 Project Structure

```
financial-data-extractor/
├── api/                    # QA service API
├── models/                 # ML models and RAG components
├── extractors/             # PDF and Excel extractors
├── processors/             # Data normalization and calculation
├── utils/                  # Utilities (chunking, visualization)
├── tests/                  # Test suite
├── docs/                   # Documentation
├── app.py                  # Streamlit UI
└── example_rag.py         # Example script
```

## 🎓 Examples

### Extract Financial Metrics

```python
from extractors.pdf_extractor import PDFExtractor

extractor = PDFExtractor('financial_report.pdf')
data = extractor.extract()
print(data['revenue'])  # Extract revenue
```

### Ask Questions with RAG

```python
from api.qa_routes import QAService

qa = QAService()
qa.add_document_from_file('report.pdf')

# Ask multiple questions
questions = [
    "What is the total revenue?",
    "What are the operating expenses?",
    "What is the net income?"
]

for q in questions:
    answer = qa.answer_question(q)
    print(f"Q: {q}")
    print(f"A: {answer['answer']}\n")
```

### Run Example Script

```bash
python example_rag.py
```

## 🚧 Roadmap

### Current Features ✅
- Document extraction (PDF, Excel)
- Financial metrics calculation
- RAG-based question answering
- Multi-document support

### Planned Features 🔮
- [ ] LLM integration (GPT-4, Claude)
- [ ] Conversation history
- [ ] Chart and image understanding
- [ ] Multi-language support
- [ ] REST API endpoints
- [ ] Batch processing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- SentenceTransformers for embeddings
- FAISS for vector similarity search
- Streamlit for the amazing UI framework
- All open-source contributors

## 📧 Contact

For questions or support, please open an issue on GitHub.

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Built with ❤️ for financial data analysis and AI-powered insights**
