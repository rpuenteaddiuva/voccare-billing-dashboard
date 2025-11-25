import pandas as pd

def analyze_pr_split(file_path):
    print(f"Analyzing Puerto Rico Split: {file_path}")
    
    try:
        df = pd.read_csv(file_path, sep=';', on_bad_lines='skip', low_memory=False)
        
        # Date Parsing (Flexible)
        date_col = 'creacion_asistencia' # PR often uses this or fecha_finalizacion
        # Based on peek: 2023-01-02 13:44:18 (YYYY-MM-DD)
        df['date_obj'] = pd.to_datetime(df[date_col], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        
        # Filter Jan 2025
        df_jan = df[(df['date_obj'].dt.year == 2025) & (df['date_obj'].dt.month == 1)].copy()
        
        print(f"Total Records Jan 2025: {len(df_jan)}")
        
        # Classification Logic
        def classify_client(row):
            account = str(row['cuenta']).upper()
            if 'MCS' in account:
                return 'MCS'
            else:
                return 'OTROS'
        
        df_jan['Client_Group'] = df_jan.apply(classify_client, axis=1)
        
        # App Types
        app_types = ['APP', 'ANCLAJE APP SOA', 'ANCLAJE', 'ANCLAJE_APP', 'ANCLAJE_APP_SOA']

        # Metrics per Group
        results = {}
        for group_name, group_df in df_jan.groupby('Client_Group'):
            
            # SC
            if 'estado_asistencia' in group_df.columns:
                sc_df = group_df[group_df['estado_asistencia'] == 'CONCLUIDA']
                cancelled_df = group_df[group_df['estado_asistencia'].astype(str).str.upper().str.contains('CANCEL')]
            else:
                sc_df = group_df
                cancelled_df = pd.DataFrame()
                
            total_sc = len(sc_df)
            sc_app = sc_df[sc_df['tipo_asignacion'].astype(str).str.strip().isin(app_types)].shape[0]
            sc_voice = total_sc - sc_app
            
            # LV (90% factor)
            raw_calls = group_df['cantidad_llamadas'].sum()
            total_lv = int(raw_calls * 0.90)
            
            # Cancelled
            cp = 0
            cm = 0
            if not cancelled_df.empty and 'usuario_que_asigna' in cancelled_df.columns:
                # Simple check for assignment
                import numpy as np
                assigned = cancelled_df['usuario_que_asigna'].replace('', np.nan).notna()
                cp = assigned.sum()
                cm = len(cancelled_df) - cp
            
            results[group_name] = {
                'SC_Total': total_sc,
                'SC_App': sc_app,
                'SC_Voice': sc_voice,
                'LV_Total': total_lv,
                'CP': cp,
                'CM': cm,
                'Adoption': (sc_app/total_sc*100) if total_sc else 0
            }
            
        print("\n--- PUERTO RICO (JAN 2025) BREAKDOWN ---")
        df_res = pd.DataFrame(results).T
        print(df_res.to_string())
        
        # Export for user visibility if needed
        # df_res.to_csv('reports/pr_split_jan2025.csv')

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_pr_split("Paises/Client01_Puerto_Rico_20251027.csv")
