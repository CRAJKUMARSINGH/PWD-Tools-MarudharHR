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

# Custom CSS for beautiful styling
st.markdown("""
<style>
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
        max-width: 800px;
    }
    
    /* Title styling */
    .custom-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .custom-subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Balloon animation */
    .balloon {
        font-size: 3rem;
        animation: float 3s ease-in-out infinite;
        display: inline-block;
        margin: 0 0.5rem;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 50px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 50px;
        box-shadow: 0 10px 30px rgba(17, 153, 142, 0.4);
        width: 100%;
    }
    
    /* File uploader */
    .stFileUploader {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 2px dashed #667eea;
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
        color: #667eea;
        margin-bottom: 1rem;
    }
    
    .credits p {
        color: #666;
        margin: 0.5rem 0;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stInfo {
        border-radius: 10px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header with balloons
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <span class='balloon'>🎈</span>
    <span class='balloon'>🎊</span>
    <span class='balloon'>🎉</span>
</div>
""", unsafe_allow_html=True)

# Main content in a card
st.markdown("<div class='custom-card'>", unsafe_allow_html=True)

# Title
st.markdown("<h1 class='custom-title'>📄 Hand Receipt Generator</h1>", unsafe_allow_html=True)
st.markdown("<p class='custom-subtitle'>RPWA 28 - PWD Electric Division, Udaipur</p>", unsafe_allow_html=True)

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

# File uploader
st.markdown("<br>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "📁 Choose your Excel file",
    type=['xlsx'],
    help="Upload .xlsx file (max 10MB, 50 rows)"
)

if uploaded_file is not None:
    # Show file details with nice styling
    st.markdown(f"""
    <div style='background: #e3f2fd; padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
        <p style='margin: 0; color: #1976d2;'>
            <strong>📁 File:</strong> {uploaded_file.name} 
            <strong>📊 Size:</strong> {uploaded_file.size / 1024:.2f} KB
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Process button
    if st.button("🚀 Generate PDF", type="primary"):
        with st.spinner("✨ Processing your file and generating beautiful PDFs..."):
            pdf_bytes, error = process_excel_file(uploaded_file)
            
            if error:
                st.error(f"❌ {error}")
            else:
                st.success("✅ PDF generated successfully!")
                st.balloons()
                
                # Download button
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name="hand_receipts.pdf",
                    mime="application/pdf"
                )

st.markdown("</div>", unsafe_allow_html=True)

# Credits section
st.markdown("""
<div class='credits'>
    <h3>🏛️ PWD Electric Division, Udaipur</h3>
    <p><strong>Hand Receipt Generator v2.0</strong></p>
    <p>Developed for efficient receipt generation and management</p>
    <p style='margin-top: 1rem; font-size: 0.9rem; color: #999;'>
        Made with ❤️ for PWD | Powered by Streamlit
    </p>
</div>
""", unsafe_allow_html=True)

# Footer balloons
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <span class='balloon'>🎈</span>
    <span class='balloon'>🎊</span>
    <span class='balloon'>🎉</span>
</div>
""", unsafe_allow_html=True)
