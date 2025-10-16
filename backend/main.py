from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.core.config import settings
from app.core.scheduler import BackupScheduler
from app.repositories.strategy_repo import StrategyRepository
from app.api.routes_backup import router as backup_router
from app.api.routes_logs import router as logs_router
from app.api.routes_system import router as system_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Inicializar servicios globales
scheduler = BackupScheduler()
strategy_repo = StrategyRepository()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando Sistema de Gestión de Respaldo Oracle...")
    
    # Iniciar programador
    scheduler.start()
    logger.info("Programador iniciado")
    
    # Cargar y programar estrategias activas
    try:
        strategies = await strategy_repo.get_active_strategies()
        scheduler.reschedule_all_strategies(strategies)
        logger.info(f"Estrategias activas programadas: {len(strategies)}")
    except Exception as e:
        logger.error(f"Error programando estrategias al iniciar: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Deteniendo Sistema de Gestión de Respaldo Oracle...")
    scheduler.shutdown()
    logger.info("Programador detenido")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(backup_router)
app.include_router(logs_router)
app.include_router(system_router)

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Sistema de Gestión de Respaldo Oracle",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/system/health"
    }

@app.get("/health")
async def health():
    """Endpoint de salud simple"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )