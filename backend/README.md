# ⚙️ Proyecto de Gestión de Respaldos (Backend)

Este repositorio contiene el backend de un sistema de gestión de respaldos, construido con **FastAPI** y siguiendo una arquitectura en **Capas** o **Clean Architecture** para asegurar el desacoplamiento, la escalabilidad y la facilidad de mantenimiento.

## 🧠 Arquitectura y Diseño

El proyecto implementa un patrón de **Arquitectura en Capas** que separa claramente las responsabilidades, mejorando la organización y permitiendo que los cambios en una capa (como la base de datos) tengan un impacto mínimo en otras (como la lógica de negocio).

| Capa | Rol Principal | Ejemplo |
| :--- | :--- | :--- |
| **Routers (API Layer)** | Expone los endpoints REST. Valida las solicitudes HTTP. | `/api/strategies`, `/api/logs` |
| **Services (Business Logic Layer)** | Contiene la lógica de negocio (validaciones, ejecución RMAN, scheduler, notificaciones). | `backup_service.py`, `email_service.py` |
| **Repositories (Data Access Layer)** | Accede a la base de datos Oracle (usando `cx_Oracle` o SQLAlchemy). | `strategy_repository.py`, `log_repository.py` |
| **Models / Schemas (Domain Layer)** | Define entidades, DTOs y validadores (Pydantic). | `strategy.py`, `backup_log.py` |

---

### Flujo de Ejecución Típico

1.  **Ruta:** Un usuario envía una petición **`POST /api/strategies`** para crear una nueva estrategia de respaldo.
2.  **Validación (Routers):** Se valida la estructura de la solicitud.
3.  **Lógica (Services):** El `backup_service` valida la lógica de negocio (tipo de respaldo, tablas, etc.) y usa el repositorio.
4.  **Persistencia (Repositories):** El `strategy_repo` accede a la **Base de Datos** para registrar la estrategia.
5.  **Programación (Services/Core):** El `scheduler` (parte de `core/`) programa la tarea.
6.  **Ejecución Programada:** Cuando la hora llega, el `backup_service` ejecuta el respaldo (comandos **RMAN**) y el `log_service` guarda el resultado en la bitácora.
7.  **Notificación (Services):** Si hay un error, el `email_service` envía una notificación.
8.  **Consulta:** El frontend puede consultar los resultados con **`GET /api/logs`**.

## 📁 Estructura del Directorio

```
📁 sistema-respaldos/
├── 📁 backend/
│   ├── 📁 __pycache__/ 🚫 (auto-hidden)
│   ├── 📁 app/
│   │   ├── 📁 api/                          # 🎯 Endpoints REST API
│   │   │   ├── 🐍 __init__.py               # Inicialización del módulo API
│   │   │   ├── 🐍 routes_backup.py          # Rutas para gestión de respaldos
│   │   │   ├── 🐍 routes_logs.py            # Rutas para consulta de bitácoras
│   │   │   └── 🐍 routes_system.py          # Rutas para configuración del sistema
│   │   ├── 📁 core/                         # 🔧 Configuración y componentes centrales
│   │   │   ├── 🐍 config.py                 # Configuración de la aplicación
│   │   │   ├── 🐍 email_utils.py            # Utilidades para envío de correos
│   │   │   └── 🐍 scheduler.py              # Programador de tareas automáticas
│   │   ├── 📁 models/                       # 🗃️ Modelos de datos y esquemas
│   │   │   ├── 🐍 log.py                    # Modelo de registro de bitácoras
│   │   │   ├── 🐍 strategy.py               # Modelo de estrategias de respaldo
│   │   │   └── 🐍 user.py                   # Modelo de usuarios y autenticación
│   │   ├── 📁 repositories/                 # 💾 Acceso a base de datos
│   │   │   ├── 🐍 log_repo.py               # Operaciones CRUD para registros
│   │   │   ├── 🐍 strategy_repo.py          # Operaciones CRUD para estrategias
│   │   │   └── 🐍 user_repo.py              # Operaciones CRUD para usuarios
│   │   ├── 📁 services/                     # ⚙️ Lógica de negocio principal
│   │   │   ├── 🐍 backup_service.py         # Servicio de ejecución de respaldos
│   │   │   ├── 🐍 email_service.py          # Servicio de notificaciones por email
│   │   │   ├── 🐍 log_service.py            # Servicio de gestión de bitácoras
│   │   │   └── 🐍 oracle_service.py         # Servicio de conexión y consultas Oracle
│   │   └── 📁 utils/                        # 🛠️ Utilidades y helpers
│   │       ├── 🐍 file_utils.py             # Utilidades para manejo de archivos
│   │       └── 🐍 oracle_connection.py      # Gestión de conexiones a Oracle
│   ├── 📁 venv/ 🚫 (auto-hidden)            # Entorno virtual de Python
│   ├── 🔒 .env 🚫 (auto-hidden)             # Variables de entorno
│   ├── 📖 README.md                         # Documentación del backend
│   ├── 🐍 main.py                           # 🚀 Punto de entrada de la aplicación
│   └── 📄 requirements.txt                  # Dependencias de Python

```

