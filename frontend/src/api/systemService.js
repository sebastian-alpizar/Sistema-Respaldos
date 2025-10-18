import apiClient from './apiClient';

export const systemService = {
    // Verificar estado del sistema
    getHealthStatus: () => 
        apiClient.get('/system/health'),

    // Obtener información de la base de datos
    getDatabaseInfo: () => 
        apiClient.get('/system/database/info'),

    // Verificar modo ARCHIVELOG
    checkArchiveLogMode: () => 
        apiClient.get('/system/database/archivelog'),

    // Probar configuración de email
    testEmail: (email) => 
        apiClient.post('/system/email/test', null, { params: { email } }),

    // Control del programador
    startScheduler: () => 
        apiClient.post('/system/scheduler/start'),

    stopScheduler: () => 
        apiClient.post('/system/scheduler/stop'),

    getSchedulerStatus: () => 
        apiClient.get('/system/scheduler/status'),

    // Obtener configuración
    getConfiguration: () => 
        apiClient.get('/system/config'),
};