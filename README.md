# Documentación de la Estructura del Backend

## Visión General
Este documento describe la estructura y componentes del sistema backend para el proyecto FINKAGKO ejecutándose linux.

## Tecnologías Principales
- **Python** 3.12.3
- **FastAPI** 0.111.0
- **Pydantic** 2.11.3
- **Uvicorn** 0.29.0
- **PostgreSQL** (vía Psycopg2 2.9.9)
- **Pytest** 8.3.5
- **python-dotenv** 1.0.1 (para manejo de variables de entorno)

## Estructura de Directorios
```plaintext
├── database/
│   ├── __init__.py
│   ├── connection.py        # Configuración de conexión a la base de datos
│   └── support_queries.py   # Consultas SQL/queries de base de datos
│
├── models/
│   ├── __init__.py
│   ├── support_responses.py # Modelos de respuestas API
│   └── support_schema.py    # Esquemas/validación de datos
│
├── routes/
│   ├── __init__.py
│   └── support_cases.py     # Definición de endpoints/rutas API
│
├── services/
│   ├── __init__.py
│   └── support_service.py   # Lógica de negocio principal
│
├── tests/
│   ├── __init__.py
│   └── test_support_cases.py # Pruebas unitarias/integración
│
├── utils/
│   └── exceptions_handler.py # Manejo personalizado de excepciones
│
├── .env                     # Variables de entorno
├── .gitignore
├── config.py                # Configuración de la aplicación
├── generate_test_data.py    # Script para datos de prueba
├── main.py                  # Punto de entrada de la aplicación
├── pytest.ini               # Configuración de pytest
├── README.md
└── requirements.txt         # Dependencias de Python
```

## Instrucciones de Configuración
1. Clonar el repositorio e ingresar 

```
git clone [https://github.com/libardo2s/finkargo-support-backend.git]
cd finkargo-support-backend
```

2. Crear entorno virtual: 
```
python -m venv venv
```
3. Activar entorno virtual:
```
source venv/bin/activate # Linux/WSL 
o 
source venv/bin/activate # Windows
```
4. Instalar dependencias: 
```
pip install -r requirements.txt
```
5. Configurar base de datos/variables de entorno en archivo .env 
```plaintext
DB_HOST=localhost
DB_PORT=5432
DB_NAME=finkargo_support
DB_USER=postgres
DB_PASSWORD=newpassword
```
6. Ejecutar aplicación: 
```plaintext
python main.py
```
7. Ejecutar pruebas: 
```
pytest
```

## Pruebas
Las pruebas pueden ejecutarse usando pytest. Las configuraciones de prueba están especificadas en `pytest.ini`.


# Documentación de Endpoints API

## Endpoints de Casos de Soporte

### 1. Obtener casos paginados
**GET** `/api/support-cases/`

Obtiene una lista paginada de casos de soporte con filtros opcionales.

**Parámetros de consulta:**
- `page` (int): Número de página (default: 1)
- `size` (int): Items por página (default: 10, max: 100)
- `status` (str): Filtrar por estado
- `database_name` (str): Filtrar por nombre de base de datos
- `start_date` (date): Filtrar casos creados después de esta fecha
- `end_date` (date): Filtrar casos creados antes de esta fecha

**Ejemplo de solicitud:**
```bash
curl -X GET "http://localhost:8000/api/support-cases/?page=1&size=20&status=pendiente&database_name=clientes"

Respuesta exitosa (200):
{
    "success": true,
    "message": "Casos obtenidos exitosamente",
    "data": {
        "items": [
            {
                "id": "case_123",
                "title": "Problema con consulta SQL",
                "status": "pendiente",
                "created_at": "2025-04-20T10:30:00"
            }
        ],
        "total": 15,
        "page": 1,
        "size": 20
    }
}
```

### 2. Obtener caso por ID
**GET** `/api/support-cases/case/{case_id}`


**Ejemplo de solicitud:**
```bash
curl -X GET "http://localhost:8000/api/support-cases/case/case_123"

Respuesta exitosa (200):
{
    "success": true,
    "message": "Caso encontrado",
    "case": {
        "id": "case_123",
        "title": "Problema con consulta SQL",
        "description": "La consulta no retorna los resultados esperados",
        "status": "pendiente",
        "priority": "alta",
        "sql_query": "SELECT * FROM users WHERE active = true",
        "executed_by": "user@example.com",
        "created_at": "2025-04-20T10:30:00"
    }
}
```

