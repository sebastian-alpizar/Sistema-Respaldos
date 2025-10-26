import cx_Oracle
from typing import Optional, Dict, Any, List
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class OracleConnection:
    _connection = None
    
    @classmethod
    def get_connection(cls):
        """Obtiene una conexión a la base de datos Oracle"""
        if cls._connection is None:
            try:
                # Parsear DSN
                if ':' in settings.ORACLE_DSN and '/' in settings.ORACLE_DSN:
                    host_port, service_name = settings.ORACLE_DSN.split('/')
                    if ':' in host_port:
                        host, port = host_port.split(':')
                    else:
                        host, port = host_port, '1521'
                    
                    dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
                else:
                    dsn = settings.ORACLE_DSN
                
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
    def execute_query(cls, query: str, params: Optional[Dict] = None) -> List:
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
                SELECT NAME, DBID, CREATED, LOG_MODE, OPEN_MODE, 
                        (SELECT COUNT(*) FROM V$DATAFILE) as datafiles,
                        (SELECT COUNT(*) FROM V$TABLESPACE) as tablespaces
                FROM V$DATABASE
            """
            db_result = cls.execute_query(db_query)
            if db_result:
                info.update({
                    'name': db_result[0][0],
                    'dbid': db_result[0][1],
                    'created': db_result[0][2],
                    'log_mode': db_result[0][3],
                    'open_mode': db_result[0][4],
                    'datafiles_count': db_result[0][5],
                    'tablespaces_count': db_result[0][6]
                })
            
            # Información de tablespaces
            ts_query = """
                SELECT TABLESPACE_NAME, STATUS, CONTENTS, 
                        (SELECT SUM(BYTES) FROM DBA_DATA_FILES WHERE TABLESPACE_NAME = ts.TABLESPACE_NAME) as size_bytes
                FROM DBA_TABLESPACES ts
                ORDER BY TABLESPACE_NAME
            """
            ts_result = cls.execute_query(ts_query)
            info['tablespaces'] = [
                {
                    'name': row[0], 
                    'status': row[1], 
                    'contents': row[2],
                    'size_bytes': row[3] or 0
                }
                for row in ts_result
            ]
            
            # Información de schemas
            schema_query = """
                SELECT USERNAME, ACCOUNT_STATUS, CREATED, DEFAULT_TABLESPACE
                FROM DBA_USERS 
                WHERE ACCOUNT_STATUS = 'OPEN'
                ORDER BY USERNAME
            """
            schema_result = cls.execute_query(schema_query)
            info['schemas'] = [
                {
                    'username': row[0], 
                    'status': row[1], 
                    'created': row[2],
                    'default_tablespace': row[3]
                }
                for row in schema_result
            ]
            
            return info
        except Exception as e:
            logger.error(f"Error obteniendo información de la BD: {str(e)}")
            return {}