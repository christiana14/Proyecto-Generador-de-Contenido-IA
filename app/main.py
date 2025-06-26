from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import logging
from app.core.config import settings
from app.api.v1 import auth, generation
from app.core.database import engine
from app.models import user, generation as generation_model, api_key

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Crear tablas
user.Base.metadata.create_all(bind=engine)
generation_model.Base.metadata.create_all(bind=engine)
api_key.Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="Generador de contenido inteligente con sistema de monetización",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Incluir routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(generation.router, prefix="/api/v1", tags=["generation"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Página principal
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """
    Verificar estado de la aplicación
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": "1.0.0"
    }

@app.get("/api/v1/plans")
async def get_plans():
    """
    Obtener información de planes disponibles
    """
    return {
        "plans": [
            {
                "id": "free",
                "name": "Plan Gratuito",
                "price": 0,
                "monthly_generations": settings.free_plan_limit,
                "features": [
                    "10 generaciones por mes",
                    "Contenido básico",
                    "Soporte por email"
                ]
            },
            {
                "id": "pro",
                "name": "Plan Pro",
                "price": settings.pro_plan_price / 100,  # Convertir de centavos
                "monthly_generations": settings.pro_plan_limit,
                "features": [
                    "1000 generaciones por mes",
                    "Todos los tipos de contenido",
                    "API access",
                    "Analytics avanzados",
                    "Soporte prioritario"
                ]
            },
            {
                "id": "enterprise",
                "name": "Plan Enterprise",
                "price": settings.enterprise_plan_price / 100,  # Convertir de centavos
                "monthly_generations": settings.enterprise_plan_limit,
                "features": [
                    "Generaciones ilimitadas",
                    "Prioridad en cola",
                    "Soporte dedicado",
                    "White-label disponible",
                    "Integración personalizada"
                ]
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 