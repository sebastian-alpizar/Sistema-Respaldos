from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, Sequence
from sqlalchemy.dialects.oracle import VARCHAR2, NUMBER, TIMESTAMP, CLOB
from sqlalchemy.sql import func
from app.core.database import Base

class UserModel(Base):
    __tablename__ = "backup_users"

    # CAMBIAR: Usar Sequence en lugar de autoincrement
    id = Column(Integer, Sequence('backup_users_id_seq'), primary_key=True)
    username = Column(VARCHAR2(50), unique=True, index=True, nullable=False)
    email = Column(VARCHAR2(100), unique=True, index=True, nullable=False)
    full_name = Column(VARCHAR2(100), nullable=False)
    role = Column(VARCHAR2(20), default="dba", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

class StrategyModel(Base):
    __tablename__ = "backup_strategies"

    # CAMBIAR: Usar Sequence en lugar de autoincrement
    id = Column(Integer, Sequence('backup_strategies_id_seq'), primary_key=True)
    name = Column(VARCHAR2(100), nullable=False, index=True)
    description = Column(CLOB)
    backup_type = Column(VARCHAR2(20), nullable=False)
    priority = Column(VARCHAR2(20), default="medium")
    is_active = Column(Boolean, default=True)
    
    # Schedule Configuration
    schedule_frequency = Column(VARCHAR2(20), nullable=False)
    schedule_time = Column(VARCHAR2(8), nullable=False)
    schedule_days = Column(CLOB)
    schedule_months = Column(CLOB)
    
    # Backup Configuration
    tablespaces = Column(CLOB)
    schemas = Column(CLOB)
    tables = Column(CLOB)
    include_archivelogs = Column(Boolean, default=True)
    compression = Column(Boolean, default=True)
    encryption = Column(Boolean, default=False)
    
    # Retention
    retention_days = Column(Integer, default=30)
    
    # Advanced Options
    parallel_degree = Column(Integer)
    max_backup_size = Column(VARCHAR2(50))
    custom_parameters = Column(CLOB)
    
    # Metadata
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class LogModel(Base):
    __tablename__ = "backup_logs"

    # CAMBIAR: Usar Sequence en lugar de autoincrement
    id = Column(Integer, Sequence('backup_logs_id_seq'), primary_key=True)
    strategy_id = Column(Integer, nullable=False, index=True)
    level = Column(VARCHAR2(20), nullable=False)
    status = Column(VARCHAR2(20), nullable=False)
    message = Column(CLOB, nullable=False)
    details = Column(CLOB)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP)
    duration_seconds = Column(Float)
    backup_size_mb = Column(Float)
    rman_output = Column(CLOB)
    rman_log_content = Column(CLOB)
    error_message = Column(CLOB)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())