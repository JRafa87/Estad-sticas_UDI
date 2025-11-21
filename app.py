import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import binom
import io

# Configuración de la página
st.set_page_config(page_title="Análisis de Datos", layout="wide", page_icon="📊")

# --- ESTILOS CSS MEJORADOS Y PERSONALIZACIÓN DE COLORES DE MÉTRICAS ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    /* Estilo base para todas las métricas */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: 0.3s;
    }
    div[data-testid="stMetric"]:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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

    /* CLASES PARA COLORES DE FONDO EN MÉTRICAS NUMÉRICAS */
    /* Tendencia Central: Azul */
    .metric-central > div[data-testid="stMetric"] {
        background-color: #e6f7ff; 
        border-left: 5px solid #3498db;
    }
    /* Dispersión y Rango: Verde */
    .metric-dispersion > div[data-testid="stMetric"] {
        background-color: #eafaea; 
        border-left: 5px solid #2ecc71;
    }
    /* Posición (Cuartiles): Púrpura */
    .metric-position > div[data-testid="stMetric"] {
        background-color: #f7e6ff; 
        border-left: 5px solid #9b59b6;
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
        # PESTAÑA 1: DESCRIPTIVA (MODIFICADA)
        # ==========================================
        with tab_desc:
            col_var, _ = st.columns([1, 2])
            with col_var:
                selected_variable = st.selectbox("Variable a analizar:", df.columns)
            
            export_df = None
            export_filename = "resultados.csv"

            # --- 1. ANÁLISIS UNIVARIADO (MÉTRICAS Y GRÁFICOS DE UNA VARIABLE) ---
            
            # --- CASO NUMÉRICO ---
            if df[selected_variable].dtype in ['float64', 'int64']:
                # Cálculos
                mean_val = df[selected_variable].mean()
                median_val = df[selected_variable].median() # Q2
                mode_val = df[selected_variable].mode()[0] if not df[selected_variable].mode().empty else 'N/A'
                std_val = df[selected_variable].std()
                var_val = df[selected_variable].var() # Varianza
                min_val = df[selected_variable].min()
                max_val = df[selected_variable].max()
                q1 = df[selected_variable].quantile(0.25)
                q3 = df[selected_variable].quantile(0.75)
                iqr = q3 - q1

                # Preparar Exportación
                export_df = pd.DataFrame({
                    "Estadístico": ["Media", "Mediana (Q2)", "Moda", "Desviación Std", "Varianza", "Mínimo", "Q1 (25%)", "Q3 (75%)", "Máximo", "IQR"],
                    "Valor": [mean_val, median_val, mode_val, std_val, var_val, min_val, q1, q3, max_val, iqr]
                })
                export_filename = f"estadisticas_{selected_variable}.csv"

                st.subheader("1. Resumen Estadístico")
                
                # TENDENCIA CENTRAL (AZUL)
                st.markdown("**Tendencia Central**")
                c1, c2, c3 = st.columns(3)
                c1.markdown('<div class="metric-central">', unsafe_allow_html=True)
                c1.metric("Media", f"{mean_val:.2f}")
                c1.markdown('</div>', unsafe_allow_html=True)

                c2.markdown('<div class="metric-central">', unsafe_allow_html=True)
                c2.metric("Mediana (Q2)", f"{median_val:.2f}")
                c2.markdown('</div>', unsafe_allow_html=True)

                c3.markdown('<div class="metric-central">', unsafe_allow_html=True)
                c3.metric("Moda", f"{mode_val}")
                c3.markdown('</div>', unsafe_allow_html=True)
                
                # DISPERSIÓN (VERDE)
                st.markdown("**Dispersión y Rango**")
                c4, c5, c6 = st.columns(3)
                c4.markdown('<div class="metric-dispersion">', unsafe_allow_html=True)
                c4.metric("Desv. Estándar", f"{std_val:.2f}")
                c4.markdown('</div>', unsafe_allow_html=True)

                c5.markdown('<div class="metric-dispersion">', unsafe_allow_html=True)
                c5.metric("Varianza", f"{var_val:.2f}")
                c5.markdown('</div>', unsafe_allow_html=True)

                c6.markdown('<div class="metric-dispersion">', unsafe_allow_html=True)
                c6.metric("Rango (Max - Min)", f"{max_val - min_val:.2f}")
                c6.markdown('</div>', unsafe_allow_html=True)

                # POSICIÓN (PÚRPURA)
                st.markdown("**Posición (Cuartiles)**")
                c7, c8, c9, c10 = st.columns(4) 

                c7.markdown('<div class="metric-position">', unsafe_allow_html=True)
                c7.metric("Mínimo", f"{min_val:.2f}")
                c7.markdown('</div>', unsafe_allow_html=True)

                c8.markdown('<div class="metric-position">', unsafe_allow_html=True)
                c8.metric("Q1 (25%)", f"{q1:.2f}")
                c8.markdown('</div>', unsafe_allow_html=True)

                c9.markdown('<div class="metric-position">', unsafe_allow_html=True)
                c9.metric("Q2 (Mediana)", f"{median_val:.2f}")
                c9.markdown('</div>', unsafe_allow_html=True)
                
                c10.markdown('<div class="metric-position">', unsafe_allow_html=True)
                c10.metric("Q3 (75%)", f"{q3:.2f}")
                c10.markdown('</div>', unsafe_allow_html=True)
                
                col_iqr = st.columns(3)[1]
                col_iqr.markdown('<div class="metric-position">', unsafe_allow_html=True)
                col_iqr.metric("Rango Intercuartílico (IQR)", f"{iqr:.2f}")
                col_iqr.markdown('</div>', unsafe_allow_html=True)


                st.divider()

                # GRÁFICOS UNIVARIADOS NUMÉRICOS
                st.subheader("2. Visualización Univiariada")
                
                col_hist, col_box = st.columns(2)

                with col_hist:
                    st.markdown("**Histograma** (Distribución)")
                    fig_h, ax_h = plt.subplots(figsize=(8, 5))
                    sns.histplot(df[selected_variable], kde=True, color='#3498db', ax=ax_h)
                    st.pyplot(fig_h, use_container_width=True)

                with col_box:
                    st.markdown("**Boxplot** (Valores Atípicos)")
                    fig_b, ax_b = plt.subplots(figsize=(8, 5))
                    sns.boxplot(x=df[selected_variable], color='#2ecc71', ax=ax_b)
                    st.pyplot(fig_b, use_container_width=True)

                # INTERPRETACIÓN
                st.markdown("### 📝 Interpretación Univiariada")
                st.info(f"""
                **Análisis de Resultados:**
                * **Centralidad:** El promedio es **{mean_val:.2f}** y la mediana (Q2) es **{median_val:.2f}**.
                * **Dispersión:** La **Desviación Estándar** es **{std_val:.2f}**, indicando una variabilidad típica.
                * **Ubicación:** El 50% central de los datos (IQR) oscila entre **{q1:.2f}** (Q1) y **{q3:.2f}** (Q3).
                """)
                
                st.divider()
                
                # --- ANÁLISIS BIVARIADO NUMÉRICO (DISPERSIÓN) ---
                st.subheader("3. Análisis Bivariado: Gráfico de Dispersión")
                
                numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                comparison_options = [col for col in numerical_cols if col != selected_variable]

                if comparison_options:
                    selected_comparison = st.selectbox("Selecciona la variable numérica para comparar (Eje Y):", comparison_options)
                    
                    # GRÁFICO DE DISPERSIÓN
                    fig_scatter, ax_scatter = plt.subplots(figsize=(8, 5))
                    sns.scatterplot(x=df[selected_variable], y=df[selected_comparison], ax=ax_scatter)
                    ax_scatter.set_title(f"Dispersión: {selected_variable} vs {selected_comparison}")
                    st.pyplot(fig_scatter, use_container_width=True)
                    
                    # Cálculo de Correlación
                    correlation = df[[selected_variable, selected_comparison]].corr().iloc[0, 1]
                    st.success(f"**Coeficiente de Correlación de Pearson:** **{correlation:.4f}**")
                    st.caption("Indica la fuerza y dirección de la relación lineal.")

                else:
                    st.warning("No hay suficientes variables numéricas para realizar un análisis de dispersión.")


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

                st.subheader("1. Resumen de Frecuencias")
                
                c_kpi1, c_kpi2 = st.columns(2)
                c_kpi1.markdown('<div class="metric-central">', unsafe_allow_html=True)
                c_kpi1.metric("Categoría más común (Moda)", freq.idxmax())
                c_kpi1.markdown('</div>', unsafe_allow_html=True)
                
                c_kpi2.markdown('<div class="metric-dispersion">', unsafe_allow_html=True)
                c_kpi2.metric("Total de Registros", len(df))
                c_kpi2.markdown('</div>', unsafe_allow_html=True)


                # 1. TABLA 
                st.markdown("### 📋 Tabla de Frecuencias")
                st.dataframe(
                    freq_table.style.format("{:.2f}", subset=['Frec. Relativa (%)', 'Acumulada Rel. (%)'])
                    .background_gradient(cmap="Blues", subset=['Frec. Absoluta']),
                    use_container_width=True
                )

                # 2. GRÁFICO UNIVARIADO CATEGÓRICO
                st.markdown("### 📊 Distribución Visual")
                fig, ax = plt.subplots(figsize=(10, 4))
                bars = sns.countplot(y=selected_variable, data=df, order=freq.index, palette='Spectral', ax=ax)
                ax.set_xlabel("Frecuencia")
                ax.set_ylabel("Categoría")
                
                st.pyplot(fig, use_container_width=True)
                
                # INTERPRETACIÓN
                st.markdown("### 📝 Interpretación Univiariada")
                top_cat = freq.idxmax()
                top_val = freq.max()
                top_perc = (top_val / len(df)) * 100
                st.info(f"""
                **Hallazgos Principales:**
                * La categoría predominante es **{top_cat}**, con **{top_val}** registros.
                * Esto representa el **{top_perc:.2f}%** del total de la muestra.
                """)
                
                st.divider()

                # --- ANÁLISIS BIVARIADO CATEGÓRICO (BARRAS AGRUPADAS) ---
                st.subheader("3. Análisis Bivariado: Gráfico de Barras Agrupadas")
                
                categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
                comparison_options = [col for col in categorical_cols if col != selected_variable]

                if comparison_options:
                    selected_comparison = st.selectbox("Selecciona la variable categórica para comparar (Hue):", comparison_options)
                    
                    # GRÁFICO DE BARRAS AGRUPADAS
                    fig_count, ax_count = plt.subplots(figsize=(10, 5))
                    sns.countplot(y=df[selected_variable], hue=df[selected_comparison], ax=ax_count, order=df[selected_variable].value_counts().index)
                    ax_count.set_title(f"Distribución de {selected_variable} por {selected_comparison}")
                    ax_count.legend(title=selected_comparison)
                    st.pyplot(fig_count, use_container_width=True)
                    
                    # TABLA CRUZADA (Opcional)
                    st.markdown("#### Tabla de Contingencia")
                    cross_tab = pd.crosstab(df[selected_variable], df[selected_comparison], margins=True, normalize=False)
                    st.dataframe(cross_tab, use_container_width=True)

                else:
                    st.warning("No hay suficientes variables categóricas para realizar un análisis agrupado.")


            # BOTÓN DESCARGA (Se mantiene al final de la pestaña)
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
        # PESTAÑA 2: PROBABILIDADES (Original)
        # ==========================================
        with tab_prob:
            st.header("Laboratorio de Probabilidades")
            
            # 1. Simple
            with st.container():
                st.markdown("### 🎲 1. Probabilidad Simple")
                c1, c2 = st.columns([1, 3])
                red_simple = c1.selectbox("Evento (Red Social):", df['Red_social_mas_utilizada'].unique())
                
                p_simple = len(df[df['Red_social_mas_utilizada'] == red_simple]) / len(df)
                
                # Resultado con porcentaje
                c2.metric("Resultado Matemático", f"{p_simple:.4f}", f"{p_simple*100:.2f}%")
                st.info(f"**Interpretación:** Existe una probabilidad de **{p_simple:.4f}** de seleccionar aleatoriamente un usuario de **{red_simple}**.")
            
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
                        st.metric("Resultado Condicional", f"{p_cond:.4f}", f"{p_cond*100:.2f}%")
                    else:
                        st.warning("No hay datos para esta condición.")
                
                # Interpretación debajo
                if not subset.empty:
                    st.info(f"**Interpretación:** Dado que sabemos que el usuario está en **{lugar_cond}**, la probabilidad ajustada de que **{trabajo_cond}** use redes es **{p_cond:.4f}**.")

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
                        st.metric("Resultado Binomial", f"{prob_k:.4f}", f"{prob_k*100:.2f}%")
                    else:
                        st.error("Sin datos suficientes.")
                
                # Interpretación debajo
                if not sub_bin.empty:
                    st.info(f"**Interpretación:** En una muestra de **{n}** usuarios en **{lugar_bin}**, la probabilidad de encontrar exactamente **{k}** usuarios de **{red_bin}** es **{prob_k:.4f}** (usando p_base={p:.4f}).")

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
else:
    st.info("👈 Sube un archivo Excel para comenzar.")





