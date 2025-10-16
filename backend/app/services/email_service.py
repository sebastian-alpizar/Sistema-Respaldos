from typing import List, Optional
import logging
from app.core.email_utils import EmailUtils
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.email_utils = EmailUtils()
    
    async def send_notification(
        self,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        custom_recipients: Optional[List[str]] = None
    ) -> bool:
        """Envía una notificación por email"""
        try:
            recipients = custom_recipients or [settings.NOTIFICATION_EMAIL]
            
            if not recipients:
                logger.warning("No hay destinatarios configurados para notificaciones")
                return False
            
            success = await self.email_utils.send_email(
                subject=subject,
                body=text_body,
                to_emails=recipients,
                html_body=html_body
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error en servicio de email: {str(e)}")
            return False
    
    def create_backup_notification_template(
        self,
        strategy_name: str,
        status: str,
        start_time: str,
        end_time: str,
        duration: str,
        backup_size: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> tuple[str, str, str]:
        """Crea el template para notificación de backup"""
        return self.email_utils.create_backup_notification_template(
            strategy_name=strategy_name,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            backup_size=backup_size,
            error_message=error_message
        )
    
    async def send_test_email(self, test_email: str) -> bool:
        """Envía un email de prueba"""
        try:
            subject = "Prueba de Notificación - Sistema de Respaldo Oracle"
            text_body = """
            Este es un email de prueba del Sistema de Gestión de Respaldo Oracle.
            
            Si recibes este mensaje, la configuración SMTP es correcta.
            
            Fecha y hora de envío: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            """
            
            html_body = """
            <html>
                <body>
                    <h2>Prueba de Notificación</h2>
                    <p>Este es un email de prueba del <strong>Sistema de Gestión de Respaldo Oracle</strong>.</p>
                    <p>Si recibes este mensaje, la configuración SMTP es correcta.</p>
                    <p><em>Fecha y hora de envío: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</em></p>
                </body>
            </html>
            """
            
            success = await self.send_notification(
                subject=subject,
                text_body=text_body,
                html_body=html_body,
                custom_recipients=[test_email]
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error enviando email de prueba: {str(e)}")
            return False