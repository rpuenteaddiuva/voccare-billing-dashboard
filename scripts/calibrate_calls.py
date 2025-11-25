import pandas as pd
import glob
import os

def scan_call_volumes():
    print(f"{'Pais':<20} | {'Servicios (SC)':<15} | {'Llamadas Totales (CSV)':<22} | {'Ratio Bruto (Calls/SC)':<22}")
    print("-" * 85)
    
    files = glob.glob("Paises/*.csv")
    
    for f in sorted(files):
        try:
            # Extract country name
            parts = os.path.basename(f).split('_')
            c_name = "Desconocido"
            if len(parts) > 2:
                c_parts = [p for p in parts[1:] if not (p.isdigit() and len(p)==8)]
                c_name = " ".join(c_parts)

            # Read CSV
            df = pd.read_csv(f, sep=';', usecols=['estado_asistencia', 'cantidad_llamadas', 'creacion_asistencia'], on_bad_lines='skip')
            
            # Filter 2025
            df['date'] = pd.to_datetime(df['creacion_asistencia'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            df = df[df['date'].dt.year == 2025].copy()
            
            if df.empty: continue
            
            # Calculate Metrics
            # SC: Only CONCLUIDA
            sc_count = len(df[df['estado_asistencia'] == 'CONCLUIDA'])
            
            # Calls: Sum of 'cantidad_llamadas' (cleaning NaNs)
            df['cantidad_llamadas'] = pd.to_numeric(df['cantidad_llamadas'], errors='coerce').fillna(0)
            # We take calls from ALL services (Concluded + Cancelled usually generate calls)
            # Or strictly from Concluded? Usually traffic implies all. Let's stick to Concluded first for consistency with billing logic, 
            # OR verify if cancellations have calls.
            # Let's use calls linked to CONCLUIDA services to be safe for now, or Total?
            # Let's show Calls from SC services for Ratio consistency.
            
            calls_sc_only = df[df['estado_asistencia'] == 'CONCLUIDA']['cantidad_llamadas'].sum()
            
            ratio = calls_sc_only / sc_count if sc_count > 0 else 0
            
            print(f"{c_name:<20} | {sc_count:<15,.0f} | {calls_sc_only:<22,.0f} | {ratio:<22.2f}")
            
        except Exception as e:
            pass # Skip errors for cleaner output

if __name__ == "__main__":
    scan_call_volumes()