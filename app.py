import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =====================
# CONFIGURACIÓN DE PÁGINA
# =====================
st.set_page_config(
    page_title="Análisis de anuncios de vehículos",
    page_icon="🚗",
    layout="wide"
)

# =====================
# ESTILO PERSONALIZADO
# =====================
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f6fa;
        color: #2e2e3f;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #4a69bd;
    }
    .stDataFrame {
        border-radius: 10px;
        border: 2px solid #a5b1c2;
    }
    .stButton>button {
        background-color: #6a89cc;
        color: white;
        border-radius: 10px;
        height: 3em;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #4a69bd;
    }
    </style>
""", unsafe_allow_html=True)

# =====================
# CARGA Y LIMPIEZA DE DATOS
# =====================
@st.cache_data
def load_and_clean_data(path="vehicles_us.csv"):
    df = pd.read_csv(path)
    df = df.drop_duplicates()
    for col in ["price", "odometer", "model_year"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["price", "odometer"])
    current_year = datetime.now().year
    df = df[(df["price"] > 0) & (df["price"] <= 200000)]
    df = df[(df["odometer"] >= 0) & (df["odometer"] <= 1_000_000)]
    if "model_year" in df.columns:
        df = df[(df["model_year"] >= 1950) & (df["model_year"] <= current_year)]
    if "date_posted" in df.columns:
        df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
    df = df.sort_values(by="price", ascending=False).reset_index(drop=True)
    return df

car_data = load_and_clean_data()

# =====================
# ENCABEZADO
# =====================
st.title("🚗 Análisis de anuncios de venta de vehículos")
st.markdown("""
Este dashboard interactivo te permite explorar anuncios de venta de automóviles.
Se han limpiado los datos para mostrar únicamente información relevante y coherente.
Usa los filtros y gráficos para descubrir tendencias y relaciones entre precio, año y kilometraje.
""")

# =====================
# FILTRO DE FECHAS
# =====================
if "date_posted" in car_data.columns:
    st.subheader("📅 Filtrar por rango de fechas")
    start_date, end_date = st.date_input(
        "Selecciona el rango de fechas",
        [car_data["date_posted"].min(), car_data["date_posted"].max()]
    )

    if start_date and end_date:
        car_data = car_data[
            (car_data["date_posted"] >= pd.to_datetime(start_date)) &
            (car_data["date_posted"] <= pd.to_datetime(end_date))
        ]

# =====================
# VISTA DE TABLA
# =====================
st.subheader("Datos disponibles")
if st.checkbox("Mostrar tabla de datos completa"):
    st.dataframe(car_data, use_container_width=True)
else:
    st.dataframe(car_data.head(10), use_container_width=True)

# =====================
# HISTOGRAMA
# =====================
st.subheader("Distribución de precios (Dólares)")
hist_bins = st.slider("Número de bins del histograma", min_value=10, max_value=100, value=30)
fig_hist = px.histogram(
    car_data,
    x="price",
    nbins=hist_bins,
    title="Distribución de precios de vehículos",
    color_discrete_sequence=["#60a3bc"]
)
st.plotly_chart(fig_hist, use_container_width=True)

# =====================
# GRÁFICO DE DISPERSIÓN
# =====================
st.subheader("Relación entre odómetro y precio")
fig_scatter = px.scatter(
    car_data,
    x="odometer",
    y="price",
    color="model_year",
    title="Kilometraje vs Precio",
    color_continuous_scale=px.colors.sequential.Blues
)
st.plotly_chart(fig_scatter, use_container_width=True)

# =====================
# BOTÓN DE ACCIÓN
# =====================
if st.button("💡 Mostrar conclusión rápida"):
    st.success("Los vehículos más nuevos y con menor kilometraje tienden a tener precios más altos.")