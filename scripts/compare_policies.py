import pandas as pd
import glob
import os
import sys

class GlobalPolicyReport:
    def __init__(self, app_discount_pct=10, app_fee=0.45, base_fee=None):
        # Shared Pricing
        self.app_discount_pct = app_discount_pct
        self.app_fee = app_fee
        self.base_fee = base_fee if base_fee is not None else 3150.0 # Make base_fee configurable

        # Tiers for SC costs (2024 & 2025)
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
        
        # LV per SC Ratios (Derived from Excel: LV / SC)
        self.country_ratios = {
            "Dominicana": 1.02,   # Very efficient (MCS)
            "Puerto Rico": 3.00,  # High coordination (PR)
            "Guatemala": 2.12,    # High coordination (GU)
            "Mexico": 1.50,
            "Costa Rica": 3.12,   # Very high coordination (CR + CR-CR)
            "default": 1.50
        }
        
        # Price Adjustment Factors (To match Excel Revenue Targets)
        self.price_adjustment_factors = {
            "Dominicana": 1.0,
            "default": 1.0
        }
        
        # Call Efficiency Factors (Valid >15s / Total Raw Calls)
        # Calibrated from 'REPORTE ACUMULADO INDICES SEPTIEMBRE 2025 (1).xlsx' vs CSV `cantidad_llamadas` (Jan-Sep 2025)
        self.call_efficiency_factors = {
            "Argentina": 0.49,  
            "Chile": 0.50, # Factor 1.27 (Excel > CSV) - Using default 0.50 as a safeguard
            "Colombia": 0.50, # CSV calls are 0. Using default 0.50
            "Costa Rica": 0.41, 
            "Dominicana": 0.47, 
            "Ecuador": 0.23,    
            "Guatemala": 0.32,  
            "Honduras": 0.50, # CSV calls are 0. Using default 0.50
            "Mexico": 0.47,     
            "Nicaragua": 0.50, # CSV calls are 0. Using default 0.50
            "Paraguay": 0.50, # CSV calls are 0. Using default 0.50
            "Peru": 0.95,       
            "Puerto Rico": 0.633, 
            "Salvador": 0.50, # Factor 16.41 (Excel > CSV) - Using default 0.50 as a safeguard
            "Uruguay": 0.45,    
            "Bolivia": 0.46,    
            "default": 0.50 # Fallback for any other country or zero cases if not caught above
        }

    def get_ratio(self, country):
        return self.country_ratios.get(country, self.country_ratios['default'])
    
    def get_price_adjust(self, country):
        return self.price_adjustment_factors.get(country, self.price_adjustment_factors['default'])
        
    def get_efficiency_factor(self, country):
        return self.call_efficiency_factors.get(country, self.call_efficiency_factors['default'])

    def calculate_tier_cost(self, volume, tiers, adjustment_factor=1.0):
        remaining = volume
        total_cost = 0.0
        current_tier_start = 0
        for limit, price in tiers:
            if remaining <= 0: break
            
            # Apply adjustment to price
            effective_price = price * adjustment_factor
            
            tier_capacity = limit - current_tier_start
            count = min(remaining, tier_capacity)
            total_cost += count * effective_price
            remaining -= count
            current_tier_start = limit
        return total_cost

    def process_country(self, file_path, country_name, year_filter=2025):
        try:
            lv_ratio = self.get_ratio(country_name)
            price_adj = self.get_price_adjust(country_name)
            
            df = pd.read_csv(file_path, sep=';', on_bad_lines='skip')
            # Clean column names to remove accidental whitespace
            df.columns = df.columns.str.strip()
            
            df['date_obj'] = pd.to_datetime(df['creacion_asistencia'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            
            # Dynamic Year Filter
            df = df[df['date_obj'].dt.year == year_filter].copy()
            
            if df.empty: return pd.DataFrame() 

            df['month'] = df['date_obj'].dt.to_period('M')
            
            app_types = ['APP', 'ANCLAJE APP SOA', 'ANCLAJE', 'ANCLAJE_APP', 'ANCLAJE_APP_SOA']
            results = []
            
            for month, group in df.groupby('month'):
                sc_df = group[group['estado_asistencia'] == 'CONCLUIDA']
                total_sc = len(sc_df)
                app_sc = sc_df[sc_df['tipo_asignacion'].astype(str).str.strip().isin(app_types)].shape[0]
                voice_sc = total_sc - app_sc
                
                valid_calls_total = int(total_sc * lv_ratio)

                # DEBUG: Check LV Logic path
                # print(f"DEBUG LV {country_name} - Month {month}: Starting LV calculation.")
                
                # LV Logic: FORCE READING FROM CSV
                # We trust the column exists because debug_columns.py proved it.
                # If this crashes, we know EXACTLY why.
                
                if 'cantidad_llamadas' not in group.columns:
                    raise ValueError(f"CRITICAL: 'cantidad_llamadas' missing for {country_name}. Available: {group.columns.tolist()}")

                raw_calls = pd.to_numeric(group['cantidad_llamadas'], errors='coerce').fillna(0).sum()
                eff_factor = self.get_efficiency_factor(country_name)
                valid_calls_total = int(raw_calls * eff_factor)
                
                # Remove Fallback logic to prevent silent failures
                # valid_calls_total = int(total_sc * lv_ratio) <--- DELETED

                # Calculate Cancelled
                cancelled_df = group[group['estado_asistencia'].astype(str).str.upper().str.contains('CANCEL')]
                cp = 0
                cm = 0
                if not cancelled_df.empty:
                    if 'usuario_que_asigna' in cancelled_df.columns:
                         vals = cancelled_df['usuario_que_asigna'].astype(str).str.strip()
                         # Filter out common null string representations
                         is_assigned = ~vals.isin(['', 'nan', 'None']) & cancelled_df['usuario_que_asigna'].notna()
                         cp = is_assigned.sum()
                         cm = len(cancelled_df) - cp
                    else:
                         cm = len(cancelled_df)
                
                # 2024 Calculation
                cost_sc_24 = self.calculate_tier_cost(total_sc, self.tiers_sc, price_adj)
                cost_lv_24 = self.calculate_tier_cost(valid_calls_total, self.tiers_lv, price_adj)
                bill_2024 = (self.base_fee * price_adj) + cost_sc_24 + cost_lv_24
                
                # 2025 Calculation (Dynamic)
                base_sc_cost = self.calculate_tier_cost(total_sc, self.tiers_sc, price_adj)
                discount_amount = 0
                if total_sc > 0:
                    app_share = (base_sc_cost * (app_sc / total_sc))
                    discount_amount = app_share * (self.app_discount_pct / 100.0)
                
                cost_sc_25 = base_sc_cost - discount_amount
                cost_lv_25 = self.calculate_tier_cost(valid_calls_total, self.tiers_lv, price_adj)
                
                # Dynamic App Fee
                ratio_fee = self.app_fee / 0.45 
                scaled_app_tiers = [(l, p * ratio_fee) for l, p in self.tiers_app]
                cost_app_25 = self.calculate_tier_cost(app_sc, scaled_app_tiers, 1.0) 

                bill_2025 = (self.base_fee * price_adj) + cost_sc_25 + cost_lv_25 + cost_app_25
                
                # Dictionary keys match Dashboard requirements
                results.append({
                    'Pais': country_name,
                    'Mes': str(month),
                    'SC Total': int(total_sc),
                    'SC App': int(app_sc),
                    'SC Voz': int(voice_sc),
                    'Adopcion (%)': round((app_sc/total_sc*100), 1) if total_sc else 0,
                    'Llamadas Validas': int(valid_calls_total),
                    'Cancelado Posterior': int(cp),
                    'Cancelado Momento': int(cm),
                    
                    # Detalles 2024
                    '2024 SC': round(cost_sc_24, 2),
                    '2024 LV': round(cost_lv_24, 2),
                    'Factura 2024': round(bill_2024, 2),
                    
                    # Detalles 2025
                    '2025 SC Base': round(base_sc_cost, 2),
                    '2025 Desc.': round(discount_amount, 2),
                    '2025 App Fee': round(cost_app_25, 2),
                    '2025 LV': round(cost_lv_25, 2),
                    'Factura 2025': round(bill_2025, 2),
                    
                    'Ahorro': round(bill_2024 - bill_2025, 2)
                })
                
            return pd.DataFrame(results)
        except Exception as e:
            print(f"ERROR in process_country for {country_name}: {e}")
            return pd.DataFrame()

    def generate_latex(self, input_dir="Paises/"):
        # Minimal logic to avoid import errors, full implementation preserved in backup if needed
        pass 

if __name__ == "__main__":
    report = GlobalPolicyReport()
    print("Module loaded.")