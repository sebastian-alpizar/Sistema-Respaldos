import React, { useState } from 'react';
import {
    Box,
    Typography,
    Button,
    Tabs,
    Tab,
    Paper,
    } from '@mui/material';
import {
    Add,
    Refresh,
} from '@mui/icons-material';
import { useScheduler } from '../context/SchedulerContext';
import BackupList from '../components/BackupList';
import BackupForm from '../components/BackupForm';
import NotificationSnackbar from '../components/NotificationSnackbar';

const BackupsPage = () => {
    const { 
        strategies, 
        fetchStrategies, 
        createStrategy, 
        updateStrategy, 
        deleteStrategy,
        executeStrategy,
        toggleStrategy,
        schedulerStatus,
        error 
    } = useScheduler();
    
    const [formOpen, setFormOpen] = useState(false);
    const [editingStrategy, setEditingStrategy] = useState(null);
    const [activeTab, setActiveTab] = useState(0);
    const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });

    const showNotification = (message, severity = 'info') => {
        setNotification({ open: true, message, severity });
    };

    const handleCreateStrategy = async (strategyData) => {
        try {
            await createStrategy(strategyData);
            showNotification('Estrategia creada exitosamente', 'success');
        } catch (err) {
            showNotification('Error creando estrategia: ' + err.message, 'error');
        }
    };

    const handleUpdateStrategy = async (strategyData) => {
        try {
            await updateStrategy(editingStrategy.id, strategyData);
            showNotification('Estrategia actualizada exitosamente', 'success');
        } catch (err) {
            showNotification('Error actualizando estrategia: ' + err.message, 'error');
        }
    };

    const handleSaveStrategy = (strategyData) => {
        if (editingStrategy) {
            handleUpdateStrategy(strategyData);
        } else {
            handleCreateStrategy(strategyData);
        }
    };

    const handleEdit = (strategy) => {
        setEditingStrategy(strategy);
        setFormOpen(true);
    };

    const handleDelete = async (strategyId) => {
        try {
            await deleteStrategy(strategyId);
            showNotification('Estrategia eliminada exitosamente', 'success');
        } catch (err) {
            showNotification('Error eliminando estrategia: ' + err.message, 'error');
        }
    };

    const handleExecute = async (strategyId) => {
        try {
            await executeStrategy(strategyId);
            showNotification('Backup ejecutado exitosamente', 'success');
        } catch (err) {
            showNotification('Error ejecutando backup: ' + err.message, 'error');
        }
    };

    const handleToggle = async (strategyId) => {
        try {
            const result = await toggleStrategy(strategyId);
            showNotification(
                `Estrategia ${result.strategy.is_active ? 'activada' : 'desactivada'}`, 
                'success'
            );
        } catch (err) {
            showNotification('Error cambiando estado de estrategia: ' + err.message, 'error');
        }
    };

    const handleFormClose = () => {
        setFormOpen(false);
        setEditingStrategy(null);
    };

    const handleRefresh = () => {
        fetchStrategies();
        showNotification('Lista actualizada', 'info');
    };

    const activeStrategies = strategies.filter(s => s.is_active);
    const inactiveStrategies = strategies.filter(s => !s.is_active);

    const tabContent = [
        {
            label: `Activas (${activeStrategies.length})`,
            strategies: activeStrategies
        },
        {
            label: `Inactivas (${inactiveStrategies.length})`,
            strategies: inactiveStrategies
        },
        {
            label: `Todas (${strategies.length})`,
            strategies: strategies
        }
    ];

    return (
        <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Box>
            <Typography variant="h4" gutterBottom>
                Estrategias de Backup
            </Typography>
            <Typography variant="body1" color="textSecondary">
                Gestiona y programa tus estrategias de respaldo Oracle
            </Typography>
            </Box>
            
            <Box display="flex" gap={1}>
            <Button
                startIcon={<Refresh />}
                onClick={handleRefresh}
                variant="outlined"
            >
                Actualizar
            </Button>
            <Button
                startIcon={<Add />}
                onClick={() => setFormOpen(true)}
                variant="contained"
            >
                Nueva Estrategia
            </Button>
            </Box>
        </Box>

        <Paper sx={{ width: '100%', mb: 2 }}>
            <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            indicatorColor="primary"
            textColor="primary"
            >
            {tabContent.map((tab, index) => (
                <Tab key={index} label={tab.label} />
            ))}
            </Tabs>
        </Paper>

        <BackupList
            strategies={tabContent[activeTab].strategies}
            scheduledJobs={schedulerStatus.scheduled_jobs || []}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onExecute={handleExecute}
            onToggle={handleToggle}
        />

        {/* Formulario de estrategia */}
        <BackupForm
            open={formOpen}
            onClose={handleFormClose}
            onSave={handleSaveStrategy}
            strategy={editingStrategy}
        />

        {/* Notificación */}
        <NotificationSnackbar
            open={notification.open}
            message={notification.message}
            severity={notification.severity}
            onClose={() => setNotification(prev => ({ ...prev, open: false }))}
        />
        </Box>
    );
};

export default BackupsPage;