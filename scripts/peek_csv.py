import pandas as pd
import os
import glob
import re

def get_country_name(filename):
    base = os.path.basename(filename)
    name_part = base.replace('.csv', '')
    match = re.match(r'Client\d+_(.+)', name_part)
    if match:
        raw_name = match.group(1)
        raw_name = re.sub(r'_\d{8}$', '', raw_name)
        return raw_name.replace('_', ' ')
    return name_part

def peek_file_with_delimiter_detection(file_path, n_lines=10):
    print(f"--- Peeking at {file_path} ---")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            first_line = f.readline()
            f.seek(0) # Reset file pointer
        
        delimiters = [' ', ',', ';', '\t', '|']
        detected_delimiter = ','
        for delim in delimiters:
            if first_line.count(delim) > 0:
                 if len(first_line.split(delim)) > 1:
                    detected_delimiter = delim
                    break
        print(f"Detected Delimiter: '{detected_delimiter}'")
        
        df = pd.read_csv(file_path, sep=detected_delimiter, nrows=n_lines, encoding='utf-8', on_bad_lines='skip')
        print(df.head().to_string())
        
        potential_date_cols = ['creacion_asistencia', 'fecha_finalizacion_asistencia', 'fecha_cierre']
        for col in potential_date_cols:
            if col in df.columns:
                print(f"\n--- Sample of '{col}' values ---")
                print(df[col].head().to_string())
                sample_dates = df[col].dropna().head(3).tolist()
                for date_str in sample_dates:
                    try:
                        pd.to_datetime(date_str, dayfirst=True)
                        print(f"  -> Appears dayfirst format: {date_str}")
                    except:
                        try:
                            pd.to_datetime(date_str)
                            print(f"  -> Appears yearfirst format: {date_str}")
                        except:
                            print(f"  -> Could not parse: {date_str}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    paises_dir = "Paises"
    files_to_check = [
        "Client07_Egipto_20251027.csv",
        "Client18_Paraguay_20251027.csv",
        "Client22_Nicaragua_20251027.csv",
        "Client24_Estados_Unidos_20251027.csv",
        "Client19_Colombia_20251027.csv",
        "Client20_Honduras_20251027.csv",
    ]
    
    for f_name in files_to_check:
        full_path = os.path.join(paises_dir, f_name)
        peek_file_with_delimiter_detection(full_path)
