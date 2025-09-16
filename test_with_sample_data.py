#!/usr/bin/env python3
"""
Test Script with Actual Sample Data
Shows real outputs from test files
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_with_sample_files():
    """Test with actual sample files"""
    print("HAND RECEIPT GENERATOR - SAMPLE DATA TESTING")
    print("Testing with actual sample files...")
    print("=" * 80)
    
    try:
        from utils import ExcelProcessor, convert_to_words
        from config import get_config
        
        config = get_config()
        processor = ExcelProcessor(config)
        
        # Get sample files
        test_dir = Path("test_input_files")
        sample_files = list(test_dir.glob("*.xlsx"))
        
        print(f"Found {len(sample_files)} sample files:")
        for file in sample_files:
            print(f"  - {file.name}")
        
        # Test with first few files
        for i, file_path in enumerate(sample_files[:3]):
            print(f"\n{'='*60}")
            print(f"SAMPLE FILE {i+1}: {file_path.name}")
            print(f"{'='*60}")
            
            try:
                # Read file
                df = pd.read_excel(file_path, nrows=5)  # Limit to 5 rows for testing
                
                print(f"📊 File Info:")
                print(f"   - Rows: {len(df)}")
                print(f"   - Columns: {list(df.columns)}")
                
                # Find columns
                payee_col, amount_col, work_col, error = processor.find_columns(df)
                
                if all([payee_col, amount_col, work_col]):
                    print(f"✅ Columns found:")
                    print(f"   - Payee: {payee_col}")
                    print(f"   - Amount: {amount_col}")
                    print(f"   - Work: {work_col}")
                    
                    # Process data
                    receipts = processor.process_data(df, payee_col, amount_col, work_col)
                    
                    print(f"📋 Processed Receipts:")
                    for j, receipt in enumerate(receipts[:3]):  # Show first 3
                        print(f"   Receipt {j+1}:")
                        print(f"     - Payee: {receipt['payee']}")
                        print(f"     - Amount: Rs.{receipt['amount']}")
                        print(f"     - Amount in Words: {receipt['amount_words']}")
                        print(f"     - Work: {receipt['work']}")
                        print()
                        
                else:
                    print(f"❌ Column detection failed: {error}")
                    
            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample data test failed: {str(e)}")
        return False

def test_number_conversion():
    """Test number to words conversion with various amounts"""
    print(f"\n{'='*60}")
    print("NUMBER TO WORDS CONVERSION TEST")
    print(f"{'='*60}")
    
    try:
        from utils import convert_to_words
        
        test_amounts = [
            100.50,      # Small amount
            1500.75,     # Medium amount
            25000.00,    # Large amount
            100000.25,   # Very large amount
            999999.99    # Maximum reasonable amount
        ]
        
        print("📊 Number to Words Conversion:")
        for amount in test_amounts:
            words = convert_to_words(amount)
            print(f"   Rs.{amount:>10.2f} -> {words}")
        
        return True
        
    except Exception as e:
        print(f"❌ Number conversion test failed: {str(e)}")
        return False

def test_template_rendering():
    """Test template rendering with sample data"""
    print(f"\n{'='*60}")
    print("TEMPLATE RENDERING TEST")
    print(f"{'='*60}")
    
    try:
        from app import receipt_template
        
        # Sample receipt data
        sample_receipts = [
            {
                'payee': 'Babulal Electric Contractor',
                'amount': '15000.00',
                'amount_words': 'Fifteen Thousand',
                'work': 'Electrical Installation Work'
            },
            {
                'payee': 'Rajkumar Electrical Works',
                'amount': '25000.50',
                'amount_words': 'Twenty Five Thousand And Fifty Paise',
                'work': 'Wiring and Maintenance'
            }
        ]
        
        # Render template
        rendered_html = receipt_template.render(receipts=sample_receipts)
        
        print("✅ Template rendered successfully")
        print(f"   - HTML length: {len(rendered_html)} characters")
        print(f"   - Receipts in template: {sample_receipts[0]['payee'] in rendered_html}")
        print(f"   - Amount in template: {sample_receipts[0]['amount'] in rendered_html}")
        
        # Show sample of rendered HTML
        print(f"\n📄 Sample HTML Output (first 200 chars):")
        print(f"{rendered_html[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Template rendering test failed: {str(e)}")
        return False

def main():
    """Run all sample data tests"""
    tests = [
        test_with_sample_files,
        test_number_conversion,
        test_template_rendering
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append(False)
    
    # Summary
    print(f"\n{'='*80}")
    print("SAMPLE DATA TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total} tests")
    print(f"❌ Failed: {total - passed}/{total} tests")
    print(f"📊 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All sample data tests successful!")
    else:
        print("⚠️  Some tests need attention")

if __name__ == "__main__":
    main()
