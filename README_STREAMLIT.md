# Hand Receipt Generator - Streamlit Deployment

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## ☁️ Deploy to Streamlit Cloud

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Streamlit deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `streamlit_app.py`
6. Click "Deploy"

### Step 3: Configure (if needed)
The app will automatically use:
- `requirements.txt` for Python dependencies
- `packages.txt` for system dependencies (WeasyPrint)
- `.streamlit/config.toml` for Streamlit configuration

## 📋 Features

- ✅ Upload Excel files (.xlsx)
- ✅ Automatic column detection
- ✅ Generate professional PDF receipts
- ✅ Download generated PDFs
- ✅ Process up to 50 rows
- ✅ Clean, modern UI

## 📁 Required Excel Columns

Your Excel file should contain:
- **Payee Name** (or Name, Contractor, Payee)
- **Amount** (or Value, Cost, Payment, Total)
- **Work** (or Description, Item, Project, Job)

## 🔧 Configuration

### File Size Limit
Default: 10MB (configured in `.streamlit/config.toml`)

### Row Limit
Default: 50 rows (configured in `streamlit_app.py`)

## 🐛 Troubleshooting

### WeasyPrint Issues
If you encounter WeasyPrint errors locally:

**Windows:**
```bash
# Install GTK3 runtime
# Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
```

**Linux:**
```bash
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0
```

**macOS:**
```bash
brew install pango gdk-pixbuf libffi
```

### Excel Reading Issues
Make sure your Excel file:
- Is in .xlsx format (not .xls)
- Has headers in the first row
- Contains the required columns

## 📊 File Structure

```
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt          # Python dependencies
├── packages.txt             # System dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
└── README_STREAMLIT.md      # This file
```

## 🌐 Alternative Deployment Options

### Render
1. Create a new Web Service
2. Connect your repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`

### Heroku
1. Create `Procfile`:
   ```
   web: streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0
   ```
2. Deploy using Heroku CLI or GitHub integration

### Railway
1. Connect your GitHub repository
2. Railway will auto-detect Streamlit
3. Deploy automatically

## 📝 Notes

- The app processes a maximum of 50 rows per file
- File size limit is 10MB
- PDF generation uses WeasyPrint (better than wkhtmltopdf for cloud deployment)
- All processing happens in-memory for better performance

## 🆘 Support

If you encounter issues:
1. Check the Streamlit logs in the deployment dashboard
2. Verify all dependencies are installed
3. Test locally first with `streamlit run streamlit_app.py`
4. Check that your Excel file format is correct

---

**PWD Electric Division, Udaipur**
