# backend/check_tables.py
import asyncio
import sys
import os

# === Agregar el directorio raíz del proyecto (backend) al sys.path ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine
from app.core.config import settings
from sqlalchemy import text

async def check_created_tables():
    """Verificar las tablas creadas en la base de datos"""
    try:
        print(f"🔗 Conectando a: {settings.ORACLE_DSN}")
        print(f"👤 Usuario: {settings.ORACLE_USER}")
        
        async with engine.connect() as conn:
            # Consulta para obtener todas las tablas del usuario
            result = await conn.execute(text("""
                SELECT table_name, tablespace_name 
                FROM user_tables 
                WHERE table_name LIKE 'BACKUP_%'
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            
            print("📋 TABLAS CREADAS:")
            
            if tables:
                for table in tables:
                    print(f"   ✅ {table[0]} (Tablespace: {table[1]})")
            else:
                print("   ❌ No se encontraron tablas")
                
            return tables
            
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return []

if __name__ == "__main__":
    asyncio.run(check_created_tables())