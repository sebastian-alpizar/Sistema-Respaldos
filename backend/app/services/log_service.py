import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from app.models.log import Log, LogCreate, LogUpdate, LogLevel, BackupStatus
from app.repositories.log_repo import LogRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class LogService:
    def __init__(self, db: AsyncSession):
        self.log_repo = LogRepository(db)
    
    # Los métodos permanecen iguales, pero ahora usan Oracle real
    async def create_log(self, log_data: LogCreate) -> Log:
        return await self.log_repo.create(log_data)
    
    async def get_log(self, log_id: int) -> Optional[Log]:
        return await self.log_repo.get_by_id(log_id)
    
    async def get_strategy_logs(
        self, 
        strategy_id: int, 
        limit: int = 100,
        offset: int = 0
    ) -> List[Log]:
        """Obtiene los logs de una estrategia específica"""
        try:
            return await self.log_repo.get_by_strategy(strategy_id, limit, offset)
        except Exception as e:
            logger.error(f"Error obteniendo logs de estrategia {strategy_id}: {str(e)}")
            return []
    
    async def get_logs_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        level: Optional[LogLevel] = None,
        status: Optional[BackupStatus] = None
    ) -> List[Log]:
        """Obtiene logs por rango de fecha"""
        try:
            return await self.log_repo.get_by_date_range(start_date, end_date, level, status)
        except Exception as e:
            logger.error(f"Error obteniendo logs por rango de fecha: {str(e)}")
            return []
    
    async def update_log(self, log_id: int, update_data: LogUpdate) -> Optional[Log]:
        """Actualiza un registro de log"""
        try:
            # Convertir a dict para Pydantic v2
            if isinstance(update_data, dict):
                update_dict = update_data
            else:
                update_dict = update_data.model_dump(exclude_unset=True)
            
            return await self.log_repo.update(log_id, update_dict)
        except Exception as e:
            logger.error(f"Error actualizando log {log_id}: {str(e)}")
            return None
    
    async def delete_log(self, log_id: int) -> bool:
        """Elimina un registro de log"""
        try:
            return await self.log_repo.delete(log_id)
        except Exception as e:
            logger.error(f"Error eliminando log {log_id}: {str(e)}")
            return False
    
    async def get_backup_statistics(
        self, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de backups"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            logs = await self.log_repo.get_by_date_range(start_date, end_date)
            
            total_backups = len(logs)
            completed = len([log for log in logs if log.status == BackupStatus.COMPLETED])
            failed = len([log for log in logs if log.status == BackupStatus.FAILED])
            running = len([log for log in logs if log.status == BackupStatus.RUNNING])
            
            success_rate = (completed / total_backups * 100) if total_backups > 0 else 0
            
            total_size = sum([log.backup_size_mb or 0 for log in logs if log.backup_size_mb])
            avg_duration = sum([log.duration_seconds or 0 for log in logs if log.duration_seconds]) / total_backups if total_backups > 0 else 0
            
            return {
                'period': f"Últimos {days} días",
                'total_backups': total_backups,
                'completed': completed,
                'failed': failed,
                'running': running,
                'success_rate': round(success_rate, 2),
                'total_size_mb': round(total_size, 2),
                'average_duration_seconds': round(avg_duration, 2),
                'most_common_errors': self._get_common_errors(logs)
            }
            
        except Exception as e:
            logger.error(f"Error generando estadísticas: {str(e)}")
            return {}
    
    def _get_common_errors(self, logs: List[Log]) -> List[Dict[str, Any]]:
        """Obtiene los errores más comunes de los logs"""
        error_messages = {}
        
        for log in logs:
            if log.error_message and log.status == BackupStatus.FAILED:
                error_key = log.error_message.split('\n')[0]  # Tomar primera línea
                error_messages[error_key] = error_messages.get(error_key, 0) + 1
        
        # Ordenar por frecuencia
        sorted_errors = sorted(
            error_messages.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]  # Top 10 errores
        
        return [{'error': error, 'count': count} for error, count in sorted_errors]
    
    async def export_logs_to_csv(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> str:
        """Exporta logs a formato CSV"""
        try:
            logs = await self.get_logs_by_date_range(start_date, end_date)
            
            csv_lines = [
                "ID,Strategy ID,Level,Status,Message,Start Time,End Time,Duration (s),Size (MB),Error"
            ]
            
            for log in logs:
                csv_line = [
                    str(log.id),
                    str(log.strategy_id),
                    log.level.value,
                    log.status.value,
                    f'"{log.message.replace('"', '""')}"',  # Escapar comillas
                    log.start_time.isoformat(),
                    log.end_time.isoformat() if log.end_time else "",
                    str(log.duration_seconds or ""),
                    str(log.backup_size_mb or ""),
                    f'"{log.error_message.replace('"', '""') if log.error_message else ""}"'
                ]
                csv_lines.append(",".join(csv_line))
            
            return "\n".join(csv_lines)
            
        except Exception as e:
            logger.error(f"Error exportando logs a CSV: {str(e)}")
            return ""