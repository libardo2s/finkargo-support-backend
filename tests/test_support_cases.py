from unittest.mock import AsyncMock, patch
import uuid
import pytest
from typing import Optional, Tuple
import warnings
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from uuid import uuid4
from main import app
from models.support_responses import PaginatedResponse, SupportCase

client = TestClient(app)

# Datos de prueba mejorados
TEST_CASES = [
    SupportCase(
        id=str(uuid4()),
        title="Actualizar estado de envío",
        description="Cliente reportó envío pendiente",
        database_name="finkargo_transacciones",
        schema_name="operaciones",
        sql_query="UPDATE operaciones SET estado = 'enviado' WHERE id = 123",
        executed_by="juan.perez@finkargo.com",
        status="completado",
        created_at=(datetime.now() - timedelta(days=1)).isoformat(),
        updated_at=datetime.now().isoformat(),
        execution_result="1 fila actualizada"
    ),
    SupportCase(
        id=str(uuid4()),
        title="Corregir dirección cliente",
        description="Dirección incorrecta en registro",
        database_name="finkargo_clientes",
        schema_name="clientes",
        sql_query="UPDATE clientes SET direccion = 'Av. Principal 123' WHERE id = 456",
        executed_by="maria.gonzalez@finkargo.com",
        status="pendiente",
        created_at=(datetime.now() - timedelta(days=2)).isoformat(),
        updated_at=(datetime.now() - timedelta(days=1)).isoformat(),
        execution_result=None
    )
]

# Mock de datos para pruebas
VALID_CASE_DATA = {
    "title": "Error en consulta SQL",
    "description": "La consulta no devuelve los resultados esperados",
    "database_name": "finkargo_db",
    "schema_name": "clientes",
    "sql_query": "SELECT * FROM clientes WHERE id = 123",
    "executed_by": "juan.perez@finkargo.com",
    "priority": "alta"
}

@pytest.fixture
def mock_db_success(monkeypatch):
    """Fixture para mockear respuesta exitosa de la base de datos"""
    async def mock_get_paginated_cases(
        page: int, 
        size: int,
        status: Optional[str] = None,
        database_name: Optional[str] = None,
        schema_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        executed_by: Optional[str] = None
    ):
        # Aplicar filtros a los casos de prueba
        filtered_cases = TEST_CASES
        if status:
            filtered_cases = [c for c in filtered_cases if c.status == status]
        if database_name:
            filtered_cases = [c for c in filtered_cases if c.database_name == database_name]
        # Aplicar otros filtros según sea necesario...
        
        start = (page - 1) * size
        end = start + size
        paginated_items = filtered_cases[start:end]
        
        return PaginatedResponse(
            success=True,
            message=f"Se obtuvieron {len(paginated_items)} casos",
            items=paginated_items,
            total=len(filtered_cases),
            page=page,
            size=size
        )
    
    monkeypatch.setattr(
        "services.support_service.SupportService.get_paginated_cases",
        mock_get_paginated_cases
    )

@pytest.fixture
def mock_db_error(monkeypatch):
    """Fixture para mockear error de la base de datos"""
    async def mock_get_paginated_cases(*args, **kwargs):
        raise Exception("Error simulado en la base de datos")
    
    monkeypatch.setattr(
        "services.support_service.SupportService.get_paginated_cases",
        mock_get_paginated_cases
    )

