import React, { createContext, useContext, useState, useEffect } from 'react';
import { systemService } from '../api/systemService';

const ConfigContext = createContext();

export const useConfig = () => {
    const context = useContext(ConfigContext);
    if (!context) {
        throw new Error('useConfig debe ser usado dentro de un ConfigProvider');
    }
    return context;
};

export const ConfigProvider = ({ children }) => {
    const [systemHealth, setSystemHealth] = useState(null);
    const [databaseInfo, setDatabaseInfo] = useState(null);
    const [archiveLogMode, setArchiveLogMode] = useState(null);
    const [schedulerStatus, setSchedulerStatus] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const refreshSystemHealth = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await systemService.getHealthStatus();
            setSystemHealth(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    const refreshDatabaseInfo = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await systemService.getDatabaseInfo();
            setDatabaseInfo(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            setDatabaseInfo(null);
        } finally {
            setLoading(false);
        }
    };

    const checkArchiveLogMode = async () => {
        try {
            const response = await systemService.checkArchiveLogMode();
            setArchiveLogMode(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        return null;
        }
    };

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
            await systemService.startScheduler();
            await refreshSchedulerStatus();
            await refreshSystemHealth();
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        }
    };

    const stopScheduler = async () => {
        try {
            await systemService.stopScheduler();
            await refreshSchedulerStatus();
            await refreshSystemHealth();
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        }
    };

    useEffect(() => {
        refreshSystemHealth();
        refreshDatabaseInfo();
        refreshSchedulerStatus();
        
        // Actualizar cada 30 segundos
        const interval = setInterval(() => {
            refreshSystemHealth();
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    const value = {
        systemHealth,
        databaseInfo,
        archiveLogMode,
        schedulerStatus,
        loading,
        error,
        refreshSystemHealth,
        refreshDatabaseInfo,
        checkArchiveLogMode,
        refreshSchedulerStatus,
        startScheduler,
        stopScheduler,
    };

    return (
        <ConfigContext.Provider value={value}>
            {children}
        </ConfigContext.Provider>
    );
};