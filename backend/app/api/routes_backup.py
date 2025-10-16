from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
from app.models.strategy import Strategy, StrategyCreate, StrategyUpdate
from app.models.log import Log
from app.services.backup_service import BackupService
from app.repositories.strategy_repo import StrategyRepository
from app.core.scheduler import BackupScheduler

router = APIRouter(prefix="/api/backup", tags=["backup"])

# Inicializar servicios
strategy_repo = StrategyRepository()
backup_service = BackupService()
scheduler = BackupScheduler()

@router.get("/strategies", response_model=List[Strategy])
async def get_strategies(active_only: bool = False):
    """Obtiene todas las estrategias de backup"""
    try:
        if active_only:
            return await strategy_repo.get_active_strategies()
        return await strategy_repo.get_all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estrategias: {str(e)}"
        )

@router.get("/strategies/{strategy_id}", response_model=Strategy)
async def get_strategy(strategy_id: int):
    """Obtiene una estrategia específica"""
    strategy = await strategy_repo.get_by_id(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estrategia no encontrada"
        )
    return strategy

@router.post("/strategies", response_model=Strategy, status_code=status.HTTP_201_CREATED)
async def create_strategy(strategy_data: StrategyCreate, created_by: int = 1):  # TODO: Authentication
    """Crea una nueva estrategia de backup"""
    try:
        # Validar la estrategia antes de crearla
        validation = await backup_service.validate_strategy(
            Strategy(**strategy_data.dict(), id=0, created_by=created_by, created_at="", updated_at="")
        )
        
        if not validation['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Validación fallida",
                    "errors": validation['errors'],
                    "warnings": validation['warnings']
                }
            )
        
        strategy = await strategy_repo.create(strategy_data, created_by)
        
        # Programar la estrategia si está activa
        if strategy.is_active:
            scheduler.schedule_strategy(strategy)
        
        return strategy
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando estrategia: {str(e)}"
        )

@router.put("/strategies/{strategy_id}", response_model=Strategy)
async def update_strategy(strategy_id: int, strategy_data: StrategyUpdate):
    """Actualiza una estrategia existente"""
    try:
        strategy = await strategy_repo.update(strategy_id, strategy_data)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estrategia no encontrada"
            )
        
        # Reprogramar la estrategia
        if strategy.is_active:
            scheduler.schedule_strategy(strategy)
        else:
            scheduler.unschedule_strategy(strategy_id)
        
        return strategy
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando estrategia: {str(e)}"
        )

@router.delete("/strategies/{strategy_id}")
async def delete_strategy(strategy_id: int):
    """Elimina una estrategia"""
    try:
        # Eliminar programación primero
        scheduler.unschedule_strategy(strategy_id)
        
        success = await strategy_repo.delete(strategy_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estrategia no encontrada"
            )
        
        return {"message": "Estrategia eliminada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando estrategia: {str(e)}"
        )

@router.post("/strategies/{strategy_id}/execute")
async def execute_strategy(strategy_id: int):
    """Ejecuta una estrategia de backup inmediatamente"""
    try:
        strategy = await strategy_repo.get_by_id(strategy_id)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estrategia no encontrada"
            )
        
        result = await backup_service.execute_backup_strategy(strategy)
        
        return {
            "message": "Backup ejecutado",
            "success": result['success'],
            "log_id": result.get('log_id'),
            "backup_files": result.get('backup_files', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ejecutando backup: {str(e)}"
        )

@router.post("/strategies/{strategy_id}/toggle")
async def toggle_strategy(strategy_id: int):
    """Activa/desactiva una estrategia"""
    try:
        strategy = await strategy_repo.toggle_active(strategy_id)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estrategia no encontrada"
            )
        
        # Programar o eliminar programación
        if strategy.is_active:
            scheduler.schedule_strategy(strategy)
        else:
            scheduler.unschedule_strategy(strategy_id)
        
        return {
            "message": f"Estrategia {'activada' if strategy.is_active else 'desactivada'}",
            "strategy": strategy
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cambiando estado de estrategia: {str(e)}"
        )

@router.get("/strategies/{strategy_id}/validate")
async def validate_strategy(strategy_id: int):
    """Valida una estrategia de backup"""
    try:
        strategy = await strategy_repo.get_by_id(strategy_id)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estrategia no encontrada"
            )
        
        validation = await backup_service.validate_strategy(strategy)
        
        return {
            "strategy_id": strategy_id,
            "validation": validation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validando estrategia: {str(e)}"
        )

@router.get("/scheduled-jobs")
async def get_scheduled_jobs():
    """Obtiene información de los jobs programados"""
    try:
        jobs = scheduler.get_scheduled_jobs()
        return {"scheduled_jobs": jobs}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo jobs programados: {str(e)}"
        )