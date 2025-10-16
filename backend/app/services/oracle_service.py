import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
import logging
from app.utils.oracle_connection import OracleConnection
from app.core.config import settings

logger = logging.getLogger(__name__)

class OracleService:
    def __init__(self):
        self.connection = OracleConnection()
    
    def generate_rman_script(self, strategy_data: Dict[str, Any], backup_path: str) -> str:
        """Genera el script RMAN para la estrategia de backup"""
        
        script_lines = [
            "RUN {"
        ]
        
        # Configuración básica
        if strategy_data.get('compression', True):
            script_lines.append("  CONFIGURE COMPRESSION ALGORITHM 'HIGH' AS OF RELEASE 'DEFAULT' OPTIMIZE FOR LOAD TRUE;")
        
        if strategy_data.get('parallel_degree'):
            script_lines.append(f"  CONFIGURE DEVICE TYPE DISK PARALLELISM {strategy_data['parallel_degree']};")
        
        # Comando de backup según el tipo
        backup_type = strategy_data['backup_type']
        
        if backup_type == 'full':
            script_lines.append(f"  BACKUP AS COMPRESSED BACKUPSET DATABASE PLUS ARCHIVELOG DELETE INPUT;")
        
        elif backup_type == 'incremental':
            script_lines.append(f"  BACKUP AS COMPRESSED BACKUPSET INCREMENTAL LEVEL 1 DATABASE PLUS ARCHIVELOG DELETE INPUT;")
        
        elif backup_type == 'partial':
            backup_parts = []
            
            if strategy_data.get('tablespaces'):
                for ts in strategy_data['tablespaces']:
                    backup_parts.append(f"TABLESPACE {ts}")
            
            if strategy_data.get('schemas'):
                # Para schemas, necesitamos hacer backup de tablespaces correspondientes
                # Esto es una simplificación - en producción se necesitaría más lógica
                for schema in strategy_data['schemas']:
                    backup_parts.append(f"TABLESPACE USERS")  # Ejemplo
            
            if backup_parts:
                backup_command = " BACKUP AS COMPRESSED BACKUPSET " + " ".join(backup_parts)
                script_lines.append(backup_command)
            
            if strategy_data.get('include_archivelogs', True):
                script_lines.append("  BACKUP ARCHIVELOG ALL DELETE INPUT;")
        
        # Backup de control file y spfile
        script_lines.append("  BACKUP CURRENT CONTROLFILE;")
        script_lines.append("  BACKUP SPFILE;")
        
        script_lines.append("}")
        
        # Configuración de formato y ubicación
        script_lines.append(f"CONFIGURE CHANNEL DEVICE TYPE DISK FORMAT '{backup_path}/%U';")
        
        # Listar backups
        script_lines.append("LIST BACKUP SUMMARY;")
        
        return "\n".join(script_lines)
    
    def execute_rman_backup(self, rman_script: str, strategy_id: int) -> Dict[str, Any]:
        """Ejecuta el script RMAN y retorna el resultado"""
        result = {
            'success': False,
            'output': '',
            'error': '',
            'backup_files': []
        }
        
        try:
            # Crear archivo temporal para el script RMAN
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rman', delete=False) as temp_file:
                temp_file.write(rman_script)
                temp_file_path = temp_file.name
            
            # Comando RMAN
            rman_cmd = [
                'rman',
                'target', f'{settings.ORACLE_USER}/{settings.ORACLE_PASSWORD}@{settings.ORACLE_DSN}',
                'cmdfile', temp_file_path
            ]
            
            # Ejecutar comando
            process = subprocess.Popen(
                rman_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            # Limpiar archivo temporal
            os.unlink(temp_file_path)
            
            result['output'] = stdout
            result['error'] = stderr
            result['success'] = process.returncode == 0
            
            # Extraer información de archivos de backup del output
            if result['success']:
                result['backup_files'] = self._extract_backup_files(stdout)
            
            return result
            
        except Exception as e:
            logger.error(f"Error ejecutando backup RMAN: {str(e)}")
            result['error'] = str(e)
            return result
    
    def _extract_backup_files(self, rman_output: str) -> list:
        """Extrae la lista de archivos de backup del output de RMAN"""
        backup_files = []
        lines = rman_output.split('\n')
        
        for line in lines:
            if 'piece handle=' in line:
                # Ejemplo: piece handle=/backup/oracle/0ABC1234_1_1.bkp
                parts = line.split('piece handle=')
                if len(parts) > 1:
                    file_path = parts[1].strip()
                    if file_path and not file_path.startswith('+'):  # Excluir ASM
                        backup_files.append(file_path)
        
        return backup_files
    
    def verify_backup(self, backup_files: list) -> bool:
        """Verifica la integridad de los archivos de backup"""
        try:
            for file_path in backup_files:
                if not os.path.exists(file_path):
                    logger.error(f"Archivo de backup no encontrado: {file_path}")
                    return False
                
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    logger.error(f"Archivo de backup vacío: {file_path}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error verificando backup: {str(e)}")
            return False