def test_get_support_cases_success(mock_db_success):
    """Prueba obtener casos de soporte exitosamente"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        response = client.get("/api/support-cases/?page=1&size=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["size"] == 10

def test_pagination(mock_db_success):
    """Prueba la paginación de resultados"""
    response = client.get("/api/support-cases/?page=1&size=1")
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == TEST_CASES[0].title

def test_invalid_page_parameter():
    """Prueba parámetro de página inválido"""
    response = client.get("/api/support-cases/?page=0&size=10")
    assert response.status_code == 422
    error_data = response.json()
    
    # Verificar la estructura básica de la respuesta de error
    assert error_data["success"] is False
    assert error_data["error_code"] == "VALIDATION_ERROR"
    
    # Verificar los detalles del error
    assert len(error_data["errors"]) > 0
    page_error = next(
        (e for e in error_data["errors"] if e["field"] == "page"),
        None
    )
    assert page_error is not None
    assert "mayor que 0" in page_error["message"]

def test_invalid_size_parameter():
    """Prueba parámetro de tamaño inválido"""
    response = client.get("/api/support-cases/?page=1&size=101")
    assert response.status_code == 422
    error_data = response.json()
    
    # Verificar la estructura básica de la respuesta de error
    assert error_data["success"] is False
    assert error_data["error_code"] == "VALIDATION_ERROR"
    
    # Verificar los detalles del error
    assert len(error_data["errors"]) > 0
    size_error = next(
        (e for e in error_data["errors"] if e["field"] == "size"),
        None
    )
    assert size_error is not None
    assert "menor o igual a 100" in size_error["message"]

def test_missing_parameters(mock_db_success):
    """Prueba parámetros faltantes (usará valores por defecto)"""
    response = client.get("/api/support-cases/")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1  # Valor por defecto
    assert data["size"] == 10  # Valor por defecto

def test_error_handling(mock_db_error):
    """Prueba manejo de errores del servidor"""
    response = client.get("/api/support-cases/?page=1&size=10")
    assert response.status_code == 500
    error_data = response.json()
    assert error_data["success"] is False
    assert error_data["error_code"] == "INTERNAL_SERVER_ERROR"

def test_filter_by_status(mock_db_success):
    """Prueba filtrado por estado"""
    response = client.get("/api/support-cases/?status=completado")
    assert response.status_code == 200
    data = response.json()
    assert all(case["status"] == "completado" for case in data["items"])

def test_filter_by_date_range(mock_db_success):
    """Prueba filtrado por rango de fechas"""
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    response = client.get(f"/api/support-cases/?start_date={start_date}&end_date={end_date}")
    assert response.status_code == 200

def test_multiple_filters(mock_db_success):
    """Prueba múltiples filtros combinados"""
    response = client.get("/api/support-cases/?database_name=finkargo_transacciones&status=pendiente")
    assert response.status_code == 200
    data = response.json()
    assert all(
        case["database_name"] == "finkargo_transacciones" and 
        case["status"] == "pendiente"
        for case in data["items"]
    )

@pytest.mark.asyncio
async def test_create_support_case_success():
    """Prueba creación exitosa de caso de soporte"""
    with patch('services.support_service.execute', new_callable=AsyncMock) as mock_execute:
        # Configurar mock para devolver un resultado exitoso
        mock_execute.return_value = {"id": str(uuid.uuid4())}
        
        from services.support_service import SupportService
        response = await SupportService.create_support_case(**VALID_CASE_DATA)
        
        # Verificar respuesta
        assert response.success is True
        assert "Caso de soporte creado exitosamente" in response.message
        assert response.case is not None
        assert response.case.title == VALID_CASE_DATA["title"]
        assert response.case.status == "pendiente"  # Estado por defecto
        
        # Verificar que se llamó al execute con los parámetros correctos
        mock_execute.assert_called_once()

@pytest.mark.asyncio
async def test_create_support_case_missing_fields():
    """Prueba que faltan campos obligatorios"""
    from services.support_service import SupportService
    
    # Probar con cada campo faltante
    for field in VALID_CASE_DATA:
        test_data = VALID_CASE_DATA.copy()
        test_data[field] = ""  # Campo vacío
        
        response = await SupportService.create_support_case(**test_data)
        
        assert response.success is False
        assert "Todos los campos son obligatorios" in response.message
        assert response.case is None

@pytest.mark.asyncio
async def test_create_support_case_db_error():
    """Prueba error al insertar en base de datos"""
    with patch('services.support_service.execute', new_callable=AsyncMock) as mock_execute:
        # Configurar mock para devolver None (error)
        mock_execute.return_value = None
        
        from services.support_service import SupportService
        response = await SupportService.create_support_case(**VALID_CASE_DATA)
        
        assert response.success is False
        assert "Error al crear el caso de soporte" in response.message
        assert response.case is None
    
@pytest.mark.asyncio
async def test_create_support_case_exception():
    """Prueba manejo de excepciones generales"""
    with patch('services.support_service.execute', side_effect=Exception("Error de conexión")) as mock_execute:
        from services.support_service import SupportService
        response = await SupportService.create_support_case(**VALID_CASE_DATA)
        
        assert response.success is False
        assert "Error al crear el caso de soporte" in response.message
        assert "Error de conexión" in response.message
        assert response.case is None

@pytest.mark.asyncio
async def test_create_support_case_data_structure():
    """Prueba que los datos se estructuran correctamente"""
    with patch('services.support_service.execute', new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = {"id": str(uuid.uuid4())}
        
        from services.support_service import SupportService
        response = await SupportService.create_support_case(**VALID_CASE_DATA)
        
        # Verificar estructura del caso creado
        assert isinstance(response.case, SupportCase)
        assert isinstance(response.case.id, uuid.UUID)
        assert isinstance(response.case.created_at, datetime)
        assert response.case.updated_at == response.case.created_at
