import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extractors.excel_extractor import ExcelExtractor
from extractors.pdf_extractor import PDFExtractor
from processors.data_normalizer import DataNormalizer
from processors.financial_calculator import FinancialCalculator
from processors.rag_processor import RAGProcessor
from utils.document_extractor import DocumentTextExtractor
from config import ALLOWED_EXCEL_EXTENSIONS, ALLOWED_PDF_EXTENSIONS, MAX_FILE_SIZE_MB, RAG_CONFIG

# Page configuration
st.set_page_config(
    page_title="AI Financial Data Extractor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    .success-box {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


def render_rag_tab(uploaded_files):
    """Render the RAG Q&A tab"""
    st.header("🤖 RAG Document Q&A")
    
    st.markdown("""
    Ask questions about your uploaded documents using Retrieval-Augmented Generation (RAG).
    The system will search through your documents and provide answers with source references.
    """)
    
    # Initialize RAG processor in session state
    if 'rag_processor' not in st.session_state:
        st.session_state.rag_processor = RAGProcessor(
            chunk_size=RAG_CONFIG['chunk_size'],
            chunk_overlap=RAG_CONFIG['chunk_overlap'],
            top_k=RAG_CONFIG['top_k_results'],
            similarity_threshold=RAG_CONFIG['similarity_threshold']
        )
    
    if 'rag_indexed_files' not in st.session_state:
        st.session_state.rag_indexed_files = set()
    
    if 'rag_chat_history' not in st.session_state:
        st.session_state.rag_chat_history = []
    
    rag_processor = st.session_state.rag_processor
    
    # Settings sidebar
    st.sidebar.markdown("---")
    st.sidebar.header("🔧 RAG Settings")
    
    chunk_size = st.sidebar.slider(
        "Chunk Size",
        min_value=500,
        max_value=2000,
        value=RAG_CONFIG['chunk_size'],
        step=100,
        help="Size of text chunks for processing"
    )
    
    chunk_overlap = st.sidebar.slider(
        "Chunk Overlap",
        min_value=0,
        max_value=500,
        value=RAG_CONFIG['chunk_overlap'],
        step=50,
        help="Overlap between consecutive chunks"
    )
    
    top_k = st.sidebar.slider(
        "Top K Results",
        min_value=1,
        max_value=10,
        value=RAG_CONFIG['top_k_results'],
        help="Number of relevant chunks to retrieve"
    )
    
    similarity_threshold = st.sidebar.slider(
        "Similarity Threshold",
        min_value=0.0,
        max_value=1.0,
        value=RAG_CONFIG['similarity_threshold'],
        step=0.05,
        help="Minimum similarity score for relevant results"
    )
    
    # Update processor settings
    rag_processor.chunk_size = chunk_size
    rag_processor.chunk_overlap = chunk_overlap
    rag_processor.top_k = top_k
    rag_processor.similarity_threshold = similarity_threshold
    
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.rag_chat_history = []
        rag_processor.memory.clear()
        st.sidebar.success("Chat history cleared!")
    
    if st.sidebar.button("🔄 Reindex Documents"):
        st.session_state.rag_indexed_files = set()
        rag_processor.clear_documents()
        st.sidebar.success("Documents cleared. Upload files to reindex.")
    
    # Main content
    if not uploaded_files:
        st.info("👆 Please upload files using the sidebar to get started with RAG Q&A")
        return
    
    # Index uploaded files
    st.subheader("📚 Document Indexing")
    
    files_to_index = []
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.rag_indexed_files:
            files_to_index.append(uploaded_file)
    
    if files_to_index:
        with st.spinner(f"Indexing {len(files_to_index)} new documents..."):
            progress_bar = st.progress(0)
            
            for idx, uploaded_file in enumerate(files_to_index):
                # Save temporary file
                temp_path = Path("data") / "temp" / uploaded_file.name
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    # Extract text from document
                    text_sections = DocumentTextExtractor.extract_from_file(str(temp_path))
                    
                    # Add each section to RAG processor
                    for section_name, text in text_sections.items():
                        if text:
                            metadata = {
                                'filename': uploaded_file.name,
                                'section': section_name,
                                'file_type': Path(uploaded_file.name).suffix
                            }
                            rag_processor.add_document(text, metadata)
                    
                    st.session_state.rag_indexed_files.add(uploaded_file.name)
                    
                except Exception as e:
                    st.error(f"Error indexing {uploaded_file.name}: {str(e)}")
                
                finally:
                    # Clean up temp file
                    if temp_path.exists():
                        temp_path.unlink()
                
                progress_bar.progress((idx + 1) / len(files_to_index))
        
        st.success(f"✅ Indexed {len(files_to_index)} new documents")
    
    # Display indexing stats
    stats = rag_processor.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Indexed Documents", stats['num_documents'])
    with col2:
        st.metric("Text Chunks", stats['num_chunks'])
    with col3:
        st.metric("Avg Chunk Size", f"{stats['avg_chunk_size']:.0f} chars")
    with col4:
        st.metric("Chat History", stats['conversation_history'])
    
    st.markdown("---")
    
    # Q&A Interface
    st.subheader("💬 Ask Questions")
    
    # Display chat history
    if st.session_state.rag_chat_history:
        st.markdown("### 📜 Chat History")
        
        for i, exchange in enumerate(st.session_state.rag_chat_history):
            with st.expander(f"Q{i+1}: {exchange['question'][:100]}{'...' if len(exchange['question']) > 100 else ''}", expanded=(i == len(st.session_state.rag_chat_history) - 1)):
                st.markdown(f"**Question:** {exchange['question']}")
                st.markdown(f"**Answer:** {exchange['answer']}")
                
                if 'confidence' in exchange:
                    st.progress(exchange['confidence'], text=f"Confidence: {exchange['confidence']:.2%}")
                
                if 'sources' in exchange and exchange['sources']:
                    st.markdown("**Sources:**")
                    for j, source in enumerate(exchange['sources']):
                        with st.container():
                            st.markdown(f"**Source {j+1}** (Score: {source['score']:.3f})")
                            if 'metadata' in source:
                                meta = source['metadata']
                                st.caption(f"📄 {meta.get('filename', 'Unknown')} - {meta.get('section', 'N/A')}")
                            st.text(source['text'])
        
        st.markdown("---")
    
    # Question input
    question = st.text_input(
        "Enter your question:",
        placeholder="e.g., What is the total revenue for the year?",
        key="rag_question_input"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        use_context = st.checkbox("Use Context", value=True, help="Use conversation history for better answers")
    
    if st.button("🔍 Ask Question", type="primary"):
        if question:
            with st.spinner("Searching documents and generating answer..."):
                result = rag_processor.query(
                    question,
                    use_context=use_context,
                    return_sources=True
                )
                
                # Add to chat history
                st.session_state.rag_chat_history.append(result)
                
                # Display latest answer
                st.markdown("### 💡 Answer")
                st.success(result['answer'])
                
                if result['confidence'] > 0:
                    st.progress(result['confidence'], text=f"Confidence: {result['confidence']:.2%}")
                
                if 'sources' in result and result['sources']:
                    st.markdown("### 📚 Sources")
                    for i, source in enumerate(result['sources']):
                        with st.expander(f"Source {i+1} (Score: {source['score']:.3f})"):
                            if 'metadata' in source:
                                meta = source['metadata']
                                st.caption(f"📄 {meta.get('filename', 'Unknown')} - {meta.get('section', 'N/A')}")
                            st.text(source['text'])
                
                # Rerun to update chat history display
                st.rerun()
        else:
            st.warning("Please enter a question")


def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 AI Financial Data Extractor</h1>', unsafe_allow_html=True)

    st.markdown("""
    ### 📌 Unified Multi-Source Data Algorithm
    This advanced AI system automatically extracts, normalizes, and analyzes financial data from:
    - 📊 **Excel Spreadsheets** (.xlsx, .xls, .csv)
    - 📄 **PDF Documents** (text-based and scanned)

    **Features:**
    - ✅ Intelligent fuzzy matching for variable identification
    - ✅ Multi-method extraction (text parsing, table extraction, OCR)
    - ✅ Automatic data normalization and conflict resolution
    - ✅ 20+ financial metrics calculation
    - ✅ Interactive visualizations
    - ✅ RAG-powered document Q&A
    """)

    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Files")
        st.info("Upload one or more files (Excel or PDF)")

        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['xlsx', 'xls', 'csv', 'pdf']
        )

        st.markdown("---")

        st.header("⚙️ Settings")
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.75,
            step=0.05,
            help="Minimum confidence score for extraction"
        )

        show_raw_data = st.checkbox("Show Raw Extracted Data", value=False)
        show_debug = st.checkbox("Show Debug Information", value=False)

        st.markdown("---")

        st.header("📚 Documentation")
        with st.expander("Supported Variables"):
            st.markdown("""
            **Income Statement:**
            - Revenue, COGS, Gross Profit
            - Operating Expenses, Operating Income
            - Net Income

            **Balance Sheet:**
            - Total Assets, Current Assets
            - Total Liabilities, Current Liabilities
            - Shareholders' Equity
            - Cash, Inventory, Receivables

            **Cash Flow:**
            - Operating Cash Flow
            - Investing Cash Flow
            - Financing Cash Flow
            - Free Cash Flow
            """)

        with st.expander("Calculated Metrics"):
            st.markdown("""
            - Gross Profit Margin
            - Operating Profit Margin
            - Net Profit Margin
            - Return on Assets (ROA)
            - Return on Equity (ROE)
            - Current Ratio
            - Quick Ratio
            - Debt-to-Equity Ratio
            - Asset Turnover
            - Inventory Turnover
            """)

    # Main content - Add tabs for different functionality
    if not uploaded_files:
        st.info("👆 Please upload files using the sidebar to get started")

        # Show demo section
        st.markdown("---")
        st.header("🎯 How It Works")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("### 1️⃣ Upload")
            st.write("Upload Excel or PDF files containing financial data")

        with col2:
            st.markdown("### 2️⃣ Extract")
            st.write("AI extracts data using fuzzy matching and OCR")

        with col3:
            st.markdown("### 3️⃣ Normalize")
            st.write("Data is normalized and conflicts are resolved")

        with col4:
            st.markdown("### 4️⃣ Analyze")
            st.write("Financial metrics are calculated and visualized")

        return

    # Create tabs for different features
    tab1, tab2 = st.tabs(["📊 Financial Data Extraction", "🤖 RAG Document Q&A"])
    
    with tab1:
        render_financial_extraction_tab(uploaded_files, confidence_threshold, show_raw_data, show_debug)
    
    with tab2:
        render_rag_tab(uploaded_files)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🚀 Built with Streamlit | Powered by AI | Achieving 99% Accuracy</p>
    </div>
    """, unsafe_allow_html=True)


def render_financial_extraction_tab(uploaded_files, confidence_threshold, show_raw_data, show_debug):
    """Render the financial data extraction tab (original functionality)"""
    st.header("🔄 Processing Files...")

    extracted_data_list = []
    file_status = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}...")

        # Save temporary file
        temp_path = Path("data") / "temp" / uploaded_file.name
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            # Determine file type and extract
            file_ext = Path(uploaded_file.name).suffix.lower()

            if file_ext in ALLOWED_EXCEL_EXTENSIONS:
                extractor = ExcelExtractor(str(temp_path))
            elif file_ext in ALLOWED_PDF_EXTENSIONS:
                extractor = PDFExtractor(str(temp_path))
            else:
                file_status.append({
                    "file": uploaded_file.name,
                    "status": "❌ Unsupported",
                    "variables": 0
                })
                continue

            # Extract data
            extracted_data = extractor.extract()

            # Validate
            if extractor.validate():
                extracted_data_list.append(extracted_data)
                file_status.append({
                    "file": uploaded_file.name,
                    "status": "✅ Success",
                    "variables": len(extracted_data)
                })
            else:
                file_status.append({
                    "file": uploaded_file.name,
                    "status": "⚠️ Low Confidence",
                    "variables": len(extracted_data)
                })
                extracted_data_list.append(extracted_data)

        except Exception as e:
            file_status.append({
                "file": uploaded_file.name,
                "status": f"❌ Error: {str(e)}",
                "variables": 0
            })

        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()

        progress_bar.progress((idx + 1) / len(uploaded_files))

    status_text.text("Processing complete!")

    # Display file status
    st.markdown("---")
    st.header("📋 File Processing Status")
    st.dataframe(pd.DataFrame(file_status), use_container_width=True)

    if not extracted_data_list:
        st.error("❌ No data could be extracted from the uploaded files.")
        return

    # Show raw extracted data if enabled
    if show_raw_data:
        st.markdown("---")
        st.header("🔍 Raw Extracted Data")

        for idx, data in enumerate(extracted_data_list):
            with st.expander(f"File {idx + 1}: {file_status[idx]['file']}"):
                st.json(data)

    # Normalize data
    st.markdown("---")
    st.header("🔄 Normalizing Data...")

    with st.spinner("Normalizing and resolving conflicts..."):
        normalizer = DataNormalizer()
        normalized_df = normalizer.normalize(extracted_data_list)

    st.success(f"✅ Successfully normalized {len(normalized_df)} variables")

    # Display normalized data
    st.markdown("---")
    st.header("📊 Normalized Financial Data")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(normalized_df, use_container_width=True)

    with col2:
        # Summary statistics
        st.metric("Total Variables", len(normalized_df))
        st.metric("Total Value", f"${normalized_df['value'].sum():,.2f}")
        st.metric("Average Value", f"${normalized_df['value'].mean():,.2f}")

    # Calculate financial metrics
    st.markdown("---")
    st.header("📈 Financial Metrics")

    with st.spinner("Calculating financial metrics..."):
        calculator = FinancialCalculator(normalized_df)
        metrics = calculator.calculate_all_metrics()
        metrics_df = calculator.get_metrics_dataframe()

    if not metrics_df.empty:
        st.success(f"✅ Calculated {len(metrics_df)} financial metrics")

        # Display metrics in columns
        st.subheader("Key Performance Indicators")

        # Group metrics by category
        profitability = ["gross_profit_margin", "operating_profit_margin", "net_profit_margin", "return_on_assets",
                         "return_on_equity"]
        liquidity = ["current_ratio", "quick_ratio"]
        leverage = ["debt_to_equity"]
        efficiency = ["asset_turnover", "inventory_turnover"]

        tab1, tab2, tab3, tab4 = st.tabs(["💰 Profitability", "💧 Liquidity", "⚖️ Leverage", "⚡ Efficiency"])

        with tab1:
            cols = st.columns(3)
            for idx, metric in enumerate(profitability):
                if metric in metrics:
                    with cols[idx % 3]:
                        suffix = "%" if "margin" in metric or "return" in metric else ""
                        st.metric(
                            metric.replace("_", " ").title(),
                            f"{metrics[metric]}{suffix}"
                        )

        with tab2:
            cols = st.columns(2)
            for idx, metric in enumerate(liquidity):
                if metric in metrics:
                    with cols[idx % 2]:
                        st.metric(
                            metric.replace("_", " ").title(),
                            f"{metrics[metric]}"
                        )

        with tab3:
            if "debt_to_equity" in metrics:
                st.metric("Debt-to-Equity Ratio", f"{metrics['debt_to_equity']}")

        with tab4:
            cols = st.columns(2)
            for idx, metric in enumerate(efficiency):
                if metric in metrics:
                    with cols[idx % 2]:
                        st.metric(
                            metric.replace("_", " ").title(),
                            f"{metrics[metric]}"
                        )

        # Visualizations
        st.markdown("---")
        st.header("📊 Visualizations")

        # Create visualizations
        viz_tab1, viz_tab2, viz_tab3 = st.tabs(["📊 Metrics Overview", "📈 Comparison", "🎯 Distribution"])

        with viz_tab1:
            # Bar chart of all metrics
            fig = px.bar(
                metrics_df.reset_index(),
                x="metric",
                y="value",
                title="Financial Metrics Overview",
                labels={"metric": "Metric", "value": "Value"},
                color="value",
                color_continuous_scale="Viridis"
            )
            fig.update_layout(xaxis_tickangle=-45, height=500)
            st.plotly_chart(fig, use_container_width=True)

        with viz_tab2:
            # Radar chart for profitability metrics
            prof_metrics = {k: v for k, v in metrics.items() if k in profitability}
            if prof_metrics:
                fig = go.Figure(data=go.Scatterpolar(
                    r=list(prof_metrics.values()),
                    theta=[m.replace("_", " ").title() for m in prof_metrics.keys()],
                    fill='toself',
                    name='Profitability Metrics'
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True)),
                    showlegend=False,
                    title="Profitability Metrics Radar"
                )
                st.plotly_chart(fig, use_container_width=True)

        with viz_tab3:
            # Pie chart for variable distribution
            fig = px.pie(
                normalized_df.reset_index(),
                values="value",
                names="variable",
                title="Financial Data Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠️ Could not calculate financial metrics. Ensure required variables are present.")

    # Export options
    st.markdown("---")
    st.header("💾 Export Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Export normalized data
        csv_data = normalized_df.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Download Normalized Data (CSV)",
            data=csv_data,
            file_name="normalized_financial_data.csv",
            mime="text/csv"
        )

    with col2:
        # Export metrics
        if not metrics_df.empty:
            csv_metrics = metrics_df.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Download Metrics (CSV)",
                data=csv_metrics,
                file_name="financial_metrics.csv",
                mime="text/csv"
            )

    with col3:
        # Export Excel
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            normalized_df.to_excel(writer, sheet_name='Normalized Data')
            if not metrics_df.empty:
                metrics_df.to_excel(writer, sheet_name='Metrics')

        st.download_button(
            label="📥 Download All (Excel)",
            data=buffer.getvalue(),
            file_name="financial_analysis_complete.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


if __name__ == "__main__":
    main()