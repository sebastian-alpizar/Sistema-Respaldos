import React, { useState } from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Chip,
    IconButton,
    Tooltip,
    Typography,
    Box,
    TablePagination,
} from '@mui/material';
import {
    Visibility,
    Delete,
    CheckCircle,
    Error,
    Schedule,
    PlayArrow,
} from '@mui/icons-material';
import { formatDate } from '../utils/formatDate';

const LogTable = ({ logs, onViewLog, onDeleteLog, loading = false }) => {
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed': return 'success';
            case 'running': return 'info';
            case 'failed': return 'error';
            case 'cancelled': return 'warning';
            default: return 'default';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'completed': return <CheckCircle />;
            case 'running': return <PlayArrow />;
            case 'failed': return <Error />;
            case 'cancelled': return <Schedule />;
            default: return null;
        }
    };

    const getLevelColor = (level) => {
        switch (level) {
            case 'error': return 'error';
            case 'warning': return 'warning';
            case 'critical': return 'error';
            default: return 'info';
        }
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const paginatedLogs = logs.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
                <Typography>Cargando logs...</Typography>
            </Box>
        );
    }

    if (logs.length === 0) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
                <Typography color="textSecondary">
                No hay logs disponibles
                </Typography>
            </Box>
        );
    }

    return (
        <Paper>
        <TableContainer>
            <Table>
            <TableHead>
                <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Estrategia</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Nivel</TableCell>
                <TableCell>Mensaje</TableCell>
                <TableCell>Inicio</TableCell>
                <TableCell>Duración</TableCell>
                <TableCell>Tamaño</TableCell>
                <TableCell>Acciones</TableCell>
                </TableRow>
            </TableHead>
            <TableBody>
                {paginatedLogs.map((log) => (
                <TableRow key={log.id} hover>
                    <TableCell>{log.id}</TableCell>
                    <TableCell>
                    <Typography variant="body2">
                        #{log.strategy_id}
                    </Typography>
                    </TableCell>
                    <TableCell>
                    <Chip
                        icon={getStatusIcon(log.status)}
                        label={log.status}
                        color={getStatusColor(log.status)}
                        size="small"
                        variant="outlined"
                    />
                    </TableCell>
                    <TableCell>
                    <Chip
                        label={log.level}
                        color={getLevelColor(log.level)}
                        size="small"
                    />
                    </TableCell>
                    <TableCell>
                    <Tooltip title={log.message}>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                        {log.message}
                        </Typography>
                    </Tooltip>
                    </TableCell>
                    <TableCell>
                    <Typography variant="body2">
                        {formatDate.short(log.start_time)}
                    </Typography>
                    </TableCell>
                    <TableCell>
                    <Typography variant="body2">
                        {log.duration_seconds ? `${log.duration_seconds}s` : '-'}
                    </Typography>
                    </TableCell>
                    <TableCell>
                    <Typography variant="body2">
                        {log.backup_size_mb ? `${log.backup_size_mb.toFixed(2)} MB` : '-'}
                    </Typography>
                    </TableCell>
                    <TableCell>
                    <Box display="flex" gap={1}>
                        <Tooltip title="Ver detalles">
                        <IconButton
                            size="small"
                            onClick={() => onViewLog(log)}
                            color="primary"
                        >
                            <Visibility />
                        </IconButton>
                        </Tooltip>
                        <Tooltip title="Eliminar">
                        <IconButton
                            size="small"
                            onClick={() => onDeleteLog(log.id)}
                            color="error"
                        >
                            <Delete />
                        </IconButton>
                        </Tooltip>
                    </Box>
                    </TableCell>
                </TableRow>
                ))}
            </TableBody>
            </Table>
        </TableContainer>
        <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={logs.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            labelRowsPerPage="Filas por página:"
            labelDisplayedRows={({ from, to, count }) =>
            `${from}-${to} de ${count !== -1 ? count : `más de ${to}`}`
            }
        />
        </Paper>
    );
};

export default LogTable;