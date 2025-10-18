import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Grid,
    FormControlLabel,
    Checkbox,
    FormGroup,
    Typography,
    Box,
    Chip,
    Alert,
    Stepper,
    Step,
    StepLabel,
} from '@mui/material';
import { LocalizationProvider, TimePicker } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { es } from 'date-fns/locale';

const BackupForm = ({ open, onClose, onSave, strategy = null }) => {
    const [activeStep, setActiveStep] = useState(0);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        backup_type: 'full',
        priority: 'medium',
        is_active: true,
        schedule_frequency: 'daily',
        schedule_time: new Date(new Date().setHours(2, 0, 0, 0)),
        schedule_days: [],
        schedule_months: [],
        tablespaces: [],
        schemas: [],
        tables: [],
        include_archivelogs: true,
        compression: true,
        encryption: false,
        retention_days: 30,
        parallel_degree: '',
        max_backup_size: '',
    });

    const [errors, setErrors] = useState({});
    const [validationResult, setValidationResult] = useState(null);

    useEffect(() => {
        if (strategy) {
            setFormData({
                ...strategy,
                schedule_time: new Date(`1970-01-01T${strategy.schedule_time}`),
            });
        } else {
            setFormData({
                name: '',
                description: '',
                backup_type: 'full',
                priority: 'medium',
                is_active: true,
                schedule_frequency: 'daily',
                schedule_time: new Date(new Date().setHours(2, 0, 0, 0)),
                schedule_days: [],
                schedule_months: [],
                tablespaces: [],
                schemas: [],
                tables: [],
                include_archivelogs: true,
                compression: true,
                encryption: false,
                retention_days: 30,
                parallel_degree: '',
                max_backup_size: '',
            });
        }
        setActiveStep(0);
        setErrors({});
        setValidationResult(null);
    }, [strategy, open]);

    const handleChange = (field) => (event) => {
        const value = event.target.value;
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
        
        // Limpiar error del campo
        if (errors[field]) {
            setErrors(prev => ({
                ...prev,
                [field]: null
            }));
        }
    };

    const handleTimeChange = (newTime) => {
        setFormData(prev => ({
            ...prev,
            schedule_time: newTime
        }));
    };

    const handleArrayChange = (field) => (event) => {
        const value = event.target.value;
            setFormData(prev => ({
            ...prev,
            [field]: typeof value === 'string' ? value.split(',') : value
        }));
    };

    const validateStep = (step) => {
        const newErrors = {};
        
        if (step === 0) {
            if (!formData.name.trim()) {
                newErrors.name = 'El nombre es requerido';
            }
            if (!formData.backup_type) {
                newErrors.backup_type = 'El tipo de backup es requerido';
            }
        }
        
        if (step === 1) {
            if (!formData.schedule_frequency) {
                newErrors.schedule_frequency = 'La frecuencia es requerida';
            }
            if (!formData.schedule_time) {
                newErrors.schedule_time = 'La hora es requerida';
            }
        }
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleNext = () => {
        if (validateStep(activeStep)) {
            setActiveStep(prev => prev + 1);
        }
    };

    const handleBack = () => {
        setActiveStep(prev => prev - 1);
    };

    const handleSubmit = async () => {
        try {
            // Preparar datos para enviar
            const submitData = {
                ...formData,
                schedule_time: formData.schedule_time.toTimeString().slice(0, 8), // HH:mm:ss
            };
            
            await onSave(submitData);
            onClose();
        } catch (error) {
            console.error('Error guardando estrategia:', error);
        }
    };

    const steps = ['Información Básica', 'Programación', 'Configuración Avanzada'];

    const renderStepContent = (step) => {
        switch (step) {
        case 0:
            return (
            <Grid container spacing={3}>
                <Grid item xs={12}>
                <TextField
                    fullWidth
                    label="Nombre de la estrategia"
                    value={formData.name}
                    onChange={handleChange('name')}
                    error={!!errors.name}
                    helperText={errors.name}
                    required
                />
                </Grid>
                <Grid item xs={12}>
                <TextField
                    fullWidth
                    label="Descripción"
                    value={formData.description}
                    onChange={handleChange('description')}
                    multiline
                    rows={3}
                />
                </Grid>
                <Grid item xs={12} sm={6}>
                <FormControl fullWidth required error={!!errors.backup_type}>
                    <InputLabel>Tipo de Backup</InputLabel>
                    <Select
                    value={formData.backup_type}
                    onChange={handleChange('backup_type')}
                    label="Tipo de Backup"
                    >
                    <MenuItem value="full">Completo</MenuItem>
                    <MenuItem value="partial">Parcial</MenuItem>
                    <MenuItem value="incremental">Incremental</MenuItem>
                    <MenuItem value="custom">Personalizado</MenuItem>
                    </Select>
                </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                    <InputLabel>Prioridad</InputLabel>
                    <Select
                    value={formData.priority}
                    onChange={handleChange('priority')}
                    label="Prioridad"
                    >
                    <MenuItem value="low">Baja</MenuItem>
                    <MenuItem value="medium">Media</MenuItem>
                    <MenuItem value="high">Alta</MenuItem>
                    <MenuItem value="critical">Crítica</MenuItem>
                    </Select>
                </FormControl>
                </Grid>
            </Grid>
            );

        case 1:
            return (
            <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                <FormControl fullWidth required error={!!errors.schedule_frequency}>
                    <InputLabel>Frecuencia</InputLabel>
                    <Select
                    value={formData.schedule_frequency}
                    onChange={handleChange('schedule_frequency')}
                    label="Frecuencia"
                    >
                    <MenuItem value="daily">Diario</MenuItem>
                    <MenuItem value="weekly">Semanal</MenuItem>
                    <MenuItem value="monthly">Mensual</MenuItem>
                    <MenuItem value="custom">Personalizado</MenuItem>
                    </Select>
                </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={es}>
                    <TimePicker
                    label="Hora de ejecución"
                    value={formData.schedule_time}
                    onChange={handleTimeChange}
                    renderInput={(params) => (
                        <TextField
                        {...params}
                        fullWidth
                        required
                        error={!!errors.schedule_time}
                        helperText={errors.schedule_time}
                        />
                    )}
                    />
                </LocalizationProvider>
                </Grid>

                {formData.schedule_frequency === 'weekly' && (
                <Grid item xs={12}>
                    <FormControl fullWidth>
                    <InputLabel>Días de la semana</InputLabel>
                    <Select
                        multiple
                        value={formData.schedule_days}
                        onChange={handleArrayChange('schedule_days')}
                        label="Días de la semana"
                        renderValue={(selected) => (
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                {selected.map((value) => (
                                    <Chip 
                                        key={value} 
                                        label={['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'][value - 1]} 
                                        size="small" 
                                    />
                                ))}
                            </Box>
                        )}
                    >
                        {[1, 2, 3, 4, 5, 6, 7].map((day) => (
                            <MenuItem key={day} value={day}>
                                <Typography component="span"> {/* ← AQUÍ EL CAMBIO */}
                                    {['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'][day - 1]}
                                </Typography>
                            </MenuItem>
                        ))}
                    </Select>
                    </FormControl>
                </Grid>
                )}

                {formData.schedule_frequency === 'monthly' && (
                <Grid item xs={12}>
                    <FormControl fullWidth>
                    <InputLabel>Días del mes</InputLabel>
                    <Select
                        multiple
                        value={formData.schedule_months}
                        onChange={handleArrayChange('schedule_months')}
                        label="Días del mes"
                    >
                        {Array.from({ length: 31 }, (_, i) => i + 1).map((day) => (
                            <MenuItem key={day} value={day}>
                                <Typography component="span">
                                    {day}
                                </Typography>
                            </MenuItem>
                        ))}
                    </Select>
                    </FormControl>
                </Grid>
                )}

                <Grid item xs={12}>
                <FormGroup>
                    <FormControlLabel
                    control={
                        <Checkbox
                        checked={formData.is_active}
                        onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                        />
                    }
                    label="Estrategia activa"
                    />
                </FormGroup>
                </Grid>
            </Grid>
            );

        case 2:
            return (
            <Grid container spacing={3}>
                {formData.backup_type === 'partial' && (
                <>
                    <Grid item xs={12}>
                    <Typography variant="h6" gutterBottom>
                        Selección de Objetos
                    </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Tablespaces (separados por coma)"
                        value={formData.tablespaces.join(',')}
                        onChange={handleArrayChange('tablespaces')}
                        placeholder="USERS, SYSTEM, TEMP"
                    />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                    <TextField
                        fullWidth
                        label="Esquemas (separados por coma)"
                        value={formData.schemas.join(',')}
                        onChange={handleArrayChange('schemas')}
                        placeholder="HR, FINANCE, SALES"
                    />
                    </Grid>
                    <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="Tablas (separadas por coma)"
                        value={formData.tables.join(',')}
                        onChange={handleArrayChange('tables')}
                        placeholder="employees, departments, salaries"
                    />
                    </Grid>
                </>
                )}

                <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                    Opciones de Backup
                </Typography>
                </Grid>

                <Grid item xs={12} sm={6}>
                <TextField
                    fullWidth
                    label="Días de retención"
                    type="number"
                    value={formData.retention_days}
                    onChange={handleChange('retention_days')}
                    InputProps={{ inputProps: { min: 1, max: 365 } }}
                />
                </Grid>

                <Grid item xs={12} sm={6}>
                <TextField
                    fullWidth
                    label="Grado de paralelismo"
                    type="number"
                    value={formData.parallel_degree}
                    onChange={handleChange('parallel_degree')}
                    placeholder="Automático"
                    InputProps={{ inputProps: { min: 1, max: 32 } }}
                />
                </Grid>

                <Grid item xs={12}>
                <FormGroup>
                    <FormControlLabel
                    control={
                        <Checkbox
                        checked={formData.include_archivelogs}
                        onChange={(e) => setFormData(prev => ({ ...prev, include_archivelogs: e.target.checked }))}
                        />
                    }
                    label="Incluir archivelogs"
                    />
                    <FormControlLabel
                    control={
                        <Checkbox
                        checked={formData.compression}
                        onChange={(e) => setFormData(prev => ({ ...prev, compression: e.target.checked }))}
                        />
                    }
                    label="Compresión"
                    />
                    <FormControlLabel
                    control={
                        <Checkbox
                        checked={formData.encryption}
                        onChange={(e) => setFormData(prev => ({ ...prev, encryption: e.target.checked }))}
                        />
                    }
                    label="Encriptación"
                    />
                </FormGroup>
                </Grid>

                {validationResult && (
                <Grid item xs={12}>
                    <Alert 
                    severity={validationResult.valid ? 'success' : 'warning'}
                    sx={{ mt: 2 }}
                    >
                    {validationResult.valid ? '✅ Validación exitosa' : '⚠️ Advertencias en validación'}
                    {validationResult.warnings?.map((warning, index) => (
                        <div key={index}>• {warning}</div>
                    ))}
                    {validationResult.errors?.map((error, index) => (
                        <div key={index}>• {error}</div>
                    ))}
                    </Alert>
                </Grid>
                )}
            </Grid>
            );

        default:
            return null;
        }
    };

    return (
        <Dialog 
        open={open} 
        onClose={onClose} 
        maxWidth="md" 
        fullWidth
        scroll="paper"
        >
        <DialogTitle>
            {strategy ? 'Editar Estrategia' : 'Nueva Estrategia de Backup'}
        </DialogTitle>
        
        <DialogContent>
            <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
            {steps.map((label) => (
                <Step key={label}>
                <StepLabel>{label}</StepLabel>
                </Step>
            ))}
            </Stepper>

            {renderStepContent(activeStep)}
        </DialogContent>

        <DialogActions sx={{ p: 3, gap: 1 }}>
            <Button onClick={onClose}>
            Cancelar
            </Button>
            
            <Box flex={1} />
            
            {activeStep > 0 && (
            <Button onClick={handleBack}>
                Anterior
            </Button>
            )}
            
            {activeStep < steps.length - 1 ? (
            <Button onClick={handleNext} variant="contained">
                Siguiente
            </Button>
            ) : (
            <Button onClick={handleSubmit} variant="contained" color="primary">
                {strategy ? 'Actualizar' : 'Crear'} Estrategia
            </Button>
            )}
        </DialogActions>
        </Dialog>
    );
};

export default BackupForm;