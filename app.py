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
st.markdown("Esta herramienta permite explorar patrones de comportamiento digital y calcular probabilidades.")

if uploaded_file is not None:
    # Cargar los datos
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("✅ Archivo cargado correctamente")
        
        with st.sidebar.expander("🔍 Vista previa de los datos", expanded=False):
            st.dataframe(df.head())
            st.caption(f"Dimensiones del dataset: {df.shape[0]} filas x {df.shape[1]} columnas")

        # --- PESTAÑAS PRINCIPALES ---
        tab_desc, tab_prob = st.tabs(["📈 Análisis Descriptivo", "🎲 Probabilidades"])

        # ==============================================================================
        # PESTAÑA 1: ANÁLISIS DESCRIPTIVO
        # ==============================================================================
        with tab_desc:
            st.header("Análisis Estadístico de Variables")
            
            # Selección de variable (SOLO AQUÍ)
            st.markdown("##### Configuración del análisis")
            selected_variable = st.selectbox("Selecciona la variable a analizar:", df.columns)
            st.markdown("---")

            # Variable para almacenar datos de exportación
            export_df = None
            export_filename = "resultados.csv"

            # ---------------------------------------------------------
            # LÓGICA PARA VARIABLES NUMÉRICAS
            # ---------------------------------------------------------
            if df[selected_variable].dtype in ['float64', 'int64']:
                
                # Cálculos
                mean_val = df[selected_variable].mean()
                median_val = df[selected_variable].median()
                mode_val = df[selected_variable].mode()[0]
                std_val = df[selected_variable].std()
                var_val = df[selected_variable].var()

                # Preparar datos para exportar
                export_df = pd.DataFrame({
                    "Métrica": ["Media", "Mediana", "Moda", "Desviación Estándar", "Varianza"],
                    "Valor": [mean_val, median_val, mode_val, std_val, var_val]
                })
                export_filename = f"estadisticas_{selected_variable}.csv"

                # Fila de Métricas (Dashboard style)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Media", f"{mean_val:.2f}", delta_color="off")
                col2.metric("Mediana", f"{median_val:.2f}", delta_color="off")
                col3.metric("Moda", f"{mode_val}", delta_color="off")
                col4.metric("Desv. Estándar", f"{std_val:.2f}", help="Indica qué tan dispersos están los datos")

                st.markdown("### Visualización e Interpretación")
                
                # Layout: Gráfico (Izquierda, Grande) | Interpretación (Derecha, Pequeña)
                col_graph, col_text = st.columns([2, 1])
                
                with col_graph:
                    # Gráficos lado a lado
                    subtab1, subtab2 = st.tabs(["Histograma (Distribución)", "Boxplot (Valores Atípicos)"])
                    
                    with subtab1:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        sns.histplot(df[selected_variable], kde=True, ax=ax, color='#3498db', bins=20)
                        ax.set_title(f"Distribución de {selected_variable}")
                        st.pyplot(fig)
                    
                    with subtab2:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        sns.boxplot(x=df[selected_variable], ax=ax, color='#2ecc71')
                        ax.set_title(f"Rango y Atípicos de {selected_variable}")
                        st.pyplot(fig)

                with col_text:
                    st.subheader("📝 Análisis")
                    st.info(f"**Centralidad:**\nEl usuario promedio pasa **{mean_val:.2f}** minutos. La mitad de los usuarios está por debajo de **{median_val:.2f}**.")
                    st.warning(f"**Dispersión:**\nCon una desviación de **{std_val:.2f}**, existe una variabilidad {'alta' if std_val > mean_val/2 else 'moderada'} en los hábitos.")
                    st.success(f"**Tendencia:**\nEl valor más frecuente es **{mode_val}**.")

            # ---------------------------------------------------------
            # LÓGICA PARA VARIABLES CATEGÓRICAS
            # ---------------------------------------------------------
            else:
                # Cálculos completos (4 columnas)
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

                # Métricas Resumidas
                col_kpi1, col_kpi2 = st.columns(2)
                col_kpi1.metric("Moda (Más común)", freq.idxmax())
                col_kpi2.metric("Total Registros", total_n)
                
                st.markdown("### Visualización e Interpretación")
                
                # Layout: Gráfico vs Interpretación
                col_chart, col_insight = st.columns([2, 1])

                with col_chart:
                    fig, ax = plt.subplots(figsize=(10, 5))
                    sns.countplot(y=selected_variable, data=df, order=freq.index, palette='viridis', ax=ax)
                    ax.set_title(f"Conteo por {selected_variable}")
                    ax.set_xlabel("Cantidad de Usuarios")
                    st.pyplot(fig)

                with col_insight:
                    st.subheader("📝 Análisis Rápido")
                    top_val = freq.idxmax()
                    top_perc = freq_rel.max()
                    st.success(f"**Dominancia:**\nLa categoría **{top_val}** es la predominante, representando el **{top_perc:.2f}%** de la muestra.")
                    st.info(f"**Diversidad:**\nSe encontraron **{len(freq)}** categorías únicas en esta variable.")

                # TABLA COMPLETA DE ANCHO TOTAL
                st.subheader("📋 Tabla de Frecuencias Detallada")
                st.dataframe(
                    freq_table.style.format({
                        'Frecuencia Relativa (%)': "{:.2f}%",
                        'Frec. Acumulada Relativa (%)': "{:.2f}%"
                    }).background_gradient(cmap="Blues", subset=['Frecuencia Absoluta']),
                    use_container_width=True  # Ocupa todo el ancho disponible
                )

            # --- SECCIÓN DE EXPORTACIÓN ---
            st.markdown("---")
            if export_df is not None:
                st.markdown("<h3 style='text-align: center; color: #2c3e50;'>📂 Exportar Datos del Análisis</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center;'>Descarga los resultados actuales en formato CSV.</p>", unsafe_allow_html=True)
                
                col_vacio1, col_btn, col_vacio2 = st.columns([1, 2, 1])
                with col_btn:
                    st.download_button(
                        label="📥 DESCARGAR RESULTADOS AHORA",
                        data=export_df.to_csv(index=False).encode('utf-8'),
                        file_name=export_filename,
                        mime='text/csv',
                        help="Haz clic para guardar los datos calculados arriba."
                    )

        # ==============================================================================
        # PESTAÑA 2: PROBABILIDADES
        # ==============================================================================
        with tab_prob:
            st.header("Laboratorio de Probabilidades")
            st.caption("Modifica los parámetros en cada pestaña para actualizar las preguntas y los resultados.")

            # Sub-tabs para organizar los ejercicios
            subtab_p1, subtab_p2, subtab_p3 = st.tabs(["🎲 Probabilidad Simple", "🔗 Probabilidad Condicional", "📊 Distribución Binomial"])

            # --- EJERCICIO 1 ---
            with subtab_p1:
                col_sel, col_res = st.columns([1, 2])
                with col_sel:
                    red_social_sel = st.selectbox(
                        "Selecciona la Red Social:", 
                        df['Red_social_mas_utilizada'].unique(),
                        key="red_simple"
                    )
                
                with col_res:
                    st.markdown(f"### ❓ Pregunta: ¿Cuál es la probabilidad de que un usuario use **{red_social_sel}**?")
                    
                    count = df[df['Red_social_mas_utilizada'] == red_social_sel].shape[0]
                    total = df.shape[0]
                    prob = count / total
                    
                    st.metric(label=f"Probabilidad (P = {count}/{total})", value=f"{prob:.4f}", delta=f"{prob*100:.2f}%")

            # --- EJERCICIO 2 ---
            with subtab_p2:
                col_sel_a, col_sel_b, col_res_2 = st.columns([1, 1, 2])
                
                with col_sel_a:
                    lugar_sel = st.selectbox("Dado que está en (Lugar):", df['Lugar_habitual_conexion'].unique())
                with col_sel_b:
                    trabajo_sel = st.selectbox("¿Usa redes en el trabajo?:", df['Uso_redes_durante_trabajo'].unique())

                with col_res_2:
                    st.markdown(f"### ❓ Pregunta: Dado que un usuario está en **{lugar_sel}**, ¿cuál es la probabilidad de que **{trabajo_sel}** use redes en el trabajo?")
                    
                    subset = df[df['Lugar_habitual_conexion'] == lugar_sel]
                    if not subset.empty:
                        target = subset[subset['Uso_redes_durante_trabajo'] == trabajo_sel].shape[0]
                        prob_cond = target / subset.shape[0]
                        st.metric(label="Probabilidad Condicional", value=f"{prob_cond:.4f}", delta=f"{prob_cond*100:.2f}%")
                    else:
                        st.error("No hay datos para esta combinación.")

            # --- EJERCICIO 3 ---
            with subtab_p3:
                col_params, col_calc = st.columns([1, 2])
                
                with col_params:
                    lugar_bin = st.selectbox("Lugar de conexión:", df['Lugar_habitual_conexion'].unique(), key="lugar_bin")
                    red_bin = st.selectbox("Red Social éxito:", df['Red_social_mas_utilizada'].unique(), key="red_bin")
                    k_val = st.number_input("Cantidad de éxitos (k)", min_value=0, max_value=20, value=5)
                    n_val = st.number_input("Tamaño de muestra (n)", min_value=1, max_value=100, value=10)

                with col_calc:
                    st.markdown(f"### ❓ Pregunta: Si tomamos **{n_val}** usuarios en **{lugar_bin}**, ¿cuál es la probabilidad de que exactamente **{k_val}** usen **{red_bin}**?")
                    
                    subset_bin = df[df['Lugar_habitual_conexion'] == lugar_bin]
                    if not subset_bin.empty:
                        p_real = subset_bin['Red_social_mas_utilizada'].value_counts(normalize=True).get(red_bin, 0)
                        
                        if p_real > 0:
                            prob_binom = binom.pmf(k_val, n_val, p_real)
                            st.info(f"La probabilidad base (p) calculada de los datos es: **{p_real:.4f}**")
                            st.metric(label=f"Probabilidad Binomial (k={k_val}, n={n_val})", value=f"{prob_binom:.4f}")
                            
                            # Gráfico pequeño de la distribución
                            fig_bin, ax_bin = plt.subplots(figsize=(6, 2))
                            x = range(n_val + 1)
                            y = [binom.pmf(i, n_val, p_real) for i in x]
                            sns.barplot(x=list(x), y=y, ax=ax_bin, color="#9b59b6")
                            ax_bin.axvline(k_val, color='red', linestyle='--')
                            ax_bin.set_title("Distribución de Probabilidad")
                            st.pyplot(fig_bin)
                        else:
                            st.warning(f"La probabilidad base es 0. Nadie en {lugar_bin} usa {red_bin}.")
                    else:
                        st.error("No hay datos suficientes en el filtro.")

    except Exception as e:
        st.error(f"Hubo un error al procesar el archivo: {e}")
        st.info("Asegúrate de que el Excel tenga las columnas correctas.")

else:
    st.info("👈 Por favor, carga un archivo Excel desde la barra lateral para comenzar el análisis.")
    st.markdown("""
    ### Formato esperado del Excel:
    | Red_social_mas_utilizada | Uso_redes_durante_trabajo | Lugar_habitual_conexion | Tiempo_minutos |
    |--------------------------|---------------------------|-------------------------|----------------|
    | Twitter                  | Sí                        | Casa                    | 120            |
    | Instagram                | No                        | Oficina                 | 45             |
    """)




