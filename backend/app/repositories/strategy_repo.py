from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import json
from app.models.database_models import StrategyModel
from app.models.strategy import Strategy, StrategyCreate, StrategyUpdate, BackupType, BackupPriority, ScheduleFrequency
import logging

logger = logging.getLogger(__name__)

class StrategyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(self) -> List[Strategy]:
        """Obtiene todas las estrategias"""
        try:
            result = await self.db.execute(select(StrategyModel))
            strategies = result.scalars().all()
            return [self._model_to_strategy(strategy) for strategy in strategies]
        except Exception as e:
            logger.error(f"Error obteniendo estrategias: {str(e)}")
            return []
    
    async def get_by_id(self, strategy_id: int) -> Optional[Strategy]:
        """Obtiene una estrategia por ID"""
        try:
            result = await self.db.execute(
                select(StrategyModel).where(StrategyModel.id == strategy_id)
            )
            strategy = result.scalar_one_or_none()
            return self._model_to_strategy(strategy) if strategy else None
        except Exception as e:
            logger.error(f"Error obteniendo estrategia {strategy_id}: {str(e)}")
            return None
    
    async def get_active_strategies(self) -> List[Strategy]:
        """Obtiene las estrategias activas"""
        try:
            result = await self.db.execute(
                select(StrategyModel).where(StrategyModel.is_active == True)
            )
            strategies = result.scalars().all()
            return [self._model_to_strategy(strategy) for strategy in strategies]
        except Exception as e:
            logger.error(f"Error obteniendo estrategias activas: {str(e)}")
            return []
    
    async def get_by_backup_type(self, backup_type: str) -> List[Strategy]:
        """Obtiene estrategias por tipo de backup"""
        try:
            result = await self.db.execute(
                select(StrategyModel).where(StrategyModel.backup_type == backup_type)
            )
            strategies = result.scalars().all()
            return [self._model_to_strategy(strategy) for strategy in strategies]
        except Exception as e:
            logger.error(f"Error obteniendo estrategias por tipo {backup_type}: {str(e)}")
            return []
    
    async def create(self, strategy_data: StrategyCreate, created_by: int) -> Strategy:
        """Crea una nueva estrategia"""
        try:
            db_strategy = StrategyModel(
                name=strategy_data.name,
                description=strategy_data.description,
                backup_type=strategy_data.backup_type.value,
                priority=strategy_data.priority.value,
                is_active=strategy_data.is_active,
                schedule_frequency=strategy_data.schedule_frequency.value,
                schedule_time=str(strategy_data.schedule_time),
                schedule_days=json.dumps(strategy_data.schedule_days) if strategy_data.schedule_days else None,
                schedule_months=json.dumps(strategy_data.schedule_months) if strategy_data.schedule_months else None,
                tablespaces=json.dumps(strategy_data.tablespaces) if strategy_data.tablespaces else None,
                schemas=json.dumps(strategy_data.schemas) if strategy_data.schemas else None,
                tables=json.dumps(strategy_data.tables) if strategy_data.tables else None,
                include_archivelogs=strategy_data.include_archivelogs,
                compression=strategy_data.compression,
                encryption=strategy_data.encryption,
                retention_days=strategy_data.retention_days,
                parallel_degree=strategy_data.parallel_degree,
                max_backup_size=strategy_data.max_backup_size,
                custom_parameters=json.dumps(strategy_data.custom_parameters) if strategy_data.custom_parameters else None,
                created_by=created_by
            )
            
            self.db.add(db_strategy)
            await self.db.commit()
            await self.db.refresh(db_strategy)
            
            logger.info(f"Estrategia creada: {db_strategy.name} (ID: {db_strategy.id})")
            return self._model_to_strategy(db_strategy)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creando estrategia: {str(e)}")
            raise
    
    async def update(self, strategy_id: int, update_data: StrategyUpdate) -> Optional[Strategy]:
        """Actualiza una estrategia"""
        try:
            result = await self.db.execute(
                select(StrategyModel).where(StrategyModel.id == strategy_id)
            )
            db_strategy = result.scalar_one_or_none()
            
            if not db_strategy:
                return None
            
            # Actualizar campos
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                if hasattr(db_strategy, field):
                    if field in ['schedule_days', 'schedule_months', 'tablespaces', 'schemas', 'tables', 'custom_parameters'] and value is not None:
                        setattr(db_strategy, field, json.dumps(value))
                    elif field in ['backup_type', 'priority', 'schedule_frequency'] and value is not None:
                        setattr(db_strategy, field, value.value)
                    elif field == 'schedule_time' and value is not None:
                        setattr(db_strategy, field, str(value))
                    else:
                        setattr(db_strategy, field, value)
            
            await self.db.commit()
            await self.db.refresh(db_strategy)
            
            logger.info(f"Estrategia actualizada: {db_strategy.name} (ID: {strategy_id})")
            return self._model_to_strategy(db_strategy)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error actualizando estrategia {strategy_id}: {str(e)}")
            return None
    
    async def delete(self, strategy_id: int) -> bool:
        """Elimina una estrategia"""
        try:
            result = await self.db.execute(
                select(StrategyModel).where(StrategyModel.id == strategy_id)
            )
            db_strategy = result.scalar_one_or_none()
            
            if not db_strategy:
                return False
            
            await self.db.delete(db_strategy)
            await self.db.commit()
            
            logger.info(f"Estrategia eliminada: {db_strategy.name} (ID: {strategy_id})")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error eliminando estrategia {strategy_id}: {str(e)}")
            return False
    
    async def toggle_active(self, strategy_id: int) -> Optional[Strategy]:
        """Activa/desactiva una estrategia"""
        try:
            result = await self.db.execute(
                select(StrategyModel).where(StrategyModel.id == strategy_id)
            )
            db_strategy = result.scalar_one_or_none()
            
            if not db_strategy:
                return None
            
            db_strategy.is_active = not db_strategy.is_active
            await self.db.commit()
            await self.db.refresh(db_strategy)
            
            logger.info(f"Estrategia {'activada' if db_strategy.is_active else 'desactivada'}: {db_strategy.name}")
            return self._model_to_strategy(db_strategy)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error cambiando estado de estrategia {strategy_id}: {str(e)}")
            return None
    
    def _model_to_strategy(self, db_strategy: StrategyModel) -> Strategy:
        """Convierte StrategyModel a Strategy"""
        import json
        from datetime import time
        
        return Strategy(
            id=db_strategy.id,
            name=db_strategy.name,
            description=db_strategy.description,
            backup_type=BackupType(db_strategy.backup_type),
            priority=BackupPriority(db_strategy.priority),
            is_active=db_strategy.is_active,
            schedule_frequency=ScheduleFrequency(db_strategy.schedule_frequency),
            schedule_time=time.fromisoformat(db_strategy.schedule_time) if db_strategy.schedule_time else time(2, 0, 0),
            schedule_days=json.loads(db_strategy.schedule_days) if db_strategy.schedule_days else None,
            schedule_months=json.loads(db_strategy.schedule_months) if db_strategy.schedule_months else None,
            tablespaces=json.loads(db_strategy.tablespaces) if db_strategy.tablespaces else None,
            schemas=json.loads(db_strategy.schemas) if db_strategy.schemas else None,
            tables=json.loads(db_strategy.tables) if db_strategy.tables else None,
            include_archivelogs=db_strategy.include_archivelogs,
            compression=db_strategy.compression,
            encryption=db_strategy.encryption,
            retention_days=db_strategy.retention_days,
            parallel_degree=db_strategy.parallel_degree,
            max_backup_size=db_strategy.max_backup_size,
            custom_parameters=json.loads(db_strategy.custom_parameters) if db_strategy.custom_parameters else None,
            created_by=db_strategy.created_by,
            created_at=db_strategy.created_at.isoformat() if db_strategy.created_at else None,
            updated_at=db_strategy.updated_at.isoformat() if db_strategy.updated_at else None
        )