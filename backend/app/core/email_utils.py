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
        """Envía un email usando SMTP"""
        try:
            message = MIMEMultipart()
            message["From"] = settings.SMTP_USERNAME
            message["To"] = ", ".join(to_emails)
            message["Subject"] = subject
            
            # Parte de texto plano
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Parte HTML (opcional)
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Enviar email
            smtp = aiosmtplib.SMTP(
                hostname=settings.SMTP_SERVER,
                port=settings.SMTP_PORT
            )
            
            await smtp.connect()
            await smtp.starttls()
            await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            await smtp.send_message(message)
            await smtp.quit()
            
            logger.info(f"Email enviado exitosamente a {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {str(e)}")
            return False
    
    @staticmethod
    def create_backup_notification_template(
        strategy_name: str,
        status: str,
        start_time: str,
        end_time: str,
        duration: str,
        backup_size: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> tuple[str, str, str]:
        """Crea el contenido del email de notificación de backup"""
        
        subject = f"Backup {status} - {strategy_name}"
        
        # Cuerpo en texto plano
        text_body = f"""
Estado del Backup: {status.upper()}
Estrategia: {strategy_name}
Hora de inicio: {start_time}
Hora de finalización: {end_time}
Duración: {duration}
"""
        
        if backup_size:
            text_body += f"Tamaño del backup: {backup_size:.2f} MB\n"
        
        if error_message:
            text_body += f"Error: {error_message}\n"
        
        # Cuerpo en HTML
        status_color = "green" if status == "completed" else "red"
        html_body = f"""
<html>
    <body>
        <h2>Notificación de Backup Oracle</h2>
        <table border="1" cellpadding="8" style="border-collapse: collapse;">
            <tr><td><strong>Estado del Backup:</strong></td><td style="color: {status_color};"><strong>{status.upper()}</strong></td></tr>
            <tr><td><strong>Estrategia:</strong></td><td>{strategy_name}</td></tr>
            <tr><td><strong>Hora de inicio:</strong></td><td>{start_time}</td></tr>
            <tr><td><strong>Hora de finalización:</strong></td><td>{end_time}</td></tr>
            <tr><td><strong>Duración:</strong></td><td>{duration}</td></tr>
"""
        
        if backup_size:
            html_body += f'<tr><td><strong>Tamaño del backup:</strong></td><td>{backup_size:.2f} MB</td></tr>'
        
        if error_message:
            html_body += f'<tr><td><strong>Error:</strong></td><td style="color: red;">{error_message}</td></tr>'
        
        html_body += """
        </table>
        <br>
        <p><em>Sistema de Gestión de Respaldo Oracle</em></p>
    </body>
</html>
"""
        
        return subject, text_body, html_body