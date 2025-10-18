import React, { createContext, useContext, useState, useEffect } from 'react';
import { backupService } from '../api/backupService';

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
    const [scheduledJobs, setScheduledJobs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

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

    const fetchScheduledJobs = async () => {
        try {
            const response = await backupService.getScheduledJobs();
            setScheduledJobs(response.data.scheduled_jobs || []);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        }
    };

    const createStrategy = async (strategyData) => {
        try {
            setError(null);
            const response = await backupService.createStrategy(strategyData);
            await fetchStrategies();
            await fetchScheduledJobs();
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
            await fetchScheduledJobs();
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
            await fetchScheduledJobs();
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
            await fetchScheduledJobs();
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

    useEffect(() => {
        fetchStrategies();
        fetchScheduledJobs();
        
        // Actualizar jobs programados cada minuto
        const interval = setInterval(() => {
            fetchScheduledJobs();
        }, 60000);

        return () => clearInterval(interval);
    }, []);

    const value = {
        strategies,
        scheduledJobs,
        loading,
        error,
        fetchStrategies,
        fetchScheduledJobs,
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