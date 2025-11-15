import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS




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
/* Tarjetas */
div[data-testid="stMetricValue"] { color: #2c3e50; }
div[data-testid="stMetricLabel"] { color: #7f8c8d; }
/* Encabezados */
h1, h2, h3 {
    color: #2c3e50;
    font-weight: 600;
}
/* Gráficos */
[data-testid="stPlotlyChart"] {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    padding: 15px;
}
/* Card métrica */
.card {
    background-color: white;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    padding: 25px;
    text-align: center;
    transition: transform 0.2s ease;
}
.card:hover { transform: translateY(-3px); }
.card h4 { color: #7f8c8d; margin-bottom: 5px; }
.card p { font-size: 22px; font-weight: 600; color: #2c3e50; }
/* Separador */
hr {
    border: none;
    height: 1px;
    background-color: #ddd;
    margin: 25px 0;
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
# FUNCIONES DE CONSULTA (TODAS AQUÍ)
# ===============================

def obtener_sitios(dep):
    try:
        resp = requests.get(f"{BASE_URL}/foursquare/sities_clean?departamento={dep}", timeout=10)
        resp.raise_for_status()
        return pd.DataFrame(resp.json().get("sitios", []))
    except:
        return pd.DataFrame()

def obtener_reseñantes(dep):
    try:
        resp = requests.get(f"{BASE_URL}/foursquare/reseñantes?departamento={dep}", timeout=10)
        resp.raise_for_status()
        return pd.DataFrame(resp.json().get("reseñantes", []))
    except:
        return pd.DataFrame()

def obtener_tips(dep):
    try:
        resp = requests.get(f"{BASE_URL}/foursquare/tips_expand?departamento={dep}", timeout=10)
        resp.raise_for_status()
        return pd.DataFrame(resp.json().get("tips", []))
    except:
        return pd.DataFrame()

def obtener_google_sities_puntuacion(dep):
    try:
        resp = requests.get(f"{BASE_URL}/google/sities?departamento={dep}", timeout=10)
        resp.raise_for_status()
        return pd.DataFrame(resp.json().get("sitios", []))
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
        "Seleccione un departamento:",
        options=departamentos_caribe,
        index=None
    )

# ===============================
# CUERPO PRINCIPAL
# ===============================
if departamento:
    df_sities = obtener_sitios(departamento)
    df_reviewers = obtener_reseñantes(departamento)
    df_tips = obtener_tips(departamento)
    df_google = obtener_google_sities_puntuacion(departamento)  

    if df_sities.empty:
        st.warning("No se encontraron sitios para este departamento.")
    else:

        # TARJETAS PRINCIPALES
        st.markdown("### 🔹 Indicadores Generales")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"""
            <div class="card">
                <h4>Total de Sitios</h4>
                <p>{len(df_sities):,}</p>
            </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="card">
                <h4>Total de Reseñantes</h4>
                <p>{len(df_reviewers):,}</p>
            </div>""", unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="card">
                <h4>Total de Tips</h4>
                <p>{len(df_tips):,}</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ===============================
        # MAPA + CATEGORÍAS
        # ===============================
        col1, col2 = st.columns([2.8, 1.0])

        # ------------ MAPA ------------
        with col1:
            df_sities = df_sities.dropna(subset=["latitude", "longitude"])
            df_grouped = (
                df_sities
                .groupby(["latitude", "longitude"])
                .agg(
                    categorias_list=("categoria", lambda x: "<br>".join(sorted(set(x)))),
                    num_sitios=("nombre", "count")
                )
                .reset_index()
            )

            fig_map = px.density_map(
                df_grouped,
                lat="latitude",
                lon="longitude",
                z="num_sitios",
                radius=18,
                hover_name="num_sitios",
                hover_data={"categorias_list": True},
                color_continuous_scale="rainbow",
                title=f"Mapa de Calor - {departamento}",
                height=500
            )

            fig_map.update_layout(
                margin=dict(l=0, r=0, t=40, b=0),
                coloraxis_colorbar=dict(
                    title=dict(text="Cantidad de sitios", side="right")
                ),
            )

            st.plotly_chart(fig_map, width="stretch")

        # ------------ CATEGORÍAS ------------
        with col2:
            st.markdown("""
                <h5 style="text-align:center; color:#333; margin-bottom:15px; font-weight:600;">
                    Categorías de Sitios
                </h5>
            """, unsafe_allow_html=True)

            trad = {
                "Food and Services": "Comida y Servicios",
                "Entertainment": "Entretenimiento",
                "Heritage": "Patrimonio",
                "Cultural buildings": "Edificios Culturales",
                "Nature": "Naturaleza",
                "Other": "Otros",
                "Viewpoints": "Miradores"
            }
            df_sities["categoria"] = df_sities["categoria"].replace(trad)

            df_top = (
                df_sities.groupby("categoria")
                .size()
                .reset_index(name="cantidad")
                .sort_values("cantidad", ascending=False)
            )

            colors = [
                "#00B3A4", "#F39C12", "#E74C3C", "#9B59B6", "#3498DB",
                "#1ABC9C", "#2ECC71", "#E67E22", "#16A085", "#7F8C8D"
            ]

            max_val = df_top["cantidad"].max()
            for i, row in enumerate(df_top.itertuples(), start=0):
                st.markdown(f"""
                <div style="display:flex; align-items:center; margin-bottom:6px;">
                    <div style="flex:1; font-size:13px;">{row.categoria}</div>
                    <div style="flex:3; height:14px; background:#f2f2f2; border-radius:6px;">
                        <div style="width:{(row.cantidad/max_val)*100}%; height:100%; background:{colors[i%len(colors)]}; border-radius:6px;"></div>
                    </div>
                    <div style="width:40px; text-align:right; font-size:13px;">{row.cantidad}</div>
                </div>
                """, unsafe_allow_html=True)

        # ===============================
        # DEMANDA + PUNTUACIÓN
        # ===============================
        st.markdown("---")
        st.markdown(f"###  Demanda Turística y Puntuación Promedio - {departamento}")

        col3, col4 = st.columns(2)

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


        # ------------ PROMEDIO DE PUNTUACIÓN ------------
        with col4:
            try:
                data_google = obtener_google_sities_puntuacion(departamento)

                df_google = pd.DataFrame(data_google)

                if not df_google.empty:

                    # --- Agrupación ---
                    df_promedio = (
                        df_google.groupby(["municipio", "categoria"])["puntuacion"]
                        .mean()
                        .reset_index()
                    )

                    # --- GRÁFICO ---
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
                    )

                    fig_puntuacion.update_yaxes(showticklabels=True)
                    st.plotly_chart(fig_puntuacion, width="stretch")

                else:
                    st.info("No se encontraron sitios en Google Maps para este departamento.")

            except Exception as e:
                st.error(f"Error al obtener datos: {e}")



        # ===============================
        # NUBE DE PALABRAS + LÍNEA TEMPORAL
        # ===============================
        st.markdown("---")
        st.markdown(f"###  Análisis de Reseñas - {departamento}")

        if df_tips.empty:
            st.info("No hay tips en Foursquare.")
        else:
            df_tips["comment"] = df_tips["tip"].apply(lambda t: t.get("comment", ""))

            texto_tips = " ".join(df_tips["comment"]).replace('"', "")
            stopwords_es = STOPWORDS.union({
                "el", "la", "los", "las", "un", "una", "unos", "unas", "yo",
                "que", "de", "del", "al", "y", "o", "a", "en", "es"
            })

            col_wc, col_time = st.columns([1, 1])

            # ----------- NUBE ----------- 
            with col_wc:
                if len(texto_tips.split()) < 3:
                    st.info("No hay suficientes palabras.")
                else:
                    fig_wc, ax_wc = plt.subplots(figsize=(10, 7), dpi=150)
                    wc = WordCloud(
                        width=2000, height=1600,
                        background_color="white",
                        stopwords=stopwords_es
                    ).generate(texto_tips)

                    ax_wc.imshow(wc, interpolation="bilinear")
                    ax_wc.axis("off")
                    st.pyplot(fig_wc)

            # ----------- LÍNEA TEMPORAL ----------- 
            with col_time:
                meses_map = {
                    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
                    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
                    "Septiembre": 9, "Setiembre": 9, "Octubre": 10,
                    "Noviembre": 11, "Diciembre": 12
                }

                df_tips["mes"] = df_tips["tip"].apply(
                    lambda t: meses_map.get(t.get("date", "").split()[0], None)
                )

                df_mes = df_tips.dropna(subset=["mes"]) \
                                .groupby("mes") \
                                .size() \
                                .reset_index(name="total_tips")

                fig_linea = px.line(
                    df_mes, x="mes", y="total_tips", markers=True
                )

                fig_linea.update_traces(
                    fill='tozeroy',
                    fillcolor='rgba(0,123,255,0.2)',
                    line=dict(width=3, color='rgba(0,123,255,1)')
                )

                fig_linea.update_layout(
                    xaxis=dict(
                        tickmode="array",
                        tickvals=list(range(1, 13)),
                        ticktext=["Ene","Feb","Mar","Abr","May","Jun",
                                "Jul","Ago","Sep","Oct","Nov","Dic"]
                    ),
                    yaxis_title="Cantidad de Tips",
                    plot_bgcolor="white"
                )

                st.plotly_chart(fig_linea, width="stretch")
