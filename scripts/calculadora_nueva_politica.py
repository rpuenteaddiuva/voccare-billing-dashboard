import pandas as pd
import argparse
import sys

class VoccareCalculator:
    def __init__(self, country_name):
        self.country = country_name
        # 2025 Pricing Structure
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
        self.cancel_fee = 2.47
        
        # Configuration per country
        self.config = {
            'Mexico': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Dominicana': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Puerto Rico': {'date_col': 'fecha_finalizacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Argentina': {'date_col': 'fecha_finalizacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Costa Rica': {'date_col': 'fecha_finalizacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Salvador': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Egipto': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Ecuador': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Chile': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Uruguay': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Bolivia': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Guatemala': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Peru': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Paraguay': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Colombia': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Honduras': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Nicaragua': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
            'Estados Unidos': {'date_col': 'creacion_asistencia', 'date_fmt': '%Y-%m-%d %H:%M:%S', 'valid_call_factor': 0.90},
        }
        
    def calculate_service_cost(self, total_services_volume, voice_services_count):
        """
        Calculates the cost for voice-originated services based on tiered pricing.
        The tiers are determined by `total_services_volume` (voice + app).
        The actual charged quantity is `voice_services_count`, but only for services
        beyond the initial 50 (total services) which are covered by the base fee.
        """
        if voice_services_count == 0: return 0.0

        total_cost = 0.0
        
        # Determine how many voice services are in the 'chargeable' portion (after the first 50 total services)
        # This assumes voice and app services are distributed proportionally after the initial 50 free slots.
        chargeable_slots = max(0, total_services_volume - 50)
        if total_services_volume == 0: # Avoid division by zero
            proportion_voice = 0
        else:
            proportion_voice = voice_services_count / total_services_volume
            
        effective_chargeable_voice_count = int(chargeable_slots * proportion_voice)

        # Now, apply the tiered pricing to these `effective_chargeable_voice_count`
        remaining_to_charge = effective_chargeable_voice_count
        current_tier_start_for_charge = 0 # This refers to the *count within the chargeable slots*

        for limit_total_volume, price in self.tiers_sc:
            if remaining_to_charge <= 0: break
            
            # Map the `limit_total_volume` to the chargeable slots. E.g., if tier is 500, but first 50 are free,
            # then this tier actually covers from 51 to 500, which is 450 chargeable slots.
            tier_start_in_chargeable_slots = max(0, limit_total_volume - 50 - (limit_total_volume - (self.tiers_sc[self.tiers_sc.index((limit_total_volume, price)) - 1][0] if self.tiers_sc.index((limit_total_volume, price)) > 0 else 0) if limit_total_volume > 50 else 0) ) # This logic is too complex.

            # Let's simplify: the *tier prices* are for slots 51-500, 501-1000 etc.
            # We just need to determine how many `effective_chargeable_voice_count` fall into these ranges.
            
            # Simplified logic based on example 2 (485 services): first 50 free, next 435 charged at $10.51.
            # This implies the tiers apply to the count *after* 50. So, tier 51-500 means 1-450 of the *charged* services.
            
            # Let's recalculate the tiers relative to 0 being the 51st service.
            relative_tiers = []
            for idx, (limit, price) in enumerate(self.tiers_sc):
                if limit <= 50: # These are covered by base fee, cost is 0
                    continue
                # Adjust limits: 500 becomes 450 (500-50), 1000 becomes 950 (1000-50), etc.
                adjusted_limit = limit - 50
                relative_tiers.append((adjusted_limit, price))

            # Now, apply this to `effective_chargeable_voice_count`
            remaining_to_charge_relative = effective_chargeable_voice_count
            current_relative_start = 0

            for limit_rel, price_rel in relative_tiers:
                if remaining_to_charge_relative <= 0: break
                
                tier_capacity_rel = limit_rel - current_relative_start
                count_in_tier_rel = min(remaining_to_charge_relative, tier_capacity_rel)
                
                total_cost += count_in_tier_rel * price_rel
                
                remaining_to_charge_relative -= count_in_tier_rel
                current_relative_start = limit_rel
        
        return total_cost
    def calculate_call_cost(self, voice_calls_count):
        remaining = voice_calls_count
        total_cost = 0.0
        current_tier_start = 0
        
        for limit, price in self.tiers_lv:
            if remaining <= 0: break
            
            tier_capacity = limit - current_tier_start
            count_in_tier = min(remaining, tier_capacity)
            
            total_cost += count_in_tier * price
            
            remaining -= count_in_tier
            current_tier_start = limit
            
        return total_cost

    def calculate_app_transaction_cost(self, app_transactions_count):
        if app_transactions_count == 0: return 0.0
        
        remaining = app_transactions_count
        total_cost = 0.0
        current_tier_start = 0
        
        for limit, price in self.tiers_app:
            if remaining <= 0: break
            
            tier_capacity = limit - current_tier_start
            count_in_tier = min(remaining, tier_capacity)
            
            total_cost += count_in_tier * price
            
            remaining -= count_in_tier
            current_tier_start = limit
            
        return total_cost
    def run(self, file_path):
        print(f"--- Processing {self.country} ---")
        cfg = self.config.get(self.country, self.config['Mexico'])
        
        try:
            sep = ';' # Assume semicolon for all files in Paises directory
            
            df = pd.read_csv(file_path, sep=sep, on_bad_lines='skip')
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return

        try:
            # Try format based on config first
            df['date_obj'] = pd.to_datetime(df[cfg['date_col']], format=cfg['date_fmt'], errors='coerce')
        except Exception as e:
             print(f"Date parsing error: {e}")
             return
        
        df = df[df['date_obj'].dt.year == 2025].copy()
        df['month'] = df['date_obj'].dt.to_period('M')
        
        app_types = ['APP', 'ANCLAJE APP SOA', 'ANCLAJE', 'ANCLAJE_APP', 'ANCLAJE_APP_SOA']
        
        totals = {'sc_count': 0, 'app_transactions_count': 0, 'valid_voice_calls': 0, 'sc_cost': 0, 'lv_cost': 0, 'app_cost': 0, 'total_bill': 0}
        
        print(f"{'Month':<10} | {'SC':<5} | {'APP Tx':<7} | {'LV':<5} | {'Cost SC':<10} | {'Cost LV':<10} | {'Cost APP':<10} | {'Base Fee':<10} | {'Total Bill':<12}")
        print("-" * 110)
        
        for month, group in df.groupby('month'):
            # Services Concluidos (SC) - Total volume for tiers
            sc_df = group[group['estado_asistencia'] == 'CONCLUIDA']
            total_sc_volume = len(sc_df)
            
            # App Transactions (APP) - Direct count for APP billing
            app_transactions_count = sc_df[sc_df['tipo_asignacion'].astype(str).str.strip().isin(app_types)].shape[0]
            
            # Voice Services for SC cost calculation
            voice_sc_count = total_sc_volume - app_transactions_count

            # Llamadas Validas (LV) - Count ALL calls from the group, regardless of source
            raw_total_calls = 0
            if 'cantidad_llamadas' in group.columns:
                raw_total_calls = group['cantidad_llamadas'].sum()
            valid_voice_calls = int(raw_total_calls * cfg['valid_call_factor'])
            
            # Calculate costs
            # SC Cost: Applies to TOTAL volume (Voice + App), as per Policy v2.1 Formula
            cost_sc = self.calculate_service_cost(total_sc_volume, total_sc_volume)
            cost_lv = self.calculate_call_cost(valid_voice_calls)
            cost_app = self.calculate_app_transaction_cost(app_transactions_count)
            
            # Total monthly bill
            monthly_bill = self.base_fee + cost_sc + cost_lv + cost_app
            
            # Accumulate totals
            totals['sc_count'] += total_sc_volume
            totals['app_transactions_count'] += app_transactions_count
            totals['valid_voice_calls'] += valid_voice_calls
            totals['sc_cost'] += cost_sc
            totals['lv_cost'] += cost_lv
            totals['app_cost'] += cost_app
            totals['total_bill'] += monthly_bill
            
            print(f"{str(month):<10} | {total_sc_volume:<5} | {app_transactions_count:<7} | {valid_voice_calls:<5} | ${cost_sc:,.2f}   | ${cost_lv:,.2f}   | ${cost_app:,.2f}   | ${self.base_fee:,.2f}   | ${monthly_bill:,.2f}")

        print("-" * 110)
        print(f"TOTAL      | {totals['sc_count']:<5} | {totals['app_transactions_count']:<7} | {totals['valid_voice_calls']:<5} | ${totals['sc_cost']:,.2f}   | ${totals['lv_cost']:,.2f}   | ${totals['app_cost']:,.2f}   | ${self.base_fee * len(df['month'].unique()):,.2f}   | ${totals['total_bill']:,.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--country', default='Mexico')
    args = parser.parse_args()
    
    calc = VoccareCalculator(args.country)
    calc.run(args.file)
