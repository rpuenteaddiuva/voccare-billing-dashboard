import pandas as pd
import glob
import os
import re

class GlobalPolicyComparator:
    def __init__(self):
        self.base_fee = 3150.00
        
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
        
        self.valid_call_factor = 0.90

    def calculate_tier_cost(self, volume, tiers):
        remaining = volume
        total_cost = 0.0
        current_tier_start = 0
        for limit, price in tiers:
            if remaining <= 0: break
            tier_capacity = limit - current_tier_start
            # Fix for first 50 free in SC:
            # The pricing tiers provided usually imply the price applies to that slice.
            # If the first tier is (50, 0.00), it handles the deduction naturally.
            count = min(remaining, tier_capacity)
            total_cost += count * price
            remaining -= count
            current_tier_start = limit
        return total_cost

    def calculate_sc_cost_2025(self, total_volume, app_volume):
        # Policy v2.1 + Commercial Negotiation:
        # 1. Calculate Base Cost for TOTAL volume (determines the tier price)
        base_cost = self.calculate_tier_cost(total_volume, self.tiers_sc)
        
        # 2. Apply 10% Discount ONLY to App Volume
        # We need the average effective rate to apply the discount correctly,
        # or we can re-run the tier logic for the app portion? 
        # No, the tier is determined by the TOTAL volume.
        # So the discount applies to the allocated cost.
        
        if total_volume == 0: return 0.0
        
        # Pro-rata cost allocation
        app_ratio = app_volume / total_volume
        app_base_cost = base_cost * app_ratio
        
        # Discount
        discount = app_base_cost * 0.10
        
        return base_cost - discount

    def process_file(self, file_path):
        try:
            df = pd.read_csv(file_path, sep=';', on_bad_lines='skip')
            
            # Date parsing
            date_col = 'creacion_asistencia'
            if date_col not in df.columns:
                # Fallback for some files
                if 'fecha_finalizacion_asistencia' in df.columns:
                    date_col = 'fecha_finalizacion_asistencia'
                else:
                    return None

            df['date_obj'] = pd.to_datetime(df[date_col], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            # Fallback for dayfirst
            if df['date_obj'].isnull().all():
                 df['date_obj'] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')

            df = df[df['date_obj'].dt.year == 2025].copy()
            if len(df) == 0:
                return None # No 2025 data
                
            df['month'] = df['date_obj'].dt.to_period('M')
            
            app_types = ['APP', 'ANCLAJE APP SOA', 'ANCLAJE', 'ANCLAJE_APP', 'ANCLAJE_APP_SOA']
            
            total_bill_2024 = 0
            total_bill_2025 = 0
            total_sc_vol = 0
            total_app_vol = 0
            
            # Iterate months to calculate monthly bills (fees apply monthly)
            for month, group in df.groupby('month'):
                # Filter Concluded
                if 'estado_asistencia' in group.columns:
                    sc_df = group[group['estado_asistencia'] == 'CONCLUIDA']
                else:
                    sc_df = group # Fallback
                
                month_sc = len(sc_df)
                month_app = sc_df[sc_df['tipo_asignacion'].astype(str).str.strip().isin(app_types)].shape[0]
                
                raw_calls = 0
                if 'cantidad_llamadas' in group.columns:
                    raw_calls = group['cantidad_llamadas'].sum()
                month_valid_calls = int(raw_calls * self.valid_call_factor)
                
                # --- 2024 Calculation ---
                # SC: Paid on Total (after 50)
                cost_sc_24 = self.calculate_tier_cost(month_sc, self.tiers_sc)
                # LV: Paid on Total
                cost_lv_24 = self.calculate_tier_cost(month_valid_calls, self.tiers_lv)
                bill_24 = self.base_fee + cost_sc_24 + cost_lv_24
                
                # --- 2025 Calculation (Strict Policy v2.1 + 10% App Disc) ---
                # SC: Paid on Total (Voice + App) with discount on App portion
                cost_sc_25 = self.calculate_sc_cost_2025(month_sc, month_app)
                # LV: Paid on Total (Assuming NO call reduction for App users yet)
                cost_lv_25 = self.calculate_tier_cost(month_valid_calls, self.tiers_lv)
                # APP: Transaction Fee
                cost_app_25 = self.calculate_tier_cost(month_app, self.tiers_app)
                
                bill_25 = self.base_fee + cost_sc_25 + cost_lv_25 + cost_app_25
                
                total_bill_2024 += bill_24
                total_bill_2025 += bill_25
                total_sc_vol += month_sc
                total_app_vol += month_app
            
            return {
                'sc_vol': total_sc_vol,
                'app_vol': total_app_vol,
                'bill_2024': total_bill_2024,
                'bill_2025': total_bill_2025
            }

        except Exception as e:
            return None

def get_country_name(filename):
    base = os.path.basename(filename)
    name_part = base.replace('.csv', '')
    match = re.match(r'Client\d+_(.+)', name_part)
    if match:
        raw_name = match.group(1)
        raw_name = re.sub(r'_\d{8}$', '', raw_name)
        return raw_name.replace('_', ' ')
    return name_part

def run_all():
    comparator = GlobalPolicyComparator()
    files = glob.glob('Paises/Client*.csv')
    
    print(f"{'Country':<20} | {'Adoption':<8} | {'Bill 2024':<12} | {'Bill 2025':<12} | {'Diff $':<12} | {'Diff %':<8}")
    print("-" * 85)
    
    total_global_savings = 0
    
    for file in files:
        country = get_country_name(file)
        res = comparator.process_file(file)
        
        if res and res['sc_vol'] > 0:
            adoption = (res['app_vol'] / res['sc_vol']) * 100
            diff = res['bill_2024'] - res['bill_2025']
            diff_pct = (diff / res['bill_2024']) * 100
            total_global_savings += diff
            
            print(f"{country:<20} | {adoption:>6.1f}% | ${res['bill_2024']:<11,.0f} | ${res['bill_2025']:<11,.0f} | ${diff:<11,.0f} | {diff_pct:>6.2f}%")
        else:
             # Skip countries with no valid 2025 data or 0 SC
             pass
             
    print("-" * 85)
    print(f"GLOBAL NET SAVINGS: ${total_global_savings:,.2f}")

if __name__ == "__main__":
    run_all()
