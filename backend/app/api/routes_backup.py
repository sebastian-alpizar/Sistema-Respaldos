from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.strategy import Strategy, StrategyCreate, StrategyUpdate
from app.services.backup_service import BackupService
from app.repositories.strategy_repo import StrategyRepository

router = APIRouter(prefix="/api/backup", tags=["backup"])

@router.get("/strategies", response_model=List[Strategy])
async def get_strategies(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todas las estrategias de backup"""
    try:
        strategy_repo = StrategyRepository(db)
        if active_only:
            return await strategy_repo.get_active_strategies()
        return await strategy_repo.get_all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estrategias: {str(e)}"
        )

@router.get("/strategies/{strategy_id}", response_model=Strategy)
async def get_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene una estrategia específica"""
    strategy_repo = StrategyRepository(db)
    strategy = await strategy_repo.get_by_id(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estrategia no encontrada"
        )
    return strategy

@router.post("/strategies", response_model=Strategy, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy_data: StrategyCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crea una nueva estrategia de backup"""
    try:
        strategy_repo = StrategyRepository(db)
        backup_service = BackupService(db)
        
        # Validar la estrategia antes de crearla
        validation = await backup_service.validate_strategy(
            Strategy(**strategy_data.model_dump(), id=0, created_by=1, created_at="", updated_at="")
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
        
        # Crear estrategia (usuario 1 como creador por defecto)
        strategy = await strategy_repo.create(strategy_data, created_by=1)
        return strategy
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando estrategia: {str(e)}"
        )

@router.put("/strategies/{strategy_id}", response_model=Strategy)
async def update_strategy(
    strategy_id: int,
    strategy_data: StrategyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualiza una estrategia existente"""
    try:
        strategy_repo = StrategyRepository(db)
        strategy = await strategy_repo.update(strategy_id, strategy_data)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estrategia no encontrada"
            )
        return strategy
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando estrategia: {str(e)}"
        )

@router.delete("/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Elimina una estrategia"""
    try:
        strategy_repo = StrategyRepository(db)
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
async def execute_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Ejecuta una estrategia de backup inmediatamente"""
    try:
        strategy_repo = StrategyRepository(db)
        strategy = await strategy_repo.get_by_id(strategy_id)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estrategia no encontrada"
            )
        
        backup_service = BackupService(db)
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
async def toggle_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Activa/desactiva una estrategia"""
    try:
        strategy_repo = StrategyRepository(db)
        strategy = await strategy_repo.toggle_active(strategy_id)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estrategia no encontrada"
            )
        
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
async def validate_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Valida una estrategia de backup"""
    try:
        strategy_repo = StrategyRepository(db)
        strategy = await strategy_repo.get_by_id(strategy_id)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estrategia no encontrada"
            )
        
        backup_service = BackupService(db)
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
        from app.core.scheduler import backup_scheduler
        jobs = backup_scheduler.get_scheduled_jobs()
        return {"scheduled_jobs": jobs}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo jobs programados: {str(e)}"
        )