import pandas as pd
import glob
import os
import re
import json
import numpy as np

def get_country_name(filename):
    base = os.path.basename(filename)
    name_part = base.replace('.csv', '')
    match = re.match(r'Client\d+_(.+)', name_part)
    if match:
        raw_name = match.group(1)
        raw_name = re.sub(r'_\d{8}$', '', raw_name)
        return raw_name.replace('_', ' ')
    return name_part

def audit_file(file_path):
    try:
        df = pd.read_csv(file_path, sep=';', on_bad_lines='skip', low_memory=False)
        
        date_col = 'creacion_asistencia'
        if date_col not in df.columns:
            if 'fecha_finalizacion_asistencia' in df.columns:
                date_col = 'fecha_finalizacion_asistencia'
            else:
                return None

        df['date_obj'] = pd.to_datetime(df[date_col], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        if df['date_obj'].isnull().all():
             df['date_obj'] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
        
        df = df[df['date_obj'].dt.year == 2025].copy()
        if len(df) == 0: return None
        
        df['month'] = df['date_obj'].dt.to_period('M')
        
        app_types = ['APP', 'ANCLAJE APP SOA', 'ANCLAJE', 'ANCLAJE_APP', 'ANCLAJE_APP_SOA']
        
        monthly_results = {}
        
        for month, group in df.groupby('month'):
            # Metrics for the month
            total_sc = 0
            sc_app = 0
            sc_voice = 0
            total_lv = 0
            cancelled_posterior = 0
            cancelled_moment = 0
            
            if 'estado_asistencia' in group.columns:
                sc_df = group[group['estado_asistencia'] == 'CONCLUIDA']
                cancelled_df = group[group['estado_asistencia'].astype(str).str.upper().str.contains('CANCEL')]
            else:
                sc_df = group
                cancelled_df = pd.DataFrame()

            total_sc = len(sc_df)
            sc_app = sc_df[sc_df['tipo_asignacion'].astype(str).str.strip().isin(app_types)].shape[0]
            sc_voice = total_sc - sc_app
            
            # 2. Valid Calls (from Concluded Services only, then apply factor)
            raw_calls_sc = 0
            if 'cantidad_llamadas' in sc_df.columns:
                raw_calls_sc = sc_df['cantidad_llamadas'].sum()
            total_lv = int(raw_calls_sc * 0.90)
            
            if not cancelled_df.empty:
                if 'usuario_que_asigna' in cancelled_df.columns:
                    assigned = cancelled_df['usuario_que_asigna'].replace('', np.nan).notna()
                    cancelled_posterior = assigned.sum()
                    cancelled_moment = len(cancelled_df) - cancelled_posterior
                else:
                    cancelled_moment = len(cancelled_df)
            
            monthly_results[str(month)] = {
                'sc_total': int(total_sc),
                'sc_app': int(sc_app),
                'sc_voice': int(sc_voice),
                'lv_total': int(total_lv),
                'cp': int(cancelled_posterior),
                'cm': int(cancelled_moment),
                'adoption_pct': (sc_app / total_sc * 100) if total_sc > 0 else 0.0
            }
            
        return monthly_results

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    files = glob.glob('Paises/Client*.csv')
    results = {}
    
    for file in files:
        country = get_country_name(file)
        data = audit_file(file)
        if data:
            results[country] = data
            
    with open('reports/monthly_audit_results.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("Monthly audit complete. Results saved to reports/monthly_audit_results.json")

if __name__ == "__main__":
    main()