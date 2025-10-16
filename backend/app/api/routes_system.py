from fastapi import APIRouter, HTTPException, status
from app.core.config import settings
from app.utils.oracle_connection import OracleConnection
from app.services.email_service import EmailService
from app.core.scheduler import BackupScheduler
from app.repositories.strategy_repo import StrategyRepository
import logging

router = APIRouter(prefix="/api/system", tags=["system"])

oracle_connection = OracleConnection()
email_service = EmailService()
strategy_repo = StrategyRepository()
scheduler = BackupScheduler()

logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """Verifica el estado del sistema"""
    try:
        # Verificar conexión a Oracle
        oracle_healthy = False
        try:
            oracle_healthy = oracle_connection.check_archivelog_mode() is not None
        except:
            pass
        
        # Verificar programador
        scheduler_healthy = scheduler.scheduler.running
        
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en health check: {str(e)}"
        )

@router.get("/database/info")
async def get_database_info():
    """Obtiene información de la base de datos Oracle"""
    try:
        info = oracle_connection.get_database_info()
        if not info:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo obtener información de la base de datos"
            )
        
        # Verificar modo ARCHIVELOG
        archivelog_enabled = oracle_connection.check_archivelog_mode()
        info['archivelog_enabled'] = archivelog_enabled
        info['archivelog_warning'] = not archivelog_enabled
        
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo información de la BD: {str(e)}"
        )

@router.get("/database/archivelog")
async def check_archivelog():
    """Verifica el estado del modo ARCHIVELOG"""
    try:
        enabled = oracle_connection.check_archivelog_mode()
        return {
            "archivelog_enabled": enabled,
            "message": "Modo ARCHIVELOG habilitado" if enabled else "Modo ARCHIVELOG NO habilitado - Los backups pueden no ser consistentes"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verificando modo ARCHIVELOG: {str(e)}"
        )

@router.post("/email/test")
async def send_test_email(email: str):
    """Envía un email de prueba"""
    try:
        success = await email_service.send_test_email(email)
        
        if success:
            return {"message": "Email de prueba enviado exitosamente"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo enviar el email de prueba. Verifique la configuración SMTP."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando email de prueba: {str(e)}"
        )

@router.post("/scheduler/start")
async def start_scheduler():
    """Inicia el programador de backups"""
    try:
        scheduler.start()
        
        # Reprogramar todas las estrategias activas
        strategies = await strategy_repo.get_active_strategies()
        scheduler.reschedule_all_strategies(strategies)
        
        return {"message": "Programador iniciado exitosamente"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error iniciando programador: {str(e)}"
        )

@router.post("/scheduler/stop")
async def stop_scheduler():
    """Detiene el programador de backups"""
    try:
        scheduler.shutdown()
        return {"message": "Programador detenido exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deteniendo programador: {str(e)}"
        )

@router.get("/scheduler/status")
async def get_scheduler_status():
    """Obtiene el estado del programador"""
    try:
        jobs = scheduler.get_scheduled_jobs()
        
        return {
            "running": scheduler.scheduler.running,
            "scheduled_jobs_count": len(jobs),
            "scheduled_jobs": jobs
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo configuración: {str(e)}"
        )