### 3. Crear nuevo caso
**GET** `/api/support-cases`

Crea un nuevo caso de soporte.

**Cuerpo de la solicitud (ejemplo):**
```bash
{
    "title": "Consulta lenta",
    "description": "La consulta tarda más de 30 segundos",
    "database_name": "ventas",
    "schema_name": "public",
    "sql_query": "SELECT * FROM orders WHERE created_at > '2025-01-01'",
    "executed_by": "analista@empresa.com",
    "priority": "alta"
}
```

**Ejemplo de solicitud:**
```bash
curl -X POST "http://localhost:8000/api/support-cases/" \
-H "Content-Type: application/json" \
-d '{
    "title": "Consulta lenta",
    "description": "La consulta tarda más de 30 segundos",
    "database_name": "ventas",
    "schema_name": "public",
    "sql_query": "SELECT * FROM orders WHERE created_at > '2025-01-01'",
    "executed_by": "analista@empresa.com",
    "priority": "alta"
}'
```

**Ejemplo de solicitud:**
```bash
{
    "success": true,
    "message": "Caso creado exitosamente",
    "case_id": "case_124",
    "created_at": "2025-04-20T11:45:00"
}
```

### Manejo de Errores

Todos los endpoints devuelven respuestas estandarizadas de error:


**Ejemplo de error (404):**
```bash
{
    "success": false,
    "message": "Case not found",
    "error_code": "NOT_FOUND"
}
```


**Ejemplo de error de validación (422):**
```bash
{
    "success": false,
    "message": "Validation error",
    "error_code": "VALIDATION_ERROR",
    "detail": {
        "loc": ["body", "priority"],
        "msg": "value is not a valid enumeration member; permitted: 'baja', 'media', 'alta'",
        "type": "type_error.enum"
    }
}
```

**Ejemplo de error interno (500):**
```bash
{
    "success": false,
    "message": "Error interno del servidor",
    "error_code": "INTERNAL_SERVER_ERROR",
    "detail": "Database connection failed"
}
```

# Script de Generación de Datos de Prueba

## Descripción General
El script `generate_test_data.py` automatiza la creación de una base de datos PostgreSQL con datos de prueba

## Funcionamiento del Script

### 1. Configuración Inicial
- **Recreación de la base de datos**: 
  - Elimina la base de datos existente `finkargo_support_cases` si existe
  - Crea una nueva base de datos con el mismo nombre
  - Establece la estructura de la tabla `support_cases` con todos los campos necesarios

### 2. Generación de Datos
Crea 100 casos de soporte con datos realistas que incluyen:

**Campos generados:**
- **ID**: Identificador único (UUID)
- **Título**: Descripción breve del caso (en español)
- **Descripción**: Explicación detallada del problema
- **Base de datos**: Una de las bases de datos predefinidas (`finkargo_transacciones`, `finkargo_clientes`, etc.)
- **Esquema**: Esquema relacionado (`operaciones`, `clientes`, etc.)
- **Query SQL**: Consultas SQL realistas en español de tipo:
  - UPDATE (actualizaciones)
  - INSERT (inserciones)
  - DELETE (eliminaciones)
- **Estado**: Valores como `pendiente`, `completado`, etc.
- **Prioridad**: `baja`, `media` o `alta`
- **Fechas**: Creadas en los últimos 6 meses
- **Resultado**: Posibles resultados de ejecución

## Ejecución del Script

**Antes de ejecutar el script**, asegúrate de:

1. Tener el entorno virtual activado:
```bash
source venv/bin/activate  # Linux/WSL
# o 
.\venv\Scripts\activate   # Windows
```

2. Verificar que las dependencias estén instaladas:
```bash
pip install -r requirements.txt
```

3. Ejecutar el script:
```bash
python generate_test_data.py
```

## Solución de Problemas Comunes
Si recibes errores:
1. Verifica que el entorno esté activado (deberías ver (venv) al inicio de tu línea de comandos)
2. Confirma que PostgreSQL esté corriendo en localhost:5432
3. Revisa que las credenciales en tu .env sean correctas
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=finkargo_support
DB_USER=postgres
DB_PASSWORD=newpassword
```