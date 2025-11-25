import pandas as pd

def debug_costa_rica(file_path):
    print(f"Debugging Costa Rica: {file_path}")
    try:
        df = pd.read_csv(file_path, sep=';', on_bad_lines='skip')
        
        # Date Parsing
        df['date_obj'] = pd.to_datetime(df['creacion_asistencia'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        
        # Filter Jan 2025
        df_jan = df[(df['date_obj'].dt.year == 2025) & (df['date_obj'].dt.month == 1)].copy()
        
        print(f"Total Records Jan 2025: {len(df_jan)}")
        
        # Count SC
        sc_jan = df_jan[df_jan['estado_asistencia'] == 'CONCLUIDA']
        print(f"Total SC (CONCLUIDA) Jan 2025: {len(sc_jan)}")
        
        # Breakdown by Service Type / Plan to see if we are including things we shouldn't
        print("\n--- Breakdown by 'plan' (Top 10) ---")
        print(sc_jan['plan'].value_counts().head(10))

        print("\n--- Breakdown by 'cuenta' (Top 10) ---")
        print(sc_jan['cuenta'].value_counts().head(10))
        
        # Check for duplicates
        unique_ids = sc_jan['id_asistencia'].nunique()
        print(f"\nUnique 'id_asistencia' in SC: {unique_ids}")
        if len(sc_jan) > unique_ids:
             print(f"WARNING: POTENTIAL DUPLICATES FOUND. {len(sc_jan) - unique_ids} extra rows.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_costa_rica("Paises/Client08_Costa_Rica_20251027.csv")
