import pandas as pd
import re

def extract_pr_billing():
    file_path = "Facturacion/01. Calculadora PR Nov Cabina.xlsx"
    print(f"Extrayendo Facturación Real PR de: {file_path}")
    
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    print(f"{'Mes':<15} | {'Fuente':<25} | {'Cabina':<15} | {'Fee Corp':<15} | {'Total Real':<15}")
    print("-" * 95)
    
    billing_data = {}
    
    excel_file = pd.ExcelFile(file_path)
    all_sheets = excel_file.sheet_names
    
    for i, month in enumerate(months):
        month_num = i + 1
        sheet_name = f"Consolidado {month}"
        
        cabina = 0
        fee = 0
        source = "N/A"
        
        if sheet_name == "Consolidado Agosto":
             try:
                df_debug = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=10)
                print(f"DEBUG: Consolidado Agosto Head:\n{df_debug}")
             except: pass

        if sheet_name in all_sheets:
            # Process Consolidado sheet
            source = sheet_name
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                
                # Debug: Print first few rows of col 0
                # print(f"DEBUG {sheet_name}: First 5 rows col 0: {df[0].head(5).tolist()}")

                # Find 'CABINA' row
                for idx, row in df.iterrows():
                    # Check Column 1 (index 1) for labels based on debug
                    col_label = str(row[1]).strip().upper()
                    
                    if 'CABINA' in col_label:
                        # Found Cabina row
                        try:
                            # Value seems to be in Column 4 (index 4)
                            val = pd.to_numeric(row[4], errors='coerce')
                            if not pd.isna(val):
                                cabina = val
                        except: pass
                        
                    if 'FEE CORPORATIVO' in col_label:
                        try:
                            val = pd.to_numeric(row[4], errors='coerce')
                            if not pd.isna(val):
                                fee = val
                        except: pass
                        
            except Exception as e:
                print(f"Error reading {sheet_name}: {e}")
        
        else:
            # Try to find partial sheets (Conec + Corp + Cabina??)
            # Or check if 'Calculadora Cabina {Month}' exists
            # Logic: Maybe 'Calculadora Cabina' has the total?
            cab_sheet = f"Calculadora Cabina {month}"
            if cab_sheet in all_sheets:
                source = cab_sheet + " (Partial?)"
                # Logic for these sheets is unknown, skipping for now to avoid bad data
                # But usually 'Cabina' implies the variable cost.
                pass

        total = cabina + fee
        if total > 0:
            # Formatting month for matching (2025-MM)
            month_key = f"2025-{month_num:02d}"
            billing_data[month_key] = total
            print(f"{month:<15} | {source:<25} | {cabina:<15,.2f} | {fee:<15,.2f} | {total:<15,.2f}")
        else:
            print(f"{month:<15} | {source:<25} | {'-':<15} | {'-':<15} | {'-':<15}")

    return billing_data

if __name__ == "__main__":
    extract_pr_billing()