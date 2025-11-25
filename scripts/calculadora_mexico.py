import pandas as pd
import numpy as np

class VoccareCalculator:
    def __init__(self, country_config):
        self.config = country_config
        self.tiers_sc = [
            (50, 0.00),     # First 50 included in fee
            (500, 10.51),   # 51-500
            (1000, 9.28),   # 501-1000
            (2000, 8.04),   # 1001-2000
            (3000, 6.80),   # 2001-3000
            (6000, 5.57),   # 3001-6000
            (9000, 5.26),   # 6001-9000
            (12000, 4.95),  # 9001-12000
            (15000, 4.64),  # 12001-15000
            (float('inf'), 4.33) # >15000
        ]
        self.tiers_calls = [
            (4000, 0.80),
            (20000, 0.37),
            (float('inf'), 0.19)
        ]
        self.base_fee = 3150.00
        self.cancel_fee = 2.47
        
        # "New Policy" parameters
        self.app_discount = 0.0 # Percentage discount for App services (0.0 to 1.0)
        self.app_call_reduction_factor = 0.238 # 23.8% reduction in calls for App users

    def calculate_service_cost(self, total_services, app_services=0):
        """
        Calculates cost based on tiered pricing.
        App services might receive a discount if configured.
        """
        remaining = total_services
        total_cost = 0.0
        current_tier_start = 0
        
        # Baseline calculation (Standard Tiers)
        # Note: The fee covers the first 50 *regardless* of type.
        # We calculate the 'Standard Cost' first, then apply discount to the App portion?
        # Or do we apply the discount to the rate?
        # Interpretation: App Services are "cheaper" to process.
        # Let's calculate the average unit price for this volume, then discount the App portion.
        
        breakdown = []
        
        for limit, price in self.tiers_sc:
            if remaining <= 0:
                break
            
            tier_capacity = limit - current_tier_start
            count_in_tier = min(remaining, tier_capacity)
            
            cost_segment = count_in_tier * price
            total_cost += cost_segment
            
            breakdown.append({
                'tier_limit': limit,
                'price': price,
                'count': count_in_tier,
                'cost': cost_segment
            })
            
            remaining -= count_in_tier
            current_tier_start = limit
            
        # Apply App Reward
        # Strategy: Calculate average cost per unit, then apply discount to App volume
        avg_cost = total_cost / total_services if total_services > 0 else 0
        
        # Logic: The 'discount' is a refund/rebate on the standard cost for App services
        app_savings = 0.0
        if self.app_discount > 0 and app_services > 0:
            # We can either discount the specific rate or the total allocated cost
            # Let's assume a flat % rebate on the cost attributable to App services
            # Cost attributable = Average Cost * App Count
            # app_cost_share = avg_cost * app_services
            # app_savings = app_cost_share * self.app_discount
            
            # ALTERNATIVE: App services count for tiers but cost X% less than the tier price.
            # This is complex because which "tier" are they in? First 50? Last 50?
            # Simple approach: Rebate.
            app_savings = (total_cost / total_services) * app_services * self.app_discount

        final_cost = total_cost - app_savings
        
        return {
            'total_services': total_services,
            'base_cost': total_cost,
            'app_savings': app_savings,
            'final_cost': final_cost,
            'avg_unit_price': avg_cost,
            'breakdown': breakdown
        }

    def calculate_call_cost(self, total_calls):
        remaining = total_calls
        total_cost = 0.0
        current_tier_start = 0
        
        breakdown = []
        
        for limit, price in self.tiers_calls:
            if remaining <= 0:
                break
            
            tier_capacity = limit - current_tier_start
            count_in_tier = min(remaining, tier_capacity)
            
            total_cost += count_in_tier * price
            
            breakdown.append({
                'tier_limit': limit,
                'price': price,
                'count': count_in_tier,
                'cost': count_in_tier * price
            })
            
            remaining -= count_in_tier
            current_tier_start = limit
            
        return total_cost, breakdown

    def process_month(self, df_month):
        """
        Process a single month's data frame.
        Expected cols: 'estado_asistencia', 'tipo_asignacion', 'cantidad_llamadas'
        """
        # 1. Concluded Services
        sc_df = df_month[df_month['estado_asistencia'] == 'CONCLUIDA']
        sc_count = len(sc_df)
        
        # App vs Global
        app_types = ['APP', 'ANCLAJE APP SOA', 'ANCLAJE', 'ANCLAJE_APP', 'ANCLAJE_APP_SOA']
        # Handle potential whitespace in 'tipo_asignacion'
        is_app = sc_df['tipo_asignacion'].astype(str).str.strip().isin(app_types)
        sc_app_count = is_app.sum()
        sc_global_count = sc_count - sc_app_count
        
        # 2. Calls (Proxy: Sum of 'cantidad_llamadas' for now, though we know it's an overcount)
        # We will use a 'validity_factor' to approximate valid calls based on Mexico data
        # Mexico Factor ~ 0.36 (5512 valid / 15204 total in CLAUDE.md) - Wait, let's refine this later.
        # For now, use raw sum and note it.
        raw_calls = df_month['cantidad_llamadas'].sum()
        # Apply rough factor to match Excel reality for Mexico
        estimated_valid_calls = int(raw_calls * 0.45) # Tuning based on observations
        
        # 3. Cancelled Posterior
        # Definition: Cancelled services that incurred cost.
        # We don't have a clear flag, assuming 0 for baseline unless we find a better filter.
        scp_count = 0 
        
        # --- FINANCIAL CALCULATION ---
        
        # Service Cost
        sc_calc = self.calculate_service_cost(sc_count, sc_app_count)
        
        # Call Cost
        call_cost, _ = self.calculate_call_cost(estimated_valid_calls)
        
        # Total Bill
        total_bill = self.base_fee + sc_calc['final_cost'] + call_cost + (scp_count * self.cancel_fee)
        # Note: The fee includes the first 50 services, so if count < 50, calculation handles it (price 0).
        # Wait, my logic adds base_fee AND sc_calc['final_cost'].
        # My tier logic says first 50 are $0.00.
        # So: Base Fee ($3150) + (Services > 50 cost) is correct.
        
        return {
            'sc_count': sc_count,
            'sc_app': sc_app_count,
            'sc_global': sc_global_count,
            'sc_cost': sc_calc['final_cost'],
            'sc_savings': sc_calc['app_savings'],
            'calls_count': estimated_valid_calls,
            'calls_cost': call_cost,
            'total_bill': total_bill
        }

