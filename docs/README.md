# 📚 Documentation & Testing

This folder contains all documentation and test files for the Hand Receipt Generator.

## 📄 Documentation

### DEPLOYMENT_CHECK.md
Complete deployment verification checklist including:
- What should be visible in the deployed app
- Troubleshooting steps
- Repository configuration
- Browser cache clearing instructions

## 🧪 Test Files

### test_app_functionality.py
**Main automated test suite** - Tests all core functionality:
- ✅ Number to words conversion (Indian format)
- ✅ Excel file processing
- ✅ PDF generation
- ✅ Processes test files: 01 rasid.xlsx, 18 rasid.xlsx, 50 rasid.xlsx

**Run:** `python docs/test_app_functionality.py`

### test_streamlit_setup.py
Tests Streamlit installation and dependencies

### test_all_excel_files.py
Batch test all Excel files in the project

### test_receipts.py
Tests receipt generation logic

### test_babulal.py
Specific test case for Babulal contractor data

### test_with_sample_data.py
Tests with sample/mock data

### test_all_components.py
Comprehensive component testing

## 🚀 Quick Test

To verify everything works:

```bash
# Run main test suite
python docs/test_app_functionality.py

# Expected output:
# 🎉 ALL TESTS PASSED! 🎈🎊🎉
# ✅ 3/3 tests passed
```

## 📊 Test Outputs

Generated PDFs are saved to:
- `test_outputs/` - Test PDF files
- `batch_outputs/` - Batch processing results

## 🔍 What Gets Tested

1. **Number Conversion**
   - 1,000 → "One Thousand"
   - 100,000 → "One Lakh"
   - 10,000,000 → "One Crore"

2. **Excel Processing**
   - Column detection (Payee, Amount, Work)
   - Data validation
   - Row limits (max 50)

3. **PDF Generation**
   - A4 Portrait format
   - 10mm margins
   - No shrinking
   - Proper formatting

4. **File Handling**
   - Single receipt (1 row)
   - Multiple receipts (16 rows)
   - Maximum receipts (50 rows)

## 📝 Notes

- All test files use the Excel files in the root directory
- Tests create output in `test_outputs/` folder
- Tests are non-destructive and can be run multiple times
- Warnings about ScriptRunContext can be ignored (normal for non-Streamlit execution)

---

**For deployment issues, see:** `DEPLOYMENT_CHECK.md`  
**For main documentation, see:** `../README.md`
