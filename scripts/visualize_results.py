import json
import matplotlib.pyplot as plt
import pandas as pd
import os

def generate_plots():
    with open('reports/audit_results.json', 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index.name = 'Country'
    df.reset_index(inplace=True)
    
    # Sort by SC Volume for consistency in some charts, or Adoption in others
    
    # 1. App Adoption %
    df_adopt = df.sort_values('adoption_pct', ascending=True)
    plt.figure(figsize=(10, 8))
    bars = plt.barh(df_adopt['Country'], df_adopt['adoption_pct'], color='teal')
    plt.xlabel('Adopción App (%)')
    plt.title('Tasa de Adopción Digital por País (2025)')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add labels
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', ha='left', va='center')
        
    plt.tight_layout()
    plt.savefig('reports/img/adopcion_app.png')
    plt.close()

    # 2. Valid Calls vs SC
    # Show comparison of Volume vs Calls
    df_vol = df.sort_values('sc_total', ascending=False).head(10) # Top 10 by volume
    
    x = range(len(df_vol))
    width = 0.35
    
    plt.figure(figsize=(12, 6))
    plt.bar([i - width/2 for i in x], df_vol['sc_total'], width, label='Servicios Concluidos', color='#2c3e50')
    plt.bar([i + width/2 for i in x], df_vol['lv_total'], width, label='Llamadas Válidas (Est. 90%)', color='#e74c3c')
    
    plt.xlabel('País')
    plt.ylabel('Volumen')
    plt.title('Volumen Operativo: Servicios vs Llamadas (Top 10)')
    plt.xticks(x, df_vol['Country'], rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig('reports/img/volumen_operativo.png')
    plt.close()

    # 3. Cancellations Breakdown (Stacked)
    df_canc = df[['Country', 'cp', 'cm']].copy()
    df_canc['total'] = df_canc['cp'] + df_canc['cm']
    df_canc = df_canc.sort_values('total', ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    plt.bar(df_canc['Country'], df_canc['cm'], label='Cancelada al Momento', color='#f1c40f')
    plt.bar(df_canc['Country'], df_canc['cp'], bottom=df_canc['cm'], label='Cancelada Posterior', color='#c0392b')
    
    plt.xlabel('País')
    plt.ylabel('Cantidad de Cancelaciones')
    plt.title('Tipología de Cancelaciones (Top 10)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig('reports/img/cancelaciones.png')
    plt.close()

    print("Graphs generated in reports/img/")

if __name__ == "__main__":
    if not os.path.exists('reports/img'):
        os.makedirs('reports/img')
    generate_plots()
