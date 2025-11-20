import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import binom

# Título de la aplicación
st.title("Análisis Interactivo de Datos de Redes Sociales y Productividad")

# Cargar archivo de datos
uploaded_file = st.file_uploader("Sube el archivo de datos (Excel)", type="xlsx")

if uploaded_file is not None:
    # Cargar los datos
    df = pd.read_excel(uploaded_file)
    st.write("Datos cargados exitosamente")
    st.dataframe(df.head())  # Mostrar las primeras filas

    # Selección de la variable para análisis
    selected_variable = st.selectbox("Selecciona la variable para el análisis", df.columns)

    # Verificar si la variable seleccionada es numérica o categórica
    if df[selected_variable].dtype in ['float64', 'int64']:  # Variables numéricas
        st.write(f"**Estadísticas de {selected_variable}:**")
        
        # Calcular estadísticas para variables numéricas
        mean_value = df[selected_variable].mean()
        median_value = df[selected_variable].median()
        mode_value = df[selected_variable].mode()[0]
        std_dev = df[selected_variable].std()
        var_value = df[selected_variable].var()

        # Mostrar estadísticas
        st.write(f"Media: {mean_value}")
        st.write(f"Mediana: {median_value}")
        st.write(f"Moda: {mode_value}")
        st.write(f"Desviación Estándar: {std_dev}")
        st.write(f"Varianza: {var_value}")
        
        # Crear histogramas
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(df[selected_variable], kde=True, ax=ax, color='skyblue', bins=20)
        ax.set_title(f"Histograma de {selected_variable}")
        ax.set_xlabel(selected_variable)
        ax.set_ylabel('Frecuencia')
        st.pyplot(fig)

        # Crear boxplot
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df[selected_variable], ax=ax, color='lightgreen')
        ax.set_title(f"Boxplot de {selected_variable}")
        ax.set_xlabel(selected_variable)
        st.pyplot(fig)
    
    else:  # Variables categóricas
        st.write(f"**Frecuencia y Porcentaje de {selected_variable}:**")
        
        # Calcular la frecuencia y el porcentaje
        freq = df[selected_variable].value_counts()
        percent = df[selected_variable].value_counts(normalize=True) * 100
        freq_table = pd.DataFrame({'Frecuencia': freq, 'Porcentaje': percent})
        st.dataframe(freq_table)

        # Crear gráfico de barras
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.countplot(x=selected_variable, data=df, ax=ax, palette='viridis')
        ax.set_title(f"Distribución de {selected_variable}")
        ax.set_xlabel(selected_variable)
        ax.set_ylabel('Frecuencia')
        st.pyplot(fig)

    # Ejercicio 1: Probabilidad Simple
    red_social = st.selectbox("Selecciona una red social para calcular la probabilidad", df['Red_social_mas_utilizada'].unique())
    usuarios_red_social = df[df['Red_social_mas_utilizada'] == red_social].shape[0]
    probabilidad_red_social = usuarios_red_social / df.shape[0]
    st.write(f"Probabilidad de que un usuario esté usando {red_social}: {probabilidad_red_social:.2f}")

    # Ejercicio 2: Probabilidad Condicional
    plataforma_mensajeria = st.selectbox("Selecciona si se usa redes durante el trabajo", df['Uso_redes_durante_trabajo'].unique())
    lugar_conexion = st.selectbox("Selecciona el lugar habitual de conexión", df['Lugar_habitual_conexion'].unique())
    
    usuarios_laborales = df[df['Lugar_habitual_conexion'] == lugar_conexion]
    usuarios_plataforma_laborales = usuarios_laborales[usuarios_laborales['Uso_redes_durante_trabajo'] == plataforma_mensajeria].shape[0]
    probabilidad_condicional = usuarios_plataforma_laborales / usuarios_laborales.shape[0]
    
    st.write(f"Probabilidad de que un usuario esté usando {plataforma_mensajeria} en {lugar_conexion}: {probabilidad_condicional:.2f}")

    # Ejercicio 3: Distribución Binomial
    lugar_conexion = st.selectbox("Selecciona el lugar habitual de conexión para distribución binomial", df['Lugar_habitual_conexion'].unique())
    red_social = st.selectbox("Selecciona la red social para distribución binomial", df['Red_social_mas_utilizada'].unique())

    usuarios_lugar = df[df['Lugar_habitual_conexion'] == lugar_conexion]
    p = usuarios_lugar['Red_social_mas_utilizada'].value_counts(normalize=True).get(red_social, 0)

    n = 10  # Número total de usuarios
    k = 5   # Queremos saber la probabilidad de que 5 usuarios estén usando la red social seleccionada

    probabilidad_binomial = binom.pmf(k, n, p)

    st.write(f"Probabilidad de que 5 de 10 usuarios en {lugar_conexion} estén usando {red_social}: {probabilidad_binomial:.4f}")

    # Exportar Resultados
    if st.button("Exportar Resultados a CSV"):
        # Crear un DataFrame con los resultados
        analysis_results = pd.DataFrame({
            "Estadísticas": ["Media", "Mediana", "Moda", "Desviación Estándar", "Varianza"],
            "Valores": [mean_value, median_value, mode_value, std_dev, var_value]
        })
        
        # Convertir el DataFrame a CSV
        csv = analysis_results.to_csv(index=False)
        st.download_button(
            label="Descargar CSV",
            data=csv,
            file_name="resultados_analisis.csv",
            mime="text/csv"
        )
