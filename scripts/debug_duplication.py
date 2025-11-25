import pandas as pd
import numpy as np

def analyze_duplication(file_path):
    print(f"Analyzing Duplication in: {file_path}")
    
    try:
        df = pd.read_csv(file_path, sep=';', on_bad_lines='skip', low_memory=False)
        
        # Filter Jan 2025 for consistency with previous checks
        # Date Parsing (Flexible)
        date_col = 'creacion_asistencia'
        df['date_obj'] = pd.to_datetime(df[date_col], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        df_jan = df[(df['date_obj'].dt.year == 2025) & (df['date_obj'].dt.month == 1)].copy()
        
        print(f"Total Records Jan 2025: {len(df_jan)}")
        
        # 1. Check Identifiers
        unique_expedientes = df_jan['id_expediente'].nunique()
        unique_asistencias = df_jan['id_asistencia'].nunique()
        
        print(f"Unique Expedientes: {unique_expedientes}")
        print(f"Unique Asistencias: {unique_asistencias}")
        
        # 2. Duplication Check
        # Group by Expediente and check calls
        print("\n--- Checking Expediente Duplication Logic ---")
        
        # Identify expedientes with multiple rows
        exp_counts = df_jan['id_expediente'].value_counts()
        multi_row_exps = exp_counts[exp_counts > 1].index
        
        print(f"Expedientes with >1 row: {len(multi_row_exps)}")
        
        if len(multi_row_exps) > 0:
            sample_id = multi_row_exps[0]
            print(f"\nSample Expediente (ID: {sample_id}):")
            sample_rows = df_jan[df_jan['id_expediente'] == sample_id][['id_asistencia', 'servicio', 'estado_asistencia', 'cantidad_llamadas']]
            print(sample_rows.to_string())
            
            # Analyze call summation
            raw_sum = sample_rows['cantidad_llamadas'].sum()
            max_val = sample_rows['cantidad_llamadas'].max()
            print(f"Raw Sum of Calls: {raw_sum}")
            print(f"Max Calls (if duplicated): {max_val}")
            
        # 3. Global Calculation Scenarios
        
        # Scenario A: Sum ALL rows (Current Logic)
        total_calls_sum = df_jan['cantidad_llamadas'].sum()
        
        # Scenario B: Sum MAX per Expediente (Hypothesis: Calls are case-level attribute)
        total_calls_exp_max = df_jan.groupby('id_expediente')['cantidad_llamadas'].max().sum()
        
        # Scenario C: Sum MAX per Asistencia (Hypothesis: Calls are assistance-level but duplicated rows exist)
        total_calls_assist_max = df_jan.groupby('id_asistencia')['cantidad_llamadas'].max().sum()

        print("\n--- Aggregation Scenarios (Jan 2025) ---")
        print(f"A) Sum All Rows (Current): {total_calls_sum:,.0f}")
        print(f"B) Sum Max per Expediente: {total_calls_exp_max:,.0f}")
        print(f"C) Sum Max per Asistencia: {total_calls_assist_max:,.0f}")
        
        print(f"\nTarget from Excel (Approx): ~38,000")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_duplication("Paises/Client01_Puerto_Rico_20251027.csv")