## 🚀 Configuración e Instalación (Desarrollo)

Sigue estos pasos para configurar y ejecutar el backend localmente.

### 1. Requisitos Previos

Asegúrate de tener instalado:

* **Python 3.x**
* **PIP** (gestor de paquetes de Python)
* **Rust** (necesario para compilar ciertas dependencias, como `cryptography`, si no se usan wheels precompilados)

#### Instalación de Rust (Windows)

Si no tienes Rust instalado:

1.  Abre **PowerShell** como **administrador**.
2.  Ejecuta:
    ```bash
    winget install Rustlang.Rustup
    ```
3.  **Configura el PATH (si es necesario):**
    * Presiona `Windows + R` y escribe `sysdm.cpl`.
    * Ve a "Variables de entorno".
    * En "Variables del sistema", selecciona `Path` y haz clic en "Editar".
    * Agrega la ruta de instalación de Rust (ej: `C:\Users\sebas\.cargo\bin`).
    * Acepta los cambios.

### 2. Instalación de Dependencias

1.  Navega al directorio `backend/`:
    ```bash
    cd backend
    ```

2.  Crea y activa un entorno virtual:
    ```bash
    # Crear entorno
    python -m venv venv
    
    # Activar entorno (Windows)
    venv\Scripts\activate
    ```

3.  Instala todas las dependencias listadas en `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    *(Alternativamente, puedes instalar las principales manualmente: `pip install fastapi uvicorn[standard] sqlalchemy cx_Oracle apscheduler aiosmtplib python-dotenv`)*

### 3. Configuración del Entorno Virtual en VS Code

Para evitar advertencias de importación y asegurar un desarrollo fluido, configura el entorno virtual en tu editor.
Seleccionar el Intérprete en Python:

#### Abrir la Paleta de Comandos
- Presiona `Ctrl + Shift + P` en VS Code  
- Escribe: `Python: Select Interpreter`

#### Seleccionar la Ruta del Intérprete
- Selecciona: `Enter interpreter path...`  
- Elige: `Find...`

#### Navegar al Entorno Virtual
- Ve a la carpeta en donde tienes el proyecto:  
  `C:\Users\sebas\Downloads\Sistema-Respaldos\backend\venv\Scripts`
- Selecciona el archivo:  
  `python.exe`

#### Verificar la Configuración
- En la esquina inferior derecha de VS Code, deberías ver algo como:  
  `Python 3.x.x ('venv': venv)`

### 4. Configuración de Variables de Entorno

Crea un archivo **`.env`** en la raíz del directorio **`backend/`** con las siguientes variables:

```env
# Configuración de Base de Datos Oracle
ORACLE_USER=tu_usuario
ORACLE_PASSWORD=tu_password
ORACLE_DSN=localhost:1521/XE

# Configuración SMTP para Notificaciones (No son necesarias por ahora)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
NOTIFICATION_EMAIL=destinatario@empresa.com

# Configuración de la Aplicación
DEBUG=True
BACKUP_BASE_PATH=/backup/oracle
RETENTION_DAYS=30
```

6. Ejecución

Para iniciar la aplicación con **Uvicorn** en modo desarrollo:

```bash
# Asegúrate de estar en el directorio 'backend/'
uvicorn main:app --reload
```
La aplicación estará disponible en:
👉 http://127.0.0.1:8000
