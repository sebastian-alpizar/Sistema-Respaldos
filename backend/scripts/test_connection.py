# test_connection.py
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import AsyncSessionLocal
from app.utils.oracle_connection import OracleConnection

async def test_database_connection():
    print("🔍 Probando conexión a la base de datos...")
    
    # Probar conexión SQLAlchemy
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute("SELECT 1 FROM DUAL")
            value = result.scalar()
            print(f"✅ Conexión SQLAlchemy: OK (resultado: {value})")
    except Exception as e:
        print(f"❌ Error SQLAlchemy: {e}")
        return False
    
    # Probar conexión Oracle directa
    try:
        oracle_conn = OracleConnection()
        info = oracle_conn.get_database_info()
        print(f"✅ Conexión Oracle directa: OK")
        print(f"   Base de datos: {info.get('name', 'N/A')}")
        print(f"   Versión: {info.get('version', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Error conexión Oracle: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_database_connection())