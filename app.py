from flask import Flask, render_template, request, send_file
import logging
from io import BytesIO
import tempfile
import os
from jinja2 import Template

from config import get_config
from utils import ExcelProcessor, PDFGenerator, DataValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with configuration
app = Flask(__name__)
config = get_config()
app.config.from_object(config)

# Initialize processors
excel_processor = ExcelProcessor(config)
pdf_generator = PDFGenerator(config)
data_validator = DataValidator()

# Pre-compiled template for better performance
receipt_template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=210mm, height: 297mm">
    <title>Hand Receipt (RPWA 28)</title>
    <style>
        body { font-family: sans-serif; margin: 0; }
        @page {
            margin: 10mm;  /* Page margins */
        }
        .container {
            width: 210mm !important; /* Added !important */
            min-height: 297mm;
            margin: 10mm 20mm !important; /* Added !important */
            border: 2px solid #ccc !important;
            padding: 0mm; /* Changed to 0mm */
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
         @media print {
            .container {
                border: none;
                width: 210mm;
                min-height: 297mm;
                margin: 0;
                padding: 0;
            }
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

@app.route("/", methods=["GET", "POST"])
def index():
    """Main route for file upload and PDF generation"""
    if request.method == "POST":
        file = request.files["file"]
        
        # Validate file
        is_valid, error_msg = excel_processor.validate_file(file, file.filename)
        if not is_valid:
            return error_msg, 400

        try:
            # Read file into memory efficiently
            file_stream = BytesIO(file.read())
            
            # Process Excel file
            df, error_msg = excel_processor.read_excel(file_stream)
            if df is None:
                return error_msg, 400

            # Find required columns
            payee_col, amount_col, work_col, error_msg = excel_processor.find_columns(df)
            if not all([payee_col, amount_col, work_col]):
                return error_msg, 400

            # Process data
            receipts = excel_processor.process_data(df, payee_col, amount_col, work_col)
            if not receipts:
                return config.ERROR_MESSAGES['no_valid_data'], 400

            # Render HTML template
            rendered_html = receipt_template.render(receipts=receipts)

            # Generate PDF with temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                pdf_file = tmp_file.name

            if not pdf_generator.generate_pdf(rendered_html, pdf_file):
                return "Error generating PDF", 500

            # Send file and clean up
            try:
                return send_file(
                    pdf_file,
                    as_attachment=True,
                    download_name="receipts.pdf",
                    mimetype='application/pdf'
                )
            finally:
                # Clean up temporary file
                try:
                    os.unlink(pdf_file)
                except OSError:
                    pass

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return config.ERROR_MESSAGES['processing_error'].format(error=str(e)), 500

    return render_template("index.html")

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return "OK"

@app.route("/status", methods=["GET"])
def status():
    """Application status endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "max_rows": config.MAX_ROWS,
        "max_file_size": config.MAX_CONTENT_LENGTH
    }

if __name__ == "__main__":
    # Check if running in Streamlit environment
    try:
        import streamlit
        # If we can import streamlit, disable debug mode to avoid signal errors
        app.run(debug=False, host='127.0.0.1', port=5000)
    except ImportError:
        # Normal Flask environment, can use debug mode
        app.run(debug=config.DEBUG, host='127.0.0.1', port=5000)