import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Button,
    Grid,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    TextField,
    Paper,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Alert,
    Card,
    CardContent,
    Tab,
    Tabs
} from '@mui/material';
import {
    Download,
    Refresh,
    FilterList,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { es } from 'date-fns/locale';
import { formatDate } from '../utils/formatDate';
import LogTable from '../components/LogTable';
import { logService } from '../api/logService';

const LogsPage = () => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [filters, setFilters] = useState({
        strategy_id: '',
        level: '',
        status: '',
        days: 7,
        start_date: null,
        end_date: null,
    });
    const [selectedLog, setSelectedLog] = useState(null);
    const [detailDialogOpen, setDetailDialogOpen] = useState(false);
    const [statistics, setStatistics] = useState(null);
    const [activeTab, setActiveTab] = useState(0);

    useEffect(() => {
        loadLogs();
        loadStatistics();
    }, []);

    // Función para formatear el log de RMAN
    const formatRmanLog = (logContent) => {
        if (!logContent) return 'No hay contenido de log disponible';
        
        // Dividir en líneas y limpiar
        const lines = logContent.split('\n').filter(line => line.trim());
        
        return lines.map((line, index) => {
            // Detectar tipos de línea para colorear
            let color = 'text.primary';
            let bgcolor = 'transparent';
            let fontWeight = 'normal';
            let padding = '2px 0';
            
            // Líneas de error
            if (line.includes('RMAN-') || line.includes('Error') || line.includes('error')) {
                color = 'error.main';
                fontWeight = 'bold';
            }
            // Líneas de éxito
            else if (line.includes('finalizado') || line.includes('completado') || line.includes('exitoso')) {
                color = 'success.main';
            }
            // Líneas de advertencia
            else if (line.includes('Advertencia') || line.includes('Warning')) {
                color = 'warning.main';
            }
            // Líneas de comando
            else if (line.startsWith('RMAN>') || line.includes('CONFIGURE') || line.includes('BACKUP')) {
                color = 'primary.main';
                fontWeight = 'medium';
            }
            // Encabezados/secciones
            else if (line.includes('====') || line.includes('----') || line.includes('Empezando backup')) {
                color = 'text.secondary';
                fontWeight = 'bold';
                bgcolor = 'action.hover';
                padding = '4px 8px';
            }
            
            return (
                <Box
                    key={index}
                    sx={{
                        color,
                        fontWeight,
                        backgroundColor: bgcolor,
                        padding,
                        fontFamily: 'monospace',
                        fontSize: '0.75rem',
                        lineHeight: '1.2',
                        borderBottom: bgcolor !== 'transparent' ? '1px solid' : 'none',
                        borderColor: 'divider'
                    }}
                >
                    {line}
                </Box>
            );
        });
    };

    const loadLogs = async () => {
        try {
            setLoading(true);
            const params = {
                ...filters,
                start_date: filters.start_date?.toISOString(),
                end_date: filters.end_date?.toISOString(),
            };
        
        // Limpiar parámetros vacíos
        Object.keys(params).forEach(key => {
            if (!params[key] && params[key] !== 0) {
            delete params[key];
            }
        });

        const response = await logService.getLogs(params);
            setLogs(response.data);
        } catch (error) {
            console.error('Error cargando logs:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadStatistics = async () => {
        try {
            const response = await logService.getBackupStatistics(30);
            setStatistics(response.data);
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        }
    };

    const handleFilterChange = (field) => (event) => {
        const value = event.target.value;
        setFilters(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleDateChange = (field) => (newValue) => {
        setFilters(prev => ({
            ...prev,
            [field]: newValue
        }));
    };

    const handleApplyFilters = () => {
        loadLogs();
    };

    const handleClearFilters = () => {
        setFilters({
        strategy_id: '',
        level: '',
        status: '',
        days: 7,
        start_date: null,
        end_date: null,
        });
    };

    const handleExportCSV = async () => {
        try {
            const startDate = filters.start_date || new Date(Date.now() - filters.days * 24 * 60 * 60 * 1000);
            const endDate = filters.end_date || new Date();
            
            const response = await logService.exportLogsToCSV(
                startDate.toISOString(),
                endDate.toISOString(),
                filters.level || undefined,
                filters.status || undefined
            );

            // Crear y descargar archivo
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `backup_logs_${formatDate.dateOnly(startDate)}_to_${formatDate.dateOnly(endDate)}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exportando logs:', error);
        }
    };

    const handleViewLog = (log) => {
        setSelectedLog(log);
        setDetailDialogOpen(true);
    };

    const handleDeleteLog = async (logId) => {
        if (window.confirm('¿Estás seguro de que deseas eliminar este log?')) {
            try {
                await logService.deleteLog(logId);
                loadLogs();
            } catch (error) {
                console.error('Error eliminando log:', error);
            }
        }
    };

    const getStatusSummary = () => {
        const summary = {
            completed: logs.filter(log => log.status === 'completed').length,
            failed: logs.filter(log => log.status === 'failed').length,
            running: logs.filter(log => log.status === 'running').length,
            cancelled: logs.filter(log => log.status === 'cancelled').length,
        };
        
        const total = logs.length;
        const successRate = total > 0 ? (summary.completed / total * 100).toFixed(1) : 0;
        
        return { ...summary, total, successRate };
    };

    const statusSummary = getStatusSummary();

    return (
        <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Box>
            <Typography variant="h4" gutterBottom>
                Logs de Backups
            </Typography>
            <Typography variant="body1" color="textSecondary">
                Monitorea y audita la ejecución de tus backups
            </Typography>
            </Box>
            
            <Box display="flex" gap={1}>
            <Button
                startIcon={<Download />}
                onClick={handleExportCSV}
                variant="outlined"
            >
                Exportar CSV
            </Button>
            <Button
                startIcon={<Refresh />}
                onClick={loadLogs}
                variant="contained"
            >
                Actualizar
            </Button>
            </Box>
        </Box>

        {/* Resumen de estadísticas */}
        {statistics && (
            <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
                <Card>
                <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                    Total Backups
                    </Typography>
                    <Typography variant="h4">
                    {statistics.total_backups}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                    Últimos {statistics.period}
                    </Typography>
                </CardContent>
                </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <Card>
                <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                    Tasa de Éxito
                    </Typography>
                    <Typography variant="h4" color="success.main">
                    {statistics.success_rate}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                    {statistics.completed} exitosos
                    </Typography>
                </CardContent>
                </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <Card>
                <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                    Fallidos
                    </Typography>
                    <Typography variant="h4" color="error.main">
                    {statistics.failed}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                    {statistics.most_common_errors?.length || 0} tipos de error
                    </Typography>
                </CardContent>
                </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <Card>
                <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                    Tamaño Total
                    </Typography>
                    <Typography variant="h4">
                    {(statistics.total_size_mb / 1024).toFixed(2)} GB
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                    {statistics.average_duration_seconds}s promedio
                    </Typography>
                </CardContent>
                </Card>
            </Grid>
            </Grid>
        )}

        {/* Filtros */}
        <Paper sx={{ p: 2, mb: 3 }}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
            <FilterList color="action" />
            <Typography variant="h6">Filtros</Typography>
            </Box>

            <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={2}>
                <FormControl fullWidth size="small">
                <InputLabel>Nivel</InputLabel>
                <Select
                    value={filters.level}
                    onChange={handleFilterChange('level')}
                    label="Nivel"
                >
                    <MenuItem value="">Todos</MenuItem>
                    <MenuItem value="info">Info</MenuItem>
                    <MenuItem value="warning">Warning</MenuItem>
                    <MenuItem value="error">Error</MenuItem>
                    <MenuItem value="critical">Critical</MenuItem>
                </Select>
                </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
                <FormControl fullWidth size="small">
                <InputLabel>Estado</InputLabel>
                <Select
                    value={filters.status}
                    onChange={handleFilterChange('status')}
                    label="Estado"
                >
                    <MenuItem value="">Todos</MenuItem>
                    <MenuItem value="completed">Completado</MenuItem>
                    <MenuItem value="running">Ejecutándose</MenuItem>
                    <MenuItem value="failed">Fallido</MenuItem>
                    <MenuItem value="cancelled">Cancelado</MenuItem>
                </Select>
                </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
                <FormControl fullWidth size="small">
                <InputLabel>Período</InputLabel>
                <Select
                    value={filters.days}
                    onChange={handleFilterChange('days')}
                    label="Período"
                >
                    <MenuItem value={1}>Últimas 24h</MenuItem>
                    <MenuItem value={7}>Última semana</MenuItem>
                    <MenuItem value={30}>Último mes</MenuItem>
                    <MenuItem value={90}>Últimos 3 meses</MenuItem>
                    <MenuItem value={365}>Último año</MenuItem>
                    <MenuItem value={0}>Personalizado</MenuItem>
                </Select>
                </FormControl>
            </Grid>

            {filters.days === 0 && (
                <>
                <Grid item xs={12} sm={6} md={2}>
                    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={es}>
                    <DatePicker
                        label="Desde"
                        value={filters.start_date}
                        onChange={handleDateChange('start_date')}
                        renderInput={(params) => <TextField {...params} size="small" fullWidth />}
                    />
                    </LocalizationProvider>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={es}>
                    <DatePicker
                        label="Hasta"
                        value={filters.end_date}
                        onChange={handleDateChange('end_date')}
                        renderInput={(params) => <TextField {...params} size="small" fullWidth />}
                    />
                    </LocalizationProvider>
                </Grid>
                </>
            )}

            <Grid item xs={12} sm={6} md={2}>
                <Box display="flex" gap={1}>
                <Button
                    onClick={handleApplyFilters}
                    variant="contained"
                    size="small"
                    fullWidth
                >
                    Aplicar
                </Button>
                <Button
                    onClick={handleClearFilters}
                    variant="outlined"
                    size="small"
                    fullWidth
                >
                    Limpiar
                </Button>
                </Box>
            </Grid>
            </Grid>
        </Paper>

        {/* Resumen de estado actual */}
        {statusSummary.total > 0 && (
            <Box display="flex" gap={1} sx={{ mb: 2 }} flexWrap="wrap">
            <Chip
                label={`Total: ${statusSummary.total}`}
                variant="outlined"
            />
            <Chip
                label={`Exitosos: ${statusSummary.completed}`}
                color="success"
                variant="outlined"
            />
            <Chip
                label={`Fallidos: ${statusSummary.failed}`}
                color="error"
                variant="outlined"
            />
            <Chip
                label={`En ejecución: ${statusSummary.running}`}
                color="info"
                variant="outlined"
            />
            <Chip
                label={`Tasa de éxito: ${statusSummary.successRate}%`}
                color={statusSummary.successRate > 90 ? "success" : statusSummary.successRate > 70 ? "warning" : "error"}
            />
            </Box>
        )}

        {/* Tabla de logs */}
        <LogTable
            logs={logs}
            onViewLog={handleViewLog}
            onDeleteLog={handleDeleteLog}
            loading={loading}
        />

        {/* Diálogo de detalles del log */}
        
        <Dialog
            open={detailDialogOpen}
            onClose={() => {
                setDetailDialogOpen(false);
                setActiveTab(0); // Resetear pestaña al cerrar
            }}
            maxWidth="lg"
            fullWidth
            sx={{
                '& .MuiDialog-paper': {
                    height: '80vh'
                }
            }}
        >
            <DialogTitle>
                Detalles del Log - ID: {selectedLog?.id}
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    Estrategia #{selectedLog?.strategy_id} - {selectedLog?.message}
                </Typography>
            </DialogTitle>
            
            <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column' }}>
                <Tabs 
                    value={activeTab} 
                    onChange={(e, newValue) => setActiveTab(newValue)}
                    sx={{ 
                        borderBottom: 1, 
                        borderColor: 'divider',
                        px: 2,
                        pt: 1
                    }}
                >
                    <Tab label="Información General" />
                    <Tab label="Log RMAN Completo" />
                    <Tab label="Resumen" />
                </Tabs>

                <Box sx={{ flex: 1, overflow: 'auto' }}>
                    {selectedLog && (
                        <>
                            {/* Pestaña 1: Información General */}
                            {activeTab === 0 && (
                                <Box sx={{ p: 3 }}>
                                    <Grid container spacing={2}>
                                        <Grid item xs={12} sm={6}>
                                            <Typography variant="subtitle2" color="textSecondary">
                                                Estrategia
                                            </Typography>
                                            <Typography variant="body1">
                                                #{selectedLog.strategy_id}
                                            </Typography>
                                        </Grid>
                                        <Grid item xs={12} sm={6}>
                                            <Typography variant="subtitle2" color="textSecondary">
                                                Estado
                                            </Typography>
                                            <Chip
                                                label={selectedLog.status}
                                                color={
                                                    selectedLog.status === 'completed' ? 'success' :
                                                    selectedLog.status === 'failed' ? 'error' :
                                                    selectedLog.status === 'running' ? 'info' : 'default'
                                                }
                                                size="small"
                                            />
                                        </Grid>
                                        <Grid item xs={12} sm={6}>
                                            <Typography variant="subtitle2" color="textSecondary">
                                                Nivel
                                            </Typography>
                                            <Chip
                                                label={selectedLog.level}
                                                color={
                                                    selectedLog.level === 'error' ? 'error' :
                                                    selectedLog.level === 'warning' ? 'warning' :
                                                    selectedLog.level === 'critical' ? 'error' : 'info'
                                                }
                                                size="small"
                                            />
                                        </Grid>
                                        <Grid item xs={12} sm={6}>
                                            <Typography variant="subtitle2" color="textSecondary">
                                                Tamaño
                                            </Typography>
                                            <Typography variant="body1">
                                                {selectedLog.backup_size_mb ? `${selectedLog.backup_size_mb.toFixed(2)} MB` : 'N/A'}
                                            </Typography>
                                        </Grid>
                                        <Grid item xs={12} sm={6}>
                                            <Typography variant="subtitle2" color="textSecondary">
                                                Inicio
                                            </Typography>
                                            <Typography variant="body1">
                                                {formatDate.full(selectedLog.start_time)}
                                            </Typography>
                                        </Grid>
                                        <Grid item xs={12} sm={6}>
                                            <Typography variant="subtitle2" color="textSecondary">
                                                Duración
                                            </Typography>
                                            <Typography variant="body1">
                                                {selectedLog.duration_seconds ? `${selectedLog.duration_seconds}s` : 'N/A'}
                                            </Typography>
                                        </Grid>
                                        <Grid item xs={12}>
                                            <Typography variant="subtitle2" color="textSecondary">
                                                Mensaje
                                            </Typography>
                                            <Typography variant="body1" sx={{ mt: 1 }}>
                                                {selectedLog.message}
                                            </Typography>
                                        </Grid>
                                        {selectedLog.error_message && (
                                            <Grid item xs={12}>
                                                <Alert severity="error" sx={{ mt: 1 }}>
                                                    <Typography variant="subtitle2" gutterBottom>
                                                        Error:
                                                    </Typography>
                                                    <Typography variant="body2">
                                                        {selectedLog.error_message}
                                                    </Typography>
                                                </Alert>
                                            </Grid>
                                        )}
                                        {selectedLog.details && Object.keys(selectedLog.details).length > 0 && (
                                            <Grid item xs={12}>
                                                <Typography variant="subtitle2" color="textSecondary">
                                                    Detalles Adicionales
                                                </Typography>
                                                <Paper variant="outlined" sx={{ p: 2, mt: 1 }}>
                                                    <pre style={{ margin: 0, fontSize: '0.875rem' }}>
                                                        {JSON.stringify(selectedLog.details, null, 2)}
                                                    </pre>
                                                </Paper>
                                            </Grid>
                                        )}
                                    </Grid>
                                </Box>
                            )}

                            {/* Pestaña 2: Log RMAN Completo */}
                            {activeTab === 1 && (
                                <Box sx={{ p: 0 }}>
                                    <Box sx={{ 
                                        p: 2, 
                                        borderBottom: 1, 
                                        borderColor: 'divider',
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        backgroundColor: 'background.default'
                                    }}>
                                        <Typography variant="subtitle1">
                                            Log de Ejecución RMAN
                                        </Typography>
                                        <Chip 
                                            label={`${selectedLog.rman_log_content?.length || 0} caracteres`} 
                                            size="small" 
                                            variant="outlined" 
                                        />
                                    </Box>
                                    <Box sx={{ 
                                        p: 2, 
                                        backgroundColor: 'grey.50',
                                        fontFamily: 'monospace',
                                        fontSize: '0.75rem',
                                        lineHeight: '1.2',
                                        height: '400px',
                                        overflow: 'auto'
                                    }}>
                                        {formatRmanLog(selectedLog.rman_log_content)}
                                    </Box>
                                </Box>
                            )}

                            {/* Pestaña 3: Resumen del Log */}
                            {activeTab === 2 && (
                                <Box sx={{ p: 3 }}>
                                    <Typography variant="h6" gutterBottom>
                                        Resumen de Ejecución
                                    </Typography>
                                    
                                    {selectedLog.rman_log_content && (
                                        <Grid container spacing={2}>
                                            <Grid item xs={12}>
                                                <Alert 
                                                    severity={
                                                        selectedLog.status === 'completed' ? 'success' : 
                                                        selectedLog.status === 'failed' ? 'error' : 'info'
                                                    }
                                                >
                                                    <Typography variant="subtitle2">
                                                        Estado: {selectedLog.status.toUpperCase()}
                                                    </Typography>
                                                    <Typography variant="body2">
                                                        {selectedLog.message}
                                                    </Typography>
                                                </Alert>
                                            </Grid>

                                            {/* Estadísticas del log RMAN */}
                                            <Grid item xs={12} md={6}>
                                                <Paper variant="outlined" sx={{ p: 2 }}>
                                                    <Typography variant="subtitle2" gutterBottom>
                                                        Información del Backup
                                                    </Typography>
                                                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                                        <Box display="flex" justifyContent="space-between">
                                                            <Typography variant="body2">Duración:</Typography>
                                                            <Typography variant="body2" fontWeight="medium">
                                                                {selectedLog.duration_seconds ? `${selectedLog.duration_seconds}s` : 'N/A'}
                                                            </Typography>
                                                        </Box>
                                                        <Box display="flex" justifyContent="space-between">
                                                            <Typography variant="body2">Tamaño:</Typography>
                                                            <Typography variant="body2" fontWeight="medium">
                                                                {selectedLog.backup_size_mb ? `${selectedLog.backup_size_mb.toFixed(2)} MB` : 'N/A'}
                                                            </Typography>
                                                        </Box>
                                                        <Box display="flex" justifyContent="space-between">
                                                            <Typography variant="body2">Archivos:</Typography>
                                                            <Typography variant="body2" fontWeight="medium">
                                                                {selectedLog.rman_log_content?.includes('.BKP') ? 
                                                                    (selectedLog.rman_log_content.match(/\.BKP/g) || []).length : 0
                                                                }
                                                            </Typography>
                                                        </Box>
                                                    </Box>
                                                </Paper>
                                            </Grid>

                                            <Grid item xs={12} md={6}>
                                                <Paper variant="outlined" sx={{ p: 2 }}>
                                                    <Typography variant="subtitle2" gutterBottom>
                                                        Análisis del Log
                                                    </Typography>
                                                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                                        <Box display="flex" justifyContent="space-between">
                                                            <Typography variant="body2">Líneas de log:</Typography>
                                                            <Typography variant="body2" fontWeight="medium">
                                                                {selectedLog.rman_log_content?.split('\n').length || 0}
                                                            </Typography>
                                                        </Box>
                                                        <Box display="flex" justifyContent="space-between">
                                                            <Typography variant="body2">Errores:</Typography>
                                                            <Typography variant="body2" fontWeight="medium" color="error.main">
                                                                {(selectedLog.rman_log_content?.match(/RMAN-\d+/g) || []).length}
                                                            </Typography>
                                                        </Box>
                                                        <Box display="flex" justifyContent="space-between">
                                                            <Typography variant="body2">Advertencias:</Typography>
                                                            <Typography variant="body2" fontWeight="medium" color="warning.main">
                                                                {(selectedLog.rman_log_content?.match(/Advertencia/g) || []).length}
                                                            </Typography>
                                                        </Box>
                                                    </Box>
                                                </Paper>
                                            </Grid>

                                            {/* Vista previa del log */}
                                            <Grid item xs={12}>
                                                <Paper variant="outlined" sx={{ p: 2 }}>
                                                    <Typography variant="subtitle2" gutterBottom>
                                                        Vista Previa del Log
                                                    </Typography>
                                                    <Box sx={{ 
                                                        backgroundColor: 'grey.100',
                                                        p: 1,
                                                        borderRadius: 1,
                                                        maxHeight: '150px',
                                                        overflow: 'auto',
                                                        fontFamily: 'monospace',
                                                        fontSize: '0.7rem'
                                                    }}>
                                                        {selectedLog.rman_log_content?.substring(0, 500)}...
                                                    </Box>
                                                </Paper>
                                            </Grid>
                                        </Grid>
                                    )}
                                </Box>
                            )}
                        </>
                    )}
                </Box>
            </DialogContent>
            
            <DialogActions sx={{ p: 2 }}>
                <Button 
                    onClick={() => {
                        setDetailDialogOpen(false);
                        setActiveTab(0);
                    }}
                >
                    Cerrar
                </Button>
            </DialogActions>
        </Dialog>
        
        </Box>
    );
};

export default LogsPage;