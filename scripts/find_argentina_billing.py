import pandas as pd

def find_argentina_billing_row():
    file_path = "Facturacion/12. Calculadora AR Nov Cabina.xlsx"
    sheet = "AR"
    print(f"Buscando datos de facturación en {file_path} [{sheet}]")
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet, header=None, nrows=100)
        
        print("\n--- Primeras columnas (A y B) ---")
        for idx, row in df.iterrows():
            col_a = str(row[0]).strip() if pd.notnull(row[0]) else ""
            col_b = str(row[1]).strip() if pd.notnull(row[1]) else ""
            
            if col_a or col_b:
                print(f"Fila {idx}: A='{col_a}' | B='{col_b}'")
        
        print("\n--- Filas Relevantes (CABINA, FEE) en Columnas A a E ---")
        for idx, row in df.iterrows():
            col_label = str(row[1]).strip().upper() # Check column B for labels
            if 'CABINA' in col_label or 'FEE CORPORATIVO' in col_label:
                print(f"Fila {idx} - '{col_label}': Cols C, D, E = '{row[2]}', '{row[3]}', '{row[4]}'")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_argentina_billing_row()
