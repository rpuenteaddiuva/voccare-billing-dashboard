import pandas as pd
import re

def extract_ar_billing():
    file_path = "Facturacion/12. Calculadora AR Nov Cabina.xlsx"
    print(f"Extrayendo Facturación Real AR de: {file_path}")
    
    sheets_to_process = ["Servicios Cabina Addiuva 2025", "Servicios Cabina AON 2025"]
    
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    month_col_start_idx = 11 # Column L (0-indexed)

    monthly_billing = {f"2025-{i+1:02d}": 0.0 for i in range(12)}
    
    for sheet_name in sheets_to_process:
        print(f"Procesando hoja: {sheet_name}")
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            
            # Find Date Row and Total Row dynamically
            date_row_idx = -1
            total_row_idx = -1
            
            # Scan first 50 rows
            for idx, row in df.iterrows():
                # Check for Total USD label in first few columns
                row_str = str(row.iloc[1]).strip().upper() + " " + str(row.iloc[2]).strip().upper()
                if "TOTAL USD" in row_str:
                    total_row_idx = idx
                
                # Check for dates in the row (scan a few columns)
                # Look for datetime objects or strings containing '2025'
                for col_idx in range(10, min(30, len(row))):
                    val = row.iloc[col_idx]
                    if isinstance(val, pd.Timestamp) and val.year == 2025:
                        date_row_idx = idx
                        break
                    if isinstance(val, str) and '2025' in val:
                         date_row_idx = idx
                         break
                
                if date_row_idx != -1 and total_row_idx != -1:
                    break
            
            if date_row_idx != -1 and total_row_idx != -1:
                print(f"DEBUG {sheet_name}: Date Row={date_row_idx}, Total Row={total_row_idx}")
                
                date_row = df.iloc[date_row_idx]
                total_row = df.iloc[total_row_idx]
                
                for col_idx in range(len(date_row)):
                    cell_date = date_row[col_idx]
                    try:
                        dt = pd.to_datetime(cell_date)
                        if dt.year == 2025:
                            month_key = f"2025-{dt.month:02d}"
                            val = pd.to_numeric(total_row[col_idx], errors='coerce')
                            if pd.notna(val):
                                monthly_billing[month_key] += val
                                # print(f"DEBUG {sheet_name} {month_key} (Col {col_idx}): +{val}")
                    except: continue
            else:
                print(f"ERROR: Could not find Date Row or Total Row in {sheet_name}")
                # Fallback: Try hardcoded based on last head output (Dates=4)
                # If date_row_idx is -1 but we see dates in row 4 manually...
                if date_row_idx == -1:
                     date_row_idx = 4
                     print(f"Fallback: Using Date Row 4")
                     date_row = df.iloc[4]
                     # Try to find total row relative to start? No, scan again.
                     
                     if total_row_idx != -1:
                        total_row = df.iloc[total_row_idx]
                        for col_idx in range(len(date_row)):
                            cell_date = date_row[col_idx]
                            try:
                                dt = pd.to_datetime(cell_date)
                                if dt.year == 2025:
                                    month_key = f"2025-{dt.month:02d}"
                                    val = pd.to_numeric(total_row[col_idx], errors='coerce')
                                    if pd.notna(val):
                                        monthly_billing[month_key] += val
                            except: continue
                try:
                    dt = pd.to_datetime(cell_date)
                    if dt.year == 2025:
                        month_key = f"2025-{dt.month:02d}"
                        
                        val = pd.to_numeric(total_row[col_idx], errors='coerce')
                        if pd.notna(val):
                            monthly_billing[month_key] += val
                            # print(f"DEBUG {sheet_name} {month_key}: +{val}")
                except:
                    continue # Not a date or error parsing
                        
        except Exception as e:
            print(f"Error leyendo {sheet_name}: {e}")
            
    print("\n--- Facturación Real Argentina (2025) ---")
    print(f"{ 'Mes':<10} | { 'Total Real USD':<20}")
    print("-" * 32)
    for month, total in monthly_billing.items():
        print(f"{month:<10} | {total:<20,.2f}")
        
    return monthly_billing

if __name__ == "__main__":
    extract_ar_billing()
