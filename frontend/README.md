# 🎨 Proyecto de Gestión de Respaldos (Frontend)

Este repositorio contiene la **Single Page Application (SPA)** del frontend, desarrollada con **React** y **Vite**. La arquitectura se basa en un diseño **modular y basado en componentes** para lograr una clara **Separación de Intereses (Separation of Concerns)** y facilitar el desarrollo y mantenimiento.

## 🧠 Arquitectura y Estructura

El frontend está organizado por tipo de responsabilidad, lo que permite que el código sea predecible y escalable.

| Capa | Rol Principal | Ejemplos de Archivos |
| :--- | :--- | :--- |
| **Pages** | Vistas completas y rutas principales. | `BackupsPage.jsx`, `LogsPage.jsx` |
| **Components** | Elementos reutilizables de la UI (interfaz de usuario). | `BackupForm.jsx`, `LogTable.jsx` |
| **Services (API)** | Capa de comunicación con el Backend (FastAPI). | `backupService.js`, `logService.js` |
| **Context / Hooks** | Gestión del estado global, autenticación y lógica compartida. | `AuthContext.jsx`, `useFetch.js` |

---

### Flujo de Uso Típico

1.  El usuario accede al **Dashboard**.
2.  La capa **Services (API)** consulta las estrategias activas al backend (`/api/strategies`).
3.  La capa **Pages** (`Dashboard.jsx`) utiliza los datos para renderizar la información, delegando a los **Components** (`BackupList.jsx`).
4.  El usuario utiliza un **Component** (`BackupForm.jsx`) para crear una nueva estrategia.
5.  Los datos del formulario se envían a través de la capa **Services** al endpoint del backend.
6.  La aplicación consulta las bitácoras en tiempo real (mediante *polling* o *WebSocket* opcional) para mantener actualizado el **Component** `LogTable.jsx`.
7.  En **SettingsPage**, el frontend interactúa con `systemService.js` para modificar parámetros como el modo `ARCHIVELOG` o la configuración SMTP del backend.

## 📁 Estructura del Directorio

```
📁 sistema-respaldos/
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 api/                          # 🌐 Servicios de comunicación con backend
│   │   │   ├── 📄 apiClient.js              # Cliente HTTP configurado para API
│   │   │   ├── 📄 backupService.js          # Servicio para operaciones de respaldo
│   │   │   ├── 📄 logService.js             # Servicio para consulta de registros
│   │   │   └── 📄 systemService.js          # Servicio para configuración del sistema
│   │   ├── 📁 components/                   # 🧩 Componentes reutilizables de UI
│   │   │   ├── 📄 BackupForm.jsx            # Formulario de creación de estrategias
│   │   │   ├── 📄 BackupList.jsx            # Lista y gestión de respaldos
│   │   │   ├── 📄 LogTable.jsx              # Tabla de visualización de bitácoras
│   │   │   ├── 📄 NotificationSnackbar.jsx  # Componente de notificaciones toast
│   │   │   └── 📄 SchedulerDialog.jsx       # Diálogo para programación de tareas
│   │   ├── 📁 context/                      # 🎮 Estado global de la aplicación
│   │   │   ├── 📄 AuthContext.jsx           # Contexto de autenticación y usuario
│   │   │   ├── 📄 ConfigContext.jsx         # Contexto de configuración del sistema
│   │   │   └── 📄 SchedulerContext.jsx      # Contexto de programación de tareas
│   │   ├── 📁 hooks/                        # 🪝 Custom React Hooks
│   │   │   └── 📄 useFetch.js               # Hook para peticiones HTTP
│   │   ├── 📁 pages/                        # 🖥️ Páginas principales de la aplicación
│   │   │   ├── 📄 ArchiveModeWarning.jsx    # Advertencia modo ARCHIVELOG
│   │   │   ├── 📄 BackupsPage.jsx           # Página de gestión de respaldos
│   │   │   ├── 📄 Dashboard.jsx             # Panel principal de control
│   │   │   ├── 📄 LogsPage.jsx              # Página de visualización de bitácoras
│   │   │   └── 📄 SettingsPage.jsx          # Página de configuración
│   │   ├── 📁 styles/                       # 🎨 Estilos y temas
│   │   │   └── 🎨 global.css                # Estilos globales de la aplicación
│   │   ├── 📁 utils/                        # 🔧 Utilidades de frontend
│   │   │   └── 📄 formatDate.js             # Utilidades de formateo de fechas
│   │   ├── 📄 App.jsx                       # 🎪 Componente raíz de la aplicación
│   │   ├── 📄 index.js                      # ⚡ Punto de entrada de React
│   │   └── 📄 routes.js                     # 🗺️ Configuración de rutas y navegación
│   ├── 📖 README.md                         # Documentación del frontend
│   └── 📄 vite.config.js                    # ⚒️ Configuración de Vite

```

## 🚀 Configuración y Ejecución

Sigue estos pasos para configurar y levantar la aplicación de frontend.

### 1. Requisitos Previos

Asegúrate de tener instalado **Node.js** y **npm** (o **yarn/pnpm**).

### 2. Inicialización del Proyecto

Si el directorio `frontend/` aún no existe o está vacío, puedes inicializarlo con Vite.

1.  Abre una terminal y navega a la **frontend**:
    ```bash
    cd frontend
    ```

2.  Crea la estructura base con Vite:
    ```bash
    npm create vite@latest
    ```
    * **Project name:** `frontend`
    * **Framework:** `React`
    * **Variant:** `JavaScript`

### 3. Instalación de Dependencias

1.  Navega al nuevo directorio `frontend/`:
    ```bash
    cd frontend
    ```

2.  Instala todas las dependencias listadas en `package.json`:
    ```bash
    npm install
    ```

### 4. Ejecución

Para iniciar el servidor de desarrollo del frontend:

```bash
# Asegúrate de estar en el directorio 'frontend/'
npm run dev
