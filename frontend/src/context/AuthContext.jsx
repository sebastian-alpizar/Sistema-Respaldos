import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth debe ser usado dentro de un AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Simular verificación de autenticación
        const checkAuth = async () => {
            try {
                // En una implementación real, verificar token JWT
                const token = localStorage.getItem('auth_token');
                if (token) {
                // Verificar token con el backend
                setUser({ username: 'admin', role: 'admin' });
                }
            } catch (error) {
                console.error('Error verificando autenticación:', error);
                localStorage.removeItem('auth_token');
            } finally {
                setLoading(false);
            }
        };

        checkAuth();
    }, []);

    const login = async (username, password) => {
        try {
            // Simular login
            const token = 'simulated_jwt_token';
            localStorage.setItem('auth_token', token);
            setUser({ username, role: 'admin' });
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    };

    const logout = () => {
        localStorage.removeItem('auth_token');
        setUser(null);
    };

    const value = {
        user,
        login,
        logout,
        loading,
        isAuthenticated: !!user,
    };

    return (
        <AuthContext.Provider value={value}>
        {children}
        </AuthContext.Provider>
    );
};