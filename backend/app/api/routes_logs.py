from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi import status as http_status
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.log import Log, LogLevel, BackupStatus
from app.services.log_service import LogService
from app.repositories.log_repo import LogRepository

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get("/", response_model=List[Log])
async def get_logs(
    strategy_id: Optional[int] = None,
    level: Optional[LogLevel] = None,
    status: Optional[BackupStatus] = None,
    days: int = Query(7, ge=1, le=365),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene logs con filtros opcionales"""
    try:
        log_service = LogService(db)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        if strategy_id:
            logs = await log_service.get_strategy_logs(strategy_id, limit, offset)
            return logs
        else:
            logs = await log_service.get_logs_by_date_range(
                start_date, end_date, level, status
            )
            # Aplicar limit después de obtener los resultados
            return logs[:limit]
            
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo logs: {str(e)}"
        )

@router.get("/{log_id}", response_model=Log)
async def get_log(
    log_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene un log específico"""
    log_service = LogService(db)
    log = await log_service.get_log(log_id)
    if not log:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Log no encontrado"
        )
    return log

@router.get("/strategy/{strategy_id}", response_model=List[Log])
async def get_strategy_logs(
    strategy_id: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene logs de una estrategia específica"""
    try:
        log_service = LogService(db)
        logs = await log_service.get_strategy_logs(strategy_id, limit, offset)
        return logs
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo logs de estrategia: {str(e)}"
        )

@router.get("/statistics/backup")
async def get_backup_statistics(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene estadísticas de backups"""
    try:
        log_service = LogService(db)
        stats = await log_service.get_backup_statistics(days)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

@router.get("/export/csv")
async def export_logs_csv(
    start_date: datetime,
    end_date: datetime,
    level: Optional[LogLevel] = None,
    status: Optional[BackupStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """Exporta logs a formato CSV"""
    try:
        log_service = LogService(db)
        csv_content = await log_service.export_logs_to_csv(start_date, end_date)
        
        if not csv_content:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="No hay logs para exportar en el rango especificado"
            )
        
        # Crear respuesta con archivo CSV
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=backup_logs_{start_date.date()}_to_{end_date.date()}.csv"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exportando logs: {str(e)}"
        )

@router.delete("/{log_id}")
async def delete_log(
    log_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Elimina un log"""
    try:
        log_service = LogService(db)
        success = await log_service.delete_log(log_id)
        if not success:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Log no encontrado"
            )
        
        return {"message": "Log eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando log: {str(e)}"
        )