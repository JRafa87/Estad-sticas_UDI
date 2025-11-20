import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import binom
import io

# Configuración de la página
st.set_page_config(page_title="Análisis de Datos", layout="wide", page_icon="📊")

# --- ESTILOS CSS MEJORADOS ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    /* Ajuste para las métricas: Menos padding para evitar que se corten los números */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 10px; /* Reducido de 15px a 10px */
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1 { color: #2c3e50; }
    h2, h3, h4 { color: #34495e; }
    
    /* Botón de descarga estilizado */
    div.stDownloadButton > button:first-child {
        background-color: #27ae60;
        color: white;
        width: 100%;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stDownloadButton > button:first-child:hover {
        background-color: #219150;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1055/1055644.png", width=90)
st.sidebar.title("Configuración")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo Excel (.xlsx)", type="xlsx")

# --- TÍTULO PRINCIPAL ---
st.title("📊 Análisis Interactivo: Redes Sociales y Productividad")

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("✅ Datos cargados")
        
        # Vista de datos persistente
        with st.expander("🔍 Ver Tabla de Datos (Click para desplegar)", expanded=True):
            st.dataframe(df.head(), use_container_width=True)
            st.caption(f"Total: **{df.shape[0]} filas** | **{df.shape[1]} columnas**")
        
        st.divider()

        # --- PESTAÑAS ---
        tab_desc, tab_prob = st.tabs(["📈 Análisis Descriptivo", "🎲 Probabilidades"])

        # ==========================================
        # PESTAÑA 1: DESCRIPTIVA
        # ==========================================
        with tab_desc:
            col_var, _ = st.columns([1, 2])
            with col_var:
                selected_variable = st.selectbox("Variable a analizar:", df.columns)
            
            export_df = None
            export_filename = "resultados.csv"

            # --- CASO NUMÉRICO ---
            if df[selected_variable].dtype in ['float64', 'int64']:
                # Cálculos
                mean_val = df[selected_variable].mean()
                median_val = df[selected_variable].median()
                mode_val = df[selected_variable].mode()[0]
                std_val = df[selected_variable].std()
                min_val = df[selected_variable].min()
                max_val = df[selected_variable].max()
                q1 = df[selected_variable].quantile(0.25)
                q3 = df[selected_variable].quantile(0.75)
                iqr = q3 - q1

                # Preparar Exportación
                export_df = pd.DataFrame({
                    "Estadístico": ["Media", "Mediana", "Moda", "Desviación Std", "Mínimo", "Q1 (25%)", "Q3 (75%)", "Máximo", "IQR"],
                    "Valor": [mean_val, median_val, mode_val, std_val, min_val, q1, q3, max_val, iqr]
                })
                export_filename = f"estadisticas_{selected_variable}.csv"

                st.subheader("1. Resumen Estadístico")
                
                # DISTRIBUCIÓN EN FILAS DE 3 (Para evitar que se corten los números)
                st.markdown("**Tendencia Central**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Media", f"{mean_val:.2f}")
                c2.metric("Mediana", f"{median_val:.2f}")
                c3.metric("Moda", f"{mode_val}")
                
                st.markdown("**Dispersión y Rango**")
                c4, c5, c6 = st.columns(3)
                c4.metric("Desv. Estándar", f"{std_val:.2f}")
                c5.metric("Mínimo", f"{min_val:.2f}")
                c6.metric("Máximo", f"{max_val:.2f}")

                st.markdown("**Posición (Cuartiles)**")
                c7, c8, c9 = st.columns(3)
                c7.metric("Q1 (25%)", f"{q1:.2f}")
                c8.metric("Q3 (75%)", f"{q3:.2f}")
                c9.metric("IQR (Rango Interc.)", f"{iqr:.2f}")

                st.divider()

                # GRÁFICOS E INTERPRETACIÓN
                st.subheader("2. Visualización")
                col_viz, col_text = st.columns([2, 1])

                with col_viz:
                    # Pestañas internas solo para cambiar tipo de vista gráfica
                    g1, g2 = st.tabs(["Histograma", "Boxplot"])
                    with g1:
                        fig_h, ax_h = plt.subplots(figsize=(8, 4))
                        sns.histplot(df[selected_variable], kde=True, color='#3498db', ax=ax_h)
                        st.pyplot(fig_h)
                    with g2:
                        fig_b, ax_b = plt.subplots(figsize=(8, 4))
                        sns.boxplot(x=df[selected_variable], color='#2ecc71', ax=ax_b)
                        st.pyplot(fig_b)

                with col_text:
                    st.markdown("### 📝 Interpretación")
                    st.info(f"""
                    **Sobre el Centro:**
                    El valor promedio es **{mean_val:.2f}**, mientras que el valor central (mediana) es **{median_val:.2f}**.
                    
                    **Sobre la Dispersión:**
                    Los datos varían típicamente en **±{std_val:.2f}** unidades respecto a la media.
                    
                    **Sobre la Posición (Resultados de arriba):**
                    * El 25% inferior de los datos llega hasta **{q1:.2f}** (Q1).
                    * El 75% de los datos está por debajo de **{q3:.2f}** (Q3).
                    * El 50% central de la población se ubica entre estos dos valores (Rango Intercuartílico de **{iqr:.2f}**).
                    """)

            # --- CASO CATEGÓRICO ---
            else:
                freq = df[selected_variable].value_counts()
                freq_table = pd.DataFrame({
                    'Frec. Absoluta': freq,
                    'Frec. Relativa (%)': (freq / len(df)) * 100,
                    'Acumulada Abs.': freq.cumsum(),
                    'Acumulada Rel. (%)': ((freq / len(df)) * 100).cumsum()
                })
                
                export_df = freq_table.reset_index().rename(columns={'index': selected_variable})
                export_filename = f"frecuencias_{selected_variable}.csv"

                st.subheader("Resumen de Frecuencias")
                
                c_kpi1, c_kpi2 = st.columns(2)
                c_kpi1.metric("Categoría más común (Moda)", freq.idxmax())
                c_kpi2.metric("Total de Registros", len(df))

                c_graf, c_tbl = st.columns([1, 1])
                with c_graf:
                    fig, ax = plt.subplots(figsize=(6, 5))
                    sns.countplot(y=selected_variable, data=df, order=freq.index, palette='viridis', ax=ax)
                    st.pyplot(fig)
                
                with c_tbl:
                    st.dataframe(
                        freq_table.style.format("{:.2f}", subset=['Frec. Relativa (%)', 'Acumulada Rel. (%)'])
                        .background_gradient(cmap="Blues", subset=['Frec. Absoluta']),
                        use_container_width=True, height=400
                    )

            # BOTÓN DESCARGA
            if export_df is not None:
                st.divider()
                c_dl1, c_dl2, c_dl3 = st.columns([1, 2, 1])
                with c_dl2:
                    st.download_button(
                        label="📥 Descargar Resultados Completos (CSV)",
                        data=export_df.to_csv(index=False).encode('utf-8'),
                        file_name=export_filename,
                        mime='text/csv'
                    )

        # ==========================================
        # PESTAÑA 2: PROBABILIDADES
        # ==========================================
        with tab_prob:
            st.header("Laboratorio de Probabilidades")
            
            # 1. Simple
            with st.container():
                st.markdown("### 🎲 1. Probabilidad Simple")
                c1, c2 = st.columns([1, 3])
                red_simple = c1.selectbox("Evento (Red Social):", df['Red_social_mas_utilizada'].unique())
                
                p_simple = len(df[df['Red_social_mas_utilizada'] == red_simple]) / len(df)
                c2.info(f"Probabilidad de seleccionar un usuario de **{red_simple}** al azar:")
                c2.metric("Resultado", f"{p_simple:.4f}", f"{p_simple*100:.2f}%")
            
            st.divider()

            # 2. Condicional
            with st.container():
                st.markdown("### 🔗 2. Probabilidad Condicional")
                c_cond1, c_cond2 = st.columns([1, 3])
                
                with c_cond1:
                    lugar_cond = st.selectbox("Dado que está en:", df['Lugar_habitual_conexion'].unique())
                    trabajo_cond = st.selectbox("Calcular prob. de uso en trabajo:", df['Uso_redes_durante_trabajo'].unique())
                
                with c_cond2:
                    subset = df[df['Lugar_habitual_conexion'] == lugar_cond]
                    if not subset.empty:
                        p_cond = len(subset[subset['Uso_redes_durante_trabajo'] == trabajo_cond]) / len(subset)
                        st.info(f"Si sabemos que el usuario está en **{lugar_cond}**, la probabilidad de que **{trabajo_cond}** use redes es:")
                        st.metric("Resultado Condicional", f"{p_cond:.4f}", f"{p_cond*100:.2f}%")
                    else:
                        st.warning("No hay datos para esta condición.")

            st.divider()

            # 3. Binomial
            with st.container():
                st.markdown("### 📊 3. Distribución Binomial")
                c_bin1, c_bin2, c_bin3 = st.columns([1, 1, 2])
                
                with c_bin1:
                    lugar_bin = st.selectbox("Filtro (Población):", df['Lugar_habitual_conexion'].unique(), key="bin_l")
                    red_bin = st.selectbox("Éxito (Red):", df['Red_social_mas_utilizada'].unique(), key="bin_r")
                
                with c_bin2:
                    n = st.number_input("Muestra (n)", 1, 100, 10)
                    k = st.number_input("Éxitos (k)", 0, n, 5)
                
                with c_bin3:
                    sub_bin = df[df['Lugar_habitual_conexion'] == lugar_bin]
                    if not sub_bin.empty:
                        p = sub_bin['Red_social_mas_utilizada'].value_counts(normalize=True).get(red_bin, 0)
                        prob_k = binom.pmf(k, n, p)
                        st.success(f"Probabilidad de encontrar exactamente **{k}** usuarios de **{red_bin}** en **{n}** intentos (p_base={p:.2f}):")
                        st.metric("Resultado Binomial", f"{prob_k:.4f}")
                    else:
                        st.error("Sin datos suficientes.")

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
else:
    st.info("👈 Sube un archivo Excel para comenzar.")




