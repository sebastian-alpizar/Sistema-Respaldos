import React, { useState, useEffect } from 'react';
import {
    Grid,
    Card,
    CardContent,
    Typography,
    Box,
    Button,
    Chip,
    LinearProgress,
    Alert,
} from '@mui/material';
import {
    Storage,
    Schedule,
    Backup,
    Warning,
    PlayArrow,
    Stop,
} from '@mui/icons-material';
import { useConfig } from '../context/ConfigContext';
import { useScheduler } from '../context/SchedulerContext';
import { logService } from '../api/logService';

const Dashboard = () => {
    const { 
        systemHealth, 
        databaseInfo,
        refreshSystemHealth 
    } = useConfig();

    const { 
        strategies, 
        schedulerStatus,
        startScheduler, 
        stopScheduler 
    } = useScheduler();
    
    const [statistics, setStatistics] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadStatistics();
    }, []);

    const loadStatistics = async () => {
        try {
            setLoading(true);
            const response = await logService.getBackupStatistics(30);
            setStatistics(response.data);
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'connected': return 'success';
            case 'running': return 'success';
            case 'disconnected': return 'error';
            case 'stopped': return 'warning';
            default: return 'default';
        }
    };

    const activeStrategies = strategies.filter(s => s.is_active);
    const inactiveStrategies = strategies.filter(s => !s.is_active);

    return (
        <Box>
        <Typography variant="h4" gutterBottom>
            Dashboard
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 4 }}>
            Resumen del Sistema de Gestión de Respaldo Oracle
        </Typography>

        {/* Alertas del sistema */}
        {systemHealth && (
            <Box sx={{ mb: 3 }}>
            {systemHealth.oracle_connection === 'disconnected' && (
                <Alert severity="error" sx={{ mb: 1 }}>
                La conexión a Oracle no está disponible
                </Alert>
            )}
            {!schedulerStatus.running && (
                <Alert severity="warning" sx={{ mb: 1 }}>
                El programador de backups está detenido
                </Alert>
            )}
            {databaseInfo?.archivelog_warning && (
                <Alert severity="warning">
                El modo ARCHIVELOG no está habilitado - Los backups pueden no ser consistentes
                </Alert>
            )}
            </Box>
        )}

        {/* Tarjetas de estado */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
            <Card>
                <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                    <Storage color="primary" />
                    <Box>
                    <Typography color="textSecondary" gutterBottom>
                        Base de Datos
                    </Typography>
                    <Typography variant="h5" component="div">
                        {systemHealth?.oracle_connection === 'connected' ? 'Conectada' : 'Desconectada'}
                    </Typography>
                    </Box>
                </Box>
                <Chip
                    label={systemHealth?.oracle_connection}
                    color={getStatusColor(systemHealth?.oracle_connection)}
                    size="small"
                    sx={{ mt: 1 }}
                />
                </CardContent>
            </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
            <Card>
                <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                    <Schedule color="secondary" />
                    <Box>
                    <Typography color="textSecondary" gutterBottom>
                        Programador
                    </Typography>
                    <Typography variant="h5" component="div">
                        {schedulerStatus?.running ? 'Activo' : 'Inactivo'}
                    </Typography>
                    </Box>
                </Box>
                <Chip
                    label={schedulerStatus?.running ? 'running' : 'stopped'}
                    color={getStatusColor(schedulerStatus?.running ? 'running' : 'stopped')}
                    size="small"
                    sx={{ mt: 1 }}
                />
                </CardContent>
            </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
            <Card>
                <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                    <Backup color="success" />
                    <Box>
                    <Typography color="textSecondary" gutterBottom>
                        Estrategias
                    </Typography>
                    <Typography variant="h5" component="div">
                        {activeStrategies.length}/{strategies.length}
                    </Typography>
                    </Box>
                </Box>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    {inactiveStrategies.length} inactivas
                </Typography>
                </CardContent>
            </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
            <Card>
                <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                    <Warning color={schedulerStatus.scheduled_jobs_count > 0 ? "success" : "disabled"} />
                    <Box>
                    <Typography color="textSecondary" gutterBottom>
                        Jobs Activos
                    </Typography>
                    <Typography variant="h5" component="div">
                        {schedulerStatus.scheduled_jobs_count}
                    </Typography>
                    </Box>
                </Box>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    Programados
                </Typography>
                </CardContent>
            </Card>
            </Grid>
        </Grid>

        {/* Control del programador */}
        <Card sx={{ mb: 4 }}>
            <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                <Typography variant="h6" gutterBottom>
                    Control del Programador
                </Typography>

                {schedulerStatus?.running && (
                    <Typography variant="body2" color="textSecondary">
                        El programador está ejecutándose jobs automaticamente
                    </Typography>
                )}

                </Box>
                <Box display="flex" gap={1}>
                {schedulerStatus?.running ? (
                    <Button
                    startIcon={<Stop />}
                    onClick={stopScheduler}
                    color="warning"
                    variant="outlined"
                    >
                    Detener Programador
                    </Button>
                ) : (
                    <Button
                    startIcon={<PlayArrow />}
                    onClick={startScheduler}
                    color="success"
                    variant="contained"
                    >
                    Iniciar Programador
                    </Button>
                )}
                <Button onClick={refreshSystemHealth} variant="outlined">
                    Actualizar
                </Button>
                </Box>
            </Box>
            </CardContent>
        </Card>

        {/* Estadísticas de backups */}
        {statistics && (
            <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
                <Card>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                    Estadísticas de Backups (Últimos 30 días)
                    </Typography>
                    
                    <Box sx={{ mt: 2 }}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2">Tasa de éxito</Typography>
                        <Typography variant="body2" fontWeight="bold">
                        {statistics.success_rate}%
                        </Typography>
                    </Box>
                    <LinearProgress 
                        variant="determinate" 
                        value={statistics.success_rate} 
                        color={statistics.success_rate > 90 ? "success" : statistics.success_rate > 70 ? "warning" : "error"}
                        sx={{ height: 8, borderRadius: 4 }}
                    />
                    </Box>

                    <Grid container spacing={2} sx={{ mt: 1 }}>
                    <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                        Total
                        </Typography>
                        <Typography variant="h6">
                        {statistics.total_backups}
                        </Typography>
                    </Grid>
                    <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                        Exitosos
                        </Typography>
                        <Typography variant="h6" color="success.main">
                        {statistics.completed}
                        </Typography>
                    </Grid>
                    <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                        Fallidos
                        </Typography>
                        <Typography variant="h6" color="error.main">
                        {statistics.failed}
                        </Typography>
                    </Grid>
                    <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                        Tamaño Total
                        </Typography>
                        <Typography variant="h6">
                        {statistics.total_size_mb.toFixed(2)} MB
                        </Typography>
                    </Grid>
                    </Grid>
                </CardContent>
                </Card>
            </Grid>

            <Grid item xs={12} md={6}>
                <Card>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                    Información de la Base de Datos
                    </Typography>
                    
                    {databaseInfo ? (
                    <Box>
                        <Grid container spacing={1}>
                        <Grid item xs={6}>
                            <Typography variant="body2" color="textSecondary">
                            Nombre
                            </Typography>
                            <Typography variant="body2">
                            {databaseInfo.name}
                            </Typography>
                        </Grid>
                        <Grid item xs={6}>
                            <Typography variant="body2" color="textSecondary">
                            Modo
                            </Typography>
                            <Typography variant="body2">
                            {databaseInfo.log_mode}
                            </Typography>
                        </Grid>
                        <Grid item xs={6}>
                            <Typography variant="body2" color="textSecondary">
                            Tablespaces
                            </Typography>
                            <Typography variant="body2">
                            {databaseInfo.tablespaces?.length || 0}
                            </Typography>
                        </Grid>
                        <Grid item xs={6}>
                            <Typography variant="body2" color="textSecondary">
                            Esquemas
                            </Typography>
                            <Typography variant="body2">
                            {databaseInfo.schemas?.length || 0}
                            </Typography>
                        </Grid>
                        </Grid>
                        
                        <Box sx={{ mt: 2 }}>
                        <Chip
                            label={databaseInfo.archivelog_enabled ? 'ARCHIVELOG Habilitado' : 'ARCHIVELOG Deshabilitado'}
                            color={databaseInfo.archivelog_enabled ? 'success' : 'error'}
                            size="small"
                        />
                        </Box>
                    </Box>
                    ) : (
                    <Typography color="textSecondary">
                        No se pudo obtener información de la base de datos
                    </Typography>
                    )}
                </CardContent>
                </Card>
            </Grid>
            </Grid>
        )}
        </Box>
    );
};

export default Dashboard;