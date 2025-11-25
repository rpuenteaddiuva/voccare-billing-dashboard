import pandas as pd
import sys
import os

def inspect_excel(file_path, sheets=None):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    try:
        xls = pd.ExcelFile(file_path)
        
        target_sheets = sheets if sheets else ['PR', 'MCS'] 
        
        for sheet in target_sheets:
            if sheet in xls.sheet_names:
                print(f"\n--- Inspecting sheet '{sheet}' ---")
                # Read enough rows to cover the data block
                df = pd.read_excel(xls, sheet_name=sheet, nrows=50) 
                print(df.fillna('').to_string())
            else:
                print(f"Sheet '{sheet}' not found.")
            
    except Exception as e:
        print(f"Error reading Excel: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        sheets = sys.argv[2:] if len(sys.argv) > 2 else None
    else:
        file_path = "reports/REPORTE ACUMULADO INDICES SEPTIEMBRE 2025 (1).xlsx"
        sheets = None
    
    inspect_excel(file_path, sheets)

