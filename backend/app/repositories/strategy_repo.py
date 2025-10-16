from typing import List, Optional
from datetime import datetime
import logging
from app.models.strategy import Strategy, StrategyCreate, StrategyUpdate

logger = logging.getLogger(__name__)

class StrategyRepository:
    def __init__(self):
        # En una implementación real, esto usaría una base de datos
        self._strategies = []
        self._next_id = 1
    
    async def get_all(self) -> List[Strategy]:
        """Obtiene todas las estrategias"""
        return self._strategies.copy()
    
    async def get_by_id(self, strategy_id: int) -> Optional[Strategy]:
        """Obtiene una estrategia por ID"""
        for strategy in self._strategies:
            if strategy.id == strategy_id:
                return strategy
        return None
    
    async def get_active_strategies(self) -> List[Strategy]:
        """Obtiene las estrategias activas"""
        return [s for s in self._strategies if s.is_active]
    
    async def get_by_backup_type(self, backup_type: str) -> List[Strategy]:
        """Obtiene estrategias por tipo de backup"""
        return [s for s in self._strategies if s.backup_type == backup_type]
    
    async def create(self, strategy_data: StrategyCreate, created_by: int) -> Strategy:
        """Crea una nueva estrategia"""
        now = datetime.now().isoformat()
        
        strategy = Strategy(
            id=self._next_id,
            created_by=created_by,
            created_at=now,
            updated_at=now,
            **strategy_data.dict()
        )
        
        self._strategies.append(strategy)
        self._next_id += 1
        
        logger.info(f"Estrategia creada: {strategy.name} (ID: {strategy.id})")
        return strategy
    
    async def update(self, strategy_id: int, update_data: StrategyUpdate) -> Optional[Strategy]:
        """Actualiza una estrategia"""
        for i, strategy in enumerate(self._strategies):
            if strategy.id == strategy_id:
                update_dict = update_data.dict(exclude_unset=True)
                update_dict['updated_at'] = datetime.now().isoformat()
                
                updated_strategy = strategy.copy(update=update_dict)
                self._strategies[i] = updated_strategy
                
                logger.info(f"Estrategia actualizada: {updated_strategy.name} (ID: {strategy_id})")
                return updated_strategy
        
        return None
    
    async def delete(self, strategy_id: int) -> bool:
        """Elimina una estrategia"""
        for i, strategy in enumerate(self._strategies):
            if strategy.id == strategy_id:
                deleted_strategy = self._strategies.pop(i)
                logger.info(f"Estrategia eliminada: {deleted_strategy.name} (ID: {strategy_id})")
                return True
        
        return False
    
    async def toggle_active(self, strategy_id: int) -> Optional[Strategy]:
        """Activa/desactiva una estrategia"""
        strategy = await self.get_by_id(strategy_id)
        if strategy:
            update_data = StrategyUpdate(is_active=not strategy.is_active)
            return await self.update(strategy_id, update_data)
        return None