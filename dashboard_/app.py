import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from exporter import obtener_datos_completos, crear_excel
import asyncio
import streamlit.components.v1 as components
import calendar
import plotly.graph_objects as go
import numpy as np

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
.card p {
    font-size: 42px !important;
    font-weight: 800 !important;
    color: #2c3e50 !important;
    margin-top: 15px;
    line-height: 1.1;
}
.card h4 {
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #6b6b6b !important;
}
/* Separador */
hr {
    border: none;
    height: 1px;
    background-color: #ddd;
    margin: 25px 0;
}

/* Separador */
hr {
    border: none;
    height: 1px;
    background-color: #ddd;
    margin: 25px 0;
}

/* ========================= */
/* BOTONES PERSONALIZADOS   */
/* ========================= */

/* Botón normal (Generar Excel) */
div.stButton > button {
    background-color: #1E88E5 !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 0.6rem 1rem !important;
    border: none !important;
    font-weight: 600 !important;
    width: 100% !important;
}

/* Hover */
div.stButton > button:hover {
    background-color: #1565C0 !important;
}

/* Botón de descarga */
.stDownloadButton > button {
    background-color: #43A047 !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 0.6rem 1rem !important;
    border: none !important;
    font-weight: 600 !important;
    width: 100% !important;
}

/* Hover */
.stDownloadButton > button:hover {
    background-color: #2E7D32 !important;
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
# DESCARGA DE EXCEL COMPLETO
# ===============================
if departamento:
    st.sidebar.markdown("---")
    st.sidebar.subheader(" Exportar datos completos")

    # Botón que genera el archivo Excel
    if st.sidebar.button("Generar archivo Excel"):
        with st.spinner("Generando archivo Excel..."):

            # Llamar los 4 endpoints completos
            dataframes = asyncio.run(obtener_datos_completos(departamento))

            # Crear el archivo Excel con varias hojas
            excel_file = crear_excel(dataframes)

        st.sidebar.success("Archivo Excel listo para descargar ✔️")

        # Botón de descarga
        st.sidebar.download_button(
            label="⬇ Descargar Archivo",
            data=excel_file,
            file_name=f"Datos_Completos_{departamento}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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
        st.markdown("###  Indicadores Generales")

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
        # título
            st.markdown("""
                <h5 style="text-align:center; color:#333; margin-bottom:12px; font-weight:600;">
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

            # Si no hay datos, mostrar mensaje
            if df_top.empty:
                st.info("No hay categorías para mostrar.")
            else:

                # ===== COLORES SEGÚN POSICIÓN (mayor = rojo) =====
                escala_ordenada = [
                    "#FF0000",  # Rojo
                    "#FF6600",  # Naranja
                    "#FFCC00",  # Amarillo
                    "#66CC00",  # Verde
                    "#0099FF",  # Azul
                    "#6633CC",  # Morado
                    "#999999"   # Gris
                ]

                df_top["color"] = [
                    escala_ordenada[i % len(escala_ordenada)]
                    for i in range(len(df_top))
                ]

                max_val = int(df_top["cantidad"].max())

                # Construcción del HTML
                rows_html = ""
                for row in df_top.itertuples():
                    pct = (row.cantidad / max_val) * 100 if max_val > 0 else 0

                    rows_html += f"""
                    <div style="margin-bottom:14px;">
                        <div style="font-size:13px; font-weight:600; color:#444; margin-bottom:6px;">
                            {row.categoria}
                        </div>
                        <div style="display:flex; align-items:center;">
                            <div style="flex:1; height:16px; background:#f2f2f2; border-radius:8px; margin-right:10px; overflow:hidden;">
                                <div style="width:{pct}%; height:100%; background:{row.color}; border-radius:8px;"></div>
                            </div>
                            <div style="width:44px; text-align:right; font-size:13px; font-weight:600; color:#333;">
                                {row.cantidad}
                            </div>
                        </div>
                    </div>
                    """

                card_html = f"""
                <div style="
                    background:white;
                    padding:14px;
                    border-radius:12px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.08);
                    font-family: Roboto, Arial, sans-serif;
                ">
                    {rows_html}
                </div>
                """

                height = min(600, 60 + len(df_top) * 62)
                components.html(card_html, height=height, scrolling=False)

# -----------------------------------------------------------------

        # ===============================
        # DEMANDA + PUNTUACIÓN
        # ===============================
        st.markdown("---")
        st.markdown(f"###  Distribución de visitantes y Calificaciones - {departamento}")

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

                # -----------------------------
                # 🔥 AQUÍ SE AGREGA LO IMPORTANTE
                fig_demand.update_yaxes(type="log")
                # -----------------------------

                fig_demand.update_layout(
                    xaxis_title="",
                    yaxis_title="Número de Reseñantes",
                    xaxis_tickangle=-45,
                    xaxis=dict(showticklabels=False),
                    legend_title="Municipio",
                    margin=dict(l=20, r=20, t=50, b=80),
                    plot_bgcolor="white"
                )
                st.plotly_chart(fig_demand, use_container_width=True)


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

                    # Ordenar de menor a mayor (para barras horizontales)
                    df_promedio = df_promedio.sort_values("puntuacion", ascending=True)

                    # Categorías únicas
                    categorias = df_promedio["categoria"].unique().tolist()
                    paleta_set2 = px.colors.qualitative.Set2[:len(categorias)]
                    color_map = {cat: col for cat, col in zip(categorias, paleta_set2)}

                    # --- GRÁFICO ---
                    fig_puntuacion = px.bar(
                        df_promedio,
                        y="municipio",
                        x="puntuacion",
                        color="categoria",
                        orientation="h",
                        barmode="stack",
                        text=None,
                        height=450,
                        color_discrete_map=color_map
                    )

                    # ✔ OCULTAR TODAS LAS CATEGORÍAS MENOS LA PRIMERA
                    primera_categoria = categorias[0]

                    for trace in fig_puntuacion.data:
                        if trace.name != primera_categoria:
                            trace.visible = "legendonly"

                    fig_puntuacion.update_layout(
                        title=dict(
                            text=" Promedio de puntuación por municipio",
                            x=0.03,
                            y=0.98,
                            font=dict(size=18, color="#2c3e50")
                        ),
                        xaxis_title="Promedio de Puntuación",
                        yaxis_title=None,
                        legend_title="Categoría",
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                        bargap=0.55,       
                        bargroupgap=0.35,   
                        margin=dict(l=40, r=40, t=70, b=40),
                        xaxis=dict(showgrid=True, gridcolor="rgba(200,200,200,0.3)"),
                        yaxis=dict(showgrid=False),
                    )

                    # ✔ REMOVE TEXT ON BARS — only show on hover
                    fig_puntuacion.update_traces(
                        hovertemplate="<b>%{y}</b><br>Puntuación promedio: %{x:.2f}<extra></extra>"
                    )

                    st.plotly_chart(fig_puntuacion, use_container_width=True)

                else:
                    st.info("No se encontraron sitios en Google Maps para este departamento.")

            except Exception as e:
                st.error(f"Error al obtener datos: {e}")



        # ===============================
        # NUBE DE PALABRAS + LÍNEA TEMPORAL
        # ===============================
        st.markdown("---")
        st.markdown(f"###  Explorador de Opiniones y Actividad Turística  - {departamento}")

        # ============================================================
        #               VALIDACIÓN Y PROCESO DE TIPS
        # ============================================================
        if df_tips.empty:
            st.info("No hay tips en Foursquare.")
            texto_tips = ""
        else:
            df_tips["comment"] = df_tips["tip"].apply(lambda t: t.get("comment", ""))

            texto_tips = " ".join(df_tips["comment"]).replace('"', "")
            stopwords_es = STOPWORDS.union({
                "el", "la", "los", "las", "un", "una", "unos", "unas", "yo",
                "que", "de", "del", "al", "y", "o", "a", "en", "es", "Con", "con"
            })

            # ===== Crear columna MES numérica =====
            meses_map = {
                "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
                "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
                "Septiembre": 9, "Setiembre": 9, "Octubre": 10,
                "Noviembre": 11, "Diciembre": 12
            }

            df_tips["mes"] = df_tips["tip"].apply(
                lambda t: meses_map.get(t.get("date", "").split()[0], None)
            )

            # ===== Agrupar =====
            df_mes = df_tips.dropna(subset=["mes"]) \
                            .groupby("mes") \
                            .size() \
                            .reset_index(name="total_tips")

        # ============================================================
        #         ASEGURAR df_mes PARA EVITAR NameError SI NO EXISTE
        # ============================================================
        if "df_mes" not in locals() and "df_mes" not in globals():
            df_mes = pd.DataFrame(columns=["mes", "total_tips"])

        # ============================================================
        #                    CREAR NOMBRE DEL MES
        # ============================================================
        if df_mes.empty:
            st.warning("No hay actividad temporal.")
            df_mes = pd.DataFrame({"mes": [], "total_tips": [], "mes_nombre": []})
        else:
            df_mes["mes_nombre"] = df_mes["mes"].astype(int).apply(
                lambda m: calendar.month_name[m].capitalize() if 1 <= m <= 12 else "Desconocido"
            )

        # ============================================================
        #                     DISEÑO DE COLUMNAS
        # ============================================================
        col_wc, col_time = st.columns([1, 1])

        # Tamaño estandarizado de ambas (grandes)
        WC_WIDTH  = 7      # pulgadas (matplotlib)
        WC_HEIGHT = 5
        LINE_WIDTH = 750   # px (plotly)
        LINE_HEIGHT = 450  # px

        paleta_set2 = px.colors.qualitative.Set2
        paleta_wc = paleta_set2  # Para WordCloud y línea temporal

        # ============================================================
        #                        NUBE DE PALABRAS
        # ============================================================
        with col_wc:
           

            if len(texto_tips.split()) < 3:
                st.info("No hay suficientes palabras para generar una nube.")
            else:
                fig_wc, ax_wc = plt.subplots(figsize=(9, 6), dpi=100)
                def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
                    return np.random.choice(paleta_wc)

                wc = WordCloud(
                    width=2500, height=1800,
                    background_color="white",
                    stopwords=stopwords_es
                ).generate(texto_tips)

                ax_wc.imshow(wc, interpolation="bilinear")
                ax_wc.axis("off")

                st.pyplot(fig_wc)

        # ============================================================
        #                        LÍNEA TEMPORAL
        # ============================================================
        with col_time:
            
            if df_mes.empty:
                st.info("No hay datos para mostrar la actividad temporal.")
            else:
                # Valores
                x_vals = list(range(1, len(df_mes)+1))  # 1,2,3,...
                y_vals = df_mes["total_tips"].tolist()
                hover_texts = df_mes["mes_nombre"].tolist()

                fig_linea = px.line(
                    x=x_vals,
                    y=y_vals,
                    markers=True,
                    height=450,
                    width=750,
                    labels={"x":"Número de mes", "y":"Cantidad de Tips"},
                    hover_name=hover_texts
                )
                color_linea = paleta_wc[0]
                # Mejorar hover para que muestre el mes
                fig_linea.update_traces(
                    hovertemplate="<b>%{hovertext}</b><br>Cantidad de Tips: %{y}<extra></extra>",
                    hovertext=hover_texts,
                    line=dict(width=3, color='rgba(0,123,255,1)'),
                    fill='tozeroy',
                    fillcolor='rgba(0,123,255,0.1)'
                )

                fig_linea.update_layout(
                    xaxis=dict(tickmode='array', tickvals=x_vals, ticktext=x_vals),
                    plot_bgcolor="white",
                    margin=dict(l=50, r=50, t=30, b=50)
                    )

                st.plotly_chart(fig_linea, use_container_width=False, config={"responsive": False})