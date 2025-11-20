import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import binom
import io

# Configuración de la página para usar todo el ancho
st.set_page_config(page_title="Análisis de Datos", layout="wide", page_icon="📊")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
    }
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #2c3e50;
    }
    h2, h3 {
        color: #34495e;
    }
    
    /* --- DISEÑO PERSONALIZADO DEL BOTÓN DE DESCARGA --- */
    div.stDownloadButton {
        text-align: center;
    }
    div.stDownloadButton > button:first-child {
        background-color: #27ae60; /* Verde elegante */
        color: white;
        padding: 12px 28px;
        border-radius: 8px;
        border: none;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        width: 50%; /* Ancho del botón */
    }
    div.stDownloadButton > button:first-child:hover {
        background-color: #219150; /* Verde más oscuro al pasar el mouse */
        color: white;
        box-shadow: 0px 6px 8px rgba(0,0,0,0.2);
        transform: translateY(-2px); /* Efecto de elevación */
    }
    div.stDownloadButton > button:first-child:active {
        transform: translateY(0px);
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: CONFIGURACIÓN ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1055/1055644.png", width=100)
st.sidebar.title("Configuración")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("Sube tu archivo Excel (.xlsx)", type="xlsx")

# --- PANTALLA PRINCIPAL ---
st.title("📊 Análisis Interactivo: Redes Sociales y Productividad")

if uploaded_file is not None:
    # Cargar los datos
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("✅ Archivo cargado correctamente")
        
        # --- VISTA DE DATOS PERSISTENTE (ARRIBA) ---
        with st.expander("🔍 Vista Previa de los Datos Cargados (Click para expandir/contraer)", expanded=True):
            st.dataframe(df.head(), use_container_width=True)
            st.caption(f"Dimensiones del dataset: **{df.shape[0]} filas** x **{df.shape[1]} columnas**")
        
        st.markdown("---")

        # --- PESTAÑAS PRINCIPALES ---
        tab_desc, tab_prob = st.tabs(["📈 Análisis Descriptivo Completo", "🎲 Laboratorio de Probabilidades"])

        # ==============================================================================
        # PESTAÑA 1: ANÁLISIS DESCRIPTIVO
        # ==============================================================================
        with tab_desc:
            # Selección de variable
            col_var, col_info = st.columns([1, 3])
            with col_var:
                st.markdown("##### Variable a analizar")
                selected_variable = st.selectbox("Selecciona la columna:", df.columns)
            
            st.markdown("---")

            # Variable para almacenar datos de exportación
            export_df = None
            export_filename = "resultados.csv"

            # ---------------------------------------------------------
            # LÓGICA PARA VARIABLES NUMÉRICAS
            # ---------------------------------------------------------
            if df[selected_variable].dtype in ['float64', 'int64']:
                
                # --- CÁLCULOS ESTADÍSTICOS ---
                # Medidas de Tendencia Central
                mean_val = df[selected_variable].mean()
                median_val = df[selected_variable].median()
                mode_val = df[selected_variable].mode()[0]
                
                # Medidas de Dispersión
                std_val = df[selected_variable].std()
                var_val = df[selected_variable].var()
                min_val = df[selected_variable].min()
                max_val = df[selected_variable].max()
                rango = max_val - min_val

                # Medidas de Posición (Percentiles, Deciles, IQR)
                q1 = df[selected_variable].quantile(0.25)
                q3 = df[selected_variable].quantile(0.75)
                iqr = q3 - q1
                decil_1 = df[selected_variable].quantile(0.10)
                decil_9 = df[selected_variable].quantile(0.90)

                # Preparar datos para exportar
                export_df = pd.DataFrame({
                    "Métrica": ["Media", "Mediana", "Moda", "Desv. Estándar", "Varianza", "Mínimo", "Máximo", "Rango", "Q1 (25%)", "Q3 (75%)", "IQR", "Decil 1", "Decil 9"],
                    "Valor": [mean_val, median_val, mode_val, std_val, var_val, min_val, max_val, rango, q1, q3, iqr, decil_1, decil_9]
                })
                export_filename = f"estadisticas_{selected_variable}.csv"

                st.subheader("1. Medidas Estadísticas")
                
                # Fila 1: Tendencia Central y Dispersión Básica
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Media (Promedio)", f"{mean_val:.2f}")
                col2.metric("Mediana (Centro)", f"{median_val:.2f}")
                col3.metric("Moda (Frecuente)", f"{mode_val}")
                col4.metric("Desv. Estándar", f"{std_val:.2f}")

                # Fila 2: Medidas de Posición y Rango
                st.markdown("###### Medidas de Posición y Ubicación")
                col5, col6, col7, col8, col9 = st.columns(5)
                col5.metric("Mínimo", f"{min_val:.2f}")
                col6.metric("Q1 (25%)", f"{q1:.2f}")
                col7.metric("Q3 (75%)", f"{q3:.2f}")
                col8.metric("Máximo", f"{max_val:.2f}")
                col9.metric("IQR (Rango Interc.)", f"{iqr:.2f}", help="Diferencia entre el Q3 y el Q1. Indica la dispersión del 50% central de los datos.")

                # --- VISUALIZACIÓN ---
                st.subheader("2. Visualización de Distribución")
                
                # Layout: Gráficos juntos lado a lado (mitad y mitad)
                col_hist, col_box = st.columns(2)
                
                with col_hist:
                    st.markdown("**Histograma de Frecuencias**")
                    fig1, ax1 = plt.subplots(figsize=(6, 4))
                    sns.histplot(df[selected_variable], kde=True, ax=ax1, color='#3498db', bins=20)
                    ax1.set_xlabel(selected_variable)
                    ax1.set_ylabel("Frecuencia")
                    st.pyplot(fig1, use_container_width=True)
                    
                with col_box:
                    st.markdown("**Boxplot (Diagrama de Caja)**")
                    fig2, ax2 = plt.subplots(figsize=(6, 4))
                    sns.boxplot(y=df[selected_variable], ax=ax2, color='#2ecc71')
                    ax2.set_ylabel(selected_variable)
                    st.pyplot(fig2, use_container_width=True)

                # Interpretación debajo de los gráficos para aprovechar el ancho
                st.info(f"""
                **Interpretación Conjunta:**
                * El **histograma** muestra cómo se concentran los datos. Si la curva es simétrica, la media (**{mean_val:.2f}**) y la mediana (**{median_val:.2f}**) deberían ser similares.
                * El **boxplot** resalta los valores atípicos (puntos fuera de los bigotes). El 50% central de tus datos se encuentra entre **{q1:.2f}** y **{q3:.2f}**.
                """)

            # ---------------------------------------------------------
            # LÓGICA PARA VARIABLES CATEGÓRICAS
            # ---------------------------------------------------------
            else:
                # Cálculos completos
                freq = df[selected_variable].value_counts()
                total_n = len(df)
                
                freq_abs = freq
                freq_rel = (freq / total_n) * 100
                freq_cum_abs = freq_abs.cumsum()
                freq_cum_rel = freq_rel.cumsum()
                
                # Crear DataFrame completo
                freq_table = pd.DataFrame({
                    'Frecuencia Absoluta': freq_abs,
                    'Frecuencia Relativa (%)': freq_rel,
                    'Frec. Acumulada Absoluta': freq_cum_abs,
                    'Frec. Acumulada Relativa (%)': freq_cum_rel
                })
                
                # Preparar datos para exportar
                export_df = freq_table.reset_index().rename(columns={'index': selected_variable})
                export_filename = f"frecuencias_{selected_variable}.csv"

                st.subheader("1. Resumen Categórico")
                
                # Gráfico a la izquierda, Tabla a la derecha
                col_chart, col_table = st.columns([1, 1])

                with col_chart:
                    st.markdown("**Gráfico de Barras**")
                    fig, ax = plt.subplots(figsize=(6, 4))
                    sns.countplot(y=selected_variable, data=df, order=freq.index, palette='viridis', ax=ax)
                    ax.set_xlabel("Cantidad")
                    st.pyplot(fig, use_container_width=True)

                with col_table:
                    st.markdown("**Tabla de Frecuencias**")
                    st.dataframe(
                        freq_table.style.format({
                            'Frecuencia Relativa (%)': "{:.2f}%",
                            'Frec. Acumulada Relativa (%)': "{:.2f}%"
                        }).background_gradient(cmap="Blues", subset=['Frecuencia Absoluta']),
                        use_container_width=True,
                        height=300
                    )
                
                top_val = freq.idxmax()
                st.success(f"La categoría dominante es **{top_val}** con **{freq.max()}** registros, lo que representa el **{freq_rel.max():.2f}%** del total.")

            # --- SECCIÓN DE EXPORTACIÓN ---
            st.markdown("---")
            if export_df is not None:
                col_vacio1, col_btn, col_vacio2 = st.columns([1, 2, 1])
                with col_btn:
                    st.download_button(
                        label="📥 DESCARGAR RESULTADOS (CSV)",
                        data=export_df.to_csv(index=False).encode('utf-8'),
                        file_name=export_filename,
                        mime='text/csv'
                    )

        # ==============================================================================
        # PESTAÑA 2: PROBABILIDADES
        # ==============================================================================
        with tab_prob:
            st.header("Laboratorio de Probabilidades")
            st.markdown("Selecciona el tipo de cálculo que deseas realizar:")

            # Usar columnas para los "tabs" visuales o expanders para que se vean mejor distribuidos
            # Aquí usaremos expanders abiertos por defecto o contenedores separados
            
            # --- EJERCICIO 1: PROBABILIDAD SIMPLE ---
            with st.container():
                st.subheader("🎲 1. Probabilidad Simple (Marginal)")
                st.caption("Calcula la probabilidad de que ocurra un evento simple (ej. elegir una Red Social específica).")
                
                c1, c2 = st.columns([1, 2])
                with c1:
                    red_social_sel = st.selectbox(
                        "Evento de interés (Red Social):", 
                        df['Red_social_mas_utilizada'].unique(),
                        key="red_simple"
                    )
                with c2:
                    count = df[df['Red_social_mas_utilizada'] == red_social_sel].shape[0]
                    total = df.shape[0]
                    prob = count / total
                    
                    st.info(f"**Pregunta:** ¿Cuál es la probabilidad de elegir un usuario que use **{red_social_sel}**?")
                    st.metric("Resultado", f"{prob:.4f}", f"{prob*100:.2f}%")
            
            st.divider()

            # --- EJERCICIO 2: PROBABILIDAD CONDICIONAL ---
            with st.container():
                st.subheader("🔗 2. Probabilidad Condicional")
                st.caption("Calcula P(A|B): Probabilidad de A dado que ya ocurrió B.")
                
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown("**Condición (Dado que...):**")
                    lugar_sel = st.selectbox("Lugar de conexión:", df['Lugar_habitual_conexion'].unique(), key="cond_lugar")
                    
                    st.markdown("**Evento (Probabilidad de...):**")
                    trabajo_sel = st.selectbox("Uso en trabajo:", df['Uso_redes_durante_trabajo'].unique(), key="cond_trabajo")
                
                with c2:
                    subset = df[df['Lugar_habitual_conexion'] == lugar_sel]
                    
                    if not subset.empty:
                        target = subset[subset['Uso_redes_durante_trabajo'] == trabajo_sel].shape[0]
                        total_cond = subset.shape[0]
                        prob_cond = target / total_cond
                        
                        st.info(f"**Pregunta:** De los usuarios que se conectan en **{lugar_sel}** ({total_cond}), ¿cuál es la probabilidad de que **{trabajo_sel}** usen redes en el trabajo?")
                        st.metric("Resultado Condicional", f"{prob_cond:.4f}", f"{prob_cond*100:.2f}%")
                    else:
                        st.error("No hay datos que cumplan la condición inicial.")

            st.divider()

            # --- EJERCICIO 3: DISTRIBUCIÓN BINOMIAL ---
            with st.container():
                st.subheader("📊 3. Distribución Binomial")
                st.caption("Calcula la probabilidad de obtener exactamente 'k' éxitos en 'n' intentos.")
                
                c1, c2, c3 = st.columns([1, 1, 2])
                
                with c1:
                    st.markdown("**1. Configurar Éxito**")
                    lugar_bin = st.selectbox("Filtro Población:", df['Lugar_habitual_conexion'].unique(), key="bin_lugar")
                    red_bin = st.selectbox("Evento Éxito:", df['Red_social_mas_utilizada'].unique(), key="bin_red")
                
                with c2:
                    st.markdown("**2. Parámetros Ensayo**")
                    n_val = st.number_input("Muestra (n)", 1, 100, 10)
                    k_val = st.number_input("Éxitos deseados (k)", 0, n_val, 5)
                
                with c3:
                    subset_bin = df[df['Lugar_habitual_conexion'] == lugar_bin]
                    if not subset_bin.empty:
                        p_real = subset_bin['Red_social_mas_utilizada'].value_counts(normalize=True).get(red_bin, 0)
                        
                        st.markdown(f"**Probabilidad base (p):** `{p_real:.4f}`")
                        
                        if p_real > 0:
                            prob_binom = binom.pmf(k_val, n_val, p_real)
                            st.success(f"Probabilidad de encontrar exactamente **{k_val}** usuarios de **{red_bin}** en una muestra de **{n_val}**:")
                            st.metric("Resultado Binomial", f"{prob_binom:.4f}")
                        else:
                            st.warning(f"La probabilidad base es 0. Nadie en {lugar_bin} usa {red_bin}.")
                    else:
                        st.error("Filtro de población vacío.")

    except Exception as e:
        st.error(f"Hubo un error al procesar el archivo: {e}")
        st.info("Asegúrate de que el Excel tenga un formato compatible.")

else:
    st.info("👈 Por favor, carga un archivo Excel desde la barra lateral para comenzar.")




