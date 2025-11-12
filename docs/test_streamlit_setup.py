"""
Test script to verify Streamlit deployment setup
"""
import sys

def check_dependencies():
    """Check if all required dependencies are available"""
    required = {
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'jinja2': 'Jinja2',
        'weasyprint': 'WeasyPrint',
        'num2words': 'num2words',
        'openpyxl': 'openpyxl'
    }
    
    missing = []
    for module, name in required.items():
        try:
            __import__(module)
            print(f"✅ {name} is installed")
        except ImportError:
            print(f"❌ {name} is NOT installed")
            missing.append(name)
    
    return missing

def check_files():
    """Check if all required files exist"""
    import os
    
    required_files = [
        'streamlit_app.py',
        'requirements.txt',
        'packages.txt',
        '.streamlit/config.toml'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} is missing")
            missing.append(file)
    
    return missing

def main():
    print("=" * 50)
    print("Streamlit Deployment Setup Check")
    print("=" * 50)
    
    print("\n📦 Checking Dependencies...")
    missing_deps = check_dependencies()
    
    print("\n📁 Checking Files...")
    missing_files = check_files()
    
    print("\n" + "=" * 50)
    if not missing_deps and not missing_files:
        print("✅ All checks passed! Ready for deployment.")
        print("\nTo run locally:")
        print("  streamlit run streamlit_app.py")
        print("\nTo deploy to Streamlit Cloud:")
        print("  1. Push to GitHub")
        print("  2. Go to share.streamlit.io")
        print("  3. Deploy with streamlit_app.py as main file")
    else:
        print("❌ Some checks failed:")
        if missing_deps:
            print(f"\nMissing dependencies: {', '.join(missing_deps)}")
            print("Run: pip install -r requirements.txt")
        if missing_files:
            print(f"\nMissing files: {', '.join(missing_files)}")
    print("=" * 50)

if __name__ == "__main__":
    main()
