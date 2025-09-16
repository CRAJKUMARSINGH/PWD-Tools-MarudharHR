import requests
import pandas as pd
import os
import time

def test_excel_file(filename):
    """Test an Excel file and return the number of receipts generated"""
    try:
        # Read the Excel file to get expected count
        df = pd.read_excel(f'test_input_files/{filename}')
        expected_count = min(len(df), 10)  # App limits to 10 receipts
        
        print(f"\n📄 Testing: {filename}")
        print(f"   Expected receipts: {expected_count}")
        
        # Prepare the file for upload
        with open(f'test_input_files/{filename}', 'rb') as f:
            files = {'file': (filename, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            # Send POST request to the Flask app
            response = requests.post('http://127.0.0.1:5000/', files=files)
            
            if response.status_code == 200:
                # Check if PDF was generated (response should be PDF file)
                if 'application/pdf' in response.headers.get('content-type', ''):
                    print(f"   ✅ SUCCESS: Generated {expected_count} receipts")
                    print(f"   📊 File size: {len(response.content)} bytes")
                    return True, expected_count
                else:
                    print(f"   ❌ ERROR: Unexpected response type")
                    return False, 0
            else:
                print(f"   ❌ ERROR: HTTP {response.status_code}")
                return False, 0
                
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, 0

def main():
    print("🧪 Testing MarudharHR Receipt Generator")
    print("=" * 50)
    
    # Wait for app to start
    print("⏳ Waiting for Flask app to start...")
    time.sleep(3)
    
    # Test files to check
    test_files = [
        'small_test.xlsx',      # 3 receipts
        'medium_test.xlsx',     # 7 receipts  
        'large_test.xlsx',      # 12 receipts (limited to 10)
        '01 rasid.xlsx',        # Existing file
        '18 rasid.xlsx',        # Existing file
        '50 rasid.xlsx',        # Existing file
        'input.xlsx',           # Existing file
        'data.xlsx',            # Existing file
        'babulal.xlsx'          # Existing file
    ]
    
    results = []
    total_tested = 0
    total_successful = 0
    
    for filename in test_files:
        if os.path.exists(f'test_input_files/{filename}'):
            success, count = test_excel_file(filename)
            results.append({
                'filename': filename,
                'success': success,
                'receipts': count
            })
            
            if success:
                total_successful += 1
            total_tested += 1
        else:
            print(f"\n📄 {filename} - File not found")
    
    # Summary Report
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {result['filename']}: {result['receipts']} receipts")
    
    print(f"\n📈 Overall Results:")
    print(f"   Total files tested: {total_tested}")
    print(f"   Successful: {total_successful}")
    print(f"   Failed: {total_tested - total_successful}")
    print(f"   Success rate: {(total_successful/total_tested)*100:.1f}%")
    
    if total_successful == total_tested:
        print("\n🎉 All tests passed! Receipt generator is working perfectly.")
    else:
        print(f"\n⚠️  {total_tested - total_successful} test(s) failed. Check the errors above.")

if __name__ == "__main__":
    main()
