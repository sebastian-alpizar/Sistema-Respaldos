# app/core/database_init.py
import asyncio
import logging
from app.core.database import engine, Base
from app.models.database_models import UserModel, StrategyModel, LogModel

logger = logging.getLogger(__name__)

async def create_tables():
    """Crear todas las tablas en la base de datos"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tablas creadas exitosamente en la base de datos")
        return True
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {str(e)}")
        return False

async def drop_tables():
    """Eliminar todas las tablas (solo para desarrollo)"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("🗑️ Tablas eliminadas exitosamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error eliminando tablas: {str(e)}")
        return False

if __name__ == "__main__":
    # Ejecutar para crear tablas
    asyncio.run(create_tables())