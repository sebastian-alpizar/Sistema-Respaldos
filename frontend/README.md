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

## 📁 Estructura del Directorio (`src/`)

├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 api/
│   │   │   ├── 📄 apiClient.js
│   │   │   ├── 📄 backupService.js
│   │   │   ├── 📄 logService.js
│   │   │   └── 📄 systemService.js
│   │   ├── 📁 components/
│   │   │   ├── 📄 BackupForm.jsx
│   │   │   ├── 📄 BackupList.jsx
│   │   │   ├── 📄 LogTable.jsx
│   │   │   ├── 📄 NotificationSnackbar.jsx
│   │   │   └── 📄 SchedulerDialog.jsx
│   │   ├── 📁 context/
│   │   │   ├── 📄 AuthContext.jsx
│   │   │   ├── 📄 ConfigContext.jsx
│   │   │   └── 📄 SchedulerContext.jsx
│   │   ├── 📁 hooks/
│   │   │   └── 📄 useFetch.js
│   │   ├── 📁 pages/
│   │   │   ├── 📄 ArchiveModeWarning.jsx
│   │   │   ├── 📄 BackupsPage.jsx
│   │   │   ├── 📄 Dashboard.jsx
│   │   │   ├── 📄 LogsPage.jsx
│   │   │   └── 📄 SettingsPage.jsx
│   │   ├── 📁 styles/
│   │   │   └── 🎨 global.css
│   │   ├── 📁 utils/
│   │   │   └── 📄 formatDate.js
│   │   ├── 📄 App.jsx
│   │   ├── 📄 index.js
│   │   └── 📄 routes.js
│   ├── 📖 README.md
│   └── 📄 vite.config.js

---

## 🚀 Configuración y Ejecución

Sigue estos pasos para configurar y levantar la aplicación de frontend.

### 1. Requisitos Previos

Asegúrate de tener instalado **Node.js** y **npm** (o **yarn/pnpm**).

### 2. Inicialización del Proyecto

Si el directorio `frontend/` aún no existe o está vacío, puedes inicializarlo con Vite.

1.  Abre una terminal y navega a la **raíz del proyecto** (no dentro de `frontend/` si vas a crearla):
    ```bash
    cd <ruta_raiz_del_proyecto>
    ```

2.  Crea la estructura base con Vite:
    ```bash
    npm create vite@latest
    ```
    * **Project name:** `frontend`
    * **Framework:** `React`
    * **Variant:** `JavaScript` (o `TypeScript` si es tu elección)

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