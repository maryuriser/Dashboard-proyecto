from fastapi import FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi
import os

# ==========================================
# CARGAR VARIABLES DE ENTORNO
# ==========================================
load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_FOURSQUARE = os.getenv("MONGODB_DATABASE_FOURSQUARE") or "foursquare_scraping"
DB_GOOGLE = os.getenv("MONGODB_DATABASE_GOOGLE") or "Googlemaps_Scraping"

if not MONGO_URI:
    raise ValueError(" Falta la variable MONGODB_URI en el archivo .env")

# ==========================================
# CONEXIONES A MONGO
# ==========================================
client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
db_foursquare = client[DB_FOURSQUARE]
db_google = client[DB_GOOGLE]



# ==========================================
# CONFIGURACIÓN FASTAPI
# ==========================================
app = FastAPI(title="API Turismo - Foursquare & Google Maps", version="2.1")



# ==========================================
# ENDPOINT FOURSQUARE
# ==========================================

# SITIOS

@app.get("/foursquare/sities_clean")
async def get_foursquare_sities(departamento: str = Query(..., min_length=2)):
    """
    Devuelve los sitios de Foursquare filtrados por departamento.
    Incluye lat/lon y categoría 
    """
    try:
        filtro = {"departamento": {"$regex": departamento, "$options": "i"}}
        cursor = db_foursquare.sities_clean.find(
            filtro,
            {
                "_id": 0,
                "nombre": 1,
                "categoria": 1,
                "departamento": 1,
                "municipio": 1,
                "latitude": 1,
                "longitude": 1,
            },
        )
        sitios = await cursor.to_list(length=None)

        if not sitios:
            raise HTTPException(404, f"No hay sitios en {departamento}")

        return {
            "fuente": "Foursquare",
            "departamento": departamento,
            "total": len(sitios),
            "sitios": sitios,
        }

    except Exception as e:
        raise HTTPException(500, detail=str(e))
    

 # RESEñANTES

@app.get("/foursquare/reseñantes")
async def get_foursquare_reviewers(departamento: str = Query(..., min_length=2)):
    """
    Devuelve los reseñantes de Foursquare filtrados por departamento.
    Ideal para análisis de demanda turística.
    """
    try:
        filtro = {"departamento": {"$regex": departamento, "$options": "i"}}
        cursor = db_foursquare.reviewers.find(
            filtro,
            {
                "_id": 0,
                "nombre": 1,
                "municipio": 1,
                "departamento": 1
            }
        )
        reseñantes = await cursor.to_list(length=None)

        if not reseñantes:
            raise HTTPException(404, f"No se encontraron reseñantes en {departamento}")

        return {
            "fuente": "Foursquare",
            "departamento": departamento,
            "total": len(reseñantes),
            "reseñantes": reseñantes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   

# TIPS

@app.get("/foursquare/tips_expand")
async def get_foursquare_tips_expand(departamento: str = Query(..., min_length=2)):
    
    try:
        pipeline = [
            {
                "$match": {
                    "departamento": {"$regex": departamento, "$options": "i"}
                }
            },
            {"$unwind": "$tips"},  # Explota el array: un registro por tip
            {
                "$project": {
                    "_id": 0,
                    "user_id": 1,
                    "user_name": 1,
                    "user_location": 1,
                    "user_url": 1,
                    "municipio": 1,
                    "departamento": 1,
                    "fecha_actualizacion": 1,
                    "tip": "$tips",      # El tip individual
                    "tips_count": 1
                }
            }
        ]

        cursor = db_foursquare.tips.aggregate(pipeline)
        tips_list = await cursor.to_list(length=None)

        if not tips_list:
            raise HTTPException(
                404,
                f"No se encontraron tips en el departamento {departamento}"
            )

        return {
            "fuente": "Foursquare",
            "departamento": departamento,
            "total_tips": len(tips_list),
            "tips": tips_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# ENDPOINT GOOGLE MAPS
# ==========================================
@app.get("/google/sities")
async def get_google_sities(departamento: str = Query(..., min_length=2)):
    """
    Devuelve los sitios de Google Maps filtrados solo por departamento.
    Incluye puntuación y categoría.
    """
    try:
        filtro = {"departamento": {"$regex": departamento, "$options": "i"}}
        cursor = db_google.sities.find(
            filtro,
            {
                "_id": 0,
                "nombre": 1,
                "puntuacion": 1,
                "categoria": 1,
                "municipio": 1,
                "departamento": 1,
            },
        )
        sitios = await cursor.to_list(length=None)

        if not sitios:
            raise HTTPException(404, f"No hay sitios en {departamento}")

        return {
            "fuente": "Google Maps",
            "departamento": departamento,
            "total": len(sitios),
            "sitios": sitios,
        }

    except Exception as e:
        raise HTTPException(500, detail=str(e))
    


# ==========================================
# ENPONID PARA ARCHIVO EXCEL 
# ==========================================

# SITIOS 
@app.get("/foursquare/sities_full")
async def get_foursquare_sities_full(departamento: str = Query(..., min_length=2)):
    """
    Devuelve TODOS los campos de la colección sities_clean de Foursquare.
    Filtrado por departamento.
    """
    try:
        filtro = {"departamento": {"$regex": departamento, "$options": "i"}}
        
        cursor = db_foursquare.sities_clean.find(filtro, {"_id": 0})
        sitios = await cursor.to_list(length=None)

        if not sitios:
            raise HTTPException(404, f"No hay sitios en {departamento}")

        return {
            "fuente": "Foursquare",
            "departamento": departamento,
            "total": len(sitios),
            "sitios": sitios
        }

    except Exception as e:
        raise HTTPException(500, detail=str(e))



# SITIOS GM

@app.get("/google/sities_full")
async def get_google_sities_full(departamento: str = Query(..., min_length=2)):
    """
    Devuelve TODOS los campos de la colección sities de Google Maps.
    Filtrado por departamento.
    """
    try:
        filtro = {"departamento": {"$regex": departamento, "$options": "i"}}
        
        cursor = db_google.sities.find(filtro, {"_id": 0})
        sitios = await cursor.to_list(length=None)

        if not sitios:
            raise HTTPException(404, f"No hay sitios en {departamento}")

        return {
            "fuente": "Google Maps",
            "departamento": departamento,
            "total": len(sitios),
            "sitios": sitios
        }

    except Exception as e:
        raise HTTPException(500, detail=str(e))

# Reseñas  
@app.get("/foursquare/reseñantes_full")
async def get_foursquare_reviewers_full(departamento: str = Query(..., min_length=2)):
    """
    Devuelve TODOS los campos de la colección reviewers de Foursquare.
    Filtrado por departamento.
    """
    try:
        filtro = {"departamento": {"$regex": departamento, "$options": "i"}}

        # Traer todos los campos excepto el _id
        cursor = db_foursquare.reviewers.find(filtro, {"_id": 0})
        reseñantes = await cursor.to_list(length=None)

        if not reseñantes:
            raise HTTPException(404, f"No se encontraron reseñantes en {departamento}")

        return {
            "fuente": "Foursquare",
            "departamento": departamento,
            "total": len(reseñantes),
            "reseñantes": reseñantes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# ==========================================
# PING DE CONEXIÓN
# ==========================================
@app.get("/ping")
async def ping():
    try:
        await db_foursquare.command("ping")
        await db_google.command("ping")
        return {"status": "ok", "bases": [DB_FOURSQUARE, DB_GOOGLE]}
    except Exception as e:
        raise HTTPException(500, detail=f"Error de conexión: {e}")
