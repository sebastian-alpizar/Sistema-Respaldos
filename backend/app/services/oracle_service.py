from datetime import datetime
import glob
import subprocess
import tempfile
import os
import re
from typing import Dict, Any, Optional, List
import logging
from app.utils.oracle_connection import OracleConnection
from app.core.config import settings

logger = logging.getLogger(__name__)

class OracleService:
    def __init__(self):
        self.connection = OracleConnection()
    
    def generate_rman_script(self, strategy_data: Dict[str, Any], backup_path: str) -> str:
        """Genera el script RMAN para la estrategia de backup - USANDO PARALELISMO DE LA ESTRATEGIA"""
        
        accessible_backup_path = 'C:/temp/oracle_backups'
        os.makedirs(accessible_backup_path, exist_ok=True)
        
        backup_format = os.path.join(accessible_backup_path, "backup_%d_%T_%U.bkp").replace("\\", "/")
        script_lines = []
        
        # USAR EL PARALELISMO DE LA ESTRATEGIA O VALOR POR DEFECTO
        parallel_degree = strategy_data.get('parallel_degree', 1)
        
        script_lines.extend([
            f"CONFIGURE DEVICE TYPE DISK PARALLELISM {parallel_degree};",
            "CONFIGURE RETENTION POLICY TO REDUNDANCY 1;",
            "CONFIGURE CONTROLFILE AUTOBACKUP OFF;",
        ])
        
        # CONFIGURAR CANALES INDIVIDUALES SI HAY PARALELISMO > 1
        if parallel_degree > 1:
            for i in range(1, parallel_degree + 1):
                script_lines.append(f"CONFIGURE CHANNEL {i} DEVICE TYPE DISK FORMAT '{backup_format}';")
        
        if strategy_data.get('compression', True):
            script_lines.append("CONFIGURE COMPRESSION ALGORITHM 'HIGH' AS OF RELEASE 'DEFAULT' OPTIMIZE FOR LOAD TRUE;")

        # MANTENIMIENTO PREVENTIVO
        script_lines.extend([
            "CROSSCHECK BACKUP;",           # Sincroniza catálogo
            "DELETE EXPIRED BACKUP;",       # Elimina registros de backups físicamente desaparecidos
            "DELETE OBSOLETE;",             # Limpia según política de retención
        ])
        
        backup_type = strategy_data['backup_type']
        
        script_lines.append("RUN {")
        
        if backup_type == 'full':
            script_lines.extend([
                f"  BACKUP AS COMPRESSED BACKUPSET DATABASE FORMAT '{backup_format}';",
                f"  BACKUP AS COMPRESSED BACKUPSET ARCHIVELOG ALL FORMAT '{backup_format}' DELETE INPUT;",
                f"  BACKUP CURRENT CONTROLFILE FORMAT '{backup_format}';",
            ])
        
        elif backup_type == 'incremental':
            script_lines.extend([
                f"  BACKUP AS COMPRESSED BACKUPSET INCREMENTAL LEVEL 1 DATABASE FORMAT '{backup_format}';",
                f"  BACKUP AS COMPRESSED BACKUPSET ARCHIVELOG ALL FORMAT '{backup_format}' DELETE INPUT;",
                f"  BACKUP CURRENT CONTROLFILE FORMAT '{backup_format}';",
            ])
        
        elif backup_type == 'partial':
            backup_parts = []
            
            if strategy_data.get('tablespaces'):
                for ts in strategy_data['tablespaces']:
                    backup_parts.append(f"TABLESPACE {ts}")
            
            if strategy_data.get('schemas'):
                schema_tablespaces = self._get_tablespaces_for_schemas(strategy_data['schemas'])
                for ts in schema_tablespaces:
                    backup_parts.append(f"TABLESPACE {ts}")
            
            if backup_parts:
                tablespace_list = " ".join(backup_parts)
                script_lines.append(f"  BACKUP AS COMPRESSED BACKUPSET {tablespace_list} FORMAT '{backup_format}';")
            
            script_lines.extend([
                f"  BACKUP AS COMPRESSED BACKUPSET ARCHIVELOG ALL FORMAT '{backup_format}' DELETE INPUT;",
                f"  BACKUP CURRENT CONTROLFILE FORMAT '{backup_format}';",
            ])
        
        script_lines.append("  DELETE NOPROMPT OBSOLETE;") # Limpiar backups obsoletos
        script_lines.append("}")
        
        script_lines.extend([  # Comandos finales
            "LIST BACKUP SUMMARY;",
            "EXIT;"
        ])
        
        script_content = "\n".join(script_lines)

        return script_content
    
    def _get_tablespaces_for_schemas(self, schemas: List[str]) -> List[str]:
        """Obtiene los tablespaces asociados a los schemas especificados"""
        try:
            tablespaces = set()
            for schema in schemas:
                query = f"""
                SELECT DEFAULT_TABLESPACE 
                FROM DBA_USERS 
                WHERE USERNAME = UPPER('{schema}')
                """
                result = self.connection.execute_query(query)
                if result:
                    tablespaces.add(result[0][0])
            return list(tablespaces)
        except Exception as e:
            logger.error(f"Error obteniendo tablespaces para schemas: {str(e)}")
            return []
        
    def execute_rman_backup(self, rman_script: str, strategy_id: int) -> Dict[str, Any]:
        """Ejecuta el script RMAN y retorna el resultado - VERSIÓN MEJORADA CON LOG"""
        result = {
            'success': False,
            'output': '',
            'error': '',
            'backup_files': [],
            'backup_size_bytes': 0,
            'log_content': ''  # Nuevo campo para el contenido del log
        }
        
        temp_file_path = None
        log_file_path = None
        
        try:
            backup_dir = 'C:/temp/oracle_backups'
            os.makedirs(backup_dir, exist_ok=True)
            logger.info(f"Directorio de backup: {backup_dir}")

            # Crear archivo temporal para el script RMAN
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.rman', delete=False, encoding='utf-8')
            temp_file_path = temp_file.name
            temp_file.write(rman_script)
            temp_file.close()
            logger.info(f"Script RMAN creado en: {temp_file_path}")

            # Crear archivo de log con nombre único
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_filename = f"rman_log_{strategy_id}_{timestamp}.log"
            log_file_path = os.path.abspath(os.path.join(backup_dir, log_filename))
            logger.info(f"Archivo de log: {log_file_path}")
            
            # Buscar RMAN
            rman_executable = "rman"
            if not rman_executable:
                result['error'] = "No se pudo encontrar el ejecutable RMAN."
                return result
            
            # Comando RMAN
            rman_cmd = f'{rman_executable} target \'sys/123@XE AS SYSDBA\' cmdfile={temp_file_path} log={log_file_path}'

            logger.info(f"Comando RMAN: {rman_cmd}")
            
            # Ejecutar comando RMAN
            logger.info("🚀 Iniciando ejecución de RMAN...")
            
            process = subprocess.Popen(
                rman_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True,
                encoding='utf-8',
                errors='ignore'
            )

            try:
                stdout, stderr = process.communicate(timeout=3600)
                logger.info(f"RMAN finalizado con código: {process.returncode}")
                
                # Leer el contenido del archivo de log
                if os.path.exists(log_file_path):
                    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as log_file:
                        result['log_content'] = log_file.read()
                        logger.info(f"Contenido del log leído ({len(result['log_content'])} caracteres)")
                else:
                    logger.warning(f"Archivo de log no encontrado: {log_file_path}")
                    result['log_content'] = "Archivo de log no generado"

                # ✅ DETECTAR ARCHIVOS DE BACKUP CREADOS
                backup_files = self._find_backup_files(backup_dir, strategy_id)
                result['backup_files'] = backup_files
                result['backup_size_bytes'] = self._calculate_total_size(backup_files)
                
                logger.info(f"📁 Archivos de backup detectados: {len(backup_files)}")
                logger.info(f"📊 Tamaño total del backup: {result['backup_size_bytes'] / (1024*1024):.2f} MB")
                    
                # Combinar salidas para el resultado
                result['output'] = stdout
                result['error'] = stderr
                
                # DEBUG: Mostrar resumen del log
                if result['log_content']:
                    log_preview = result['log_content'][:500] + "..." if len(result['log_content']) > 500 else result['log_content']
                    logger.info(f"Preview del log RMAN: {log_preview}")
                    
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                result['error'] = "Timeout: El comando RMAN tardó más de 1 hora"
                logger.error("Timeout en ejecución RMAN")
                
                # Intentar leer el log incluso en timeout
                if os.path.exists(log_file_path):
                    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as log_file:
                        result['log_content'] = log_file.read()
                
                return result
            
            result['success'] = process.returncode == 0
            
            if result['success']:
                logger.info("✅ Backup completado exitosamente")
            else:
                logger.error(f"❌ Backup falló con código: {process.returncode}")

            return result
            
        except Exception as e:
            logger.error(f"💥 Error ejecutando backup RMAN: {str(e)}", exc_info=True)
            result['error'] = str(e)
            
            # Intentar leer el log incluso en error
            if log_file_path and os.path.exists(log_file_path):
                try:
                    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as log_file:
                        result['log_content'] = log_file.read()
                except Exception as log_error:
                    logger.error(f"Error leyendo archivo de log: {log_error}")
            
            return result
        finally:
            # Limpiar archivos temporales
            try:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    logger.info(f"Archivo temporal eliminado: {temp_file_path}")
            except Exception as e:
                logger.warning(f"No se pudo eliminar archivo temporal: {e}")

    def _find_backup_files(self, backup_dir: str, strategy_id: int) -> List[str]:
        """Encuentra todos los archivos de backup creados en el directorio"""
        try:
            # Patrones de nombres de archivos de backup RMAN
            patterns = [
                f"*backup*{strategy_id}*.bkp",
                f"*BACKUP*{strategy_id}*.BKP", 
                "backup_*.bkp",
                "BACKUP_*.BKP",
                "*.bkp"  # Todos los archivos .bkp
            ]
            
            backup_files = []
            for pattern in patterns:
                full_pattern = os.path.join(backup_dir, pattern)
                matches = glob.glob(full_pattern)
                backup_files.extend(matches)
            
            # Eliminar duplicados y archivos de log
            backup_files = [f for f in set(backup_files) 
                        if not f.endswith('.log') and os.path.isfile(f)]
            
            # Ordenar por fecha de modificación (más recientes primero)
            backup_files.sort(key=os.path.getmtime, reverse=True)
            
            logger.info(f"🔍 Búsqueda de archivos de backup: encontrados {len(backup_files)}")
            for file in backup_files:
                size_mb = os.path.getsize(file) / (1024 * 1024)
                logger.info(f"   📄 {os.path.basename(file)} - {size_mb:.2f} MB")
                
            return backup_files
            
        except Exception as e:
            logger.error(f"Error buscando archivos de backup: {str(e)}")
            return []

    def _calculate_total_size(self, file_paths: List[str]) -> int:
        """Calcula el tamaño total en bytes de una lista de archivos"""
        total_size = 0
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
            except Exception as e:
                logger.warning(f"Error calculando tamaño de {file_path}: {str(e)}")
        
        return total_size
    
    def _extract_oracle_errors(self, output: str) -> str:
        """Extrae errores específicos de Oracle/RMAN del output"""
        import re
        errors = []
        
        # Buscar errores RMAN
        rman_errors = re.findall(r'RMAN-\d+: [^\n]+', output)
        errors.extend(rman_errors)
        
        # Buscar errores ORA
        ora_errors = re.findall(r'ORA-\d+: [^\n]+', output)
        errors.extend(ora_errors)
        
        return "\n".join(errors) if errors else ""
    
    def _extract_backup_files(self, backup_dir: str) -> List[str]:
        """Extrae la lista de archivos de backup del directorio"""
        backup_files = []
        try:
            for file in os.listdir(backup_dir):
                if file.endswith('.bkp'):
                    file_path = os.path.join(backup_dir, file)
                    backup_files.append(file_path)
        except Exception as e:
            logger.error(f"Error extrayendo archivos de backup: {str(e)}")
        
        return backup_files
    
    def verify_backup(self, backup_files: List[str]) -> bool:
        """Verifica la integridad básica de los archivos de backup"""
        if not backup_files:
            logger.warning("No hay archivos de backup para verificar")
            return False
        
        try:
            for backup_file in backup_files:
                # Verificar que el archivo existe
                if not os.path.exists(backup_file):
                    logger.error(f"Archivo de backup no encontrado: {backup_file}")
                    return False
                
                # Verificar que tiene tamaño mayor a 0
                file_size = os.path.getsize(backup_file)
                if file_size == 0:
                    logger.error(f"Archivo de backup vacío: {backup_file}")
                    return False
                
                # Verificar que es un archivo .bkp (opcional)
                if not backup_file.lower().endswith('.bkp'):
                    logger.warning(f"Archivo con extensión inusual: {backup_file}")
            
            logger.info(f"✅ Verificación exitosa para {len(backup_files)} archivos")
            return True
            
        except Exception as e:
            logger.error(f"Error en verificación de backup: {str(e)}")
        return False
    
    def restore_test(self, backup_files: List[str]) -> bool:
        """Realiza una prueba de restauración (opcional)"""
        # Esta función podría implementar una verificación más completa
        # realizando una restauración de prueba en un área temporal
        return self.verify_backup(backup_files)