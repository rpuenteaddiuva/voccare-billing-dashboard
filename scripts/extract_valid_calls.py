import pandas as pd
import sys
import glob
import os

def extract_valid_calls():
    file_path = "reports/REPORTE ACUMULADO INDICES SEPTIEMBRE 2025 (1).xlsx"
    print(f"Extrayendo Llamadas Válidas de: {file_path}")
    
    countries_and_sheets = {
        'Argentina': ['AR'],
        'Chile': ['CL'],
        'Colombia': ['CO', 'VOCCARE CO'],
        'Costa Rica': ['CR', 'CR-CR'], # CR-CR might have separate or combined totals
        'Dominicana': ['DO'],
        'Ecuador': ['EC'],
        'Guatemala': ['GU', 'VOCCARE GU'],
        'Honduras': ['HN'],
        'Mexico': ['MX', 'VOCCARE MX'],
        'Nicaragua': ['NI'],
        'Paraguay': ['PY'],
        'Peru': ['PE'],
        'Puerto Rico': ['PR'],
        'Salvador': ['SV'],
        'Uruguay': ['ROU'],
        'Bolivia': ['BO']
    }
    
    extracted_valid_calls_data = {}
    raw_csv_calls_data = {}
    sc_counts_data = {}

    # --- Primero, obtener Llamadas Brutas (CSV) y Servicios Concluidos (SC) para cada país ---
    # Ensure absolute path for glob to prevent issues with CWD changes
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_input_dir = os.path.join(base_dir, "Paises")
    files = glob.glob(os.path.join(csv_input_dir, "*.csv"))
    
    print(f"DEBUG: Scanning CSV files in: {csv_input_dir}")
    print(f"DEBUG: Found {len(files)} CSV files.")

    for f in sorted(files):
        try:
            parts = os.path.basename(f).split('_')
            c_name_csv = " ".join([p for p in parts[1:] if not (p.isdigit() and len(p)==8)])
            print(f"DEBUG: Processing CSV file {f} for country {c_name_csv}")

            df = pd.read_csv(f, sep=';', usecols=['estado_asistencia', 'cantidad_llamadas', 'creacion_asistencia'], on_bad_lines='skip')
            df['date'] = pd.to_datetime(df['creacion_asistencia'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            df = df[df['date'].dt.year == 2025].copy()
            if df.empty:
                print(f"DEBUG: {c_name_csv} - No data for 2025 in CSV. Skipping.")
                continue

            sc_count = len(df[df['estado_asistencia'] == 'CONCLUIDA'])
            df['cantidad_llamadas'] = pd.to_numeric(df['cantidad_llamadas'], errors='coerce').fillna(0)
            calls_sc_only = df[df['estado_asistencia'] == 'CONCLUIDA']['cantidad_llamadas'].sum() # Sum calls only for concluded services
            
            # Normalize country name (remove date part if any) for dictionary key
            c_name_normalized = c_name_csv.replace(' 20251027.csv', '') # Remove specific date from filename
            c_name_normalized = c_name_normalized.replace(' 20251027', '') # Remove specific date from filename
            c_name_normalized = c_name_normalized.replace('Client', '') # Remove Client prefix
            c_name_normalized = c_name_normalized.replace('_Puerto Rico', 'Puerto Rico') # Fix underscore for PR
            c_name_normalized = c_name_normalized.replace('_Dominicana', 'Dominicana') # Fix underscore for DO
            c_name_normalized = c_name_normalized.strip()
            
            # Attempt a more robust normalization by matching directly with countries_and_sheets keys
            # Find the best matching country name from our known list
            best_match = None
            for known_country in countries_and_sheets.keys():
                if known_country in c_name_csv: # Simple substring match
                    best_match = known_country
                    break
            
            if best_match:
                raw_csv_calls_data[best_match] = calls_sc_only
                sc_counts_data[best_match] = sc_count
                print(f"DEBUG: {best_match} (Normalized) - SC Count: {sc_count}, Raw Calls: {calls_sc_only}")
            else:
                print(f"DEBUG: WARNING - No matching country found for CSV {c_name_csv}")

        except Exception as e:
            print(f"DEBUG: Error processing CSV for {c_name_csv}: {e}")

    # --- Ahora, extraer Llamadas Válidas (Excel) y calcular factores de eficiencia ---
    print(f"{ 'Pais':<20} | {'SC (CSV)':<10} | {'Llamadas Brutas (CSV)':<22} | {'Llamadas Válidas (Excel)':<25} | {'Factor Efic. Calc.':<22}")
    print("-" * 120)
    
    for country, sheets in countries_and_sheets.items():
        total_valid_calls_for_country = 0
        found_data_for_country = False
        
        for sheet_name in sheets:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                
                # Search for row with "Total de llamadas Validas" (case/accent insensitive)
                for idx, row in df.iterrows():
                    # Check column B (index 1) for the exact string
                    if not pd.isna(row[1]): 
                        cell_b_content = str(row[1]).lower().strip().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                        if "total de llamadas validas" in cell_b_content:
                            # Found the row! Sum monthly values (cols C to K = indices 2 to 10 for Jan-Sep)
                            monthly_sum = 0
                            for col_idx in range(2, 11): # Columns C to K (Jan to Sep)
                                val = row[col_idx]
                                if pd.notnull(val) and isinstance(val, (int, float)):
                                    monthly_sum += val
                            
                            total_valid_calls_for_country += monthly_sum
                            found_data_for_country = True
                            break # Found for this sheet, move to next sheet or sum next for this country
                            
            except Exception as e:
                # print(f"  Error reading sheet {sheet_name} for {country}: {e}")
                pass
        
        # Get raw calls for comparison
        csv_calls = raw_csv_calls_data.get(country, 0)
        sc_count = sc_counts_data.get(country, 0)

        efficiency_factor = total_valid_calls_for_country / csv_calls if csv_calls > 0 else 0

        print(f"{country:<20} | {sc_count:<10,.0f} | {csv_calls:<22,.0f} | {total_valid_calls_for_country:<25,.0f} | {efficiency_factor:<22.2f}")
        
        extracted_valid_calls_data[country] = efficiency_factor

    print("\n--- Factores de Eficiencia Calibrados (Diccionario) ---")
    print(extracted_valid_calls_data)
    
    return extracted_valid_calls_data

if __name__ == "__main__":
    extracted_data = extract_valid_calls()