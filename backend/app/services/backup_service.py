import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.strategy import Strategy, BackupType
from app.models.log import BackupStatus, LogLevel
from app.models.log import LogCreate, LogUpdate
from app.services.oracle_service import OracleService
from app.services.email_service import EmailService
from app.services.log_service import LogService
from app.utils.file_utils import FileUtils
from app.core.config import settings

logger = logging.getLogger(__name__)

class BackupService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.oracle_service = OracleService()
        self.email_service = EmailService()
        self.log_service = LogService(db)  # Pasar la sesión de BD al servicio de logs
        self.file_utils = FileUtils()
    
    async def execute_backup_strategy(self, strategy: Strategy) -> Dict[str, Any]:
        """Ejecuta una estrategia de backup completa - VERSIÓN CORREGIDA"""
        
        # Crear registro de log inicial
        log_data = LogCreate(
            strategy_id=strategy.id,
            level=LogLevel.INFO,
            status=BackupStatus.RUNNING,
            message=f"Iniciando backup: {strategy.name}",
            details={
                'backup_type': strategy.backup_type,
                'priority': strategy.priority,
                'schedule': f"{strategy.schedule_frequency} at {strategy.schedule_time}"
            },
            start_time=datetime.now()
        )
        
        log_entry = await self.log_service.create_log(log_data)
        
        try:
            # Preparar ruta de backup
            backup_filename = FileUtils.generate_backup_filename(
                strategy.name, 
                strategy.backup_type
            )
            backup_path = FileUtils.get_backup_path(strategy.id, '')
            
            # Generar script RMAN
            strategy_dict = strategy.model_dump()
            rman_script = self.oracle_service.generate_rman_script(
                strategy_dict, 
                backup_path
            )
            
            logger.info(f"Ejecutando backup para estrategia: {strategy.name}")
            
            # Ejecutar backup RMAN
            backup_result = self.oracle_service.execute_rman_backup(
                rman_script, 
                strategy.id
            )

            # OBTENER EL CONTENIDO DEL LOG RMAN
            log_content = backup_result.get('log_content', '')
            logger.info(f"Contenido del log RMAN obtenido: {len(log_content)} caracteres")
            
            # Actualizar log con resultados
            end_time = datetime.now()
            duration = (end_time - log_entry.start_time).total_seconds()
            
            # ✅ USAR LOS DATOS CALCULADOS EN execute_rman_backup
            backup_files = backup_result.get('backup_files', [])
            backup_size_bytes = backup_result.get('backup_size_bytes', 0)
            backup_size_mb = backup_size_bytes / (1024 * 1024)  # Convertir a MB
            
            logger.info(f"📊 Resumen backup: {len(backup_files)} archivos, {backup_size_mb:.2f} MB")
            
            if backup_result['success']:
                # Verificar integridad del backup
                backup_verified = self.oracle_service.verify_backup(backup_files)
                
                if backup_verified:
                    status = BackupStatus.COMPLETED
                    message = f"Backup completado exitosamente: {strategy.name}"
                    level = LogLevel.INFO
                else:
                    status = BackupStatus.FAILED
                    message = f"Backup completado pero verificación falló: {strategy.name}"
                    level = LogLevel.ERROR
                    backup_size_mb = None
            else:
                status = BackupStatus.FAILED
                message = f"Error en ejecución de backup: {strategy.name}"
                level = LogLevel.ERROR
                backup_size_mb = None
            
            # Actualizar registro de log
            await self.log_service.update_log(
                log_entry.id,
                LogUpdate(
                    status=status,
                    level=level,
                    message=message,
                    end_time=end_time,
                    duration_seconds=duration,
                    backup_size_mb=backup_size_mb,  # Ya calculado correctamente
                    rman_output=backup_result.get('output', ''),
                    rman_log_content=log_content,
                    error_message=backup_result['error'] if not backup_result['success'] else None,
                    details={
                        'backup_files_count': len(backup_files),
                        'backup_files': [os.path.basename(f) for f in backup_files],
                        'strategy_type': strategy.backup_type,
                        'parallel_degree': strategy.parallel_degree
                    }
                )
            )
            
            # Enviar notificación
            await self._send_backup_notification(
                strategy, 
                status, 
                log_entry.start_time, 
                end_time, 
                duration, 
                backup_size_mb,
                backup_result.get('error'),
                len(backup_files)
            )
            
            # Limpiar backups antiguos
            if status == BackupStatus.COMPLETED:
                deleted_count = FileUtils.cleanup_old_backups(
                    strategy.id, 
                    strategy.retention_days
                )
                logger.info(f"Backups antiguos eliminados: {deleted_count}")
            
            return {
                'success': backup_result['success'] and status == BackupStatus.COMPLETED,
                'log_id': log_entry.id,
                'backup_files': backup_files,
                'backup_size_mb': backup_size_mb,
                'backup_size_bytes': backup_size_bytes,
                'duration_seconds': duration,
                'error': backup_result.get('error'),
                'log_content': log_content
            }
            
        except Exception as e:
            logger.error(f"Error crítico en ejecución de backup: {str(e)}")
            
            # Actualizar log con error
            await self.log_service.update_log(
                log_entry.id,
                LogUpdate(
                    status=BackupStatus.FAILED,
                    level=LogLevel.CRITICAL,
                    message=f"Error crítico: {str(e)}",
                    end_time=datetime.now(),
                    duration_seconds=(datetime.now() - log_entry.start_time).total_seconds(),
                    error_message=str(e)
                )
            )
            
            # Enviar notificación de error
            await self._send_backup_notification(
                strategy,
                BackupStatus.FAILED,
                log_entry.start_time,
                datetime.now(),
                (datetime.now() - log_entry.start_time).total_seconds(),
                None,
                str(e)
            )
            
            return {
                'success': False,
                'log_id': log_entry.id,
                'error': str(e)
            }
    
    async def _send_backup_notification(
        self,
        strategy: Strategy,
        status: BackupStatus,
        start_time: datetime,
        end_time: datetime,
        duration: float,
        backup_size: Optional[float],
        error_message: Optional[str],
        backup_files_count: int = 0  
    ):
        """Envía notificación por email del resultado del backup"""
        try:
            duration_str = f"{duration:.2f} segundos"
            
            subject, text_body, html_body = self.email_service.create_backup_notification_template(
                strategy_name=strategy.name,
                status=status.value,
                start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
                duration=duration_str,
                backup_size=backup_size,
                error_message=error_message,
                backup_files_count=backup_files_count
            )
            
            await self.email_service.send_notification(
                subject=subject,
                text_body=text_body,
                html_body=html_body
            )
            
        except Exception as e:
            logger.warning(f"Error enviando notificación (puede continuar): {str(e)}")
            # No lanzar excepción para que el backup continúe
    
    async def validate_strategy(self, strategy: Strategy) -> Dict[str, Any]:
        """Valida una estrategia de backup antes de ejecutarla"""
        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Verificar modo ARCHIVELOG
        archivelog_enabled = self.oracle_service.connection.check_archivelog_mode()
        if not archivelog_enabled:
            validation_result['warnings'].append(
                "El modo ARCHIVELOG no está habilitado. Los backups pueden no ser consistentes."
            )
        
        # Verificar tablespaces existentes (para backups parciales)
        if strategy.backup_type == 'partial' and strategy.tablespaces:
            db_info = self.oracle_service.connection.get_database_info()
            existing_tablespaces = [ts['name'] for ts in db_info.get('tablespaces', [])]
            
            for ts in strategy.tablespaces:
                if ts not in existing_tablespaces:
                    validation_result['errors'].append(
                        f"Tablespace no encontrado: {ts}"
                    )
        
        # Verificar espacio en disco
        backup_path = FileUtils.get_backup_path(strategy.id, '')
        if not FileUtils.ensure_directory(backup_path):
            validation_result['errors'].append(
                f"No se pudo crear/acceder al directorio de backup: {backup_path}"
            )
        
        validation_result['valid'] = len(validation_result['errors']) == 0
        
        return validation_result