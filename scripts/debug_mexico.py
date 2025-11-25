import pandas as pd

def analyze_mexico_deep_dive(file_path):
    print(f"Analyzing {file_path}...")
    df = pd.read_csv(file_path)
    
    # Date conversion
    df['creacion_asistencia'] = pd.to_datetime(df['creacion_asistencia'], dayfirst=True, errors='coerce')
    
    # Filter 2025
    df_2025 = df[df['creacion_asistencia'].dt.year == 2025].copy()
    
    print(f"Total records 2025: {len(df_2025)}")
    
    # Check statuses
    print("\n--- Status Counts (2025) ---")
    print(df_2025['estado_asistencia'].value_counts())
    
    # Filter Concluded
    df_concl = df_2025[df_2025['estado_asistencia'] == 'CONCLUIDA'].copy()
    print(f"\nConcluded records: {len(df_concl)}")
    
    # Check duplicates
    dupes = df_concl[df_concl.duplicated(subset=['id_asistencia'], keep=False)]
    print(f"\nDuplicate id_asistencia count: {len(dupes)}")
    if len(dupes) > 0:
        print(dupes[['id_asistencia', 'creacion_asistencia', 'estado_asistencia']].head())
        
    # Check missing dates
    missing_fin = df_concl['fecha_finalizacion_asistencia'].isna().sum()
    print(f"\nMissing fecha_finalizacion_asistencia: {missing_fin} ({missing_fin/len(df_concl):.1%})")
    
    # Monthly grouping checks
    df_concl['month'] = df_concl['creacion_asistencia'].dt.to_period('M')
    monthly = df_concl.groupby('month').size()
    
    print("\n--- Monthly Counts (Raw Concluded) ---")
    print(monthly)
    
    # Check specific discrepancy months (April, Sept)
    # April Target: 239, Ours: 193 (Diff -46)
    # Sept Target: 268, Ours: 242 (Diff -26)
    
    # Is there another status?
    # Maybe 'CANCELADA' but billable? (Post-cancelled $2.47 mentioned in CLAUDE.md)
    # But the Excel line says "Servicios Concluidos (C)".
    
    # Let's check if there are records with 'fecha_finalizacion_asistencia' but NOT 'CONCLUIDA'
    has_date_not_concl = df_2025[
        (df_2025['fecha_finalizacion_asistencia'].notna()) & 
        (df_2025['estado_asistencia'] != 'CONCLUIDA')
    ]
    print(f"\nHas End Date but NOT Concluded: {len(has_date_not_concl)}")
    if len(has_date_not_concl) > 0:
        print(has_date_not_concl['estado_asistencia'].value_counts())

if __name__ == "__main__":
    analyze_mexico_deep_dive("Client05_Mexico.csv")
