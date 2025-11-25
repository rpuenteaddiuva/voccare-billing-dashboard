import pandas as pd
import sys
import os

def list_sheets(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    try:
        xls = pd.ExcelFile(file_path)
        print(f"Sheets found: {xls.sheet_names}")
    except Exception as e:
        print(f"Error reading Excel: {e}")

if __name__ == "__main__":
    list_sheets("reports/REPORTE ACUMULADO INDICES SEPTIEMBRE 2025 (1).xlsx")
