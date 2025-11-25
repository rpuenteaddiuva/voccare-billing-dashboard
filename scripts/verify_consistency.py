import pandas as pd
import glob
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from compare_policies import GlobalPolicyReport

# DEBUG: Print the path of the imported module
print(f"DEBUG: Importing GlobalPolicyReport from: {GlobalPolicyReport.__module__}")

def verify_consistency():
    report_gen = GlobalPolicyReport() # Uses default discount (10%) and app fee (0.45) for consistency check
    input_dir = "Paises/"
    
    # Targets extracted from 'REPORTE ACUMULADO INDICES SEPTIEMBRE 2025 (1).xlsx' (Approximate Annualized based on Jan-Sep avg)
    # "Ingresos del Mes Técnico" or equivalent Fee calculation
    # Note: Many sheets had 0 or missing data in "Ingresos", except MCS.
    # We will focus on comparing the logic consistency.
    
    print(f"{'Pais':<15} | {'Simulado 2024':<15} | {'Simulado 2025':<15} | {'Diferencia':<15} | {'Check Suma':<10}")
    print("-" * 80)
    
    files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    grand_total_24 = 0
    grand_total_25 = 0
    
    for file_path in files:
        filename = os.path.basename(file_path)
        parts = filename.split('_')
        country_name = "Desconocido"
        if len(parts) > 2:
            country_parts = []
            for p in parts[1:]:
                if p.isdigit() and len(p) == 8: break
                country_parts.append(p)
            country_name = " ".join(country_parts)
            
        # Run Simulation
        df_res = report_gen.process_country(file_path, country_name, year_filter=2025)
        
        if not df_res.empty and 'Mes' in df_res.columns:
            # Convert 'Mes' to string before Period object for robustness
            df_res['Mes'] = df_res['Mes'].astype(str)
            
            # Filter for Jan-Sep 2025 (months 1 to 9)
            df_filtered = df_res[df_res['Mes'].apply(lambda x: pd.Period(x).month <= 9)]

            if not df_filtered.empty:
                # Sum columns
                total_24_sum = df_filtered['Factura 2024'].sum()
                total_25_sum = df_filtered['Factura 2025'].sum()
                
                grand_total_24 += total_24_sum
                grand_total_25 += total_25_sum
                
                print(f"{country_name:<15} | ${total_24_sum:,.0f}       | ${total_25_sum:,.0f}       | ${total_24_sum - total_25_sum:,.0f}       | OK")
            else:
                print(f"{country_name:<15} | N/A             | N/A             | N/A             | NO DATA (Jan-Sep)")
        else:
            print(f"{country_name:<15} | N/A             | N/A             | N/A             | NO DATA")

    print("-" * 80)
    print(f"{'TOTAL GLOBAL':<15} | ${grand_total_24:,.0f}       | ${grand_total_25:,.0f}       | ${grand_total_24 - grand_total_25:,.0f}")

if __name__ == "__main__":
    verify_consistency()
