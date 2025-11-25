import pandas as pd

def debug_columns():
    file_path = "Paises/Client06_Argentina_20251027.csv"
    print(f"--- DIAGNÓSTICO DE COLUMNAS: {file_path} ---")
    
    try:
        # Leer exactamente como lo hace el script principal
        df = pd.read_csv(file_path, sep=';', on_bad_lines='skip')
        
        print("\nLista de columnas detectadas (con repr() para ver caracteres ocultos):")
        for col in df.columns:
            print(f"'{col}' -> repr: {repr(col)}")
            
        # Verificar si 'cantidad_llamadas' existe después de strip
        df.columns = df.columns.str.strip()
        print("\nDespués de strip():")
        if 'cantidad_llamadas' in df.columns:
            print("¡ÉXITO! La columna 'cantidad_llamadas' AHORA existe.")
            print("Muestra de datos:")
            print(df['cantidad_llamadas'].head())
        else:
            print("FALLO: La columna 'cantidad_llamadas' NO existe ni siquiera después de strip().")
            # Busquemos parecidas
            for col in df.columns:
                if 'llamada' in col.lower():
                    print(f"¿Quizás quisiste decir esta?: '{col}'")

    except Exception as e:
        print(f"Error leyendo archivo: {e}")

if __name__ == "__main__":
    debug_columns()
