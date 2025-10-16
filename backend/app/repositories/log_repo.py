from typing import List, Optional
from datetime import datetime
import logging
from app.models.log import Log, LogCreate, LogUpdate, LogLevel, BackupStatus

logger = logging.getLogger(__name__)

class LogRepository:
    def __init__(self):
        # En una implementación real, esto usaría una base de datos
        self._logs = []
        self._next_id = 1
    
    async def create(self, log_data: LogCreate) -> Log:
        """Crea un nuevo registro de log"""
        log = Log(
            id=self._next_id,
            created_at=datetime.now(),
            **log_data.dict()
        )
        
        self._logs.append(log)
        self._next_id += 1
        
        logger.info(f"Log creado: {log.message} (Strategy: {log.strategy_id})")
        return log
    
    async def get_by_id(self, log_id: int) -> Optional[Log]:
        """Obtiene un log por ID"""
        for log in self._logs:
            if log.id == log_id:
                return log
        return None
    
    async def get_by_strategy(
        self, 
        strategy_id: int, 
        limit: int = 100,
        offset: int = 0
    ) -> List[Log]:
        """Obtiene logs por estrategia"""
        strategy_logs = [log for log in self._logs if log.strategy_id == strategy_id]
        strategy_logs.sort(key=lambda x: x.start_time, reverse=True)
        
        return strategy_logs[offset:offset + limit]
    
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        level: Optional[LogLevel] = None,
        status: Optional[BackupStatus] = None
    ) -> List[Log]:
        """Obtiene logs por rango de fecha"""
        filtered_logs = []
        
        for log in self._logs:
            if start_date <= log.start_time <= end_date:
                if level and log.level != level:
                    continue
                if status and log.status != status:
                    continue
                filtered_logs.append(log)
        
        filtered_logs.sort(key=lambda x: x.start_time, reverse=True)
        return filtered_logs
    
    async def update(self, log_id: int, update_data: LogUpdate) -> Optional[Log]:
        """Actualiza un registro de log"""
        for i, log in enumerate(self._logs):
            if log.id == log_id:
                update_dict = update_data.dict(exclude_unset=True)
                updated_log = log.copy(update=update_dict)
                self._logs[i] = updated_log
                
                logger.info(f"Log actualizado: ID {log_id}")
                return updated_log
        
        return None
    
    async def delete(self, log_id: int) -> bool:
        """Elimina un registro de log"""
        for i, log in enumerate(self._logs):
            if log.id == log_id:
                self._logs.pop(i)
                logger.info(f"Log eliminado: ID {log_id}")
                return True
        
        return False
    
    async def get_recent_logs(self, limit: int = 50) -> List[Log]:
        """Obtiene los logs más recientes"""
        sorted_logs = sorted(self._logs, key=lambda x: x.start_time, reverse=True)
        return sorted_logs[:limit]