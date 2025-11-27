import pandas as pd
import os

def calculate_factor():
    # 1. Sum User Data (Valid Calls)
    mcs_calls = [47063, 43318, 46180, 35777, 49883, 49084, 44750, 43567, 50964, 55284]
    inc_calls = [22411, 20531, 23262, 23477, 24376, 21542, 21895, 20521, 19880, 22001]
    
    total_valid_calls = sum(mcs_calls) + sum(inc_calls)
    print(f"Total Valid Calls (User Data - Jan-Oct): {total_valid_calls:,}")

    # 2. Sum Raw Calls from CSV
    file_path = "Paises/Client01_Puerto_Rico_20251027.zip"
    try:
        # Use simple read first to check columns if needed, but we know structure
        df = pd.read_csv(file_path, sep=';', on_bad_lines='skip', compression='zip')
        df.columns = df.columns.str.strip()
        
        # Parse Dates
        # Based on compare_policies.py logic, it uses 'creacion_asistencia'
        df['date_obj'] = pd.to_datetime(df['creacion_asistencia'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        
        # Filter Jan - Oct 2025
        mask = (df['date_obj'].dt.year == 2025) & (df['date_obj'].dt.month <= 10)
        df_period = df[mask]
        
        if 'cantidad_llamadas' in df_period.columns:
            raw_calls = pd.to_numeric(df_period['cantidad_llamadas'], errors='coerce').fillna(0).sum()
            print(f"Total Raw Calls (CSV Data - Jan-Oct): {raw_calls:,.0f}")
            
            if raw_calls > 0:
                factor = total_valid_calls / raw_calls
                print(f"Calculated Factor: {factor:.4f}")
            else:
                print("Error: Raw calls is 0")
        else:
            print("Error: 'cantidad_llamadas' column not found.")
            
    except Exception as e:
        print(f"Error processing CSV: {e}")

if __name__ == "__main__":
    calculate_factor()