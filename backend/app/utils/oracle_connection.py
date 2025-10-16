import cx_Oracle
from typing import Optional, Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class OracleConnection:
    _connection = None
    
    @classmethod
    def get_connection(cls):
        """Obtiene una conexión a la base de datos Oracle"""
        if cls._connection is None:
            try:
                dsn = cx_Oracle.makedsn(
                    settings.ORACLE_DSN.split(':')[0],
                    int(settings.ORACLE_DSN.split(':')[1].split('/')[0]),
                    service_name=settings.ORACLE_DSN.split('/')[1]
                )
                cls._connection = cx_Oracle.connect(
                    user=settings.ORACLE_USER,
                    password=settings.ORACLE_PASSWORD,
                    dsn=dsn
                )
                logger.info("Conexión a Oracle establecida exitosamente")
            except Exception as e:
                logger.error(f"Error al conectar con Oracle: {str(e)}")
                raise
        return cls._connection
    
    @classmethod
    def close_connection(cls):
        """Cierra la conexión a Oracle"""
        if cls._connection is not None:
            cls._connection.close()
            cls._connection = None
            logger.info("Conexión a Oracle cerrada")
    
    @classmethod
    def execute_query(cls, query: str, params: Optional[Dict] = None) -> list:
        """Ejecuta una consulta y retorna los resultados"""
        connection = cls.get_connection()
        cursor = connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                connection.commit()
                return []
        except Exception as e:
            connection.rollback()
            logger.error(f"Error ejecutando query: {str(e)}")
            raise
        finally:
            cursor.close()
    
    @classmethod
    def check_archivelog_mode(cls) -> bool:
        """Verifica si la base de datos está en modo ARCHIVELOG"""
        try:
            query = "SELECT LOG_MODE FROM V$DATABASE"
            result = cls.execute_query(query)
            return result[0][0] == 'ARCHIVELOG' if result else False
        except Exception as e:
            logger.error(f"Error verificando modo ARCHIVELOG: {str(e)}")
            return False
    
    @classmethod
    def get_database_info(cls) -> Dict[str, Any]:
        """Obtiene información general de la base de datos"""
        try:
            info = {}
            
            # Información de la base de datos
            db_query = """
                SELECT NAME, DBID, CREATED, LOG_MODE, OPEN_MODE 
                FROM V$DATABASE
            """
            db_result = cls.execute_query(db_query)
            if db_result:
                info.update({
                    'name': db_result[0][0],
                    'dbid': db_result[0][1],
                    'created': db_result[0][2],
                    'log_mode': db_result[0][3],
                    'open_mode': db_result[0][4]
                })
            
            # Información de tablespaces
            ts_query = """
                SELECT TABLESPACE_NAME, STATUS, CONTENTS 
                FROM DBA_TABLESPACES 
                ORDER BY TABLESPACE_NAME
            """
            ts_result = cls.execute_query(ts_query)
            info['tablespaces'] = [
                {'name': row[0], 'status': row[1], 'contents': row[2]}
                for row in ts_result
            ]
            
            # Información de schemas
            schema_query = """
                SELECT USERNAME, ACCOUNT_STATUS, CREATED 
                FROM DBA_USERS 
                WHERE ACCOUNT_STATUS = 'OPEN'
                ORDER BY USERNAME
            """
            schema_result = cls.execute_query(schema_query)
            info['schemas'] = [
                {'username': row[0], 'status': row[1], 'created': row[2]}
                for row in schema_result
            ]
            
            return info
        except Exception as e:
            logger.error(f"Error obteniendo información de la BD: {str(e)}")
            return {}