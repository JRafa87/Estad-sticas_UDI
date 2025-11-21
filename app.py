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
        # PESTAÑA 1: DESCRIPTIVA
        # ==========================================
        with tab_desc:
            col_var, _ = st.columns([1, 2])
            with col_var:
                selected_variable = st.selectbox("Selecciona la variable a analizar:", df.columns)
            
            export_df = None
            export_filename = "resultados.csv"

            # Selección dinámica para comparar con otra variable
            if df[selected_variable].dtype in ['float64', 'int64']:
                # Si la variable seleccionada es numérica, elige otra variable numérica para compararla
                selected_comparison = st.selectbox("Selecciona la variable numérica para comparar:", df.select_dtypes(include=['float64', 'int64']).columns.tolist())
                
                # GRÁFICO DE DISPERSIÓN
                st.subheader(f"Gráfico de Dispersión: {selected_variable} vs {selected_comparison}")
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.scatterplot(x=df[selected_variable], y=df[selected_comparison], ax=ax)
                ax.set_title(f"Dispersión entre {selected_variable} y {selected_comparison}")
                st.pyplot(fig)

            elif df[selected_variable].dtype in ['object']:
                # Si la variable seleccionada es categórica, elige otra variable categórica para compararla
                selected_comparison = st.selectbox("Selecciona la variable categórica para comparar:", df.select_dtypes(include=['object']).columns.tolist())
                
                # GRÁFICO DE BARRAS
                st.subheader(f"Gráfico de Barras: {selected_variable} vs {selected_comparison}")
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.countplot(x=df[selected_variable], hue=df[selected_comparison], ax=ax)
                ax.set_title(f"Distribución de {selected_variable} por {selected_comparison}")
                st.pyplot(fig)

            st.divider()

        # ==========================================
        # PESTAÑA 2: PROBABILIDADES
        # ==========================================
        with tab_prob:
            st.header("Laboratorio de Probabilidades")
            
            # 1. Probabilidad Simple
            with st.container():
                st.markdown("### 🎲 1. Probabilidad Simple")
                c1, c2 = st.columns([1, 3])
                red_simple = c1.selectbox("Evento (Red Social):", df['Red_social_mas_utilizada'].unique())
                
                p_simple = len(df[df['Red_social_mas_utilizada'] == red_simple]) / len(df)
                
                # Resultado con porcentaje
                c2.metric("Resultado Matemático", f"{p_simple:.4f}", f"{p_simple*100:.2f}%")
                st.info(f"**Interpretación:** Existe una probabilidad de **{p_simple:.4f}** de seleccionar aleatoriamente un usuario de **{red_simple}**.")

            st.divider()

            # 2. Probabilidad Condicional
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

            # 3. Distribución Binomial
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





