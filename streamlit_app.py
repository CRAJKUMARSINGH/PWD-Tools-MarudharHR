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
    layout="centered"
)

# Receipt template
receipt_template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=210mm, height=297mm">
    <title>Hand Receipt (RPWA 28)</title>
    <style>
        body { font-family: sans-serif; margin: 0; }
        @page {
            margin: 10mm;
        }
        .container {
            width: 210mm !important;
            min-height: 297mm;
            margin: 10mm 20mm !important;
            border: 2px solid #ccc !important;
            padding: 0mm;
            box-sizing: border-box;
            position: relative;
            page-break-before: always;
        }
        .container:first-child {
            page-break-before: auto;
        }
        .header { text-align: center; margin-bottom: 2px; }
        .details { margin-bottom: 1px; }
        .amount-words { font-style: italic; }
        .signature-area { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .signature-area td, .signature-area th {
            border: 1px solid #ccc !important;
            padding: 5px;
            text-align: left;
        }
        .offices { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .offices td, .offices th {
            border: 1px solid black !important;
            padding: 5px;
            text-align: left;
            word-wrap: break-word;
        }
        .input-field { border-bottom: 1px dotted #ccc; padding: 3px; width: calc(100% - 10px); display: inline-block; }
        .seal-container { position: absolute; left: 10mm; bottom: 10mm; width: 40mm; height: 25mm; z-index: 10; }
        .seal { max-width: 100%; max-height: 100%; text-align: center; line-height: 40mm; color: blue; display: flex; justify-content: space-around; align-items: center; }
        .bottom-left-box { 
            position: absolute; bottom: 40mm; left: 40mm; 
            border: 2px solid blue; padding: 10px; 
            width: 450px; text-align: left; height: 55mm; 
            color: blue; 
        }
        .bottom-left-box p { margin: 3px 0; }
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
            <p>(3) Pay for ECS Rs.{{ receipt.amount }}/- (Rupees <span class="amount-words">{{ receipt.amount_words }} Only</span>)</p>
            <p>(4) Paid by me</p>
            <p>(5) Received from The Executive Engineer PWD Electric Division, Udaipur the sum of Rs. {{ receipt.amount }}/- (Rupees <span class="amount-words">{{ receipt.amount_words }} Only</span>)</p>
            <p> Name of work for which payment is made: <span id="work-name" class="input-field">{{ receipt.work }}</span></p>
            <p> Chargeable to Head:- 8443 [EMD- Refund] </p>
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
                    <td>DA &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Auditor &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Supdt. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; G.O.</td>
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
                <p></p>
                <p></p>
                <p></p>
            <p> Passed for Rs. {{ receipt.amount }}</p>
            <p> In Words Rupees: {{ receipt.amount_words }} Only</p>
            <p> Chargeable to Head:- 8443 [EMD- Refund]</p>
            <div class="seal">
                <p>Ar.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;D.A.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;E.E.</p>
            </div>
        </div>
    </div>
    {% endfor %}
</body>
</html>
""")

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
                        "amount_words": num2words(amount, lang='en').title(),
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

# Main UI
st.title("📄 Hand Receipt Generator (RPWA 28)")
st.markdown("---")

st.markdown("""
### Upload Excel File
Upload an Excel file (.xlsx) containing the following columns:
- **Payee Name**: Contractor/payee name
- **Amount**: Payment amount (numeric)
- **Work**: Work description
""")

# File uploader
uploaded_file = st.file_uploader(
    "Choose an Excel file",
    type=['xlsx'],
    help="Maximum 50 rows will be processed"
)

if uploaded_file is not None:
    # Show file details
    st.info(f"📁 File: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
    
    # Process button
    if st.button("🚀 Generate PDF", type="primary"):
        with st.spinner("Processing Excel file and generating PDF..."):
            pdf_bytes, error = process_excel_file(uploaded_file)
            
            if error:
                st.error(f"❌ {error}")
            else:
                st.success("✅ PDF generated successfully!")
                
                # Download button
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name="receipts.pdf",
                    mime="application/pdf"
                )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>PWD Electric Division, Udaipur</p>
    <p>Hand Receipt Generator v2.0</p>
</div>
""", unsafe_allow_html=True)
