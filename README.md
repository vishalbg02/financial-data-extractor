# Financial Data Extractor with RAG Q&A

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Advanced AI-powered financial data extraction system with **Retrieval Augmented Generation (RAG)** for question answering.

## 🌟 Features

### Enhanced Data Extraction & Analysis
- 📊 **Multi-Source Support:** Extract from PDF, Excel, and CSV files
- 🔍 **Intelligent Matching:** Fuzzy matching and semantic similarity
- 📈 **16 Financial Metrics:** Comprehensive ratio analysis automatically
  - Profitability: Margins, ROA, ROE, ROIC
  - Liquidity: Current, Quick, Cash ratios
  - Leverage: Debt-to-Equity, Debt ratio
  - Efficiency: Asset, Inventory, Receivables turnover
- 🎨 **Interactive Visualizations:** Dynamic charts and graphs
- 🤖 **OCR Support:** Extract from scanned documents

### Advanced Analytics (NEW)
- 🏥 **Financial Health Score:** 0-100 rating with comprehensive analysis
- 🔍 **Anomaly Detection:** Automatic identification of concerning metrics
- 💡 **Insights Generation:** Actionable recommendations based on data
- 📄 **Automated Reports:** One-click comprehensive analysis reports
- 📈 **Trend Indicators:** Visual performance indicators for all metrics

### Integrated Question Answering (RAG)
- 💬 **Natural Language Q&A:** Ask questions about your documents
- 🧠 **Context-Aware Answers:** Enhanced with calculated financial metrics
- 📚 **Multi-Document Support:** Query across multiple files simultaneously
- 🎯 **Source Citations:** View exact document sources for answers
- ⚡ **Seamless Integration:** Single upload for both extraction and Q&A
- 💡 **Smart Suggestions:** Context-aware question recommendations

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
- [**✨ Enhancements Guide**](docs/ENHANCEMENTS.md) - **NEW: Detailed guide to all new features**
- [**Project Structure**](PROJECT_STRUCTURE.md) - Complete file organization
- [**Implementation Summary**](IMPLEMENTATION_SUMMARY.md) - Development overview

## ✨ What's New

### Latest Enhancements (Current Version)

🎯 **Seamless RAG Integration**
- Single upload workflow - files automatically indexed for both extraction and Q&A
- Integrated Q&A panel directly in extraction tab
- Context-aware question suggestions based on extracted data

📊 **Enhanced Financial Metrics** (16 total)
- Added ROIC (Return on Invested Capital)
- Added Cash Ratio and Working Capital Ratio
- Added Debt Ratio
- Added Receivables Turnover
- Complete coverage of Profitability, Liquidity, Leverage, and Efficiency

🏥 **Advanced Analytics**
- **Financial Health Score**: 0-100 rating with 5-tier classification
- **Anomaly Detection**: Automatic identification of concerning metrics with severity levels
- **Insights Generation**: 8+ types of actionable recommendations
- **Automated Reports**: One-click comprehensive analysis in Markdown format

🧠 **Context-Aware Q&A**
- Questions automatically enhanced with calculated metrics
- Intelligent keyword mapping to relevant financial data
- Cross-tab metric sharing for consistent answers
- Visual indicators when metric enhancement is active

📈 **Visual Enhancements**
- Trend indicators (📈📉➡️) for all metrics
- Color-coded health ratings (🟢🟡🟠🔴)
- Severity icons for anomalies (🚨⚠️)
- Organized metric displays by category

See [ENHANCEMENTS.md](docs/ENHANCEMENTS.md) for complete details.

## 🎯 Use Cases

### 1. Comprehensive Financial Analysis
- Upload financial statements (annual reports, quarterly statements)
- **Automatically get**:
  - 16 calculated financial metrics
  - Financial health score and rating
  - Anomaly detection and warnings
  - Actionable insights and recommendations
  - Automated summary reports

### 2. Interactive Document Q&A
- Ask natural language questions about uploaded documents
- Get answers enhanced with calculated metrics
- View source citations from original documents
- Examples:
  - "What was the revenue growth in Q4?"
  - "Explain the liquidity position" → Get answer + Current/Quick/Cash ratios
  - "What is the debt-to-equity ratio?" → Document context + calculated value
  - "Summarize the cash flow statement"

### 3. Financial Health Monitoring
- Upload periodic financial reports
- Track health score over time
- Identify emerging issues via anomaly detection
- Get automated insights on financial trends
- Generate reports for stakeholders

### 4. Combined Analysis Workflow
- **Single Upload** → Multiple benefits:
  1. Extract structured financial metrics
  2. Calculate ratios and health score
  3. Detect anomalies automatically
  4. Ask questions about document details
  5. Generate comprehensive reports
- **Cross-reference** structured data with Q&A answers
- **Export** results in multiple formats

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
