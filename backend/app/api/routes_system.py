import asyncio
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.utils.oracle_connection import OracleConnection
from app.services.email_service import EmailService
from app.core.scheduler import backup_scheduler
from app.repositories.strategy_repo import StrategyRepository
import logging

router = APIRouter(prefix="/api/system", tags=["system"])

logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Verifica el estado del sistema"""
    try:
        # Verificar conexión a Oracle CORRECTAMENTE
        oracle_healthy = False
        try:
            info = OracleConnection.get_database_info()
            oracle_healthy = bool(info and 'name' in info)
        except:
            oracle_healthy = False
        
        # Verificar programador
        scheduler_healthy = backup_scheduler.scheduler.running
        
        # Verificar configuración de email
        email_configured = bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        
        return {
            "status": "healthy",
            "oracle_connection": "connected" if oracle_healthy else "disconnected",
            "scheduler": "running" if scheduler_healthy else "stopped",
            "email": "configured" if email_configured else "not_configured",
            "version": settings.APP_VERSION
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "oracle_connection": "unknown", 
            "scheduler": "unknown",
            "email": "unknown",
            "version": settings.APP_VERSION,
            "error": str(e)
        }

@router.get("/database/info")
async def get_database_info():
    """Obtiene información de la base de datos Oracle"""
    try:
        info = OracleConnection.get_database_info()
        if not info:
            raise HTTPException(
                status_code=503,
                detail="No se pudo obtener información de la base de datos"
            )
        
        # Verificar modo ARCHIVELOG
        archivelog_enabled = OracleConnection.check_archivelog_mode()
        info['archivelog_enabled'] = archivelog_enabled
        info['archivelog_warning'] = not archivelog_enabled
        
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo información de la BD: {str(e)}"
        )

@router.get("/database/archivelog")
async def check_archivelog():
    """Verifica el estado del modo ARCHIVELOG"""
    try:
        enabled = OracleConnection.check_archivelog_mode()
        return {
            "archivelog_enabled": enabled,
            "message": "Modo ARCHIVELOG habilitado" if enabled else "Modo ARCHIVELOG NO habilitado - Los backups pueden no ser consistentes"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error verificando modo ARCHIVELOG: {str(e)}"
        )

@router.post("/email/test")
async def send_test_email(email: str, db: AsyncSession = Depends(get_db)):
    """Envía un email de prueba"""
    try:
        email_service = EmailService()
        success = await email_service.send_test_email(email)
        
        if success:
            return {"message": "Email de prueba enviado exitosamente"}
        else:
            raise HTTPException(
                status_code=500,
                detail="No se pudo enviar el email de prueba. Verifique la configuración SMTP."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error enviando email de prueba: {str(e)}"
        )

@router.post("/scheduler/start")
async def start_scheduler(db: AsyncSession = Depends(get_db)):
    """Inicia el programador"""
    try:
        # Verificar estado actual
        was_running = backup_scheduler.scheduler.running
        
        if not was_running:
            # ✅ INICIALIZAR cargando estrategias desde la BD
            await backup_scheduler.initialize(db)
            await asyncio.sleep(0.5)  # Dar tiempo para que cargue
            
            message = "Scheduler iniciado correctamente con estrategias cargadas"
        else:
            message = "Scheduler ya estaba en ejecución"
        
        # Obtener estado actualizado
        jobs = backup_scheduler.get_scheduled_jobs()
        
        return {
            "status": "success",
            "running": backup_scheduler.scheduler.running,
            "was_running": was_running,
            "scheduled_jobs_count": len(jobs),
            "active_jobs_count": len(backup_scheduler.scheduler.get_jobs()),
            "message": message,
            "scheduled_jobs": jobs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error iniciando programador: {str(e)}"
        )

@router.post("/scheduler/stop")
async def stop_scheduler():
    """Detiene el programador"""
    try:
        # Verificar estado actual
        was_running = backup_scheduler.scheduler.running
        current_jobs = len(backup_scheduler.scheduler.get_jobs())
        
        if was_running:
            backup_scheduler.shutdown()
            
            # Pequeña pausa para que se detenga completamente
            import asyncio
            await asyncio.sleep(0.1)
        
        # Obtener estado actualizado
        jobs = backup_scheduler.get_scheduled_jobs()
        
        return {
            "status": "success",
            "running": backup_scheduler.scheduler.running,
            "was_running": was_running,
            "scheduled_jobs_count": len(jobs),
            "active_jobs_count": len(backup_scheduler.scheduler.get_jobs()),
            "message": "Scheduler detenido correctamente" if was_running else "Scheduler ya estaba detenido",
            "scheduled_jobs": jobs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deteniendo programador: {str(e)}"
        )

@router.get("/scheduler/status")
async def get_scheduler_status():
    """Obtiene el estado del programador"""
    try:
        jobs = backup_scheduler.get_scheduled_jobs()
        
        return {
            "running": backup_scheduler.scheduler.running,
            "scheduled_jobs_count": len(jobs),
            "scheduled_jobs": jobs
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado del programador: {str(e)}"
        )

@router.get("/config")
async def get_configuration():
    """Obtiene la configuración actual del sistema (sin contraseñas)"""
    try:
        return {
            "oracle_dsn": settings.ORACLE_DSN,
            "oracle_user": settings.ORACLE_USER,
            "smtp_server": settings.SMTP_SERVER,
            "smtp_port": settings.SMTP_PORT,
            "smtp_username": settings.SMTP_USERNAME,
            "notification_email": settings.NOTIFICATION_EMAIL,
            "backup_base_path": settings.BACKUP_BASE_PATH,
            "retention_days": settings.RETENTION_DAYS,
            "app_title": settings.APP_TITLE,
            "app_version": settings.APP_VERSION,
            "debug": settings.DEBUG
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo configuración: {str(e)}"
        )