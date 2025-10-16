from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import time

class BackupType(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    INCREMENTAL = "incremental"
    CUSTOM = "custom"

class BackupPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ScheduleFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    backup_type: BackupType
    priority: BackupPriority = BackupPriority.MEDIUM
    is_active: bool = True
    
    # Schedule Configuration
    schedule_frequency: ScheduleFrequency
    schedule_time: time
    schedule_days: Optional[List[int]] = None
    schedule_months: Optional[List[int]] = None
    
    # Backup Configuration
    tablespaces: Optional[List[str]] = None
    schemas: Optional[List[str]] = None
    tables: Optional[List[str]] = None
    include_archivelogs: bool = True
    compression: bool = True
    encryption: bool = False
    
    # Retention
    retention_days: int = 30
    
    # Advanced Options
    parallel_degree: Optional[int] = None
    max_backup_size: Optional[str] = None
    custom_parameters: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class StrategyCreate(StrategyBase):
    pass

class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    backup_type: Optional[BackupType] = None
    priority: Optional[BackupPriority] = None
    is_active: Optional[bool] = None
    schedule_frequency: Optional[ScheduleFrequency] = None
    schedule_time: Optional[time] = None
    schedule_days: Optional[List[int]] = None
    schedule_months: Optional[List[int]] = None
    tablespaces: Optional[List[str]] = None
    schemas: Optional[List[str]] = None
    tables: Optional[List[str]] = None
    include_archivelogs: Optional[bool] = None
    compression: Optional[bool] = None
    encryption: Optional[bool] = None
    retention_days: Optional[int] = None
    parallel_degree: Optional[int] = None
    max_backup_size: Optional[str] = None
    custom_parameters: Optional[Dict[str, Any]] = None

class Strategy(StrategyBase):
    id: int
    created_at: str
    updated_at: str
    created_by: int