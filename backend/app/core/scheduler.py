# app/core/scheduler.py - VERSIÓN COMPLETAMENTE CORREGIDA
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, time
from typing import List, Dict, Any, Optional
import logging
from app.models.strategy import Strategy, ScheduleFrequency
from app.services.backup_service import BackupService
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class BackupScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduled_jobs = {} 

    async def initialize(self, db: AsyncSession):
        """Inicializa el scheduler cargando las estrategias activas de la BD"""
        try:
            from app.repositories.strategy_repo import StrategyRepository
            
            strategy_repo = StrategyRepository(db)
            active_strategies = await strategy_repo.get_active_strategies()
            
            logger.info(f"🔄 Cargando {len(active_strategies)} estrategias activas...")
            
            strategies_loaded = 0
            for strategy in active_strategies:
                success = self.schedule_strategy(strategy)
                if success:
                    strategies_loaded += 1
                    logger.info(f"✅ Estrategia cargada: {strategy.name} (ID: {strategy.id})")
                else:
                    logger.error(f"❌ Error cargando estrategia: {strategy.name} (ID: {strategy.id})")
            
            logger.info(f"📊 Resumen: {strategies_loaded}/{len(active_strategies)} estrategias cargadas exitosamente")
            
            # Iniciar el scheduler después de cargar las estrategias
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("✅ Scheduler iniciado con estrategias cargadas")
                
        except Exception as e:
            logger.error(f"❌ Error inicializando scheduler: {str(e)}")
            raise
    
    def start(self):
        """Inicia el programador"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Programador de backups iniciado")
    
    def shutdown(self):
        """Detiene el programador"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 Programador de backups detenido")
    
    def schedule_strategy(self, strategy: Strategy) -> bool:
        """Programa una estrategia de backup"""
        try:
            # Eliminar job existente si hay uno
            if strategy.id in self.scheduled_jobs:
                self.unschedule_strategy(strategy.id)
            
            # Crear trigger según la frecuencia
            trigger = self._create_trigger(strategy)
            if not trigger:
                logger.error(f"❌ No se pudo crear trigger para estrategia {strategy.id}")
                return False
            
            # Crear job
            job_id = f"backup_strategy_{strategy.id}"
            job = self.scheduler.add_job(
                self._execute_backup_wrapper,
                trigger=trigger,
                args=[strategy],
                id=job_id,
                name=f"Backup: {strategy.name}",
                replace_existing=True
            )
            
            self.scheduled_jobs[strategy.id] = job_id
            logger.info(f"✅ Estrategia programada: {strategy.name} (ID: {strategy.id})")
            logger.info(f"⏰ Próxima ejecución: {job.next_run_time}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error programando estrategia {strategy.id}: {str(e)}")
            return False
    
    def _create_trigger(self, strategy: Strategy):
        """Crea el trigger apropiado según la frecuencia de la estrategia"""
        schedule_time = strategy.schedule_time
        
        if strategy.schedule_frequency == ScheduleFrequency.DAILY:
            return CronTrigger(
                hour=schedule_time.hour,
                minute=schedule_time.minute,
                second=schedule_time.second
            )
        
        elif strategy.schedule_frequency == ScheduleFrequency.WEEKLY:
            if not strategy.schedule_days:
                logger.error("❌ Estrategia semanal requiere días de la semana")
                return None
            
            return CronTrigger(
                day_of_week=','.join(str(day) for day in strategy.schedule_days),
                hour=schedule_time.hour,
                minute=schedule_time.minute,
                second=schedule_time.second
            )
        
        elif strategy.schedule_frequency == ScheduleFrequency.MONTHLY:
            if not strategy.schedule_days:
                logger.error("❌ Estrategia mensual requiere días del mes")
                return None
            
            return CronTrigger(
                day=','.join(str(day) for day in strategy.schedule_days),
                hour=schedule_time.hour,
                minute=schedule_time.minute,
                second=schedule_time.second
            )
        
        elif strategy.schedule_frequency == ScheduleFrequency.CUSTOM:
            logger.warning("⚠️ Frecuencia personalizada no implementada completamente")
            return None
        
        return None
    
    def unschedule_strategy(self, strategy_id: int) -> bool:
        """Elimina la programación de una estrategia"""
        try:
            if strategy_id in self.scheduled_jobs:
                job_id = self.scheduled_jobs[strategy_id]
                self.scheduler.remove_job(job_id)
                del self.scheduled_jobs[strategy_id]
                logger.info(f"🗑️ Programación eliminada para estrategia {strategy_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error eliminando programación de estrategia {strategy_id}: {str(e)}")
            return False
    
    async def _execute_backup_wrapper(self, strategy: Strategy):
        """Wrapper para ejecutar el backup desde el scheduler"""
        try:
            # Crear una nueva sesión de BD para el job del scheduler
            async with AsyncSessionLocal() as db:
                backup_service = BackupService(db)
                logger.info(f"🏃 Ejecutando backup programado: {strategy.name}")
                await backup_service.execute_backup_strategy(strategy)
        except Exception as e:
            logger.error(f"❌ Error en ejecución programada de {strategy.name}: {str(e)}")
    
    def schedule_immediate_backup(self, strategy: Strategy) -> bool:
        """Programa un backup para ejecución inmediata"""
        try:
            job_id = f"immediate_backup_{strategy.id}_{datetime.now().timestamp()}"
            job = self.scheduler.add_job(
                self._execute_backup_wrapper,
                trigger=DateTrigger(run_date=datetime.now()),
                args=[strategy],
                id=job_id
            )
            
            logger.info(f"⚡ Backup inmediato programado: {strategy.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error programando backup inmediato: {str(e)}")
            return False
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Obtiene información de todos los jobs programados"""
        jobs_info = []
        
        try:
            for job in self.scheduler.get_jobs():
                job_info = {
                    'id': job.id,
                    'name': getattr(job, 'name', 'Unknown'),
                    'strategy_id': self._extract_strategy_id(job.id),
                }
                
                # Manejo seguro de next_run_time
                try:
                    next_run = getattr(job, 'next_run_time', None)
                    if next_run and hasattr(next_run, 'isoformat'):
                        job_info['next_run_time'] = next_run.isoformat()
                        job_info['next_run_time_formatted'] = next_run.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        job_info['next_run_time'] = None
                        job_info['next_run_time_formatted'] = "No programado"
                except:
                    job_info['next_run_time'] = None
                    job_info['next_run_time_formatted'] = "Error"
                
                jobs_info.append(job_info)
                
        except Exception as e:
            logger.error(f"❌ Error crítico en get_scheduled_jobs: {str(e)}")
            jobs_info = [{
                'id': 'error',
                'name': 'Error obteniendo jobs',
                'next_run_time': None,
                'next_run_time_formatted': 'Error',
                'strategy_id': None
            }]
        
        return jobs_info
    
    def _extract_strategy_id(self, job_id: str) -> Optional[int]:
        """Extrae el ID de estrategia del job ID"""
        try:
            if job_id.startswith('backup_strategy_'):
                return int(job_id.split('_')[-1])
            return None
        except:
            return None
    
    def reschedule_all_strategies(self, strategies: List[Strategy]):
        """Reprograma todas las estrategias (útil al iniciar la aplicación)"""
        logger.info("🔄 Reprogramando todas las estrategias...")
        
        # Limpiar jobs existentes
        for strategy_id in list(self.scheduled_jobs.keys()):
            self.unschedule_strategy(strategy_id)
        
        # Programar estrategias activas
        active_strategies = [s for s in strategies if s.is_active]
        for strategy in active_strategies:
            self.schedule_strategy(strategy)
        
        logger.info(f"✅ {len(active_strategies)} estrategias activas reprogramadas")

# Crear instancia global del scheduler
backup_scheduler = BackupScheduler()