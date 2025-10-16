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

├── 📁 backend/
│   ├── 📁 __pycache__/ 🚫 (auto-hidden)
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   ├── 🐍 __init__.py
│   │   │   ├── 🐍 routes_backup.py
│   │   │   ├── 🐍 routes_logs.py
│   │   │   └── 🐍 routes_system.py
│   │   ├── 📁 core/
│   │   │   ├── 🐍 config.py
│   │   │   ├── 🐍 email_utils.py
│   │   │   └── 🐍 scheduler.py
│   │   ├── 📁 models/
│   │   │   ├── 🐍 log.py
│   │   │   ├── 🐍 strategy.py
│   │   │   └── 🐍 user.py
│   │   ├── 📁 repositories/
│   │   │   ├── 🐍 log_repo.py
│   │   │   ├── 🐍 strategy_repo.py
│   │   │   └── 🐍 user_repo.py
│   │   ├── 📁 services/
│   │   │   ├── 🐍 backup_service.py
│   │   │   ├── 🐍 email_service.py
│   │   │   ├── 🐍 log_service.py
│   │   │   └── 🐍 oracle_service.py
│   │   └── 📁 utils/
│   │       ├── 🐍 file_utils.py
│   │       └── 🐍 oracle_connection.py
│   ├── 📁 venv/ 🚫 (auto-hidden)
│   ├── 🔒 .env 🚫 (auto-hidden)
│   ├── 📖 README.md
│   ├── 🐍 main.py
│   └── 📄 requirements.txt

---

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

2.  **(Opcional pero Recomendado) Crea y activa un entorno virtual:**
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

### 3. Ejecución

Para iniciar la aplicación con **Uvicorn** en modo desarrollo:

```bash
# Asegúrate de estar en el directorio 'backend/'
uvicorn main:app --reload