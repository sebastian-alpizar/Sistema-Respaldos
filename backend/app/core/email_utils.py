import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailUtils:
    @staticmethod
    async def send_email(
        subject: str,
        body: str,
        to_emails: List[str],
        html_body: Optional[str] = None
    ) -> bool:
        """Envía un email usando SMTP - CONFIGURACIÓN CORREGIDA PARA GMAIL"""
        try:
            # Validar configuración
            if not all([settings.SMTP_SERVER, settings.SMTP_PORT, settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
                logger.error("❌ Configuración SMTP incompleta")
                return False
            
            message = MIMEMultipart()
            message["From"] = settings.SMTP_USERNAME
            message["To"] = ", ".join(to_emails)
            message["Subject"] = subject
            
            # Parte de texto plano
            text_part = MIMEText(body, "plain", "utf-8")
            message.attach(text_part)
            
            # Parte HTML (opcional)
            if html_body:
                html_part = MIMEText(html_body, "html", "utf-8")
                message.attach(html_part)
            
            logger.info(f"🔧 Conectando a SMTP: {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
            
            # Configuración específica para Gmail**
            smtp = aiosmtplib.SMTP(
                hostname=settings.SMTP_SERVER,
                port=settings.SMTP_PORT,
                use_tls=True, 
                timeout=30
            )
            
            await smtp.connect()
            logger.info("✅ Conexión SMTP establecida")
            
            logger.info("🔑 Iniciando autenticación...")
            await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            logger.info("✅ Autenticación SMTP exitosa")
            
            await smtp.send_message(message)
            await smtp.quit()
            
            logger.info(f"✅ Email enviado exitosamente a {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando email: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def create_backup_notification_template(
        strategy_name: str,
        status: str,
        start_time: str,
        end_time: str,
        duration: str,
        backup_size: Optional[float] = None,
        error_message: Optional[str] = None,
        backup_files_count: int = 0
    ) -> tuple[str, str, str]:
        """Crea el contenido del email de notificación de backup"""
        
        # Determinar emoji y color según estado
        if status.lower() == "completed":
            status_emoji = "✅"
            status_color = "green"
            subject = f"✅ Backup Completado - {strategy_name}"
        elif status.lower() == "failed":
            status_emoji = "❌"
            status_color = "red"
            subject = f"❌ Backup Fallido - {strategy_name}"
        else:
            status_emoji = "⚠️"
            status_color = "orange"
            subject = f"⚠️ Backup {status} - {strategy_name}"
        
        # Cuerpo en texto plano
        text_body = f"""
            {status_emoji} Estado del Backup: {status.upper()}

            Estrategia: {strategy_name}
            Hora de inicio: {start_time}
            Hora de finalización: {end_time}
            Duración: {duration}
            Archivos generados: {backup_files_count}
            """
        
        if backup_size:
            text_body += f"Tamaño del backup: {backup_size:.2f} MB\n"
        
        if error_message:
            text_body += f"\n❌ ERROR:\n{error_message}\n"
        
        text_body += f"\n--\nSistema de Gestión de Respaldo Oracle"
        
        # Cuerpo en HTML
        html_body = f"""
<html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .status {{ color: {status_color}; font-weight: bold; font-size: 18px; }}
            .details {{ background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 15px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 10px; border-bottom: 1px solid #eee; }}
            .error {{ background-color: #ffe6e6; color: #d00; padding: 15px; border-radius: 5px; margin-top: 15px; }}
            .footer {{ margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{status_emoji} Notificación de Backup Oracle</h1>
            <p class="status">Estado: {status.upper()}</p>
        </div>
        
        <div class="details">
            <table>
                <tr><td><strong>Estrategia:</strong></td><td>{strategy_name}</td></tr>
                <tr><td><strong>Hora de inicio:</strong></td><td>{start_time}</td></tr>
                <tr><td><strong>Hora de finalización:</strong></td><td>{end_time}</td></tr>
                <tr><td><strong>Duración:</strong></td><td>{duration}</td></tr>
                <tr><td><strong>Archivos generados:</strong></td><td>{backup_files_count}</td></tr>
"""
        
        if backup_size:
            html_body += f'<tr><td><strong>Tamaño del backup:</strong></td><td>{backup_size:.2f} MB</td></tr>'
        
        html_body += """
            </table>
        </div>
"""
        
        if error_message:
            html_body += f"""
        <div class="error">
            <h3>❌ Error Detectado:</h3>
            <pre>{error_message}</pre>
        </div>
"""
        
        html_body += """
        <div class="footer">
            <p><em>Sistema de Gestión de Respaldo Oracle</em></p>
        </div>
    </body>
</html>
"""
        return subject, text_body, html_body