import pandas as pd

def analyze_calls():
    file_path = "Paises/Client06_Argentina_20251027.csv"
    print(f"ANALIZANDO LLAMADAS: {file_path}")
    
    try:
        # Leer solo columnas necesarias para velocidad
        df = pd.read_csv(file_path, sep=';', usecols=['id_asistencia', 'estado_asistencia', 'cantidad_llamadas', 'creacion_asistencia'], on_bad_lines='skip')
        
        # Convertir a numérico
        df['cantidad_llamadas'] = pd.to_numeric(df['cantidad_llamadas'], errors='coerce').fillna(0)
        
        # Filtro Año 2025 (Ene-Sep para comparar con tus datos)
        df['date'] = pd.to_datetime(df['creacion_asistencia'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        df_2025 = df[(df['date'].dt.year == 2025) & (df['date'].dt.month <= 9)].copy()
        
        print(f"\n--- DATOS ENE-SEP 2025 ---")
        
        # 1. SUMA BRUTA (A lo bruto, sumando toda la columna)
        raw_sum = df_2025['cantidad_llamadas'].sum()
        print(f"1. Suma BRUTA de la columna (Todas las filas): {float(raw_sum):,.0f}")
        print(f"   (¿Coincide con tus 83k? Probablemente incluya todo estado y duplicados)")

        # 2. SUMA SOLO CONCLUIDAS (Como lo hace el Dashboard actual)
        concluded_sum = df_2025[df_2025['estado_asistencia'] == 'CONCLUIDA']['cantidad_llamadas'].sum()
        print(f"2. Suma en estado CONCLUIDA (Dashboard actual): {float(concluded_sum):,.0f}")
        print(f"   (¿Coincide con tus 25k?)")

        # 3. SUMA TOTAL ASISTENCIAS ÚNICAS (Tomando el máximo de llamadas por ID)
        # Si una asistencia aparece 2 veces con 5 llamadas, sumamos 5, no 10.
        unique_sum = df_2025.groupby('id_asistencia')['cantidad_llamadas'].max().sum()
        print(f"3. Suma Des-duplicada (Max por ID, todos los estados): {float(unique_sum):,.0f}")

        # 4. SUMA ASISTENCIAS ÚNICAS PERO SOLO DE 'CONCLUIDA' + 'CANCELADA POSTERIOR'
        # A veces las canceladas posterior también cobran llamadas.
        relevant_states = ['CONCLUIDA', 'CANCELADA POSTERIOR', 'CANCELADA AL MOMENTO']
        # Filter rows with relevant states first
        df_rel = df_2025[df_2025['estado_asistencia'].isin(relevant_states)]
        # Group by ID and take max calls
        relevant_sum = df_rel.groupby('id_asistencia')['cantidad_llamadas'].max().sum()
        
        print(f"4. Suma Des-duplicada (Max por ID) de (Concluidas + Canceladas): {float(relevant_sum):,.0f}")
        print(f"   (¿Se acerca a los 42k del reporte de indicadores?)")
        
        # Breakdown by State (Unique IDs)
        print("\n--- Desglose por Estado (Suma de Max Llamadas por ID) ---")
        state_calls = df_2025.groupby(['id_asistencia', 'estado_asistencia'])['cantidad_llamadas'].max().reset_index()
        print(state_calls.groupby('estado_asistencia')['cantidad_llamadas'].sum().sort_values(ascending=False))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_calls()
