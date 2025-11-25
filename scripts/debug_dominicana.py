import pandas as pd
import sys

def debug_dominicana(file_path):
    print(f"--- Debugging {file_path} ---")
    try:
        df = pd.read_csv(file_path, sep=';', on_bad_lines='skip')
        
        # Date parsing
        df['date_obj'] = pd.to_datetime(df['creacion_asistencia'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        df = df[df['date_obj'].dt.year == 2025].copy()
        df['month'] = df['date_obj'].dt.to_period('M')
        
        app_types = ['APP', 'ANCLAJE APP SOA', 'ANCLAJE', 'ANCLAJE_APP', 'ANCLAJE_APP_SOA']
        
        print(f"{'Month':<10} | {'Raw Calls (All)':<15} | {'Raw Calls (Non-App)':<20} | {'Raw Calls (App)':<15} | {'Excel Target':<12}")
        print("-" * 90)
        
        excel_targets = {
            '2025-01': 11119, '2025-02': 9713, '2025-03': 12772,
            '2025-04': 11082, '2025-05': 12419, '2025-06': 11495,
            '2025-07': 11473, '2025-08': 9303, '2025-09': 9999
        }
        
        for month, group in df.groupby('month'):
            total_calls = group['cantidad_llamadas'].sum()
            
            non_app_df = group[~group['tipo_asignacion'].astype(str).str.strip().isin(app_types)]
            non_app_calls = non_app_df['cantidad_llamadas'].sum()
            
            app_df = group[group['tipo_asignacion'].astype(str).str.strip().isin(app_types)]
            app_calls = app_df['cantidad_llamadas'].sum()
            
            target = excel_targets.get(str(month), 0)
            
            print(f"{str(month):<10} | {total_calls:<15} | {non_app_calls:<20} | {app_calls:<15} | {target:<12}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_dominicana("Paises/Client03_Dominicana_20251027.csv")
