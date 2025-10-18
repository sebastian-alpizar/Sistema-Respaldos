import React from 'react';
import {
    Alert,
    AlertTitle,
    Button,
    Box,
    Typography,
} from '@mui/material';
import { Warning } from '@mui/icons-material';

const ArchiveModeWarning = ({ onCheckArchiveLog }) => {
    return (
        <Alert 
        severity="warning" 
        sx={{ mb: 3 }}
        action={
            <Button 
            color="inherit" 
            size="small" 
            onClick={onCheckArchiveLog}
            >
            Verificar Ahora
            </Button>
        }
        >
        <AlertTitle>Modo ARCHIVELOG No Verificado</AlertTitle>
        <Typography variant="body2">
            El modo ARCHIVELOG de Oracle no está verificado. Los backups pueden no ser consistentes 
            si el modo ARCHIVELOG no está habilitado. Se recomienda habilitar el modo ARCHIVELOG 
            para backups confiables.
        </Typography>
        </Alert>
    );
};

export default ArchiveModeWarning;