import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Chip,
    Typography,
    Box,
    Divider,
} from '@mui/material';
import {
    Schedule,
    CheckCircle,
    Error as ErrorIcon,
} from '@mui/icons-material';
import { formatDate } from '../utils/formatDate';

const SchedulerDialog = ({ open, onClose, jobs, onStartScheduler, onStopScheduler }) => {
    const getJobStatus = (job) => {
        if (!job.next_run_time) return 'unknown';
        const nextRun = new Date(job.next_run_time);
        const now = new Date();
        return nextRun > now ? 'scheduled' : 'overdue';
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'scheduled': return 'success';
            case 'overdue': return 'warning';
            case 'unknown': return 'default';
            default: return 'default';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'scheduled': return <CheckCircle color="success" />;
            case 'overdue': return <ErrorIcon color="warning" />;
            default: return <Schedule color="disabled" />;
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>
            <Box display="flex" alignItems="center" gap={1}>
            <Schedule />
            Programador de Backups
            </Box>
        </DialogTitle>
        
        <DialogContent>
            <Box mb={3}>
            <Typography variant="h6" gutterBottom>
                Estado del Programador
            </Typography>
            <Box display="flex" gap={2} alignItems="center">
                <Chip
                label={jobs.length > 0 ? "Ejecutándose" : "Detenido"}
                color={jobs.length > 0 ? "success" : "default"}
                variant="outlined"
                />
                <Typography variant="body2" color="textSecondary">
                {jobs.length} job(s) programado(s)
                </Typography>
            </Box>
            </Box>

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" gutterBottom>
            Jobs Programados
            </Typography>

            {jobs.length === 0 ? (
            <Typography color="textSecondary" sx={{ py: 2 }}>
                No hay jobs programados actualmente.
            </Typography>
            ) : (
            <List>
                {jobs.map((job) => {
                const status = getJobStatus(job);
                return (
                    <ListItem key={job.id} divider>
                    <ListItemIcon>
                        {getStatusIcon(status)}
                    </ListItemIcon>
                    <ListItemText
                        primary={
                        <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="subtitle1">
                            {job.name}
                            </Typography>
                            <Chip
                            label={status === 'scheduled' ? 'Programado' : 'Atrasado'}
                            color={getStatusColor(status)}
                            size="small"
                            />
                        </Box>
                        }
                        secondary={
                        <Box>
                            <Typography variant="body2" color="textSecondary">
                            ID: {job.id}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                            Estrategia: {job.strategy_id || 'N/A'}
                            </Typography>
                            {job.next_run_time && (
                            <Typography variant="body2">
                                Próxima ejecución: {formatDate.full(job.next_run_time)}
                            </Typography>
                            )}
                        </Box>
                        }
                    />
                    </ListItem>
                );
                })}
            </List>
            )}
        </DialogContent>

        <DialogActions sx={{ p: 3, gap: 1 }}>
            <Button onClick={onClose}>
            Cerrar
            </Button>
            
            <Box flex={1} />
            
            {jobs.length > 0 ? (
            <Button onClick={onStopScheduler} color="warning" variant="outlined">
                Detener Programador
            </Button>
            ) : (
            <Button onClick={onStartScheduler} color="success" variant="contained">
                Iniciar Programador
            </Button>
            )}
        </DialogActions>
        </Dialog>
    );
};

export default SchedulerDialog;