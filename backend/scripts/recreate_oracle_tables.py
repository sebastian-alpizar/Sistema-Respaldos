# scripts/recreate_oracle_tables.py
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models.database_models import UserModel, StrategyModel, LogModel

async def recreate_tables():
    print("🗑️ Eliminando tablas existentes...")
    try:
        async with engine.begin() as conn:
            # Eliminar en orden correcto (por dependencias de FK)
            await conn.run_sync(Base.metadata.drop_all)
        print("✅ Tablas eliminadas")
    except Exception as e:
        print(f"⚠️ Error eliminando tablas: {e}")

    print("🔄 Creando tablas con sequences...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tablas creadas con sequences")
        
        # Verificar sequences creadas
        async with engine.connect() as conn:
            from sqlalchemy import text
            result = await conn.execute(text("""
                SELECT sequence_name 
                FROM user_sequences 
                WHERE sequence_name LIKE 'BACKUP_%'
            """))
            sequences = [row[0] for row in result]
            print(f"🔢 Sequences creadas: {sequences}")
            
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")

if __name__ == "__main__":
    asyncio.run(recreate_tables())