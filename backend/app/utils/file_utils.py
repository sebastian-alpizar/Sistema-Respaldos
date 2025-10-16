import os
import shutil
import logging
from typing import Optional
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

class FileUtils:
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Asegura que el directorio exista, creándolo si es necesario"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error creando directorio {path}: {str(e)}")
            return False
    
    @staticmethod
    def generate_backup_filename(strategy_name: str, backup_type: str) -> str:
        """Genera un nombre de archivo único para el backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = strategy_name.replace(" ", "_").lower()
        return f"{safe_name}_{backup_type}_{timestamp}.bkp"
    
    @staticmethod
    def get_backup_path(strategy_id: int, filename: str) -> str:
        """Obtiene la ruta completa para un archivo de backup"""
        strategy_path = os.path.join(settings.BACKUP_BASE_PATH, f"strategy_{strategy_id}")
        FileUtils.ensure_directory(strategy_path)
        return os.path.join(strategy_path, filename)
    
    @staticmethod
    def calculate_file_size(file_path: str) -> Optional[float]:
        """Calcula el tamaño de un archivo en MB"""
        try:
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                return size_bytes / (1024 * 1024)  # Convertir a MB
            return None
        except Exception as e:
            logger.error(f"Error calculando tamaño de archivo {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def cleanup_old_backups(strategy_id: int, retention_days: int) -> int:
        """Elimina backups antiguos según la política de retención"""
        try:
            strategy_path = os.path.join(settings.BACKUP_BASE_PATH, f"strategy_{strategy_id}")
            if not os.path.exists(strategy_path):
                return 0
            
            cutoff_time = datetime.now().timestamp() - (retention_days * 24 * 60 * 60)
            deleted_count = 0
            
            for filename in os.listdir(strategy_path):
                file_path = os.path.join(strategy_path, filename)
                if os.path.isfile(file_path):
                    file_time = os.path.getctime(file_path)
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Backup antiguo eliminado: {filename}")
            
            return deleted_count
        except Exception as e:
            logger.error(f"Error limpiando backups antiguos: {str(e)}")
            return 0