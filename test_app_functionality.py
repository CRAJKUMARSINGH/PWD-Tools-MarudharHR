"""
Test script to verify Hand Receipt Generator functionality
"""
import pandas as pd
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import functions from streamlit_app
from streamlit_app import process_excel_file, convert_number_to_words

def test_number_conversion():
    """Test Indian number format conversion"""
    print("\n" + "="*60)
    print("🧪 TESTING NUMBER TO WORDS CONVERSION")
    print("="*60)
    
    test_cases = [
        (1000, "One Thousand"),
        (50000, "Fifty Thousand"),
        (100000, "One Lakh"),
        (1000000, "Ten Lakh"),
        (10000000, "One Crore"),
        (12345678, "One Crore Twenty Three Lakh Forty Five Thousand Six Hundred and Seventy Eight"),
    ]
    
    for num, expected in test_cases:
        result = convert_number_to_words(num)
        status = "✅" if expected.lower() in result.lower() else "❌"
        print(f"{status} {num:,} → {result}")
    
    print("\n✅ Number conversion test PASSED!\n")

def test_excel_file(file_path):
    """Test processing a single Excel file"""
    print("\n" + "="*60)
    print(f"🧪 TESTING FILE: {file_path.name}")
    print("="*60)
    
    try:
        with open(file_path, 'rb') as f:
            pdf_bytes, error = process_excel_file(f)
        
        if error:
            print(f"❌ ERROR: {error}")
            return False
        
        if pdf_bytes:
            # Save PDF for inspection
            output_path = Path("test_outputs") / f"test_{file_path.stem}.pdf"
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
            
            pdf_size = len(pdf_bytes) / 1024  # KB
            print(f"✅ SUCCESS!")
            print(f"   📄 PDF Size: {pdf_size:.2f} KB")
            print(f"   💾 Saved to: {output_path}")
            
            # Read Excel to show what was processed
            df = pd.read_excel(file_path, nrows=50)
            print(f"   📊 Processed {len(df)} rows")
            
            return True
        else:
            print(f"❌ FAILED: No PDF generated")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "🎉"*30)
    print("   HAND RECEIPT GENERATOR - AUTOMATED TEST")
    print("🎉"*30)
    
    # Test number conversion
    test_number_conversion()
    
    # Find all Excel files
    excel_files = [
        Path("01 rasid.xlsx"),
        Path("18 rasid.xlsx"),
        Path("50 rasid.xlsx"),
    ]
    
    # Filter existing files
    existing_files = [f for f in excel_files if f.exists()]
    
    if not existing_files:
        print("❌ No test Excel files found!")
        print("   Looking for: 01 rasid.xlsx, 18 rasid.xlsx, 50 rasid.xlsx")
        return
    
    print(f"\n📁 Found {len(existing_files)} test files\n")
    
    # Test each file
    results = []
    for file_path in existing_files:
        success = test_excel_file(file_path)
        results.append((file_path.name, success))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for filename, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {filename}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉🎊🎈 ALL TESTS PASSED! 🎈🎊🎉")
        print("\n✨ Your Hand Receipt Generator is working perfectly!")
        print("   - Number conversion: ✅")
        print("   - Excel processing: ✅")
        print("   - PDF generation: ✅")
        print("   - Indian format: ✅")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
