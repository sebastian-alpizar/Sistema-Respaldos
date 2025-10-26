from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime

class LogLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class BackupStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class LogBase(BaseModel):
    strategy_id: int
    level: LogLevel
    status: BackupStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    backup_size_mb: Optional[float] = None
    rman_output: Optional[str] = None
    rman_log_content: Optional[str] = None  # Contenido completo del archivo .log
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class LogCreate(LogBase):
    pass

class LogUpdate(BaseModel):
    status: Optional[BackupStatus] = None
    level: Optional[LogLevel] = None  # Agregar este campo
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    backup_size_mb: Optional[float] = None
    rman_output: Optional[str] = None
    rman_log_content: Optional[str] = None  # Añadir este campo
    error_message: Optional[str] = None

class Log(LogBase):
    id: int
    created_at: datetime