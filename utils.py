import pandas as pd
import logging
from typing import List, Dict, Optional, Tuple
from functools import lru_cache
from num2words import num2words
from config import Config

logger = logging.getLogger(__name__)

class ExcelProcessor:
    """Handles Excel file processing with optimized performance"""
    
    def __init__(self, config: Config):
        self.config = config
        self.supported_columns = config.SUPPORTED_COLUMNS
        self.max_rows = config.MAX_ROWS
    
    def validate_file(self, file_stream, filename: str) -> Tuple[bool, str]:
        """Validate uploaded file"""
        if not filename or filename == '':
            return False, self.config.ERROR_MESSAGES['no_file']
        
        if not filename.lower().endswith('.xlsx'):
            return False, self.config.ERROR_MESSAGES['invalid_extension']
        
        return True, ""
    
    def read_excel(self, file_stream) -> Tuple[Optional[pd.DataFrame], str]:
        """Read Excel file with optimized settings"""
        try:
            df = pd.read_excel(
                file_stream,
                engine='openpyxl',
                nrows=self.max_rows,
                na_values=['', 'nan', 'None'],
                keep_default_na=False
            )
            
            if df.empty:
                return None, self.config.ERROR_MESSAGES['empty_file']
            
            return df, ""
            
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            return None, f"Error reading file: {str(e)}"
    
    def find_columns(self, df: pd.DataFrame) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
        """Find required columns in the dataframe"""
        df_columns = df.columns.tolist()
        
        payee_col = self._find_column_by_names(df_columns, self.supported_columns['payee'])
        amount_col = self._find_column_by_names(df_columns, self.supported_columns['amount'])
        work_col = self._find_column_by_names(df_columns, self.supported_columns['work'])
        
        if not all([payee_col, amount_col, work_col]):
            error_msg = self.config.ERROR_MESSAGES['missing_columns'].format(
                columns=list(df.columns)
            )
            return None, None, None, error_msg
        
        return payee_col, amount_col, work_col, ""
    
    def _find_column_by_names(self, df_columns: List[str], possible_names: List[str]) -> Optional[str]:
        """Find column by possible names with early return optimization"""
        for name in possible_names:
            name_lower = name.lower()
            for col in df_columns:
                if name_lower in col.strip().lower():
                    return col
        return None
    
    def process_data(self, df: pd.DataFrame, payee_col: str, amount_col: str, work_col: str) -> List[Dict]:
        """Process dataframe rows efficiently"""
        receipts = []
        
        for _, row in df.iterrows():
            receipt = self._process_row(row, payee_col, amount_col, work_col)
            if receipt:
                receipts.append(receipt)
        
        return receipts
    
    def _process_row(self, row: pd.Series, payee_col: str, amount_col: str, work_col: str) -> Optional[Dict]:
        """Process individual row with validation"""
        try:
            # Validate and convert amount
            amount_raw = row[amount_col]
            if pd.isna(amount_raw) or amount_raw == '':
                return None
            
            amount = float(amount_raw)
            if amount <= 0:
                return None
            
            # Validate payee name
            payee = str(row[payee_col]).strip()
            if not payee or payee.lower() in ['nan', 'none', '']:
                return None
            
            # Process work description with default
            work = str(row[work_col]).strip()
            if not work or work.lower() in ['nan', 'none', '']:
                work = "Electric Work"
            
            return {
                "payee": payee,
                "amount": f"{amount:.2f}",
                "amount_words": convert_to_words(amount),
                "work": work
            }
            
        except (ValueError, TypeError, KeyError) as e:
            logger.debug(f"Error processing row: {str(e)}")
            return None

@lru_cache(maxsize=128)
def convert_to_words(amount: float) -> str:
    """Cache number to words conversion for better performance"""
    return num2words(amount, lang='en').title()

class PDFGenerator:
    """Handles PDF generation with optimized settings"""
    
    def __init__(self, config: Config):
        self.config = config
        self.pdf_options = config.PDF_OPTIONS
    
    def generate_pdf(self, html_content: str, pdf_path: str) -> bool:
        """Generate PDF from HTML content"""
        try:
            import pdfkit
            pdfkit.from_string(
                html_content,
                pdf_path,
                options=self.pdf_options,
                configuration=self._get_pdf_config()
            )
            return True
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return False
    
    def _get_pdf_config(self):
        """Get PDF configuration based on OS"""
        import os
        import pdfkit
        
        if os.name == 'nt':  # Windows
            wkhtmltopdf_path = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'
        else:  # Linux or macOS
            wkhtmltopdf_path = '/usr/bin/wkhtmltopdf'
        
        return pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

class DataValidator:
    """Validates data integrity and format"""
    
    @staticmethod
    def validate_amount(amount: float) -> bool:
        """Validate amount is positive and reasonable"""
        return 0 < amount < 1000000000  # 1 billion limit
    
    @staticmethod
    def validate_payee_name(name: str) -> bool:
        """Validate payee name is not empty and reasonable length"""
        return 1 <= len(name.strip()) <= 200
    
    @staticmethod
    def validate_work_description(work: str) -> bool:
        """Validate work description"""
        return len(work.strip()) <= 500  # 500 character limit
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text input"""
        if not text:
            return ""
        return str(text).strip()[:500]  # Limit to 500 characters
