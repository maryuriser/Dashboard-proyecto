import httpx
import pandas as pd
from io import BytesIO

API_URL = "http://localhost:8000"  # Cambiar si tu API está en otro servidor


# ======================================================
# OBTENER DATOS COMPLETOS DESDE TUS ENDPOINTS REALES
# ======================================================
async def obtener_datos_completos(departamento: str):

    async with httpx.AsyncClient(timeout=40) as client:

        # --- ENDPOINTS QUE DEVUELVEN COMPLETO PARA EXCEL ---
        r_fs_sities = await client.get(f"{API_URL}/foursquare/sities_full?departamento={departamento}")
        r_gm_sities = await client.get(f"{API_URL}/google/sities_full?departamento={departamento}")
        r_fs_tips = await client.get(f"{API_URL}/foursquare/tips_expand?departamento={departamento}")
        r_fs_reviewers = await client.get(f"{API_URL}/foursquare/reseñantes_full?departamento={departamento}")


        # Convertir datos a DataFrames
        df_fs_sities = pd.DataFrame(r_fs_sities.json().get("sitios", []))
        df_gm_sities = pd.DataFrame(r_gm_sities.json().get("sitios", []))
        df_fs_tips = pd.DataFrame(r_fs_tips.json().get("tips", []))
        df_fs_reviewers = pd.DataFrame(r_fs_reviewers.json().get("reseñantes", []))

        return {
            "Foursquare_Sitios": df_fs_sities,
            "GoogleMaps_Sitios": df_gm_sities,
            "Foursquare_Tips": df_fs_tips,
            "Foursquare_Reseñantes": df_fs_reviewers
        }


# ======================================================
# CREAR EL ARCHIVO EXCEL CON MÚLTIPLES HOJAS
# ======================================================
def crear_excel(dataframes: dict) -> BytesIO:

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for sheet_name, df in dataframes.items():
            if not df.empty:
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            else:
                pd.DataFrame({"info": ["Sin datos"]}).to_excel(writer, sheet_name=sheet_name[:31], index=False)

    buffer.seek(0)
    return buffer
