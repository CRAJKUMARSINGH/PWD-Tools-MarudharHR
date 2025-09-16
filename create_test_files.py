import pandas as pd
import os

# Create test_input_files directory if it doesn't exist
os.makedirs('test_input_files', exist_ok=True)

# Test File 1: Small dataset (3 receipts)
data1 = {
    'Payee Name': ['ABC Electric', 'XYZ Contractors', 'Power Solutions'],
    'Amount': [1500.50, 2500.00, 1800.75],
    'Work': ['Street Light Installation', 'Transformer Repair', 'Cable Laying']
}
df1 = pd.DataFrame(data1)
df1.to_excel('test_input_files/small_test.xlsx', index=False)

# Test File 2: Medium dataset (7 receipts)
data2 = {
    'Payee Name': ['Electro Corp', 'Light & Power', 'Energy Works', 'Power Grid', 'Electric Plus', 'Volt Solutions', 'Current Systems'],
    'Amount': [3200.25, 4500.00, 2800.50, 3900.75, 2100.00, 5600.25, 3400.50],
    'Work': ['Substation Maintenance', 'Line Extension', 'Meter Installation', 'Pole Replacement', 'Switch Repair', 'Transformer Upgrade', 'Cable Testing']
}
df2 = pd.DataFrame(data2)
df2.to_excel('test_input_files/medium_test.xlsx', index=False)

# Test File 3: Large dataset (12 receipts) - will be limited to 10 by app
data3 = {
    'Payee Name': ['Power One', 'Electro Tech', 'Light Systems', 'Energy Corp', 'Grid Solutions', 'Volt Plus', 'Current Tech', 'Power Systems', 'Electric Corp', 'Light Works', 'Energy Plus', 'Grid Tech'],
    'Amount': [1200.00, 3400.50, 2800.25, 4500.75, 3200.00, 5600.50, 2100.25, 3900.00, 2700.75, 4800.25, 3300.50, 4100.00],
    'Work': ['Minor Repair', 'Equipment Maintenance', 'Line Check', 'System Upgrade', 'Component Replacement', 'Major Repair', 'Quick Fix', 'Preventive Maintenance', 'Emergency Repair', 'System Check', 'Line Maintenance', 'Equipment Check']
}
df3 = pd.DataFrame(data3)
df3.to_excel('test_input_files/large_test.xlsx', index=False)

print("Test files created successfully!")
print("1. small_test.xlsx - 3 receipts")
print("2. medium_test.xlsx - 7 receipts") 
print("3. large_test.xlsx - 12 receipts (will be limited to 10 by app)")
print("\nFiles saved in test_input_files/ folder")
