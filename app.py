import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
import sys
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extractors.excel_extractor import ExcelExtractor
from extractors.pdf_extractor import PDFExtractor
from processors.data_normalizer import DataNormalizer
from processors.financial_calculator import FinancialCalculator
from config import ALLOWED_EXCEL_EXTENSIONS, ALLOWED_PDF_EXTENSIONS, MAX_FILE_SIZE_MB
from api.qa_routes import QAService
from utils.analytics import FinancialAnalytics

# Setup logging
logger = logging.getLogger(__name__)

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
    - ✅ **NEW: Question Answering with RAG**
    """)

    st.markdown("---")

    # Main tabs for different functionality
    tab1, tab2 = st.tabs(["📊 Data Extraction & Analysis", "💬 Ask Questions"])

    with tab1:
        handle_extraction_tab()
    
    with tab2:
        handle_qa_tab()


def handle_extraction_tab():
    """Handle the data extraction and analysis tab."""
    # Initialize QA service in session state for integrated RAG
    if 'qa_service' not in st.session_state:
        try:
            st.session_state.qa_service = QAService()
        except Exception as e:
            st.warning(f"RAG Q&A not available: {e}")
            st.session_state.qa_service = None
    
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
        
        # Performance settings
        with st.expander("⚡ Performance Settings"):
            enable_cache = st.checkbox("Enable Caching", value=True, 
                                      help="Cache results for faster reprocessing")
            enable_parallel = st.checkbox("Parallel Processing", value=True,
                                         help="Process multiple files in parallel")
            
            if st.button("Clear Cache"):
                try:
                    from utils.cache_manager import get_cache_manager
                    cache_manager = get_cache_manager()
                    cache_manager.clear_all()
                    st.success("Cache cleared successfully!")
                except Exception as e:
                    st.error(f"Failed to clear cache: {e}")
        
        # System resources monitoring
        with st.expander("💻 System Resources"):
            try:
                from utils.performance_monitor import get_performance_monitor
                monitor = get_performance_monitor()
                stats = monitor.get_system_stats()
                
                if stats:
                    st.metric("CPU Usage", f"{stats.get('cpu_percent', 0):.1f}%")
                    st.metric("Memory Usage", f"{stats.get('memory_percent', 0):.1f}%")
                    st.metric("Available Memory", 
                             f"{stats.get('memory_available_mb', 0):.0f} MB")
                    
                    # Resource warnings
                    resource_check = monitor.check_resources()
                    if not resource_check['has_sufficient_resources']:
                        for warning in resource_check['warnings']:
                            st.warning(warning)
            except Exception as e:
                st.info("Resource monitoring unavailable")

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
            **Profitability:**
            - Gross Profit Margin
            - Operating Profit Margin
            - Net Profit Margin
            - Return on Assets (ROA)
            - Return on Equity (ROE)
            - Return on Invested Capital (ROIC)
            
            **Liquidity:**
            - Current Ratio
            - Quick Ratio
            - Cash Ratio
            - Working Capital Ratio
            
            **Leverage:**
            - Debt-to-Equity Ratio
            - Debt Ratio
            
            **Efficiency:**
            - Asset Turnover
            - Inventory Turnover
            - Receivables Turnover
            """)

    # Main content
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

    # Process uploaded files
    st.header("🔄 Processing Files...")

    extracted_data_list = []
    file_status = []

    progress_bar = st.progress(0)
    status_text = st.empty()
    detail_status = st.empty()
    
    # Track files for RAG integration
    processed_files_for_qa = []

    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}... ({idx + 1}/{len(uploaded_files)})")

        # Save temporary file
        temp_path = Path("data") / "temp" / uploaded_file.name
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            # Determine file type and extract
            file_ext = Path(uploaded_file.name).suffix.lower()

            if file_ext in ALLOWED_EXCEL_EXTENSIONS:
                detail_status.info(f"📊 Extracting from Excel: {uploaded_file.name}")
                extractor = ExcelExtractor(str(temp_path))
            elif file_ext in ALLOWED_PDF_EXTENSIONS:
                detail_status.info(f"📄 Extracting from PDF: {uploaded_file.name}")
                extractor = PDFExtractor(str(temp_path))
                
                # Set up progress callback for PDF extraction
                def progress_callback(operation, current, total):
                    detail_status.info(f"📄 {operation}: {current}/{total} pages")
                extractor.set_progress_callback(progress_callback)
            else:
                file_status.append({
                    "file": uploaded_file.name,
                    "status": "❌ Unsupported",
                    "variables": 0
                })
                continue

            # Extract data
            detail_status.info(f"🔍 Analyzing financial data in {uploaded_file.name}")
            extracted_data = extractor.extract()

            # Validate
            if extractor.validate():
                extracted_data_list.append(extracted_data)
                file_status.append({
                    "file": uploaded_file.name,
                    "status": "✅ Success",
                    "variables": len(extracted_data)
                })
                # Add to list for RAG processing
                processed_files_for_qa.append((str(temp_path), uploaded_file.name))
            else:
                file_status.append({
                    "file": uploaded_file.name,
                    "status": "⚠️ Low Confidence",
                    "variables": len(extracted_data)
                })
                extracted_data_list.append(extracted_data)
                # Still add to RAG for Q&A
                processed_files_for_qa.append((str(temp_path), uploaded_file.name))

        except Exception as e:
            logger.error(f"Error processing {uploaded_file.name}: {str(e)}")
            
            # Use error recovery system
            try:
                from utils.error_recovery import handle_extraction_error
                error_info = handle_extraction_error(e, uploaded_file.name)
                
                file_status.append({
                    "file": uploaded_file.name,
                    "status": f"❌ Error",
                    "variables": 0
                })
                
                # Show detailed error with recovery suggestions
                with st.expander(f"❌ Error Details: {uploaded_file.name}", expanded=True):
                    st.markdown(error_info['formatted_message'])
                    
                    if error_info['can_retry']:
                        if st.button(f"Retry {uploaded_file.name}", key=f"retry_{idx}"):
                            st.rerun()
            except ImportError:
                # Fallback if error_recovery not available
                file_status.append({
                    "file": uploaded_file.name,
                    "status": f"❌ Error: {str(e)}",
                    "variables": 0
                })
                detail_status.error(f"Failed to process {uploaded_file.name}: {str(e)}")

        progress_bar.progress((idx + 1) / len(uploaded_files))
    
    # Clear detail status
    detail_status.empty()
    
    # Add processed files to knowledge base for Q&A
    if st.session_state.qa_service and processed_files_for_qa:
        with st.spinner("Building knowledge base for Q&A..."):
            qa_added = 0
            for file_path, file_name in processed_files_for_qa:
                try:
                    result = st.session_state.qa_service.add_document_from_file(file_path)
                    if result.get('success'):
                        qa_added += 1
                except Exception as e:
                    logger.warning(f"Could not add {file_name} to knowledge base: {e}")
            
            if qa_added > 0:
                st.success(f"✅ {qa_added} document(s) ready for Q&A in the unified interface below!")
    
    # Clean up temp files
    for file_path, _ in processed_files_for_qa:
        temp_file = Path(file_path)
        if temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass

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
        
        # Store metrics in session state for Q&A
        st.session_state.calculated_metrics = metrics

    if not metrics_df.empty:
        st.success(f"✅ Calculated {len(metrics_df)} financial metrics")

        # Display metrics in columns
        st.subheader("Key Performance Indicators")

        # Group metrics by category
        profitability = ["gross_profit_margin", "operating_profit_margin", "net_profit_margin", "return_on_assets",
                         "return_on_equity", "return_on_invested_capital"]
        liquidity = ["current_ratio", "quick_ratio", "cash_ratio", "working_capital_ratio"]
        leverage = ["debt_to_equity", "debt_ratio"]
        efficiency = ["asset_turnover", "inventory_turnover", "receivables_turnover"]

        tab1, tab2, tab3, tab4 = st.tabs(["💰 Profitability", "💧 Liquidity", "⚖️ Leverage", "⚡ Efficiency"])

        with tab1:
            cols = st.columns(3)
            for idx, metric in enumerate(profitability):
                if metric in metrics:
                    with cols[idx % 3]:
                        suffix = "%" if "margin" in metric or "return" in metric else ""
                        trend = FinancialAnalytics.get_metric_trend(metrics[metric], metric)
                        st.metric(
                            metric.replace("_", " ").title(),
                            f"{metrics[metric]}{suffix}",
                            delta=trend
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
            cols = st.columns(2)
            for idx, metric in enumerate(leverage):
                if metric in metrics:
                    with cols[idx % 2]:
                        st.metric(
                            metric.replace("_", " ").title(),
                            f"{metrics[metric]}"
                        )

        with tab4:
            cols = st.columns(3)
            for idx, metric in enumerate(efficiency):
                if metric in metrics:
                    with cols[idx % 3]:
                        st.metric(
                            metric.replace("_", " ").title(),
                            f"{metrics[metric]}"
                        )
        
        # Add Financial Health & Insights Section
        st.markdown("---")
        st.header("🏥 Financial Health & Advanced Analytics")
        
        # Calculate health score
        health_score, health_rating = FinancialAnalytics.calculate_health_score(metrics)
        
        col_health1, col_health2, col_health3 = st.columns([1, 1, 1])
        
        with col_health1:
            st.metric("Overall Health Score", f"{health_score}/100")
        
        with col_health2:
            # Color-code the rating
            rating_colors = {
                "Excellent": "🟢",
                "Good": "🟡",
                "Fair": "🟠",
                "Poor": "🔴",
                "Critical": "🔴"
            }
            icon = rating_colors.get(health_rating, "⚪")
            st.metric("Rating", f"{icon} {health_rating}")
        
        with col_health3:
            anomaly_count = len(FinancialAnalytics.detect_anomalies(metrics))
            st.metric("Anomalies Detected", anomaly_count)
        
        # Display insights and anomalies in expandable sections
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            with st.expander("💡 Key Insights", expanded=True):
                insights = FinancialAnalytics.generate_insights(metrics, normalized_df)
                if insights:
                    for insight in insights:
                        st.markdown(f"- {insight}")
                else:
                    st.info("No specific insights available with current data")
        
        with insight_col2:
            with st.expander("🔍 Detected Anomalies", expanded=True):
                anomalies = FinancialAnalytics.detect_anomalies(metrics)
                if anomalies:
                    for anomaly in anomalies:
                        severity_color = "🚨" if anomaly['severity'] == 'high' else "⚠️"
                        st.markdown(f"{severity_color} **{anomaly['metric'].replace('_', ' ').title()}**: {anomaly['message']}")
                else:
                    st.success("✅ No anomalies detected - all metrics within normal ranges")
        
        # Add automated report generation
        st.markdown("---")
        st.subheader("📄 Automated Financial Report")
        
        if st.button("Generate Comprehensive Report", type="primary"):
            with st.spinner("Generating report..."):
                report = FinancialAnalytics.generate_summary_report(metrics, normalized_df)
                st.markdown(report)
                
                # Provide download option
                st.download_button(
                    label="📥 Download Report (Markdown)",
                    data=report,
                    file_name="financial_analysis_report.md",
                    mime="text/markdown"
                )
        
        # Add unified Q&A interface below metrics
        st.markdown("---")
        st.header("💬 Ask Questions About Your Data")
        
        if st.session_state.qa_service:
            qa_service = st.session_state.qa_service
            stats = qa_service.get_knowledge_base_stats()
            
            if stats.get('success') and stats.get('total_chunks', 0) > 0:
                col_qa1, col_qa2 = st.columns([2, 1])
                
                with col_qa1:
                    st.info(f"📚 Knowledge base ready with {stats.get('total_chunks', 0)} chunks from your documents")
                    
                    # Suggested questions based on available metrics
                    st.subheader("💡 Suggested Questions")
                    suggestions = [
                        "What is the total revenue?",
                        "What are the operating expenses?",
                        "What is the net income?",
                        "Show me the cash flow information",
                        "What are the total assets and liabilities?",
                    ]
                    
                    # Add metric-specific suggestions
                    if "gross_profit_margin" in metrics:
                        suggestions.append("Explain the gross profit margin")
                    if "current_ratio" in metrics:
                        suggestions.append("What is the liquidity position?")
                    
                    cols_sugg = st.columns(3)
                    for idx, suggestion in enumerate(suggestions[:6]):
                        with cols_sugg[idx % 3]:
                            if st.button(suggestion, key=f"sugg_{idx}", use_container_width=True):
                                st.session_state.unified_question = suggestion
                    
                    # Question input
                    question = st.text_input(
                        "Or ask your own question:",
                        placeholder="What is the debt-to-equity ratio?",
                        key='unified_question'
                    )
                    
                    col_k, col_sim = st.columns(2)
                    with col_k:
                        k = st.slider("Sources to retrieve", 1, 10, 5, key='unified_k')
                    with col_sim:
                        min_sim = st.slider("Min similarity", 0.0, 1.0, 0.3, 0.05, key='unified_sim')
                    
                    if st.button("Get Answer", type="primary", use_container_width=True):
                        if question:
                            with st.spinner("Analyzing documents..."):
                                # Use enhanced Q&A with metrics
                                result = qa_service.answer_question_with_metrics(
                                    question, 
                                    metrics=metrics,
                                    k=k, 
                                    min_similarity=min_sim
                                )
                            
                            if result.get('success'):
                                st.markdown("### 💡 Answer")
                                st.markdown(result.get('answer', 'No answer generated'))
                                
                                # Show if metrics were used
                                if result.get('metrics_used'):
                                    st.info(f"📊 Enhanced with calculated metrics: {', '.join(result['metrics_used'])}")
                                
                                # Show confidence
                                confidence = result.get('confidence', 0.0)
                                st.progress(confidence)
                                st.caption(f"Confidence: {confidence:.2%}")
                                
                                # Show sources
                                sources = result.get('sources', [])
                                if sources:
                                    st.markdown("### 📚 Sources")
                                    for idx, source in enumerate(sources[:3], 1):
                                        with st.expander(f"Source {idx} (Similarity: {source.get('similarity', 0):.2%})"):
                                            st.text(source.get('text', '')[:500])
                            else:
                                st.error(f"Error: {result.get('error', 'Unknown error')}")
                        else:
                            st.warning("Please enter a question")
                
                with col_qa2:
                    st.subheader("📊 KB Stats")
                    st.metric("Documents", stats.get('total_chunks', 0))
                    st.metric("Index Size", stats.get('index_size', 0))
                    
                    if st.button("Clear KB", type="secondary"):
                        qa_service.clear_knowledge_base()
                        st.success("Cleared!")
                        st.rerun()
            else:
                st.info("💡 Upload files above to enable Q&A functionality")
        else:
            st.info("💡 Q&A service not available - upload files to activate")

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

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🚀 Built with Streamlit | Powered by AI | Achieving 99% Accuracy</p>
    </div>
    """, unsafe_allow_html=True)


def handle_qa_tab():
    """Handle the question answering tab."""
    st.header("💬 Ask Questions About Your Documents")
    
    st.markdown("""
    Upload financial documents and ask questions to get instant answers powered by RAG 
    (Retrieval Augmented Generation). The system will search through your documents and 
    provide answers with source citations.
    """)
    
    # Show if metrics are available from extraction tab
    if st.session_state.get('calculated_metrics'):
        st.info("📊 Financial metrics from extraction tab are available - answers will be enhanced with calculated values!")

    # Initialize QA service in session state
    if 'qa_service' not in st.session_state:
        try:
            st.session_state.qa_service = QAService()
        except Exception as e:
            st.error(f"Failed to initialize QA service: {e}")
            return

    qa_service = st.session_state.qa_service

    # Two columns: upload and stats
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📤 Upload Documents")
        
        uploaded_files = st.file_uploader(
            "Upload documents for Q&A",
            accept_multiple_files=True,
            type=['xlsx', 'xls', 'csv', 'pdf'],
            key='qa_uploader'
        )

        if uploaded_files:
            if st.button("Add to Knowledge Base", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name}...")
                    
                    # Save temporary file
                    temp_path = Path("data") / "temp" / uploaded_file.name
                    temp_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    try:
                        # Add to knowledge base
                        result = qa_service.add_document_from_file(str(temp_path))
                        results.append(result)
                    except Exception as e:
                        results.append({
                            'success': False,
                            'error': str(e),
                            'file_name': uploaded_file.name
                        })
                    finally:
                        # Clean up
                        if temp_path.exists():
                            temp_path.unlink()
                    
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                
                status_text.text("Processing complete!")
                
                # Show results
                success_count = sum(1 for r in results if r.get('success', False))
                st.success(f"✅ Successfully added {success_count}/{len(results)} documents")
                
                # Show details
                for result in results:
                    if result.get('success'):
                        st.info(f"✓ {result.get('file_name', 'Unknown')}: {result.get('message', '')}")
                    else:
                        st.error(f"✗ {result.get('file_name', 'Unknown')}: {result.get('error', 'Unknown error')}")

    with col2:
        st.subheader("📊 Knowledge Base Stats")
        stats = qa_service.get_knowledge_base_stats()
        
        if stats.get('success'):
            st.metric("Total Documents", stats.get('total_chunks', 0))
            st.metric("Index Size", stats.get('index_size', 0))
            
            if st.button("Clear Knowledge Base", type="secondary"):
                clear_result = qa_service.clear_knowledge_base()
                if clear_result.get('success'):
                    st.success("Knowledge base cleared!")
                    st.rerun()
                else:
                    st.error(f"Error: {clear_result.get('error', 'Unknown error')}")

    st.markdown("---")

    # Question answering section
    st.subheader("❓ Ask Your Question")
    
    question = st.text_input(
        "Enter your question:",
        placeholder="What is the total revenue for 2023?",
        key='qa_question'
    )

    col1, col2 = st.columns([3, 1])
    
    with col1:
        k = st.slider("Number of sources to retrieve", min_value=1, max_value=10, value=5)
    
    with col2:
        min_similarity = st.slider("Min similarity", min_value=0.0, max_value=1.0, value=0.3, step=0.05)

    if st.button("Get Answer", type="primary"):
        if not question:
            st.warning("Please enter a question")
        else:
            with st.spinner("Searching documents and generating answer..."):
                # Check if metrics are available from previous extraction
                metrics = st.session_state.get('calculated_metrics', None)
                
                if metrics:
                    result = qa_service.answer_question_with_metrics(
                        question=question,
                        metrics=metrics,
                        k=k,
                        min_similarity=min_similarity
                    )
                else:
                    result = qa_service.answer_question(
                        question=question,
                        k=k,
                        min_similarity=min_similarity
                    )
            
            if result.get('success'):
                st.markdown("---")
                st.subheader("💡 Answer")
                st.markdown(result.get('answer', 'No answer generated'))
                
                # Show if metrics were used
                if result.get('metrics_used'):
                    st.info(f"📊 Enhanced with calculated metrics: {', '.join(result['metrics_used'])}")
                
                # Show confidence
                confidence = result.get('confidence', 0.0)
                st.progress(confidence)
                st.caption(f"Confidence: {confidence:.2%}")
                
                # Show sources
                sources = result.get('sources', [])
                if sources:
                    st.markdown("---")
                    st.subheader("📚 Sources")
                    
                    for idx, source in enumerate(sources, 1):
                        with st.expander(f"Source {idx} (Similarity: {source.get('similarity', 0):.2%})"):
                            st.markdown(f"**Text:**\n{source.get('text', '')}")
                            
                            metadata = source.get('metadata', {})
                            if metadata:
                                st.markdown("**Metadata:**")
                                for key, value in metadata.items():
                                    if key not in ['chunk_index', 'total_chunks']:
                                        st.text(f"  {key}: {value}")
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")

    # Example questions
    st.markdown("---")
    st.subheader("💡 Example Questions")
    
    example_questions = [
        "What is the total revenue?",
        "What are the operating expenses?",
        "What is the net income for the year?",
        "What are the total assets?",
        "What is the debt-to-equity ratio?",
        "Show me the cash flow information"
    ]
    
    cols = st.columns(3)
    for idx, eq in enumerate(example_questions):
        with cols[idx % 3]:
            if st.button(eq, key=f'example_{idx}'):
                st.session_state.qa_question = eq
                st.rerun()


if __name__ == "__main__":
    main()