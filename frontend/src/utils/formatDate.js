import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';

export const formatDate = {
    // Formato completo
    full: (dateString) => {
        if (!dateString) return 'N/A';
        const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
        return format(date, "dd/MM/yyyy 'a las' HH:mm:ss", { locale: es });
    },

    // Formato corto
    short: (dateString) => {
        if (!dateString) return 'N/A';
        const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
        return format(date, 'dd/MM/yyyy HH:mm', { locale: es });
    },

    // Tiempo relativo
    relative: (dateString) => {
        if (!dateString) return 'N/A';
        const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
        return formatDistanceToNow(date, { addSuffix: true, locale: es });
    },

    // Solo fecha
    dateOnly: (dateString) => {
        if (!dateString) return 'N/A';
        const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
        return format(date, 'dd/MM/yyyy', { locale: es });
    },

    // Solo hora
    timeOnly: (dateString) => {
        if (!dateString) return 'N/A';
        const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
        return format(date, 'HH:mm:ss', { locale: es });
    },

    // Para formularios
    forInput: (dateString) => {
        if (!dateString) return '';
        const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
        return format(date, "yyyy-MM-dd'T'HH:mm");
    },
};