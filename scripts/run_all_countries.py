import os
import subprocess
import sys
import glob
import re

def get_country_name(filename):
    # Patterns to try:
    # Client05_Mexico.csv -> Mexico
    # Client01_Puerto_Rico_20251027.csv -> Puerto Rico
    
    base = os.path.basename(filename)
    name_part = base.replace('.csv', '')
    
    # Remove "ClientXX_" prefix if present
    match = re.match(r'Client\d+_(.+)', name_part)
    if match:
        raw_name = match.group(1)
        # Remove date suffix if present (e.g., _20251027)
        raw_name = re.sub(r'_\d{8}$', '', raw_name)
        # Replace underscores with spaces for display
        return raw_name.replace('_', ' ')
    
    return name_part

def run_all_countries():
    # Find all CSV files matching the pattern
    # Assuming script is running from root or we look in root
    # The script is in 'scripts/', but execution is usually from root.
    # We'll look in the current working directory (root).
    csv_files = glob.glob('Paises/Client*.csv')
    
    if not csv_files:
        print("No 'Client*.csv' files found in the current directory.")
        return

    # Get absolute path to the calculator script
    script_path = os.path.join(os.path.dirname(__file__), 'calculadora_nueva_politica.py')
    
    print(f"Found {len(csv_files)} files to process.")

    for filename in csv_files:
        country = get_country_name(filename)
            
        print(f"\n{'='*20} {country.upper()} {'='*20}")
        
        # Construct command
        cmd = [sys.executable, script_path, "--file", filename, "--country", country]
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running for {country}: {e}")

if __name__ == "__main__":
    run_all_countries()