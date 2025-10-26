from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from datetime import datetime
import json
from app.models.database_models import LogModel
from app.models.log import Log, LogCreate, LogUpdate, LogLevel, BackupStatus
import logging

logger = logging.getLogger(__name__)

class LogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, log_data: LogCreate) -> Log:
        """Crea un nuevo registro de log"""
        try:
            db_log = LogModel(
                strategy_id=log_data.strategy_id,
                level=log_data.level.value,
                status=log_data.status.value,
                message=log_data.message,
                details=json.dumps(log_data.details) if log_data.details else None,
                start_time=log_data.start_time,
                end_time=log_data.end_time,
                duration_seconds=log_data.duration_seconds,
                backup_size_mb=log_data.backup_size_mb,
                rman_output=log_data.rman_output,
                rman_log_content=log_data.rman_log_content,
                error_message=log_data.error_message
            )
            
            self.db.add(db_log)
            await self.db.commit()
            await self.db.refresh(db_log)
            
            logger.info(f"Log creado: {db_log.message} (Strategy: {db_log.strategy_id})")
            return self._model_to_log(db_log)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creando log: {str(e)}")
            raise
    
    async def get_by_id(self, log_id: int) -> Optional[Log]:
        """Obtiene un log por ID"""
        try:
            result = await self.db.execute(
                select(LogModel).where(LogModel.id == log_id)
            )
            log = result.scalar_one_or_none()
            return self._model_to_log(log) if log else None
        except Exception as e:
            logger.error(f"Error obteniendo log {log_id}: {str(e)}")
            return None
    
    async def get_by_strategy(
        self, 
        strategy_id: int, 
        limit: int = 100,
        offset: int = 0
    ) -> List[Log]:
        """Obtiene logs por estrategia"""
        try:
            result = await self.db.execute(
                select(LogModel)
                .where(LogModel.strategy_id == strategy_id)
                .order_by(desc(LogModel.start_time))
                .offset(offset)
                .limit(limit)
            )
            logs = result.scalars().all()
            return [self._model_to_log(log) for log in logs]
        except Exception as e:
            logger.error(f"Error obteniendo logs de estrategia {strategy_id}: {str(e)}")
            return []
    
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        level: Optional[LogLevel] = None,
        status: Optional[BackupStatus] = None
    ) -> List[Log]:
        """Obtiene logs por rango de fecha"""
        try:
            query = select(LogModel).where(
                and_(
                    LogModel.start_time >= start_date,
                    LogModel.start_time <= end_date
                )
            )
            
            if level:
                query = query.where(LogModel.level == level.value)
            if status:
                query = query.where(LogModel.status == status.value)
            
            query = query.order_by(desc(LogModel.start_time))
            
            result = await self.db.execute(query)
            logs = result.scalars().all()
            return [self._model_to_log(log) for log in logs]
            
        except Exception as e:
            logger.error(f"Error obteniendo logs por rango de fecha: {str(e)}")
            return []
    
    async def update(self, log_id: int, update_data: Dict[str, Any]) -> Optional[Log]:
        """Actualiza un registro de log"""
        try:
            result = await self.db.execute(
                select(LogModel).where(LogModel.id == log_id)
            )
            db_log = result.scalar_one_or_none()
            
            if not db_log:
                return None
            
            # Actualizar campos
            for field, value in update_data.items():
                if hasattr(db_log, field):
                    if field in ['level', 'status'] and value is not None:
                        setattr(db_log, field, value.value)
                    elif field == 'details' and value is not None:
                        setattr(db_log, field, json.dumps(value))
                    else:
                        setattr(db_log, field, value)
            
            await self.db.commit()
            await self.db.refresh(db_log)
            
            logger.info(f"Log actualizado: ID {log_id}")
            return self._model_to_log(db_log)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error actualizando log {log_id}: {str(e)}")
            return None
    
    async def delete(self, log_id: int) -> bool:
        """Elimina un registro de log"""
        try:
            result = await self.db.execute(
                select(LogModel).where(LogModel.id == log_id)
            )
            db_log = result.scalar_one_or_none()
            
            if not db_log:
                return False
            
            await self.db.delete(db_log)
            await self.db.commit()
            
            logger.info(f"Log eliminado: ID {log_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error eliminando log {log_id}: {str(e)}")
            return False
    
    async def get_recent_logs(self, limit: int = 50) -> List[Log]:
        """Obtiene los logs más recientes"""
        try:
            result = await self.db.execute(
                select(LogModel)
                .order_by(desc(LogModel.start_time))
                .limit(limit)
            )
            logs = result.scalars().all()
            return [self._model_to_log(log) for log in logs]
        except Exception as e:
            logger.error(f"Error obteniendo logs recientes: {str(e)}")
            return []
    
    def _model_to_log(self, db_log: LogModel) -> Log:
        """Convierte LogModel a Log"""
        import json
        
        return Log(
            id=db_log.id,
            strategy_id=db_log.strategy_id,
            level=LogLevel(db_log.level),
            status=BackupStatus(db_log.status),
            message=db_log.message,
            details=json.loads(db_log.details) if db_log.details else None,
            start_time=db_log.start_time,
            end_time=db_log.end_time,
            duration_seconds=db_log.duration_seconds,
            backup_size_mb=db_log.backup_size_mb,
            rman_output=db_log.rman_output,
            rman_log_content=db_log.rman_log_content,  # Incluir este campo
            error_message=db_log.error_message,
            created_at=db_log.created_at
        )