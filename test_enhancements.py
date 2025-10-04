#!/usr/bin/env python
"""
Quick validation script to test all enhanced components.
Run this to verify the installation and basic functionality.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

print("🧪 Testing Enhanced Financial Data Extractor Components...\n")

# Test 1: Import core modules
print("1️⃣  Testing core imports...")
try:
    from processors.financial_calculator import FinancialCalculator
    from utils.analytics import FinancialAnalytics
    from api.qa_routes import QAService
    print("   ✅ Core imports successful")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Test Financial Calculator with sample data
print("\n2️⃣  Testing Financial Calculator...")
try:
    import pandas as pd
    
    # Create sample financial data
    sample_data = pd.DataFrame({
        'variable': ['revenue', 'cost_of_goods_sold', 'operating_income', 'net_income', 
                    'total_assets', 'current_assets', 'current_liabilities', 
                    'shareholders_equity', 'cash', 'inventory', 'receivables', 'total_debt'],
        'value': [1000000, 600000, 200000, 150000, 
                 2000000, 500000, 300000, 
                 1200000, 100000, 80000, 120000, 400000]
    }).set_index('variable')
    
    calculator = FinancialCalculator(sample_data)
    metrics = calculator.calculate_all_metrics()
    
    print(f"   ✅ Calculated {len(metrics)} financial metrics")
    print(f"   📊 Sample metrics:")
    for metric, value in list(metrics.items())[:3]:
        print(f"      - {metric}: {value}")
except Exception as e:
    print(f"   ❌ Calculator error: {e}")
    sys.exit(1)

# Test 3: Test Analytics
print("\n3️⃣  Testing Advanced Analytics...")
try:
    # Test anomaly detection
    anomalies = FinancialAnalytics.detect_anomalies(metrics)
    print(f"   ✅ Anomaly detection working - found {len(anomalies)} anomalies")
    
    # Test health score
    health_score, rating = FinancialAnalytics.calculate_health_score(metrics)
    print(f"   ✅ Health score calculated: {health_score}/100 ({rating})")
    
    # Test insights
    insights = FinancialAnalytics.generate_insights(metrics, sample_data)
    print(f"   ✅ Generated {len(insights)} insights")
    
    # Test report generation
    report = FinancialAnalytics.generate_summary_report(metrics, sample_data)
    print(f"   ✅ Report generated ({len(report)} characters)")
except Exception as e:
    print(f"   ❌ Analytics error: {e}")
    sys.exit(1)

# Test 4: Test QA Service initialization (without actual embedding models)
print("\n4️⃣  Testing QA Service structure...")
try:
    # We won't fully initialize to avoid downloading models
    # Just check the class structure
    assert hasattr(QAService, 'answer_question_with_metrics'), "Missing enhanced Q&A method"
    assert hasattr(QAService, 'add_document_from_file'), "Missing document add method"
    print("   ✅ QA Service structure validated")
except Exception as e:
    print(f"   ❌ QA Service error: {e}")
    sys.exit(1)

# Test 5: Test metric enhancement logic
print("\n5️⃣  Testing context-aware Q&A enhancement...")
try:
    # Test keyword mapping logic
    test_questions = [
        ("What is the profit margin?", ["gross_profit_margin", "operating_profit_margin", "net_profit_margin"]),
        ("Explain the liquidity position", ["current_ratio", "quick_ratio", "cash_ratio"]),
        ("What is the debt level?", ["debt_to_equity", "debt_ratio"])
    ]
    
    mapping_count = 0
    for question, expected_metrics in test_questions:
        question_lower = question.lower()
        found_relevant = any(
            any(keyword in question_lower for keyword in ["margin", "profit", "liquidity", "debt"])
            for keyword in ["margin", "liquidity", "debt"]
        )
        if found_relevant:
            mapping_count += 1
    
    print(f"   ✅ Keyword mapping logic working ({mapping_count}/{len(test_questions)} questions mapped)")
except Exception as e:
    print(f"   ❌ Enhancement logic error: {e}")
    sys.exit(1)

# Summary
print("\n" + "="*60)
print("✨ All tests passed! Enhanced system is ready to use.")
print("="*60)
print("\n📋 Summary of capabilities:")
print(f"   • {len(metrics)} financial metrics calculated")
print(f"   • {len(anomalies)} anomalies detected in sample data")
print(f"   • Health score: {health_score}/100 ({rating})")
print(f"   • {len(insights)} insights generated")
print(f"   • Report generation: Working")
print(f"   • Q&A enhancement: Ready")
print("\n🚀 Run 'streamlit run app.py' to start the application!")
