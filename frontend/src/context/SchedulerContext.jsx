// context/SchedulerContext.js - CORREGIDO Y UNIFICADO
import React, { createContext, useContext, useState, useEffect } from 'react';
import { backupService } from '../api/backupService';
import { systemService } from '../api/systemService';

const SchedulerContext = createContext();

export const useScheduler = () => {
    const context = useContext(SchedulerContext);
    if (!context) {
        throw new Error('useScheduler debe ser usado dentro de un SchedulerProvider');
    }
    return context;
};

export const SchedulerProvider = ({ children }) => {
    const [strategies, setStrategies] = useState([]);
    const [schedulerStatus, setSchedulerStatus] = useState({ 
        running: false, 
        scheduled_jobs_count: 0, 
        scheduled_jobs: [] 
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Estado del scheduler
    const refreshSchedulerStatus = async () => {
        try {
            const response = await systemService.getSchedulerStatus();
            setSchedulerStatus(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        }
    };

    const startScheduler = async () => {
        try {
            setLoading(true);
            const response = await systemService.startScheduler();
            setSchedulerStatus({
                running: response.data.running,
                scheduled_jobs_count: response.data.scheduled_jobs_count,
                scheduled_jobs: response.data.scheduled_jobs
            });
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const stopScheduler = async () => {
        try {
            setLoading(true);
            const response = await systemService.stopScheduler();
            setSchedulerStatus({
                running: response.data.running,
                scheduled_jobs_count: response.data.scheduled_jobs_count,
                scheduled_jobs: response.data.scheduled_jobs
            });
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    // Gestión de estrategias
    const fetchStrategies = async (activeOnly = false) => {
        try {
            setLoading(true);
            setError(null);
            const response = await backupService.getStrategies(activeOnly);
            setStrategies(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    const createStrategy = async (strategyData) => {
        try {
            setError(null);
            const response = await backupService.createStrategy(strategyData);
            await fetchStrategies();
            await refreshSchedulerStatus(); // Actualizar jobs después de crear
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        }
    };

    const updateStrategy = async (id, strategyData) => {
        try {
            setError(null);
            const response = await backupService.updateStrategy(id, strategyData);
            await fetchStrategies();
            await refreshSchedulerStatus(); // Actualizar jobs después de actualizar
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        }
    };

    const deleteStrategy = async (id) => {
        try {
            setError(null);
            await backupService.deleteStrategy(id);
            await fetchStrategies();
            await refreshSchedulerStatus(); // Actualizar jobs después de eliminar
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        }
    };

    const executeStrategy = async (id) => {
        try {
            setError(null);
            const response = await backupService.executeStrategy(id);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        }
    };

    const toggleStrategy = async (id) => {
        try {
            setError(null);
            const response = await backupService.toggleStrategy(id);
            await fetchStrategies();
            await refreshSchedulerStatus(); // Actualizar jobs después de toggle
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        }
    };

    const validateStrategy = async (id) => {
        try {
            setError(null);
            const response = await backupService.validateStrategy(id);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        }
    };

    // Efectos
    useEffect(() => {
        fetchStrategies();
        refreshSchedulerStatus();
        
        // Actualizar estado del scheduler cada 30 segundos
        const interval = setInterval(() => {
            refreshSchedulerStatus();
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    const value = {
        // Estado
        strategies,
        schedulerStatus,
        loading,
        error,
        
        // Gestión del scheduler
        refreshSchedulerStatus,
        startScheduler,
        stopScheduler,
        
        // Gestión de estrategias
        fetchStrategies,
        createStrategy,
        updateStrategy,
        deleteStrategy,
        executeStrategy,
        toggleStrategy,
        validateStrategy,
    };

    return (
        <SchedulerContext.Provider value={value}>
            {children}
        </SchedulerContext.Provider>
    );
};