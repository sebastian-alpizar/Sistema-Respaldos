# main.py - VERSIÓN CORREGIDA
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from app.core.config import settings
from app.core.scheduler import BackupScheduler
from app.core.database import AsyncSessionLocal

# Configurar logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Inicializar servicios globales
scheduler = BackupScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando Sistema de Gestión de Respaldo Oracle...")
    
    # Iniciar programador
    scheduler.start()
    logger.info("✅ Programador iniciado")
    
    # Cargar y programar estrategias activas
    try:
        async with AsyncSessionLocal() as db:
            from app.repositories.strategy_repo import StrategyRepository
            strategy_repo = StrategyRepository(db)
            strategies = await strategy_repo.get_active_strategies()
            
            if strategies:
                scheduler.reschedule_all_strategies(strategies)
                logger.info(f"✅ Estrategias activas programadas: {len(strategies)}")
            else:
                logger.info("ℹ️ No hay estrategias activas para programar")
                
    except Exception as e:
        logger.warning(f"⚠️ No se pudieron cargar estrategias: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Deteniendo Sistema de Gestión de Respaldo Oracle...")
    scheduler.shutdown()
    logger.info("✅ Programador detenido")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_TITLE or "Sistema de Respaldo Oracle",
    version=settings.APP_VERSION or "1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ IMPORTAR routers DESPUÉS de crear la app
from app.api.routes_backup import router as backup_router
from app.api.routes_logs import router as logs_router
from app.api.routes_system import router as system_router

# ✅ CORREGIR los prefijos para que coincidan con lo que intentas acceder
app.include_router(system_router)
app.include_router(backup_router)
app.include_router(logs_router)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Sistema de Gestión de Respaldo Oracle",
        "version": settings.APP_VERSION or "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "backup": "/backup",
            "logs": "/logs",
            "system": "/system"
        }
    }

@app.get("/health")
async def health():
    """Endpoint de salud"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Oracle Backup System"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )