import pandas as pd

def debug_argentina():
    file_path = "Paises/Client06_Argentina_20251027.csv"
    print(f"Debugging Argentina: {file_path}")
    
    try:
        # Read without skipping bad lines first to see count
        with open(file_path, 'r', encoding='latin-1') as f:
            raw_lines = len(f.readlines())
        print(f"Total líneas crudas en archivo: {raw_lines}")

        df = pd.read_csv(file_path, sep=';', on_bad_lines='skip', encoding='latin-1') # latin-1 is safer for Spanish CSVs
        print(f"Total líneas leídas por Pandas: {len(df)}")
        
        # Check for non-numeric values in calls
        non_numeric = df[pd.to_numeric(df['cantidad_llamadas'], errors='coerce').isna()]['cantidad_llamadas'].unique()
        print(f"\nValores NO numéricos encontrados en 'cantidad_llamadas': {non_numeric[:10]}")
        
        # Check max value to see if decimals are weird (e.g. 1.000 read as 1)
        df['calls_num'] = pd.to_numeric(df['cantidad_llamadas'], errors='coerce').fillna(0)
        print(f"Valor máximo encontrado: {df['calls_num'].max()}")
        
        # Date Parsing
        df['date_obj'] = pd.to_datetime(df['creacion_asistencia'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        df['month'] = df['date_obj'].dt.to_period('M')
        
        # Filter All 2025
        df_2025 = df[df['date_obj'].dt.year == 2025].copy()
        
        print(f"\n--- Conteo de LLAMADAS (cantidad_llamadas) Año 2025 ---")
        
        # Ensure numeric
        df_2025['cantidad_llamadas'] = pd.to_numeric(df_2025['cantidad_llamadas'], errors='coerce').fillna(0)
        
        monthly_calls = df_2025.groupby('month')['cantidad_llamadas'].sum()
        
        print(f"{ 'Mes':<10} | { 'Llamadas (Suma)':<20}")
        print("-" * 35)
        
        total_calls = 0
        for m in sorted(monthly_calls.index.astype(str)):
            calls = monthly_calls.get(m, 0)
            total_calls += calls
            print(f"{m:<10} | {calls:<20,.0f}")
            
        print("-" * 35)
        print(f"{ 'TOTAL 2025':<10} | {total_calls:<20,.0f}")
        
        print(f"\n(Tu suma manual fue 100,401. ¿Coincide?)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_argentina()
