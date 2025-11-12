import streamlit as st
import pandas as pd
from jinja2 import Template
from io import BytesIO
import tempfile
import os
from num2words import num2words
from weasyprint import HTML

# Page configuration
st.set_page_config(
    page_title="Hand Receipt Generator (RPWA 28)",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Force cache clear on Streamlit Cloud
import hashlib
import time
CACHE_BUSTER = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

# Receipt template - EXACT format from emd-refund.html
receipt_template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=210mm, height=297mm">
    <title>Hand Receipt (RPWA 28)</title>
    <style>
        body {
            font-family: sans-serif;
            margin: 0;
        }

        @page {
            size: A4 portrait;
            margin: 10mm;
        }

        .container {
            width: 210mm;
            height: 297mm;
            margin: 0 auto;
            border: 2px solid #ccc;
            padding: 20px;
            box-sizing: border-box;
            position: relative;
            page-break-after: always;
        }

        .header {
            text-align: center;
            margin-bottom: 2px;
        }

        .details {
            margin-bottom: 1px;
        }

        .amount-words {
            font-style: italic;
        }

        .signature-area {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        .signature-area td, .signature-area th {
            border: 1px solid #ccc;
            padding: 5px;
            text-align: left;
        }

        .offices {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        .offices td, .offices th {
            border: 1px solid black;
            padding: 5px;
            text-align: left;
            word-wrap: break-word;
        }

        .input-field {
            border-bottom: 1px dotted #ccc;
            padding: 3px;
            width: calc(100% - 10px);
            display: inline-block;
        }

        .seal-container {
            position: absolute;
            left: 10mm;
            bottom: 10mm;
            width: 40mm;
            height: 25mm;
            z-index: 10;
        }

        .seal {
            max-width: 100%;
            max-height: 100%;
            text-align: center;
            line-height: 40mm;
            color: blue;
            display: flex;
            justify-content: space-around;
            align-items: center;
        }

        .bottom-left-box {
            position: absolute;
            bottom: 40mm;
            left: 40mm;
            border: 2px solid black;
            padding: 10px;
            width: 300px;
            text-align: left;
            height: auto;
        }

        .bottom-left-box p {
            margin: 3px 0;
        }

        .bottom-left-box .blue-text {
            color: blue;
        }
    </style>
</head>
<body>
    {% for receipt in receipts %}
    <div class="container">
        <div class="header">
            <h2>Payable to: - {{ receipt.payee }} ( Electric Contractor)</h2>
            <h2>HAND RECEIPT (RPWA 28)</h2>
            <p>(Referred to in PWF&A Rules 418,424,436 & 438)</p>
            <p>Division - PWD Electric Division, Udaipur</p>
        </div>
        <div class="details">
            <p>(1)Cash Book Voucher No. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Date &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>
            <p>(2)Cheque No. and Date &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>
            <p>(3) Pay for ECS Rs.{{ receipt.amount }}/- (Rupees <span class="amount-words">{{ receipt.amount_words }} only</span>)</p>
            <p>(4) Paid by me</p>
            <p>(5) Received from The Executive Engineer PWD Electric Division, Udaipur the sum of Rs. {{ receipt.amount }}/- (Rupees <span class="amount-words">{{ receipt.amount_words }} only</span>)</p>
            <p> Name of work for which payment is made: <span class="input-field">{{ receipt.work }}</span></p>
            <p> Chargeable to Head:- 8443 [EMD-Refund] </p>   
            <table class="signature-area">
                <tr>
                    <td>Witness</td>
                    <td>Stamp</td>
                    <td>Signature of payee</td>
                </tr>
                <tr>
                    <td>Cash Book No. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Page No. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
                    <td></td>
                    <td></td>
                </tr>
            </table>
            <table class="offices">
                <tr>
                    <td>For use in the Divisional Office</td>
                    <td>For use in the Accountant General's office</td>
                </tr>
                <tr>
                    <td>Checked</td>
                    <td>Audited/Reviewed</td>
                </tr>
                <tr>
                    <td>Accounts Clerk</td>
                    <td>
                        DA &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Auditor &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Supdt. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; G.O.
                    </td>
                </tr>
            </table>
        </div>
        <div class="seal-container">
            <div class="seal">
                <p></p>
                <p></p>
                <p></p>
            </div>
        </div>
        <div class="bottom-left-box">
            <p class="blue-text"> Passed for Rs. {{ receipt.amount }}</p>
            <p class="blue-text"> In Words Rupees: {{ receipt.amount_words }} Only</p>
            <p class="blue-text"> Chargeable to Head:- 8443 [EMD-Refund]</p>
            <div class="seal">
                <p>Ar.</p>
                <p>D.A.</p>
                <p>E.E.</p>
            </div>
        </div>
    </div>
    {% endfor %}
</body>
</html>
""")

def convert_number_to_words(num):
    """Convert number to words in Indian format (Crore, Lakh, Thousand)"""
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    
    if num == 0:
        return "Zero"
    
    words = ""
    
    # Crores
    if num >= 10000000:
        crore_part = int(num / 10000000)
        words += convert_number_to_words(crore_part) + " Crore "
        num %= 10000000
    
    # Lakhs
    if num >= 100000:
        lakh_part = int(num / 100000)
        words += convert_number_to_words(lakh_part) + " Lakh "
        num %= 100000
    
    # Thousands
    if num >= 1000:
        thousand_part = int(num / 1000)
        words += convert_number_to_words(thousand_part) + " Thousand "
        num %= 1000
    
    # Hundreds
    if num >= 100:
        hundred_part = int(num / 100)
        words += ones[hundred_part] + " Hundred "
        num %= 100
    
    # Tens and ones
    if num > 0:
        if words != "":
            words += "and "
        
        if num < 10:
            words += ones[int(num)]
        elif num < 20:
            words += teens[int(num - 10)]
        else:
            words += tens[int(num / 10)]
            if num % 10 > 0:
                words += " " + ones[int(num % 10)]
    
    return words.strip()

def find_column(df_columns, possible_names):
    """Find column by matching possible names"""
    for name in possible_names:
        name_lower = name.lower()
        for col in df_columns:
            if name_lower in col.strip().lower():
                return col
    return None

def process_excel_file(file):
    """Process uploaded Excel file and generate PDF"""
    try:
        # Reset file pointer to beginning (CRITICAL for avoiding cached data!)
        file.seek(0)
        
        # Read Excel file
        df = pd.read_excel(file, nrows=50)
        
        # Find required columns
        payee_col = find_column(df.columns, ['Payee Name', 'PayeeName', 'Name', 'Contractor', 'Payee'])
        amount_col = find_column(df.columns, ['Amount', 'Value', 'Cost', 'Payment', 'Total'])
        work_col = find_column(df.columns, ['Work', 'Description', 'Item', 'Project', 'Job'])
        
        if not all([payee_col, amount_col, work_col]):
            missing = []
            if not payee_col: missing.append("Payee Name")
            if not amount_col: missing.append("Amount")
            if not work_col: missing.append("Work")
            return None, f"Missing required columns: {', '.join(missing)}"
        
        # Process data
        receipts = []
        for _, row in df.iterrows():
            try:
                payee = str(row[payee_col]).strip()
                amount = float(row[amount_col])
                work = str(row[work_col]).strip()
                
                if payee and amount > 0 and work:
                    receipts.append({
                        "payee": payee,
                        "amount": amount,
                        "amount_words": convert_number_to_words(int(amount)),
                        "work": work
                    })
            except (ValueError, TypeError):
                continue
        
        if not receipts:
            return None, "No valid data found in the Excel file"
        
        # Generate HTML
        rendered_html = receipt_template.render(receipts=receipts)
        
        # Generate PDF
        pdf_bytes = HTML(string=rendered_html).write_pdf()
        
        return pdf_bytes, None
        
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

# Custom CSS for beautiful styling - Inspired by BillGenerator (v2.1 - Cache Busted)
st.markdown(f"""
<style>
    /* Cache Buster: {CACHE_BUSTER} */
    /* Green Header Styling */
    .main-header {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    .main-header p {
        color: #ecf0f1;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    /* Card styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Custom card */
    .custom-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin: 2rem auto;
        max-width: 900px;
    }
    
    /* Balloon animation - Enhanced */
    .balloon {
        font-size: 3.5rem;
        animation: float 3s ease-in-out infinite;
        display: inline-block;
        margin: 0 0.5rem;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
    }
    
    .balloon:nth-child(1) { animation-delay: 0s; }
    .balloon:nth-child(2) { animation-delay: 0.5s; }
    .balloon:nth-child(3) { animation-delay: 1s; }
    .balloon:nth-child(4) { animation-delay: 1.5s; }
    .balloon:nth-child(5) { animation-delay: 2s; }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        25% { transform: translateY(-15px) rotate(-5deg); }
        50% { transform: translateY(-25px) rotate(0deg); }
        75% { transform: translateY(-15px) rotate(5deg); }
    }
    
    /* Celebration animation */
    .celebrate {
        animation: celebrate 2s ease-in-out infinite;
    }
    
    @keyframes celebrate {
        0%, 100% { transform: scale(1) rotate(0deg); }
        25% { transform: scale(1.1) rotate(-10deg); }
        50% { transform: scale(1.2) rotate(10deg); }
        75% { transform: scale(1.1) rotate(-10deg); }
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(52, 152, 219, 0.3);
    }
    
    .info-box h3 {
        margin-top: 0;
        font-size: 1.3rem;
    }
    
    .info-box ul {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 50px;
        box-shadow: 0 10px 30px rgba(46, 204, 113, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 40px rgba(46, 204, 113, 0.6);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 50px;
        box-shadow: 0 10px 30px rgba(52, 152, 219, 0.4);
        width: 100%;
    }
    
    /* File uploader */
    .stFileUploader {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 2px dashed #2ecc71;
    }
    
    /* Credits section */
    .credits {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 20px;
        margin-top: 3rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    
    .credits h3 {
        color: #2ecc71;
        margin-bottom: 1rem;
    }
    
    .credits p {
        color: #666;
        margin: 0.5rem 0;
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2ecc71;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stInfo {
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header with MORE balloons - REJOICING!
st.markdown("""
<div style='text-align: center; padding: 1.5rem 0;'>
    <span class='balloon'>🎈</span>
    <span class='balloon'>🎊</span>
    <span class='balloon'>🎉</span>
    <span class='balloon'>🎈</span>
    <span class='balloon'>🎊</span>
</div>
""", unsafe_allow_html=True)

# Beautiful Green Header with Credits (INLINE STYLES FOR GUARANTEED DISPLAY)
st.markdown("""
<div style='background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); 
            padding: 2rem; border-radius: 10px; margin-bottom: 2rem; 
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
    <h1 style='color: white; font-size: 2.5rem; font-weight: 700; margin: 0; 
               text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2); text-align: center;'>
        📄 Hand Receipt Generator (RPWA 28)
    </h1>
    <p style='color: #ecf0f1; font-size: 1.1rem; margin: 0.5rem 0 0 0; text-align: center;'>
        🏛️ Generate professional hand receipts for EMD refunds with perfect A4 formatting
    </p>
    <div style='text-align: center; margin-top: 1rem; padding: 0.8rem; 
                background: rgba(255,255,255,0.15); border-radius: 8px;'>
        <p style='margin: 0; font-size: 0.85rem; color: #ecf0f1;'>Prepared on Initiative of</p>
        <p style='margin: 0.3rem 0; font-size: 1.1rem; font-weight: 700; color: white;'>
            Mrs. Premlata Jain, AAO, PWD Udaipur
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content in a card
st.markdown("<div class='custom-card'>", unsafe_allow_html=True)

# Info box
st.markdown("""
<div class='info-box'>
    <h3>📋 How to Use</h3>
    <ul>
        <li><strong>Step 1:</strong> Prepare your Excel file (.xlsx) with required columns</li>
        <li><strong>Step 2:</strong> Upload the file using the button below</li>
        <li><strong>Step 3:</strong> Click Generate PDF and download your receipts</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Required columns info
st.markdown("""
<div class='info-box'>
    <h3>📊 Required Excel Columns</h3>
    <ul>
        <li><strong>Payee Name:</strong> Contractor/payee name (or Name, Contractor, Payee)</li>
        <li><strong>Amount:</strong> Payment amount in numbers (or Value, Cost, Payment, Total)</li>
        <li><strong>Work:</strong> Work description (or Description, Item, Project, Job)</li>
    </ul>
    <p style='margin-top: 1rem; font-size: 0.9rem;'>⚠️ Maximum 50 rows will be processed per file</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for file tracking
if 'last_file_name' not in st.session_state:
    st.session_state.last_file_name = None
if 'last_file_id' not in st.session_state:
    st.session_state.last_file_id = None

# File uploader with unique key to prevent caching issues
st.markdown("<br>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "📁 Choose your Excel file",
    type=['xlsx'],
    help="Upload .xlsx file (max 10MB, 50 rows)",
    key="excel_uploader"
)

if uploaded_file is not None:
    # Generate unique file ID based on name and size
    current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    # Check if this is a NEW file (different from last upload)
    if current_file_id != st.session_state.last_file_id:
        st.session_state.last_file_id = current_file_id
        st.session_state.last_file_name = uploaded_file.name
        # Clear any cached data
        if 'pdf_bytes' in st.session_state:
            del st.session_state.pdf_bytes
    # Show file details with nice styling and celebration
    file_status = "🆕 NEW FILE" if current_file_id != st.session_state.get('last_processed_id') else "✅ READY"
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                padding: 1.5rem; border-radius: 15px; margin: 1rem 0; 
                border-left: 5px solid #2196f3; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <p style='margin: 0; color: #1976d2; font-size: 1.1rem;'>
            <span class='celebrate' style='display: inline-block;'>🎉</span>
            <strong>📁 File:</strong> {uploaded_file.name} 
            <strong>📊 Size:</strong> {uploaded_file.size / 1024:.2f} KB
            <strong>🔖 Status:</strong> {file_status}
            <span class='celebrate' style='display: inline-block;'>🎉</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mini celebration only for NEW files
    if current_file_id != st.session_state.get('last_processed_id'):
        st.balloons()
    
    # Process button with columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        process_button = st.button("🚀 Generate PDF", type="primary", use_container_width=True)
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            # Clear session state
            st.session_state.last_file_id = None
            st.session_state.last_file_name = None
            if 'pdf_bytes' in st.session_state:
                del st.session_state.pdf_bytes
            st.rerun()
    
    if process_button:
        with st.spinner("✨ Processing your file and generating beautiful PDFs..."):
            # Always read fresh data from the uploaded file
            uploaded_file.seek(0)  # Reset to beginning
            pdf_bytes, error = process_excel_file(uploaded_file)
            
            if error:
                st.error(f"❌ {error}")
            else:
                # Store the processed file ID
                st.session_state.last_processed_id = current_file_id
                
                # BIG CELEBRATION!
                st.success("✅ PDF generated successfully!")
                st.balloons()
                
                # Celebration message
                st.markdown("""
                <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); 
                            border-radius: 15px; margin: 1rem 0; border: 2px solid #28a745;'>
                    <p style='margin: 0; font-size: 1.5rem;'>
                        <span class='celebrate' style='display: inline-block;'>🎊</span>
                        <span class='celebrate' style='display: inline-block;'>🎉</span>
                        <span class='celebrate' style='display: inline-block;'>🎈</span>
                        <strong style='color: #155724;'>SUCCESS!</strong>
                        <span class='celebrate' style='display: inline-block;'>🎈</span>
                        <span class='celebrate' style='display: inline-block;'>🎉</span>
                        <span class='celebrate' style='display: inline-block;'>🎊</span>
                    </p>
                    <p style='margin: 0.5rem 0 0 0; color: #155724; font-size: 1.1rem;'>
                        Your receipts are ready to download!
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Download button with celebration
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name="hand_receipts.pdf",
                    mime="application/pdf"
                )
                
                # More balloons!
                st.balloons()

st.markdown("</div>", unsafe_allow_html=True)

# Credits section - Enhanced
st.markdown("""
<div class='credits'>
    <h3>🏛️ PWD Electric Division, Udaipur</h3>
    <p><strong>Hand Receipt Generator v2.0</strong></p>
    <p>Professional EMD Refund Receipt Generation System</p>
    <div style='margin-top: 1.5rem; padding: 1rem; background: #f8f9fa; border-radius: 10px;'>
        <p style='margin: 0.3rem 0; font-size: 0.85rem; color: #666;'><strong>🌟 Prepared on Initiative of:</strong></p>
        <p style='margin: 0.3rem 0; color: #2ecc71; font-weight: 600; font-size: 1rem;'>Mrs. Premlata Jain, AAO</p>
        <p style='margin: 0.3rem 0; font-size: 0.85rem; color: #666;'>PWD Udaipur</p>
    </div>
    <p style='margin-top: 1rem; font-size: 0.9rem; color: #999;'>
        Made with ❤️ for PWD | Powered by Streamlit
    </p>
</div>
""", unsafe_allow_html=True)

# Footer balloons - REJOICING!
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <span class='balloon'>🎈</span>
    <span class='balloon'>🎊</span>
    <span class='balloon'>🎉</span>
    <span class='balloon'>🎈</span>
    <span class='balloon'>🎊</span>
    <span class='balloon'>🎉</span>
    <span class='balloon'>🎈</span>
</div>
""", unsafe_allow_html=True)
