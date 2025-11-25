import pandas as pd

def extract_do_billing():
    file_path = "Facturacion/08. Calculadora DO Nov Cabina.xlsx"
    sheet_name = "Servicios Cabina"
    print(f"Extrayendo Facturación Real DO de: {file_path} [{sheet_name}]")
    
    monthly_billing = {f"2025-{i+1:02d}": 0.0 for i in range(12)}
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        # Row 3 (index 3) contains dates
        date_row = df.iloc[3]
        # Row 39 (index 39) contains Total USD values
        total_row = df.iloc[39]
        
        print(f"DEBUG Raw date_row (df.iloc[3]):\n{date_row}")
        print(f"DEBUG Raw total_row (df.iloc[39]):\n{total_row}")
        
        # Iterate through ALL columns to find 2025 dates
        for col_idx in range(len(date_row)):
            cell_date = date_row[col_idx]
            
            # Check if it's a datetime object or can be parsed as one
            try:
                dt = pd.to_datetime(cell_date)
                if dt.year == 2025:
                    month_key = f"2025-{dt.month:02d}"
                    val = pd.to_numeric(total_row[col_idx], errors='coerce')
                    if pd.notna(val):
                        monthly_billing[month_key] += val
            except: continue

    except Exception as e:
        print(f"Error leyendo {sheet_name}: {e}")
            
    print("\n--- Facturación Real Dominicana (2025) ---")
    print(f"{ 'Mes':<10} | { 'Total Real USD':<20}")
    print("-" * 32)
    for month, total in monthly_billing.items():
        print(f"{month:<10} | {total:<20,.2f}")
        
    return monthly_billing

if __name__ == "__main__":
    extract_do_billing()
