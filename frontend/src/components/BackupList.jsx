import React, { useState } from 'react';
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
} from '@mui/material';
import {
    PlayArrow,
    Edit,
    Delete,
    Schedule,
    Pause,
    CheckCircle,
    Error as ErrorIcon,
    } from '@mui/icons-material';
import { formatDate } from '../utils/formatDate';

const BackupList = ({ 
    strategies, 
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
        // En una implementación real, obtendrías los jobs específicos de esta estrategia
        setSelectedJobs([]); // Simulado
        setJobDetailsOpen(true);
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
            {strategies.map((strategy) => (
            <Grid item xs={12} md={6} lg={4} key={strategy.id}>
                <Card 
                sx={{ 
                    height: '100%',
                    opacity: strategy.is_active ? 1 : 0.7,
                    border: strategy.is_active ? '1px solid #e0e0e0' : '1px dashed #bdbdbd'
                }}
                >
                <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Typography variant="h6" component="h2" noWrap>
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

                    <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Programación:</strong> {strategy.schedule_frequency} a las{' '}
                    {strategy.schedule_time}
                    </Typography>

                    <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    Creada: {formatDate.relative(strategy.created_at)}
                    </Typography>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box>
                        <IconButton
                        size="small"
                        onClick={() => onExecute(strategy.id)}
                        color="primary"
                        title="Ejecutar ahora"
                        >
                        <PlayArrow />
                        </IconButton>
                        <IconButton
                        size="small"
                        onClick={() => onToggle(strategy.id)}
                        color={strategy.is_active ? "warning" : "success"}
                        title={strategy.is_active ? "Pausar" : "Activar"}
                        >
                        {strategy.is_active ? <Pause /> : <CheckCircle />}
                        </IconButton>
                        <IconButton
                        size="small"
                        onClick={() => onEdit(strategy)}
                        title="Editar"
                        >
                        <Edit />
                        </IconButton>
                        <IconButton
                        size="small"
                        onClick={() => handleDeleteClick(strategy)}
                        color="error"
                        title="Eliminar"
                        >
                        <Delete />
                        </IconButton>
                    </Box>

                    <Button
                        size="small"
                        startIcon={<Schedule />}
                        onClick={() => handleViewJobs(strategy)}
                    >
                        Jobs
                    </Button>
                    </Box>
                </CardContent>
                </Card>
            </Grid>
            ))}
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
            maxWidth="sm"
            fullWidth
        >
            <DialogTitle>Jobs Programados</DialogTitle>
            <DialogContent>
            {selectedJobs.length === 0 ? (
                <Typography color="textSecondary">
                No hay jobs programados para esta estrategia.
                </Typography>
            ) : (
                <List>
                {selectedJobs.map((job) => (
                    <ListItem key={job.id}>
                    <ListItemText
                        primary={job.name}
                        secondary={`Próxima ejecución: ${formatDate.full(job.next_run_time)}`}
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