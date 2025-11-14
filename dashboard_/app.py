import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ===============================
# CONFIGURACIÓN DE LA PÁGINA
# ===============================
st.set_page_config(page_title="Análisis Turístico", layout="wide")

# ====== ESTILOS PERSONALIZADOS ======
st.markdown("""
<style>

/* Fondo general */
[data-testid="stAppViewContainer"] {
    background-color: #f5f7fa;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2c3e50, #4b6584);
    color: white;
}
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] p {
    color: white !important;
    font-weight: 500;
}

/* Tarjetas (metric y contenedores) */
div[data-testid="stMetricValue"] {
    color: #2c3e50;
}
div[data-testid="stMetricLabel"] {
    color: #7f8c8d;
}

/* Encabezados principales */
h1, h2, h3 {
    color: #2c3e50;
    font-weight: 600;
}

/* Bordes y cajas */
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

/* Gráficos y contenedores */
[data-testid="stPlotlyChart"] {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    padding: 15px;
}

/* Tarjetas personalizadas (para métricas principales) */
.card {
    background-color: white;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    padding: 25px;
    text-align: center;
    transition: transform 0.2s ease;
}
.card:hover {
    transform: translateY(-3px);
}
.card h4 {
    color: #7f8c8d;
    margin-bottom: 5px;
}
.card p {
    font-size: 22px;
    font-weight: 600;
    color: #2c3e50;
}

/* Separadores suaves */
hr {
    border: none;
    height: 1px;
    background-color: #ddd;
    margin: 25px 0;
}

/* Botones */
button[kind="primary"] {
    background: linear-gradient(90deg, #2980b9, #6dd5fa);
    color: white !important;
    border: none;
}
button[kind="primary"]:hover {
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# TÍTULO PRINCIPAL
# ===============================
st.markdown("""
# **Análisis Turístico**
Visualiza la distribución de sitios turísticos y la demanda por municipio.
""")

BASE_URL = "http://127.0.0.1:8000"

# ===============================
# FUNCIONES DE CONSULTA
# ===============================
def obtener_sitios(dep):
    if not dep:
        return pd.DataFrame()
    try:
        resp = requests.get(f"{BASE_URL}/foursquare/sities_clean?departamento={dep}", timeout=10)
        resp.raise_for_status()
        return pd.DataFrame(resp.json().get("sitios", []))
    except:
        return pd.DataFrame()

def obtener_reseñantes(dep):
    if not dep:
        return pd.DataFrame()
    try:
        resp = requests.get(f"{BASE_URL}/foursquare/reseñantes?departamento={dep}", timeout=10)
        resp.raise_for_status()
        return pd.DataFrame(resp.json().get("reseñantes", []))
    except:
        return pd.DataFrame()

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.header("Departamento")

    departamentos_caribe = [
        "Atlántico", "Bolívar", "Córdoba", "Sucre",
        "Magdalena", "La Guajira", "Cesar", "San Andrés "
    ]

    departamento = st.radio(
        "Selecciona un departamento:",
        options=departamentos_caribe,
        index=None,
        horizontal=False
    )

# ===============================
# CUERPO PRINCIPAL
# ===============================
if departamento:
    df_sities = obtener_sitios(departamento)
    df_reviewers = obtener_reseñantes(departamento)

    if df_sities.empty:
        st.warning("No se encontraron sitios para este departamento.")
    else:
        df_sities = df_sities.dropna(subset=["latitude", "longitude"])
        df_sities["num_sitios"] = 1

        total_sitios = len(df_sities)
        total_reseñantes = len(df_reviewers)
        total_categorias = df_sities["categoria"].nunique() if "categoria" in df_sities.columns else 0

        # ===============================
        # TARJETAS DE INDICADORES
        # ===============================
        st.markdown("### 🔹 Indicadores Generales")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown(f"""
            <div class="card">
                <h4>Total de Sitios</h4>
                <p>{total_sitios:,}</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="card">
                <h4>Total de Reseñantes</h4>
                <p>{total_reseñantes:,}</p>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="card">
                <h4>Categorías</h4>
                <p>{total_categorias:,}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ===============================
        # LAYOUT PRINCIPAL (Mapa + Top Categorías)
        # ===============================
        col1, col2 = st.columns([2.8, 1.0])

        # --- Mapa de calor
        with col1:
            fig_map = px.density_map(
                df_sities,
                lat="latitude",
                lon="longitude",
                z="num_sitios",
                radius=18,
                hover_name="nombre",
                hover_data={"categoria": True, "num_sitios": True},
                color_continuous_scale="rainbow",
                title=f"Mapa de Calor - {departamento}",
                height=500
            )
            fig_map.update_layout(
                margin=dict(l=0, r=0, t=40, b=0),
                coloraxis_colorbar=dict(title=dict(text="Sitios", side="right")),
            )
            st.plotly_chart(fig_map, width="stretch")

        # --- Top Categorías 
        with col2:
            if "categoria" in df_sities.columns:
                df_top = (
                    df_sities.groupby("categoria")
                    .size()
                    .reset_index(name="cantidad")
                    .sort_values("cantidad", ascending=False)
                    .head(10)
                )

                colors = [
                    "#00B3A4", "#F39C12", "#E74C3C", "#9B59B6", "#3498DB",
                    "#1ABC9C", "#2ECC71", "#E67E22", "#16A085", "#7F8C8D"
                ]

                st.markdown("""
                    <h5 style="text-align:center; color:#333; margin-bottom:15px; font-weight:600;">
                        Top Categorías
                    </h5>
                """, unsafe_allow_html=True)

                max_val = df_top["cantidad"].max()
                for i, row in enumerate(df_top.itertuples(), start=0):
                    color = colors[i % len(colors)]
                    width = (row.cantidad / max_val) * 100
                    st.markdown(
                        f"""
                        <div style="display:flex; align-items:center; margin-bottom:6px;">
                            <div style="flex:1; text-align:left; font-size:13px; color:#333;">{row.categoria}</div>
                            <div style="flex:3; height:14px; background-color:#f2f2f2; border-radius:6px; position:relative;">
                                <div style="width:{width}%; height:100%; background-color:{color}; border-radius:6px;"></div>
                            </div>
                            <div style="width:40px; text-align:right; font-size:13px; color:#333;">{row.cantidad}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No hay datos de categorías para este departamento.")

        # ===============================
        # GRÁFICAS INFERIORES
        # ===============================
        st.markdown("---")
        st.markdown(f"###  Demanda Turística y Puntuación Promedio - {departamento}")

        col3, col4 = st.columns(2)

        # --- Demanda Turística
        with col3:
            if df_reviewers.empty:
                st.warning("No se encontraron reseñantes para este departamento.")
            else:
                df_count = df_reviewers.groupby("municipio").size().reset_index(name="Número de Reseñantes")
                df_count = df_count.sort_values("Número de Reseñantes", ascending=False)

                fig_demand = px.bar(
                    df_count,
                    x="municipio",
                    y="Número de Reseñantes",
                    color="municipio",
                    text="Número de Reseñantes",
                    height=450,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )

                fig_demand.update_traces(textposition="outside", textfont_size=12)
                fig_demand.update_layout(
                    xaxis_title="",
                    yaxis_title="Número de Reseñantes",
                    xaxis_tickangle=-45,
                    xaxis=dict(showticklabels=False),
                    legend_title="Municipio",
                    margin=dict(l=20, r=20, t=50, b=80),
                    plot_bgcolor="white"
                )
                st.plotly_chart(fig_demand, width="stretch")

        # --- Promedio Puntuación
        with col4:
            try:
                resp = requests.get(f"{BASE_URL}/google/sities_puntuacion?departamento={departamento}", timeout=10)
                if resp.status_code == 200:
                    data_google = resp.json().get("sitios", [])
                    df_google = pd.DataFrame(data_google)

                    if not df_google.empty:
                        df_promedio = (
                            df_google.groupby(["municipio", "categoria"])["puntuacion"]
                            .mean()
                            .reset_index()
                        )

                        fig_puntuacion = px.bar(
                            df_promedio,
                            y="municipio",
                            x="puntuacion",
                            color="categoria",
                            orientation="h",
                            barmode="stack",
                            text_auto=".2f",
                            color_discrete_sequence=px.colors.qualitative.Set2
                        )

                        fig_puntuacion.update_layout(
                            xaxis_title="Promedio de Puntuación",
                            yaxis_title=None,
                            legend_title="Categoría",
                            plot_bgcolor="white",
                            paper_bgcolor="white",
                            bargap=0.2,
                            margin=dict(l=40, r=40, t=20, b=60),
                            xaxis=dict(showgrid=True, zeroline=False),
                            yaxis=dict(showgrid=False),
                            title=None
                        )

                        fig_puntuacion.update_yaxes(showticklabels=True)
                        st.plotly_chart(fig_puntuacion, width="stretch")

                    else:
                        st.info("No se encontraron sitios en Google Maps para este departamento.")
                else:
                    st.error(f"Error al obtener datos de Google Maps ({resp.status_code})")
            except Exception as e:
                st.error(f"Error al conectar con el endpoint: {e}")
