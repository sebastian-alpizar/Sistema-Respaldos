import { createBrowserRouter } from 'react-router-dom';
import App from '../src/app';
import Dashboard from './pages/Dashboard';
import BackupsPage from './pages/BackupsPage';
import LogsPage from './pages/LogsPage';
import SettingsPage from './pages/SettingsPage';

export const router = createBrowserRouter([
    {
        path: '/',
        element: <App />,
        children: [
            {
                index: true,
                element: <Dashboard />,
            },
            {
                path: 'backups',
                element: <BackupsPage />,
            },
            {
                path: 'logs',
                element: <LogsPage />,
            },
            {
                path: 'settings',
                element: <SettingsPage />,
            },
        ],
    },
]);