import pandas as pd

def clean_and_process_mexico(file_path):
    print(f"Processing {file_path}...")
    
    # Load CSV
    df = pd.read_csv(file_path)
    
    # Convert dates
    # Mexico format: %d/%m/%Y %H:%M
    df['creacion_asistencia'] = pd.to_datetime(df['creacion_asistencia'], dayfirst=True, errors='coerce')
    
    # Filter for 2025
    df_2025 = df[df['creacion_asistencia'].dt.year == 2025].copy()
    
    # Filter for Concluded services
    # Note: CLAUDE.md mentions filtering by 'CONCLUIDA' but usually we check the state column
    # Let's verify the column name. 'estado_asistencia'
    df_concluded = df_2025[df_2025['estado_asistencia'] == 'CONCLUIDA'].copy()
    
    # Group by Month
    df_concluded['month'] = df_concluded['creacion_asistencia'].dt.to_period('M')
    
    # Calculate Monthly Totals
    monthly_counts = df_concluded.groupby('month').size()
    
    print("\n--- Unique 'tipo_asignacion' values ---")
    print(df_concluded['tipo_asignacion'].unique())

    print("\n--- Monthly Concluded Services (Mexico 2025) ---")
    print(monthly_counts)
    
    # Define App vs Non-App
    # Note: 'ANCLAJE APP SOA' has spaces in the CSV, not underscores
    app_types = ['APP', 'ANCLAJE APP SOA', 'ANCLAJE', 'ANCLAJE_APP', 'ANCLAJE_APP_SOA']
    
    def classify_source(row):
        val = str(row['tipo_asignacion']).strip()
        if val in app_types:
            return 'EKUS (App)'
        else:
            return 'GLOBAL (No App)'
            
    df_concluded['source'] = df_concluded.apply(classify_source, axis=1)
    
    # Group by Month and Source
    breakdown = df_concluded.groupby(['month', 'source']).size().unstack(fill_value=0)
    
    print("\n--- Breakdown by Source (App vs No App) ---")
    print(breakdown)
    
    # Add Total column to verify against target
    breakdown['Total'] = breakdown.sum(axis=1)
    print("\n--- Verification ---")
    print(breakdown)
    
    # Hardcoded targets from Excel
    targets = {
        '2025-01': 288, '2025-02': 210, '2025-03': 250,
        '2025-04': 239, '2025-05': 209, '2025-06': 241,
        '2025-07': 220, '2025-08': 240, '2025-09': 268
    }
    
    print("\n--- Accuracy Check ---")
    total_diff = 0
    for month, count in monthly_counts.items():
        month_str = str(month)
        if month_str in targets:
            target = targets[month_str]
            diff = count - target
            total_diff += abs(diff)
            print(f"{month_str}: Calc={count}, Target={target}, Diff={diff}")
            
    print(f"\nTotal Absolute Difference: {total_diff}")

if __name__ == "__main__":
    clean_and_process_mexico("Client05_Mexico.csv")
