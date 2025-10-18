import apiClient from './apiClient';

export const logService = {
    // Logs generales
    getLogs: (params = {}) => 
        apiClient.get('/logs/', { params }),

    getLog: (id) => 
        apiClient.get(`/logs/${id}`),

    getStrategyLogs: (strategyId, limit = 100, offset = 0) => 
        apiClient.get(`/logs/strategy/${strategyId}`, { 
        params: { limit, offset } 
        }),

    deleteLog: (id) => 
        apiClient.delete(`/logs/${id}`),

    // Estadísticas
    getBackupStatistics: (days = 30) => 
        apiClient.get('/logs/statistics/backup', { params: { days } }),

    // Exportación
    exportLogsToCSV: (startDate, endDate, level, status) => 
        apiClient.get('/logs/export/csv', { 
            params: { start_date: startDate, end_date: endDate, level, status },
            responseType: 'blob'
        }),
};