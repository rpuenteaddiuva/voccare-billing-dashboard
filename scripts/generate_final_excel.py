import pandas as pd
import glob
import os
import datetime

class GlobalReportGenerator:
    def __init__(self):
        self.tiers_sc = [
            (50, 0.00), (500, 10.51), (1000, 9.28), (2000, 8.04),
            (3000, 6.80), (6000, 5.57), (9000, 5.26), (12000, 4.95),
            (15000, 4.64), (float('inf'), 4.33)
        ]
        self.tiers_lv = [
            (4000, 0.80), (20000, 0.37), (float('inf'), 0.19)
        ]
        self.tiers_app = [
            (5000, 0.45), (20000, 0.35), (float('inf'), 0.20)
        ]
        self.base_fee = 3150.00
        
        # Final Calibrated Factors (LV calculated from Concluded Services only)
        self.country_factors = {
            "Puerto Rico": 0.50,
            "Dominicana": 0.57,
            "Salvador": 1.00,
            "Mexico": 0.29,
            "Argentina": 0.64,
            "Costa Rica": 0.30,
            "Ecuador": 1.00,
            "Chile": 0.74,
            "Uruguay": 0.50,
            "Bolivia": 0.43,
            "Guatemala": 1.00,
            "Peru": 1.00,
            "default": 0.40
        }

    def get_factor(self, country):
        return self.country_factors.get(country, self.country_factors['default'])

    def calculate_tier_cost(self, volume, tiers):
        remaining = volume
        total_cost = 0.0
        current_tier_start = 0
        for limit, price in tiers:
            if remaining <= 0: break
            tier_capacity = limit - current_tier_start
            count = min(remaining, tier_capacity)
            total_cost += count * price
            remaining -= count
            current_tier_start = limit
        return total_cost

    def calculate_sc_cost_2025(self, total_volume, app_volume):
        base_cost = self.calculate_tier_cost(total_volume, self.tiers_sc)
        if total_volume == 0: return 0.0
        app_ratio = app_volume / total_volume
        app_base_cost = base_cost * app_ratio
        discount = app_base_cost * 0.10
        return base_cost - discount

    def process_all(self, input_dir="Paises/"):
        all_data = []
        summary_data = []
        
        files = glob.glob(os.path.join(input_dir, "*.csv"))
        print(f"Found {len(files)} files to process.")
        
        for file_path in files:
            try:
                # Extract Country Name
                filename = os.path.basename(file_path)
                parts = filename.split('_')
                if len(parts) > 2:
                    # Handles "Client01_Puerto_Rico_..." -> "Puerto Rico"
                    # Handles "Client05_Mexico_..." -> "Mexico"
                    # Logic: Join parts between Index 1 and Index of Year (usually starts with 20)
                    country_parts = []
                    for p in parts[1:]:
                        if p.isdigit() and len(p) == 8: break # Date part
                        country_parts.append(p)
                    country_name = " ".join(country_parts)
                else:
                    country_name = "Unknown"

                print(f"Processing {country_name}...")
                
                factor = self.get_factor(country_name)
                df = pd.read_csv(file_path, sep=';', on_bad_lines='skip')
                
                # Date Filter (Jan-Oct 2025)
                df['date_obj'] = pd.to_datetime(df['creacion_asistencia'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                df = df[df['date_obj'].dt.year == 2025].copy()
                df['month'] = df['date_obj'].dt.to_period('M')
                
                app_types = ['APP', 'ANCLAJE APP SOA', 'ANCLAJE', 'ANCLAJE_APP', 'ANCLAJE_APP_SOA']
                
                country_total_2024 = 0
                country_total_2025 = 0
                
                for month, group in df.groupby('month'):
                    sc_df = group[group['estado_asistencia'] == 'CONCLUIDA']
                    total_sc = len(sc_df)
                    app_sc = sc_df[sc_df['tipo_asignacion'].astype(str).str.strip().isin(app_types)].shape[0]
                    
                    # LV Logic: Calls from Concluded Services ONLY * Factor
                    raw_calls_sc = sc_df['cantidad_llamadas'].sum() if 'cantidad_llamadas' in sc_df.columns else 0
                    valid_calls = int(raw_calls_sc * factor)
                    
                    # 2024 Bill
                    cost_sc_24 = self.calculate_tier_cost(total_sc, self.tiers_sc)
                    cost_lv_24 = self.calculate_tier_cost(valid_calls, self.tiers_lv)
                    bill_2024 = self.base_fee + cost_sc_24 + cost_lv_24
                    
                    # 2025 Bill
                    cost_sc_25 = self.calculate_sc_cost_2025(total_sc, app_sc)
                    cost_lv_25 = self.calculate_tier_cost(valid_calls, self.tiers_lv)
                    cost_app_25 = self.calculate_tier_cost(app_sc, self.tiers_app)
                    bill_2025 = self.base_fee + cost_sc_25 + cost_lv_25 + cost_app_25
                    
                    row = {
                        'Pais': country_name,
                        'Mes': str(month),
                        'SC_Total': total_sc,
                        'SC_App': app_sc,
                        'Adopcion_App_%': round((app_sc/total_sc*100), 2) if total_sc else 0,
                        'Llamadas_Validas_Est': valid_calls,
                        'Factor_LV_Usado': factor,
                        'Facturacion_2024_USD': round(bill_2024, 2),
                        'Facturacion_2025_USD': round(bill_2025, 2),
                        'Diferencia_USD': round(bill_2024 - bill_2025, 2)
                    }
                    all_data.append(row)
                    
                    country_total_2024 += bill_2024
                    country_total_2025 += bill_2025

                # Summary Row
                summary_data.append({
                    'Pais': country_name,
                    'Total_2024': round(country_total_2024, 2),
                    'Total_2025': round(country_total_2025, 2),
                    'Ahorro_Total': round(country_total_2024 - country_total_2025, 2),
                    'Ahorro_%': round(((country_total_2024 - country_total_2025)/country_total_2024 * 100), 2) if country_total_2024 else 0
                })

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        # Create Excel
        print("Generating Excel...")
        # Using default engine (openpyxl usually)
        with pd.ExcelWriter('Final_Global_Report_Voccare_2025.xlsx') as writer:
            # Sheet 1: Summary
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Resumen Ejecutivo', index=False)
            
            # Sheet 2: Details
            df_details = pd.DataFrame(all_data)
            df_details.to_excel(writer, sheet_name='Detalle Mensual', index=False)
            
        print("Report generated: Final_Global_Report_Voccare_2025.xlsx")

if __name__ == "__main__":
    gen = GlobalReportGenerator()
    gen.process_all()
