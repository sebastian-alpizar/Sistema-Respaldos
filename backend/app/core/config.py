import os
from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Oracle Database Configuration
    ORACLE_USER: str = os.getenv("ORACLE_USER", "backup_admin")
    ORACLE_PASSWORD: str = os.getenv("ORACLE_PASSWORD", "")
    ORACLE_DSN: str = os.getenv("ORACLE_DSN", "localhost:1521/XE")
    
    # RMAN Configuration
    RMAN_PATH: str = os.getenv("RMAN_PATH", "rman")  # Ruta al ejecutable RMAN
    COMPRESSION_ENABLED: bool = os.getenv("COMPRESSION_ENABLED", "True").lower() == "true"
    
    # SMTP Configuration
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    NOTIFICATION_EMAIL: str = os.getenv("NOTIFICATION_EMAIL", "")
    
    # Application Configuration
    APP_TITLE: str = "Sistema de Gestión de Respaldo Oracle"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Backup Configuration
    BACKUP_BASE_PATH: str = os.getenv("BACKUP_BASE_PATH", "./backups")
    RETENTION_DAYS: int = int(os.getenv("RETENTION_DAYS", "30"))
    MAX_BACKUP_THREADS: int = int(os.getenv("MAX_BACKUP_THREADS", "4"))
    
    model_config = ConfigDict(env_file=".env")

settings = Settings()