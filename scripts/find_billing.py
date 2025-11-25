import pandas as pd

def find_billing_row():
    file_path = "Facturacion/01. Calculadora PR Nov Cabina.xlsx"
    sheet = "PR"
    print(f"Buscando datos de facturación en {file_path} [{sheet}]")
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet, header=None, nrows=100)
        
        print("\n--- Primeras columnas (A y B) ---")
        for idx, row in df.iterrows():
            col_a = str(row[0]).strip() if pd.notnull(row[0]) else ""
            col_b = str(row[1]).strip() if pd.notnull(row[1]) else ""
            
            if col_a or col_b:
                print(f"Fila {idx}: A='{col_a}' | B='{col_b}'")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_billing_row()
