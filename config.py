import os
from typing import Dict, Any
import tempfile

class Config:
    """Application configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    
    # PDF generation settings
    PDF_OPTIONS = {
        "page-size": "A4",
        "encoding": "UTF-8",
        "no-outline": None,
        "quiet": "",
        "margin-top": "10mm",
        "margin-right": "10mm",
        "margin-bottom": "10mm",
        "margin-left": "10mm"
    }
    
    # Excel processing settings
    MAX_ROWS = 50
    SUPPORTED_COLUMNS = {
        'payee': ['Payee Name', 'PayeeName', 'Name', 'Contractor', 'Payee'],
        'amount': ['Amount', 'Value', 'Cost', 'Payment', 'Total'],
        'work': ['Work', 'Description', 'Item', 'Project', 'Job']
    }
    
    # File handling
    ALLOWED_EXTENSIONS = {'.xlsx'}
    TEMP_DIR = os.environ.get('TEMP_DIR') or tempfile.gettempdir()
    
    # Performance settings
    CACHE_SIZE = 128
    CHUNK_SIZE = 8192  # 8KB chunks for file reading
    
    # Error messages
    ERROR_MESSAGES = {
        'no_file': 'No file selected',
        'invalid_extension': 'Please upload an Excel (.xlsx) file',
        'file_too_large': 'File size too large. Please select a file smaller than 10MB',
        'empty_file': 'Excel file is empty or contains no data',
        'missing_columns': 'Required columns not found. Found: {columns}. Need: Payee Name, Amount, Work',
        'no_valid_data': 'No valid data found in the Excel file. Please check the column names and data format.',
        'processing_error': 'An error occurred while processing the file: {error}'
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    PDF_OPTIONS = {
        **Config.PDF_OPTIONS,
        "no-debug-javascript": None,
        "no-stop-slow-scripts": None
    }

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    MAX_ROWS = 10  # Smaller limit for testing

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = None) -> Config:
    """Get configuration based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, config['default'])
