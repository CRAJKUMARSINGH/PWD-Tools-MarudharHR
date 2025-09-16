#!/usr/bin/env python3
"""
Optimized startup script for the Hand Receipt Generator application
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import app, config
from performance_monitor import start_performance_logging, optimize_memory

def setup_logging():
    """Setup optimized logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log', mode='a')
        ]
    )

def check_dependencies():
    """Check if all required dependencies are available"""
    required_packages = [
        'flask', 'pandas', 'jinja2', 'num2words', 
        'openpyxl', 'pdfkit', 'psutil'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def check_wkhtmltopdf():
    """Check if wkhtmltopdf is available"""
    import subprocess
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(
                ['C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe', '--version'],
                capture_output=True,
                text=True
            )
        else:  # Linux/macOS
            result = subprocess.run(['wkhtmltopdf', '--version'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"wkhtmltopdf found: {result.stdout.strip()}")
            return True
        else:
            print("wkhtmltopdf not working properly")
            return False
    except FileNotFoundError:
        print("wkhtmltopdf not found. Please install it:")
        if os.name == 'nt':
            print("Download from: https://wkhtmltopdf.org/downloads.html")
        else:
            print("Install using: sudo apt-get install wkhtmltopdf")
        return False

def optimize_environment():
    """Optimize Python environment for better performance"""
    # Set environment variables for better performance
    os.environ['PYTHONOPTIMIZE'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    # Optimize memory
    optimize_memory()
    
    print("Environment optimized for performance")

def main():
    """Main startup function"""
    print("Starting Hand Receipt Generator (Optimized Version)")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Check wkhtmltopdf
    print("Checking wkhtmltopdf...")
    if not check_wkhtmltopdf():
        print("Warning: wkhtmltopdf not available. PDF generation may fail.")
    
    # Optimize environment
    print("Optimizing environment...")
    optimize_environment()
    
    # Start performance monitoring
    print("Starting performance monitoring...")
    performance_thread = start_performance_logging(interval=300)  # Log every 5 minutes
    
    # Print configuration
    print(f"Configuration:")
    print(f"  - Max rows: {config.MAX_ROWS}")
    print(f"  - Max file size: {config.MAX_CONTENT_LENGTH / (1024*1024):.1f} MB")
    print(f"  - Debug mode: {config.DEBUG}")
    print(f"  - Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    # Start the application
    print("\nStarting Flask application...")
    print("Access the application at: http://127.0.0.1:5000")
    print("Health check: http://127.0.0.1:5000/health")
    print("Status: http://127.0.0.1:5000/status")
    print("\nPress Ctrl+C to stop the application")
    
    try:
        app.run(
            debug=config.DEBUG,
            host='127.0.0.1',
            port=5000,
            threaded=True,
            use_reloader=False  # Disable reloader for better performance
        )
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        logger.info("Application shutdown requested by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
