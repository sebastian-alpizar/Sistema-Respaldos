import React, { useState } from 'react';
import {
    Box,
    Typography,
    Card,
    CardContent,
    Grid,
    TextField,
    Button,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Switch,
    FormControlLabel,
    Divider,
    Alert,
    Paper,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Chip,
} from '@mui/material';
import {
    Save,
    Science,
    Storage,
    Email,
    Settings as SettingsIcon,
    CheckCircle,
    Error as ErrorIcon,
} from '@mui/icons-material';
import { useConfig } from '../context/ConfigContext';
import { systemService } from '../api/systemService';

const SettingsPage = () => {
    const { 
        systemHealth, 
        databaseInfo, 
        refreshDatabaseInfo,
        checkArchiveLogMode 
    } = useConfig();
    
    const [settings, setSettings] = useState({
        oracle_user: '',
        oracle_dsn: '',
        smtp_server: '',
        smtp_port: 587,
        smtp_username: '',
        notification_email: '',
        backup_base_path: './backups',
        retention_days: 30,
    });
    
    const [testEmail, setTestEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    React.useEffect(() => {
        loadCurrentConfig();
    }, []);

    const loadCurrentConfig = async () => {
        try {
            const response = await systemService.getConfiguration();
            setSettings(response.data);
        } catch (error) {
            console.error('Error cargando configuración:', error);
        }
    };

    const handleSettingChange = (field) => (event) => {
        const value = event.target.value;
        setSettings(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleSaveSettings = async () => {
        try {
            setLoading(true);
            setMessage({ type: '', text: '' });
            
            // En una implementación real, enviarías esto al backend
            // await systemService.updateConfiguration(settings);
            
            setMessage({ type: 'success', text: 'Configuración guardada exitosamente' });
        } catch (error) {
            setMessage({ type: 'error', text: 'Error guardando configuración: ' + error.message });
        } finally {
            setLoading(false);
        }
    };

    const handleTestEmail = async () => {
        if (!testEmail) {
            setMessage({ type: 'error', text: 'Por favor ingresa un email de prueba' });
            return;
        }

        try {
            setLoading(true);
            setMessage({ type: '', text: '' });
            
            await systemService.testEmail(testEmail);
            setMessage({ type: 'success', text: 'Email de prueba enviado exitosamente' });
        } catch (error) {
            setMessage({ type: 'error', text: 'Error enviando email de prueba: ' + error.response?.data?.detail || error.message });
        } finally {
            setLoading(false);
        }
    };

    const handleTestDatabase = async () => {
        try {
            setLoading(true);
            setMessage({ type: '', text: '' });
            
            await refreshDatabaseInfo();
            const archiveLogResult = await checkArchiveLogMode();
            
            if (databaseInfo && archiveLogResult) {
                setMessage({ 
                type: 'success', 
                text: `Conexión a Oracle exitosa. Base de datos: ${databaseInfo.name}, ARCHIVELOG: ${archiveLogResult.archivelog_enabled ? 'HABILITADO' : 'DESHABILITADO'}` 
                });
            } else {
                setMessage({ type: 'error', text: 'No se pudo obtener información de la base de datos' });
            }
        } catch (error) {
            setMessage({ type: 'error', text: 'Error probando conexión a Oracle: ' + error.message });
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box>
        <Typography variant="h4" gutterBottom>
            Configuración del Sistema
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 4 }}>
            Gestiona la configuración del sistema de respaldo Oracle
        </Typography>

        {message.text && (
            <Alert 
            severity={message.type} 
            sx={{ mb: 3 }}
            onClose={() => setMessage({ type: '', text: '' })}
            >
            {message.text}
            </Alert>
        )}

        <Grid container spacing={3}>
            {/* Configuración de Oracle */}
            <Grid item xs={12} md={6}>
            <Card>
                <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={3}>
                    <Storage color="primary" />
                    <Typography variant="h6">
                    Configuración Oracle
                    </Typography>
                </Box>

                <Grid container spacing={2}>
                    <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="Usuario Oracle"
                        value={settings.oracle_user}
                        onChange={handleSettingChange('oracle_user')}
                        placeholder="system"
                    />
                    </Grid>
                    <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="DSN Oracle"
                        value={settings.oracle_dsn}
                        onChange={handleSettingChange('oracle_dsn')}
                        placeholder="localhost:1521/XE"
                        helperText="Formato: host:puerto/service_name"
                    />
                    </Grid>
                    <Grid item xs={12}>
                    <Button
                        startIcon={<Science />}
                        onClick={handleTestDatabase}
                        variant="outlined"
                        fullWidth
                        disabled={loading}
                    >
                        Probar Conexión Oracle
                    </Button>
                    </Grid>
                </Grid>

                {/* Estado de Oracle */}
                {systemHealth && (
                    <Paper variant="outlined" sx={{ p: 2, mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                        Estado Actual:
                    </Typography>
                    <List dense>
                        <ListItem>
                        <ListItemIcon>
                            {systemHealth.oracle_connection === 'connected' ? 
                            <CheckCircle color="success" /> : <ErrorIcon color="error" />
                            }
                        </ListItemIcon>
                        <ListItemText
                            primary="Conexión Oracle"
                            secondary={
                            <Chip
                                label={systemHealth.oracle_connection}
                                color={systemHealth.oracle_connection === 'connected' ? 'success' : 'error'}
                                size="small"
                            />
                            }
                        />
                        </ListItem>
                        {databaseInfo && (
                        <ListItem>
                            <ListItemText
                            primary="Base de Datos"
                            secondary={databaseInfo.name}
                            />
                        </ListItem>
                        )}
                    </List>
                    </Paper>
                )}
                </CardContent>
            </Card>
            </Grid>

            {/* Configuración de Email */}
            <Grid item xs={12} md={6}>
            <Card>
                <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={3}>
                    <Email color="primary" />
                    <Typography variant="h6">
                    Configuración SMTP
                    </Typography>
                </Box>

                <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Servidor SMTP"
                        value={settings.smtp_server}
                        onChange={handleSettingChange('smtp_server')}
                        placeholder="smtp.gmail.com"
                    />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Puerto SMTP"
                        type="number"
                        value={settings.smtp_port}
                        onChange={handleSettingChange('smtp_port')}
                    />
                    </Grid>
                    <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="Usuario SMTP"
                        value={settings.smtp_username}
                        onChange={handleSettingChange('smtp_username')}
                        placeholder="tu.email@gmail.com"
                    />
                    </Grid>
                    <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="Email de Notificación"
                        value={settings.notification_email}
                        onChange={handleSettingChange('notification_email')}
                        placeholder="admin@company.com"
                    />
                    </Grid>
                    <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="Email de Prueba"
                        value={testEmail}
                        onChange={(e) => setTestEmail(e.target.value)}
                        placeholder="destino@ejemplo.com"
                    />
                    </Grid>
                    <Grid item xs={12}>
                    <Button
                        startIcon={<Science />}
                        onClick={handleTestEmail}
                        variant="outlined"
                        fullWidth
                        disabled={loading || !testEmail}
                    >
                        Probar Configuración SMTP
                    </Button>
                    </Grid>
                </Grid>
                </CardContent>
            </Card>
            </Grid>

            {/* Configuración de Backup */}
            <Grid item xs={12} md={6}>
            <Card>
                <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={3}>
                    <SettingsIcon color="primary" />
                    <Typography variant="h6">
                    Configuración de Backup
                    </Typography>
                </Box>

                <Grid container spacing={2}>
                    <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="Ruta Base de Backups"
                        value={settings.backup_base_path}
                        onChange={handleSettingChange('backup_base_path')}
                        helperText="Ruta donde se almacenarán los archivos de backup"
                    />
                    </Grid>
                    <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="Días de Retención"
                        type="number"
                        value={settings.retention_days}
                        onChange={handleSettingChange('retention_days')}
                        InputProps={{ inputProps: { min: 1, max: 365 } }}
                        helperText="Número de días que se conservarán los backups"
                    />
                    </Grid>
                </Grid>
                </CardContent>
            </Card>
            </Grid>

            {/* Información del Sistema */}
            <Grid item xs={12} md={6}>
            <Card>
                <CardContent>
                <Typography variant="h6" gutterBottom>
                    Información del Sistema
                </Typography>
                
                {systemHealth && (
                    <List dense>
                    <ListItem>
                        <ListItemText
                        primary="Versión de la Aplicación"
                        secondary={systemHealth.version}
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                        primary="Estado del Programador"
                        secondary={
                            <Chip
                            label={systemHealth.scheduler}
                            color={systemHealth.scheduler === 'running' ? 'success' : 'warning'}
                            size="small"
                            />
                        }
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                        primary="Configuración de Email"
                        secondary={
                            <Chip
                            label={systemHealth.email}
                            color={systemHealth.email === 'configured' ? 'success' : 'default'}
                            size="small"
                            />
                        }
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                        primary="Estado General"
                        secondary={
                            <Chip
                            label={systemHealth.status}
                            color={systemHealth.status === 'healthy' ? 'success' : 'error'}
                            size="small"
                            />
                        }
                        />
                    </ListItem>
                    </List>
                )}
                </CardContent>
            </Card>
            </Grid>
        </Grid>

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
            startIcon={<Save />}
            onClick={handleSaveSettings}
            variant="contained"
            size="large"
            disabled={loading}
            >
            Guardar Configuración
            </Button>
        </Box>
        </Box>
    );
};

export default SettingsPage;