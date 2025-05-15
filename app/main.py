from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.api import newsletters

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación FastAPI
app = FastAPI(
    title="Newsletter Inteligente API",
    description="API para generación y envío de newsletters personalizados usando agentes de OpenAI",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las orígenes en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas básicas
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Newsletter Inteligente"}

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Incluir routers de la API
app.include_router(newsletters.router, prefix="/api/newsletters", tags=["Newsletters"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 