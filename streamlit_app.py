import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import os
import sys

# Adjust path to import from the 'scripts' directory
# Since we are now in the root, 'scripts' is a direct subdirectory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

from compare_policies import GlobalPolicyReport

# Configuración de la página
st.set_page_config(page_title="Dashboard Financiero Voccare", layout="wide")

# Título y Descripción
st.title("📊 Simulador de Política de Facturación Voccare 2025")
st.markdown("""
Este tablero permite analizar el impacto financiero de la migración a la nueva política v2.1.
Ajuste los parámetros en la barra lateral para simular escenarios de descuento.
""")

# --- SIDEBAR: CONTROLES ---
st.sidebar.header("⚙️ Configuración de Simulación")

if st.sidebar.button("🔄 Recalcular (Limpiar Caché)"):
    st.cache_data.clear()
    st.rerun()

# Parámetro de Descuento App (Interactivo)
app_discount_pct = st.sidebar.slider(
    "Descuento por Uso de App (%)",
    min_value=0,
    max_value=50,
    value=10,
    step=1,
    help="Porcentaje de descuento aplicado al costo de los Servicios Concluidos originados por App."
)

app_fee = st.sidebar.number_input(
    "Fee Transaccional App ($)",
    min_value=0.0,
    value=0.45,
    step=0.05
)

# Filtro de País y Año
# Use absolute path relative to the script location (now root)
base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, "Paises")

files = glob.glob(os.path.join(input_dir, "*.zip"))

# DEBUG: Show path info in sidebar if no files found
if not files:
    st.sidebar.error(f"No ZIP files found in: {input_dir}")
    st.sidebar.info(f"CWD: {os.getcwd()}")

country_map = {}
for f in files:
    # Robust name extraction
    filename = os.path.basename(f)
    name_no_ext = os.path.splitext(filename)[0] # Remove .zip
    parts = name_no_ext.split('_')
    
    # Filter: Skip 'ClientXX' (index 0 usually) and Date-like parts (8 digits)
    clean_parts = []
    for p in parts[1:]: # Skip first part (ClientXX)
        if p.isdigit() and len(p) == 8:
            continue # Skip date
        clean_parts.append(p)
        
    c_name = " ".join(clean_parts)
    country_map[c_name] = f

selected_country = st.sidebar.selectbox(
    "Seleccionar País",
    options=["Todos (Global)"] + sorted(list(country_map.keys()))
)

# Filtro de Cuenta (Dinámico)
account_filter = "Todas"
if selected_country != "Todos (Global)":
    f_path = country_map[selected_country]
    try:
        # Read header to check for 'cuenta'
        header = pd.read_csv(f_path, sep=';', nrows=0, compression='zip')
        col_name = None
        for c in header.columns:
            if c.lower().strip() == 'cuenta':
                col_name = c
                break
        
        if col_name:
            # Read unique accounts efficiently
            acc_df = pd.read_csv(f_path, sep=';', usecols=[col_name], on_bad_lines='skip', compression='zip')
            unique_accs = sorted(acc_df[col_name].dropna().astype(str).unique().tolist())
            account_filter = st.sidebar.selectbox("Filtrar por Cuenta", ["Todas"] + unique_accs)
        else:
            st.sidebar.info("No se detectó columna 'cuenta' para desglose.")
            
    except Exception as e:
        pass # Silent fail on account read

selected_year = st.sidebar.selectbox(
    "Seleccionar Año",
    options=[2025, 2024, 2023],
    index=0
)

