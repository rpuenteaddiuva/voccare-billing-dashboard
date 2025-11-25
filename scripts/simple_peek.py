import pandas as pd
import sys
import os

def peek_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"--- Peeking at {file_path} ---")
    try:
        # Try semicolon first
        df = pd.read_csv(file_path, sep=';', on_bad_lines='skip', nrows=5)
        if len(df.columns) < 2:
             # Fallback to comma
             df = pd.read_csv(file_path, sep=',', on_bad_lines='skip', nrows=5)
        
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 5 rows:")
        print(df.to_string())
        
        # Check for client-like columns
        client_cols = [c for c in df.columns if 'cuenta' in c.lower() or 'plan' in c.lower() or 'cliente' in c.lower()]
        if client_cols:
             print(f"\nPotential Client Columns found: {client_cols}")
             
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        peek_file(sys.argv[1])
    else:
        print("Usage: python peek_csv.py <file_path>")
