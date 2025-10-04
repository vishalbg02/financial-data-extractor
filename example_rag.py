"""Example script demonstrating RAG functionality for financial document Q&A."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api.qa_routes import QAService


def main():
    """Demonstrate RAG Q&A functionality."""
    
    print("=" * 80)
    print("RAG Question Answering for Financial Documents - Example")
    print("=" * 80)
    print()
    
    # Initialize QA service
    print("Initializing QA service...")
    qa_service = QAService()
    print("✓ QA service initialized\n")
    
    # Example: Add a sample document
    print("Adding sample document to knowledge base...")
    sample_text = """
    Financial Report for FY 2023
    
    Income Statement:
    Total Revenue: $10,500,000
    Cost of Goods Sold: $4,200,000
    Gross Profit: $6,300,000
    
    Operating Expenses:
    - Salaries and Wages: $2,100,000
    - Rent: $500,000
    - Marketing: $800,000
    - Other Operating Expenses: $600,000
    Total Operating Expenses: $4,000,000
    
    Operating Income: $2,300,000
    Interest Expense: $150,000
    Net Income: $2,150,000
    
    Balance Sheet:
    Assets:
    - Cash and Equivalents: $3,500,000
    - Accounts Receivable: $2,800,000
    - Inventory: $1,900,000
    - Property and Equipment: $8,500,000
    Total Assets: $16,700,000
    
    Liabilities:
    - Accounts Payable: $1,200,000
    - Short-term Debt: $800,000
    - Long-term Debt: $4,500,000
    Total Liabilities: $6,500,000
    
    Shareholders' Equity: $10,200,000
    
    Cash Flow Statement:
    Operating Cash Flow: $3,200,000
    Investing Cash Flow: -$1,500,000
    Financing Cash Flow: -$800,000
    Net Change in Cash: $900,000
    """
    
    qa_service.qa_system.add_document(
        sample_text,
        metadata={'source': 'Sample Financial Report 2023', 'year': 2023}
    )
    print("✓ Sample document added\n")
    
    # Get knowledge base stats
    stats = qa_service.get_knowledge_base_stats()
    if stats.get('success'):
        print(f"Knowledge Base Stats:")
        print(f"  - Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  - Index size: {stats.get('index_size', 0)}")
        print()
    
    # Example questions
    questions = [
        "What is the total revenue for 2023?",
        "What are the operating expenses?",
        "What is the net income?",
        "What are the total assets?",
        "What is the cash position?",
    ]
    
    print("Asking sample questions:")
    print("-" * 80)
    print()
    
    for i, question in enumerate(questions, 1):
        print(f"Q{i}: {question}")
        
        result = qa_service.answer_question(
            question=question,
            k=3,
            min_similarity=0.2
        )
        
        if result.get('success'):
            print(f"A{i}: {result.get('answer', 'No answer')}")
            print(f"    Confidence: {result.get('confidence', 0):.2%}")
            print(f"    Sources: {result.get('num_sources', 0)}")
            print()
        else:
            print(f"A{i}: Error - {result.get('error', 'Unknown error')}")
            print()
    
    print("-" * 80)
    print("\nExample completed!")
    print("\nTo use the full UI, run:")
    print("  streamlit run app.py")
    print()


if __name__ == "__main__":
    main()