# --- LÓGICA DE CÁLCULO ---
@st.cache_data
def run_simulation(discount_val, fee_val, year_filter, acc_filter):
    report = GlobalPolicyReport(app_discount_pct=discount_val, app_fee=fee_val)
    
    all_results = []
    
    for c_name, f_path in country_map.items():
        try:
            # Optimization: Skip reading other countries if a specific one is selected
            # This speeds up the specific drill-down significantly
            if selected_country != "Todos (Global)" and c_name != selected_country:
                continue

            lv_ratio = report.get_ratio(c_name)
            price_adj = report.get_price_adjust(c_name)
            
            df = pd.read_csv(f_path, sep=';', on_bad_lines='skip', compression='zip')
            # CRITICAL FIX: Clean column names to find 'cantidad_llamadas'
            df.columns = df.columns.str.strip()
            
            # Filter by Account if applicable
            if acc_filter != "Todas":
                # Normalize column name check
                acc_col = None
                for c in df.columns:
                    if c.lower().strip() == 'cuenta':
                        acc_col = c
                        break
                if acc_col:
                    df = df[df[acc_col].astype(str) == acc_filter]
            
            df['date_obj'] = pd.to_datetime(df['creacion_asistencia'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            
            # Dynamic Year Filter
            df = df[df['date_obj'].dt.year == year_filter].copy()
            
            if df.empty: continue

            df['month'] = df['date_obj'].dt.to_period('M')
            
            app_types = ['APP', 'ANCLAJE APP SOA', 'ANCLAJE', 'ANCLAJE_APP', 'ANCLAJE_APP_SOA']
            
            for month, group in df.groupby('month'):
                sc_df = group[group['estado_asistencia'] == 'CONCLUIDA']
                total_sc = len(sc_df)
                app_sc = sc_df[sc_df['tipo_asignacion'].astype(str).str.strip().isin(app_types)].shape[0]
                voice_sc = total_sc - app_sc
                
                # NEW LOGIC: Valid Calls from CSV + Efficiency Factor
                if 'cantidad_llamadas' in group.columns:
                    raw_calls = pd.to_numeric(group['cantidad_llamadas'], errors='coerce').fillna(0).sum()
                    eff_factor = report.get_efficiency_factor(c_name) # Use calibrated factor
                    valid_calls = int(raw_calls * eff_factor)
                else:
                    valid_calls = int(total_sc * lv_ratio) # Fallback

                # Calculate Cancelled
                cancelled_df = group[group['estado_asistencia'].astype(str).str.upper().str.contains('CANCEL')]
                cp = 0
                cm = 0
                if not cancelled_df.empty:
                    if 'usuario_que_asigna' in cancelled_df.columns:
                         vals = cancelled_df['usuario_que_asigna'].astype(str).str.strip()
                         is_assigned = ~vals.isin(['', 'nan', 'None']) & cancelled_df['usuario_que_asigna'].notna()
                         cp = is_assigned.sum()
                         cm = len(cancelled_df) - cp
                    else:
                         cm = len(cancelled_df)
                
                # 2024 Calculation
                cost_sc_24 = report.calculate_tier_cost(total_sc, report.tiers_sc, price_adj)
                cost_lv_24 = report.calculate_tier_cost(valid_calls, report.tiers_lv, price_adj)
                bill_2024 = (report.base_fee * price_adj) + cost_sc_24 + cost_lv_24
                
                # 2025 Calculation (Dynamic)
                base_sc_cost = report.calculate_tier_cost(total_sc, report.tiers_sc, price_adj)
                discount_amount = 0
                if total_sc > 0:
                    app_share = (base_sc_cost * (app_sc / total_sc))
                    discount_amount = app_share * (discount_val / 100.0)
                
                cost_sc_25 = base_sc_cost - discount_amount
                cost_lv_25 = report.calculate_tier_cost(valid_calls, report.tiers_lv, price_adj)
                
                # Dynamic App Fee
                ratio_fee = fee_val / 0.45
                scaled_app_tiers = [(l, p * ratio_fee) for l, p in report.tiers_app]
                cost_app_25 = report.calculate_tier_cost(app_sc, scaled_app_tiers, 1.0) 

                bill_2025 = (report.base_fee * price_adj) + cost_sc_25 + cost_lv_25 + cost_app_25
                
                all_results.append({
                    'Pais': c_name,
                    'Mes': str(month),
                    'SC Total': int(total_sc),
                    'SC App': int(app_sc),
                    'SC Voz': int(voice_sc),
                    'Adopcion (%)': round((app_sc/total_sc*100), 1) if total_sc else 0,
                    'Llamadas Validas': int(valid_calls),
                    'Cancelado Posterior': int(cp),
                    'Cancelado Momento': int(cm),
                    
                    # Detalles 2024
                    '2024 SC': round(cost_sc_24, 2),
                    '2024 LV': round(cost_lv_24, 2),
                    'Factura 2024': round(bill_2024, 2),
                    
                    # Detalles 2026 (Simulación Política Nueva con Datos 2025)
                    '2026 SC Base': round(base_sc_cost, 2),
                    '2026 Desc.': round(discount_amount, 2),
                    '2026 App Fee': round(cost_app_25, 2),
                    '2026 LV': round(cost_lv_25, 2),
                    'Factura 2026': round(bill_2025, 2),
                    
                    'Ahorro': round(bill_2024 - bill_2025, 2)
                })
                
        except Exception as e:
            print(f"Error processing {c_name}: {e}")
            pass

    if not all_results:
        cols = ['Pais', 'Mes', 'SC Total', 'SC App', 'SC Voz', 'Adopcion (%)', 'Llamadas Validas', 
                'Cancelado Posterior', 'Cancelado Momento', 
                '2024 SC', '2024 LV', 'Factura 2024',
                '2026 SC Base', '2026 Desc.', '2026 App Fee', '2026 LV', 'Factura 2026', 'Ahorro']
        return pd.DataFrame(columns=cols)
            
    return pd.DataFrame(all_results)

# Ejecutar simulación
df = run_simulation(app_discount_pct, app_fee, selected_year, account_filter)

# --- FILTRO DE MESES (Sidebar) ---
# Ahora que df existe, podemos obtener los meses
all_months = sorted(df['Mes'].unique().tolist()) if not df.empty else []

with st.sidebar.expander("📅 Filtrar Meses", expanded=False):
    selected_months = st.multiselect(
        "Selecciona los meses:",
        options=all_months,
        default=all_months
    )

# --- FILTRADO ---
if selected_country != "Todos (Global)":
    df_view = df[df['Pais'] == selected_country].copy()
else:
    df_view = df.copy()

# --- FILTRADO POR MES(ES) ---
if selected_months:
    df_view = df_view[df_view['Mes'].isin(selected_months)].copy()

# --- INTEGRACIÓN FACTURACIÓN REAL (SOLO PR POR AHORA) ---
if selected_country == "Puerto Rico":
    try:
        real_bill_path = os.path.join(base_dir, "Facturacion", "facturacion_real_pr.csv")
        if os.path.exists(real_bill_path):
            df_real = pd.read_csv(real_bill_path)
            df_real['Mes'] = df_real['Mes'].astype(str)
            
            # Merge
            df_view['Mes'] = df_view['Mes'].astype(str)
            df_view = pd.merge(df_view, df_real, on='Mes', how='left')
            df_view['Facturacion Real'] = df_view['Facturacion Real'].fillna(0)
    except Exception as e:
        st.error(f"Error cargando facturación real: {e}")
elif selected_country == "Argentina":
    try:
        real_bill_path = os.path.join(base_dir, "Facturacion", "facturacion_real_ar.csv")
        if os.path.exists(real_bill_path):
            df_real = pd.read_csv(real_bill_path)
            df_real['Mes'] = df_real['Mes'].astype(str)
            
            df_view['Mes'] = df_view['Mes'].astype(str)
            df_view = pd.merge(df_view, df_real, on='Mes', how='left')
            df_view['Facturacion Real'] = df_view['Facturacion Real'].fillna(0)
    except Exception as e:
        st.error(f"Error cargando facturación real: {e}")
elif selected_country == "Dominicana":
    try:
        real_bill_path = os.path.join(base_dir, "Facturacion", "facturacion_real_do.csv")
        if os.path.exists(real_bill_path):
            df_real = pd.read_csv(real_bill_path)
            df_real['Mes'] = df_real['Mes'].astype(str)
            
            df_view['Mes'] = df_view['Mes'].astype(str)
            df_view = pd.merge(df_view, df_real, on='Mes', how='left')
            df_view['Facturacion Real'] = df_view['Facturacion Real'].fillna(0)
    except Exception as e:
        st.error(f"Error cargando facturación real: {e}")

# --- TABS PRINCIPALES ---
tab_fin, tab_ops, tab_data = st.tabs(["💰 Financiero", "📈 Operativo", "📋 Datos Detallados"])

with tab_fin:
    # --- KPIs GLOBALES ---
    col1, col2, col3, col4 = st.columns(4)

    total_2024 = df_view['Factura 2024'].sum()
    total_2025 = df_view['Factura 2026'].sum()
    
    # KPI Real (solo si existe columna)
    if 'Facturacion Real' in df_view.columns:
        total_real = df_view[df_view['Facturacion Real'] > 0]['Facturacion Real'].sum()
        st.metric("Facturación Real (Feb-Ago)", f"${total_real:,.0f}")
    
    total_savings = df_view['Ahorro'].sum()
    avg_adoption = df_view['Adopcion (%)'].mean() if not df_view.empty else 0

    col1.metric("Facturación Est. 2024", f"${total_2024:,.0f}")
    col2.metric("Facturación Est. 2026", f"${total_2025:,.0f}", delta=f"${total_savings:,.0f} Ahorro")
    col3.metric("Adopción Promedio App", f"{avg_adoption:.1f}%")
    col4.metric("Descuento Aplicado", f"{app_discount_pct}%")

    st.subheader("📉 Comparativa de Costos (2024 vs 2025 vs Real)")
    if not df_view.empty:
        df_monthly = df_view.groupby('Mes')[['Factura 2024', 'Factura 2026']].sum().reset_index()
        
        # Add Real to melt if exists
        value_vars = ['Factura 2024', 'Factura 2026']
        if 'Facturacion Real' in df_view.columns:
            # Aggregate real billing too
            df_real_sum = df_view.groupby('Mes')['Facturacion Real'].sum().reset_index()
            df_monthly = pd.merge(df_monthly, df_real_sum, on='Mes')
            value_vars.append('Facturacion Real')

        df_monthly['Mes'] = df_monthly['Mes'].astype(str) # Fix for plotting period
        df_melt = df_monthly.melt(id_vars='Mes', value_vars=value_vars, var_name='Política', value_name='Costo USD')

        fig_bar = px.bar(
            df_melt, x='Mes', y='Costo USD', color='Política', barmode='group',
            color_discrete_map={'Factura 2024': '#EF553B', 'Factura 2026': '#636EFA', 'Facturacion Real': '#00CC96'},
            title="Evolución Mensual de Facturación",
            text_auto='.2s'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # --- MENSAJE DE CIERRE ---
    if total_savings > 0:
        st.success(f"✅ Con un descuento del {app_discount_pct}%, la nueva política genera un ahorro neto de ${total_savings:,.2f} USD para el cliente.")
    else:
        st.error(f"⚠️ Con estos parámetros, la nueva política es ${abs(total_savings):,.2f} USD más cara para el cliente.")

with tab_ops:
    st.header("Análisis Operativo")
    
    if not df_view.empty:
        # Prepare data for plotting (convert Period to String) - MOVED UP
        df_plot = df_view.copy()
        df_plot['Mes'] = df_plot['Mes'].astype(str)

        # --- MÉTRICAS ANUALES (RESUMEN) ---
        total_sc_ops = df_view['SC Total'].sum()
        total_calls_ops = df_view['Llamadas Validas'].sum()
        total_cx_ops = df_view['Cancelado Posterior'].sum() + df_view['Cancelado Momento'].sum()
        
        # Adopción Global Ponderada (suma app / suma total)
        total_app_ops = df_view['SC App'].sum()
        global_adoption_ops = (total_app_ops / total_sc_ops * 100) if total_sc_ops > 0 else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Servicios (Año)", f"{total_sc_ops:,.0f}")
        m2.metric("Adopción Global App", f"{global_adoption_ops:.1f}%")
        m3.metric("Total Cancelaciones", f"{total_cx_ops:,.0f}")
        m4.metric("Total Llamadas Válidas", f"{total_calls_ops:,.0f}")
        
        st.markdown("---")
        
        # Gráfica de Volumen Total
        st.subheader("Volumen Total de Servicios Concluidos")
        df_total_sc = df_plot.groupby('Mes')['SC Total'].sum().reset_index()
        fig_total = px.line(df_total_sc, x='Mes', y='SC Total', markers=True,
                            title="Tendencia Mensual de Servicios Totales",
                            text='SC Total')
        fig_total.update_traces(textposition="top center")
        st.plotly_chart(fig_total, use_container_width=True)

        col_o1, col_o2 = st.columns(2)
        
        with col_o1:
            st.subheader("Servicios Concluidos (App vs Voz)")
            df_sc = df_plot.groupby('Mes')[['SC App', 'SC Voz']].sum().reset_index()
            fig_sc = px.bar(df_sc, x='Mes', y=['SC App', 'SC Voz'], title="Mix de Canales",
                            color_discrete_map={'SC App': '#00CC96', 'SC Voz': '#636EFA'},
                            text_auto=True)
            st.plotly_chart(fig_sc, use_container_width=True)
            
        with col_o2:
            st.subheader("Tipos de Cancelación")
            df_cx = df_plot.groupby('Mes')[['Cancelado Posterior', 'Cancelado Momento']].sum().reset_index()
            fig_cx = px.bar(df_cx, x='Mes', y=['Cancelado Posterior', 'Cancelado Momento'], 
                            title="Eficiencia de Cancelaciones",
                            color_discrete_map={'Cancelado Posterior': '#EF553B', 'Cancelado Momento': '#FFA15A'},
                            text_auto=True)
            st.plotly_chart(fig_cx, use_container_width=True)
            
        st.subheader("Volumen de Llamadas Válidas (Estimado)")
        df_calls = df_plot.groupby('Mes')['Llamadas Validas'].sum().reset_index()
        fig_calls = px.line(
            df_calls, x='Mes', y='Llamadas Validas', markers=True,
            title="Tendencia Mensual de Llamadas Válidas",
            line_shape='spline'
            # trendline removed to avoid dependency issues
        )
        fig_calls.update_traces(line_color='#636EFA') # Mantener un color consistente si se desea
        st.plotly_chart(fig_calls, use_container_width=True)
    else:
        st.info("No hay datos operativos para mostrar con los filtros seleccionados.")

with tab_data:
    # --- DATOS DETALLADOS ---
    st.subheader("📋 Tabla de Datos")
    
    if not df_view.empty:
        # Calcular Totales Anuales por País
                df_view['Total Anual 2024'] = df_view.groupby('Pais')['Factura 2024'].transform('sum')
                df_view['Total Anual 2026'] = df_view.groupby('Pais')['Factura 2026'].transform('sum')                
                with st.expander("Ver Datos Detallados"):
                    st.dataframe(df_view)