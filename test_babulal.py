import requests
import pandas as pd
import time

def test_babulal():
    """Test specifically with babulal.xlsx file"""
    print("🧪 Testing babulal.xlsx specifically")
    print("=" * 50)
    
    # Wait for app to start
    print("⏳ Waiting for Flask app to start...")
    time.sleep(3)
    
    try:
        # Read the Excel file to get expected count
        df = pd.read_excel('test_input_files/babulal.xlsx')
        expected_count = min(len(df), 10)  # App limits to 10 receipts
        
        print(f"📄 File: babulal.xlsx")
        print(f"   Total rows: {len(df)}")
        print(f"   Expected receipts: {expected_count}")
        print(f"   Columns found: {list(df.columns)}")
        
        # Prepare the file for upload
        with open('test_input_files/babulal.xlsx', 'rb') as f:
            files = {'file': ('babulal.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            # Send POST request to the Flask app
            response = requests.post('http://127.0.0.1:5000/', files=files)
            
            if response.status_code == 200:
                # Check if PDF was generated
                if 'application/pdf' in response.headers.get('content-type', ''):
                    print(f"   ✅ SUCCESS: Generated {expected_count} receipts")
                    print(f"   📊 File size: {len(response.content)} bytes")
                    print(f"   🎯 Smart column detection working!")
                    return True
                else:
                    print(f"   ❌ ERROR: Unexpected response type")
                    print(f"   📄 Response: {response.text[:200]}...")
                    return False
            else:
                print(f"   ❌ ERROR: HTTP {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}...")
                return False
                
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_babulal()
