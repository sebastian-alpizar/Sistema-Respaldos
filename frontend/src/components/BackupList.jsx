import React, { useState, useMemo } from 'react';
import {
    Card,
    CardContent,
    Typography,
    Chip,
    IconButton,
    Box,
    Grid,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Tooltip,
} from '@mui/material';
import {
    PlayArrow,
    Edit,
    Delete,
    Schedule,
    Pause,
    CheckCircle,
    Error as ErrorIcon,
    AccessTime,
    CalendarToday,
} from '@mui/icons-material';
import { formatDate } from '../utils/formatDate';

const BackupList = ({ 
    strategies, 
    scheduledJobs, // ✅ Recibe los jobs programados del contexto
    onEdit, 
    onDelete, 
    onExecute, 
    onToggle,
    loading = false 
}) => {
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [selectedStrategy, setSelectedStrategy] = useState(null);
    const [jobDetailsOpen, setJobDetailsOpen] = useState(false);
    const [selectedJobs, setSelectedJobs] = useState([]);

    // ✅ Mapea los jobs a sus estrategias correspondientes
    const strategyJobsMap = useMemo(() => {
        const map = {};
        scheduledJobs.forEach(job => {
            if (job.strategy_id) {
                if (!map[job.strategy_id]) {
                    map[job.strategy_id] = [];
                }
                map[job.strategy_id].push(job);
            }
        });
        return map;
    }, [scheduledJobs]);

    const getTypeColor = (type) => {
        switch (type) {
            case 'full': return 'primary';
            case 'partial': return 'secondary';
            case 'incremental': return 'info';
            case 'custom': return 'warning';
            default: return 'default';
        }
    };

    const getPriorityColor = (priority) => {
        switch (priority) {
            case 'critical': return 'error';
            case 'high': return 'warning';
            case 'medium': return 'info';
            case 'low': return 'success';
            default: return 'default';
        }
    };

    const getJobStatusColor = (job) => {
        if (!job.next_run_time) return 'default';
        const nextRun = new Date(job.next_run_time);
        const now = new Date();
        return nextRun > now ? 'success' : 'warning';
    };

    const handleDeleteClick = (strategy) => {
        setSelectedStrategy(strategy);
        setDeleteDialogOpen(true);
    };

    const handleDeleteConfirm = () => {
        if (selectedStrategy) {
            onDelete(selectedStrategy.id);
        }
        setDeleteDialogOpen(false);
        setSelectedStrategy(null);
    };

    const handleViewJobs = (strategy) => {
        // ✅ Obtiene los jobs específicos de esta estrategia
        const strategyJobs = strategyJobsMap[strategy.id] || [];
        setSelectedJobs(strategyJobs);
        setJobDetailsOpen(true);
    };

    const getNextExecutionText = (strategy) => {
        const jobs = strategyJobsMap[strategy.id] || [];
        if (jobs.length === 0) {
            return strategy.is_active ? 'Programando...' : 'No programado';
        }
        
        const nextJob = jobs[0]; // Tomamos el primer job (debería haber solo uno por estrategia)
        if (!nextJob.next_run_time) return 'No programado';
        
        return formatDate.relative(new Date(nextJob.next_run_time));
    };

    const getJobCountForStrategy = (strategyId) => {
        return strategyJobsMap[strategyId]?.length || 0;
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
                <Typography>Cargando estrategias...</Typography>
            </Box>
        );
    }

    if (strategies.length === 0) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
                <Typography color="textSecondary">
                    No hay estrategias configuradas
                </Typography>
            </Box>
        );
    }

    return (
        <>
            <Grid container spacing={3}>
                {strategies.map((strategy) => {
                    const jobCount = getJobCountForStrategy(strategy.id);
                    const nextExecution = getNextExecutionText(strategy);
                    
                    return (
                        <Grid item xs={12} md={6} lg={4} key={strategy.id}>
                            <Card 
                                sx={{ 
                                    height: '100%',
                                    opacity: strategy.is_active ? 1 : 0.7,
                                    border: strategy.is_active ? '1px solid #e0e0e0' : '1px dashed #bdbdbd',
                                    position: 'relative'
                                }}
                            >
                                {/* Indicador de jobs programados */}
                                {jobCount > 0 && (
                                    <Box
                                        sx={{
                                            position: 'absolute',
                                            top: 8,
                                            right: 8,
                                            width: 8,
                                            height: 8,
                                            borderRadius: '50%',
                                            bgcolor: 'success.main',
                                            animation: 'pulse 2s infinite'
                                        }}
                                    />
                                )}
                                
                                <CardContent>
                                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                                        <Typography variant="h6" component="h2" noWrap sx={{ maxWidth: '70%' }}>
                                            {strategy.name}
                                        </Typography>
                                        <Chip
                                            label={strategy.is_active ? 'Activa' : 'Inactiva'}
                                            color={strategy.is_active ? 'success' : 'default'}
                                            size="small"
                                        />
                                    </Box>

                                    {strategy.description && (
                                        <Typography 
                                            variant="body2" 
                                            color="textSecondary" 
                                            sx={{ mb: 2 }}
                                            noWrap
                                        >
                                            {strategy.description}
                                        </Typography>
                                    )}

                                    <Box sx={{ mb: 2 }}>
                                        <Chip
                                            label={strategy.backup_type}
                                            color={getTypeColor(strategy.backup_type)}
                                            size="small"
                                            sx={{ mr: 1, mb: 1 }}
                                        />
                                        <Chip
                                            label={strategy.priority}
                                            color={getPriorityColor(strategy.priority)}
                                            size="small"
                                            sx={{ mr: 1, mb: 1 }}
                                        />
                                        <Chip
                                            label={`Retención: ${strategy.retention_days}d`}
                                            variant="outlined"
                                            size="small"
                                            sx={{ mb: 1 }}
                                        />
                                    </Box>

                                    {/* Información de programación y próximo ejecución */}
                                    <Box sx={{ mb: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
                                        <Typography variant="body2" sx={{ mb: 0.5 }}>
                                            <strong>Programación:</strong> {strategy.schedule_frequency} a las{' '}
                                            {strategy.schedule_time}
                                        </Typography>
                                        
                                        <Box display="flex" alignItems="center" gap={0.5}>
                                            <AccessTime fontSize="small" color="action" />
                                            <Typography variant="body2" color="textSecondary">
                                                <strong>Próxima ejecución:</strong> {nextExecution}
                                            </Typography>
                                        </Box>
                                        
                                        {jobCount > 0 && (
                                            <Box display="flex" alignItems="center" gap={0.5} sx={{ mt: 0.5 }}>
                                                <CalendarToday fontSize="small" color="success" />
                                                <Typography variant="body2" color="success.main">
                                                    {jobCount} job{jobCount !== 1 ? 's' : ''} programado{jobCount !== 1 ? 's' : ''}
                                                </Typography>
                                            </Box>
                                        )}
                                    </Box>

                                    <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                                        Creada: {formatDate.relative(strategy.created_at)}
                                    </Typography>

                                    <Box display="flex" justifyContent="space-between" alignItems="center">
                                        <Box>
                                            <Tooltip title="Ejecutar ahora">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => onExecute(strategy.id)}
                                                    color="primary"
                                                >
                                                    <PlayArrow />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title={strategy.is_active ? "Pausar" : "Activar"}>
                                                <IconButton
                                                    size="small"
                                                    onClick={() => onToggle(strategy.id)}
                                                    color={strategy.is_active ? "warning" : "success"}
                                                >
                                                    {strategy.is_active ? <Pause /> : <CheckCircle />}
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title="Editar">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => onEdit(strategy)}
                                                >
                                                    <Edit />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title="Eliminar">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => handleDeleteClick(strategy)}
                                                    color="error"
                                                >
                                                    <Delete />
                                                </IconButton>
                                            </Tooltip>
                                        </Box>

                                        <Tooltip title="Ver jobs programados">
                                            <Button
                                                size="small"
                                                startIcon={<Schedule />}
                                                onClick={() => handleViewJobs(strategy)}
                                                variant={jobCount > 0 ? "outlined" : "text"}
                                                color={jobCount > 0 ? "success" : "inherit"}
                                            >
                                                Jobs ({jobCount})
                                            </Button>
                                        </Tooltip>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    );
                })}
            </Grid>

            {/* Diálogo de confirmación de eliminación */}
            <Dialog
                open={deleteDialogOpen}
                onClose={() => setDeleteDialogOpen(false)}
            >
                <DialogTitle>Confirmar Eliminación</DialogTitle>
                <DialogContent>
                    <Typography>
                        ¿Estás seguro de que deseas eliminar la estrategia "{selectedStrategy?.name}"?
                        Esta acción no se puede deshacer.
                    </Typography>
                    {selectedStrategy && getJobCountForStrategy(selectedStrategy.id) > 0 && (
                        <Typography variant="body2" color="warning.main" sx={{ mt: 1 }}>
                            ⚠️ Esta estrategia tiene {getJobCountForStrategy(selectedStrategy.id)} job(s) programado(s) que serán eliminados.
                        </Typography>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialogOpen(false)}>
                        Cancelar
                    </Button>
                    <Button onClick={handleDeleteConfirm} color="error" variant="contained">
                        Eliminar
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Diálogo de detalles de jobs */}
            <Dialog
                open={jobDetailsOpen}
                onClose={() => setJobDetailsOpen(false)}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>
                    Jobs Programados - {selectedJobs[0]?.name?.replace('Backup: ', '') || 'Estrategia'}
                </DialogTitle>
                <DialogContent>
                    {selectedJobs.length === 0 ? (
                        <Box textAlign="center" py={3}>
                            <Schedule sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                            <Typography color="textSecondary" variant="h6">
                                No hay jobs programados
                            </Typography>
                            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                                Esta estrategia no tiene jobs activos en el programador.
                            </Typography>
                        </Box>
                    ) : (
                        <List>
                            {selectedJobs.map((job) => (
                                <ListItem 
                                    key={job.id}
                                    sx={{ 
                                        border: '1px solid',
                                        borderColor: 'divider',
                                        borderRadius: 1,
                                        mb: 1,
                                        bgcolor: 'background.default'
                                    }}
                                >
                                    <ListItemIcon>
                                        <Schedule color={getJobStatusColor(job)} />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={
                                            <Box display="flex" alignItems="center" gap={1}>
                                                <Typography variant="subtitle1">
                                                    {job.name}
                                                </Typography>
                                                <Chip 
                                                    label={job.next_run_time ? "Programado" : "Sin programar"} 
                                                    size="small"
                                                    color={getJobStatusColor(job)}
                                                />
                                            </Box>
                                        }
                                        secondary={
                                            <Box sx={{ mt: 1 }}>
                                                <Typography variant="body2">
                                                    <strong>ID:</strong> {job.id}
                                                </Typography>
                                                {job.strategy_id && (
                                                    <Typography variant="body2">
                                                        <strong>ID Estrategia:</strong> {job.strategy_id}
                                                    </Typography>
                                                )}
                                                {job.next_run_time ? (
                                                    <Typography variant="body2" color="success.main">
                                                        <strong>Próxima ejecución:</strong> {formatDate.full(job.next_run_time)}
                                                    </Typography>
                                                ) : (
                                                    <Typography variant="body2" color="text.secondary">
                                                        <strong>Próxima ejecución:</strong> No programado
                                                    </Typography>
                                                )}
                                            </Box>
                                        }
                                    />
                                </ListItem>
                            ))}
                        </List>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setJobDetailsOpen(false)}>
                        Cerrar
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};

export default BackupList;