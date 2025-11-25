import os
import glob
import zipfile

def compress_csvs():
    input_dir = "Paises"
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    print(f"Encontrados {len(csv_files)} archivos CSV para comprimir...")
    
    for csv_file in csv_files:
        base_name = os.path.basename(csv_file)
        zip_name = csv_file.replace(".csv", ".zip")
        
        print(f"Comprimiendo: {base_name} -> {os.path.basename(zip_name)}")
        
        try:
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add file to zip with the same name
                zf.write(csv_file, arcname=base_name)
            
            # Verify zip was created
            if os.path.exists(zip_name):
                os.remove(csv_file) # Remove original huge file
                print("  -> Original eliminado.")
        except Exception as e:
            print(f"  Error comprimiendo {base_name}: {e}")

if __name__ == "__main__":
    compress_csvs()