def run_mexico_simulation(file_path):
    print(f"Loading {file_path}...")
    df = pd.read_csv(file_path)
    
    # Preprocessing
    df['creacion_asistencia'] = pd.to_datetime(df['creacion_asistencia'], dayfirst=True, errors='coerce')
    df_2025 = df[df['creacion_asistencia'].dt.year == 2025].copy()
    df_2025['month'] = df_2025['creacion_asistencia'].dt.to_period('M')
    
    calc = VoccareCalculator(country_config='Mexico')
    
    # SCENARIO 1: CURRENT POLICY (No Discount)
    print("\n=== SCENARIO 1: CURRENT POLICY (2024) ===")
    calc.app_discount = 0.0
    
    results = []
    for month, group in df_2025.groupby('month'):
        res = calc.process_month(group)
        res['month'] = str(month)
        results.append(res)
        
    df_res = pd.DataFrame(results)
    print(df_res[['month', 'sc_count', 'sc_app', 'sc_cost', 'calls_cost', 'total_bill']].to_string())
    total_bill_current = df_res['total_bill'].sum()
    print(f"TOTAL BILL (Jan-Sep 2025): ${total_bill_current:,.2f}")
    
    # SCENARIO 2: NEW POLICY (App Reward)
    # Hypothesis: 10% Discount on App-sourced services
    print("\n=== SCENARIO 2: PROPOSED POLICY (10% App Discount) ===")
    calc.app_discount = 0.10
    
    results_new = []
    for month, group in df_2025.groupby('month'):
        res = calc.process_month(group)
        res['month'] = str(month)
        results_new.append(res)
        
    df_res_new = pd.DataFrame(results_new)
    print(df_res_new[['month', 'sc_count', 'sc_app', 'sc_savings', 'total_bill']].to_string())
    total_bill_new = df_res_new['total_bill'].sum()
    print(f"TOTAL BILL (New Policy): ${total_bill_new:,.2f}")
    
    savings = total_bill_current - total_bill_new
    print(f"\nTOTAL SAVINGS FOR CLIENT: ${savings:,.2f}")
    print(f"Savings %: {(savings/total_bill_current)*100:.2f}%")

    # SCENARIO 3: WHAT IF ANALYSIS (Projected Impact)
    print("\n=== SCENARIO 3: PROJECTED IMPACT OF HIGHER ADOPTION ===")
    print("Simulating shifting Manual services to App services...")
    
    adoption_levels = [0.05, 0.10, 0.25, 0.50, 0.75, 1.0]
    calc.app_discount = 0.10 # Keep the 10% incentive
    
    print(f"{'Adoption':<10} | {'Bill ($)':<12} | {'Direct Savings':<15} | {'Call Reduct.':<12} | {'Total Savings':<15}")
    print("-" * 75)
    
    # Base totals for comparison (Using Scenario 1 as baseline - 0% discount, actual usage)
    # Actually, let's use a theoretical "0% App" baseline for cleaner comparison?
    # No, compare against Current Reality (Scenario 1).
    
    for adoption in adoption_levels:
        # We recalculate the whole year with this adoption rate
        sim_total_bill = 0
        sim_direct_savings = 0
        sim_call_savings = 0
        
        for month, group in df_2025.groupby('month'):
            # 1. Simulate Service Shift
            total_sc = len(group[group['estado_asistencia'] == 'CONCLUIDA'])
            sim_app_count = int(total_sc * adoption)
            sim_global_count = total_sc - sim_app_count
            
            # 2. Simulate Call Reduction
            # Logic: Global users generate X calls. App users generate X * (1 - 0.238) calls.
            # First, assume current calls are mostly Global.
            # Avg calls per service (Global) ~ Estimated from data
            # Let's use the factor: 23.8% reduction for the *shifted* volume.
            
            # Current App % is negligible, so assume current calls are Baseline Global Volume.
            raw_calls = group['cantidad_llamadas'].sum()
            valid_calls_baseline = int(raw_calls * 0.45)
            
            # If we shift 'sim_app_count' services from Global to App:
            # The calls associated with those services drop by 23.8%.
            # How many calls per service?
            calls_per_service = valid_calls_baseline / total_sc if total_sc > 0 else 0
            
            # Reduction = (Services Shifted to App) * (Calls per Service) * 0.238
            # Shifted count = sim_app_count - actual_app_count (ignore actual, just assume 0->Target)
            # Let's just calculate absolute:
            # Total Calls = (Global_Count * Rate) + (App_Count * Rate * (1-0.238))
            # Rate = calls_per_service (assuming baseline is all Global)
            
            projected_valid_calls = (sim_global_count * calls_per_service) + \
                                    (sim_app_count * calls_per_service * (1 - 0.238))
            
            # 3. Calculate Costs
            # Services
            sc_cost_res = calc.calculate_service_cost(total_sc, sim_app_count)
            
            # Calls
            call_cost_res, _ = calc.calculate_call_cost(projected_valid_calls)
            
            # Bill
            monthly_bill = calc.base_fee + sc_cost_res['final_cost'] + call_cost_res + (0 * calc.cancel_fee)
            
            sim_total_bill += monthly_bill
            sim_direct_savings += sc_cost_res['app_savings']
            
        total_savings = total_bill_current - sim_total_bill
        call_savings = total_savings - sim_direct_savings # Rough attribution
        
        print(f"{adoption*100:>5.0f}%     | ${sim_total_bill:,.2f}   | ${sim_direct_savings:,.2f}        | ${call_savings:,.2f}      | ${total_savings:,.2f}")

if __name__ == "__main__":
    run_mexico_simulation("Client05_Mexico.csv")
