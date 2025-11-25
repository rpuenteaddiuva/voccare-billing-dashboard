import json

def calculate_factors():
    # CSV Data (Annualized or Jan) from JSON
    with open('reports/monthly_audit_results.json', 'r') as f:
        data = json.load(f)
    
    # Excel Targets (Approximate Monthly Average from Report Inspection)
    # Based on 'Promedio' column or specific months seen in 'inspect_excel'
    targets = {
        'Dominicana': 11000,     # Sheet DO, Avg Valid Calls
        'Puerto Rico': 38000,    # Sheet MCS + PR
        'Guatemala': 4800,       # Sheet GU
        'Costa Rica': 4500,      # Sheet CR
        'Mexico': 600,           # Sheet MX
        'Argentina': 5000,       # Sheet AR
        'Chile': 4000,           # Sheet CL (Est)
        'Ecuador': 1500,         # Sheet EC (Est)
        'Peru': 1200,            # Sheet PE (Est)
        'Uruguay': 2500,         # Sheet UY (Est)
        'Bolivia': 3000,         # Sheet BO (Est)
        'Salvador': 100,         # Low vol
    }
    
    print(f"{ 'Country':<15} | {'CSV Raw (Jan)':<15} | {'Excel Target':<15} | {'Ideal Factor':<10}")
    print("-----------------------------------------------------------------")
    
    new_config = {}
    
    for country, months in data.items():
        if '2025-01' in months:
            # Get raw calls from the 90% estimate reverse engineered
            # lv_total in JSON is (raw * 0.90). So raw = lv_total / 0.90
            lv_est = months['2025-01']['lv_total']
            raw_calls = lv_est / 0.90
            
            target = targets.get(country, 0)
            
            if raw_calls > 0 and target > 0:
                factor = target / raw_calls
                print(f"{country:<15} | {raw_calls:<15.0f} | {target:<15} | {factor:<10.2f}")
                new_config[country] = round(factor, 2)
            else:
                print(f"{country:<15} | {raw_calls:<15.0f} | {target:<15} | {'N/A':<10}")
                new_config[country] = 0.40 # Default conservative
        else:
             new_config[country] = 0.40

    print("\nGenerated Config Dictionary:")
    print(json.dumps(new_config, indent=4))

if __name__ == "__main__":
    calculate_factors()
