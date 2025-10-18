import apiClient from './apiClient';

export const backupService = {
    // Estrategias
    getStrategies: (activeOnly = false) => 
        apiClient.get('/backup/strategies', { params: { active_only: activeOnly } }),

    getStrategy: (id) => 
        apiClient.get(`/backup/strategies/${id}`),

    createStrategy: (strategyData) => 
        apiClient.post('/backup/strategies', strategyData),

    updateStrategy: (id, strategyData) => 
        apiClient.put(`/backup/strategies/${id}`, strategyData),

    deleteStrategy: (id) => 
        apiClient.delete(`/backup/strategies/${id}`),

    // Ejecución de backups
    executeStrategy: (id) => 
        apiClient.post(`/backup/strategies/${id}/execute`),

    toggleStrategy: (id) => 
        apiClient.post(`/backup/strategies/${id}/toggle`),

    validateStrategy: (id) => 
        apiClient.get(`/backup/strategies/${id}/validate`),

    // Jobs programados
    getScheduledJobs: () => 
        apiClient.get('/backup/scheduled-jobs'),
};