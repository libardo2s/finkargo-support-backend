import uuid
from datetime import datetime
from typing import Optional, Tuple
from fastapi import HTTPException
from database.connection import execute
from models.support_responses import PaginatedResponse, SupportCase, SupportCaseCreatedResponse, CaseResponse

class SupportService:

    @staticmethod
    async def get_case_by_id(
        case_id: str
    ) -> SupportCaseCreatedResponse:
        try:
            # Validar que el ID no esté vacío
            if not case_id:
                return SupportCaseCreatedResponse(
                    message="El ID del caso es requerido",
                    success=False,
                    case=None
                )
            
            # Validar que el ID tenga formato UUID
            try:
                uuid.UUID(case_id)
            except ValueError:
                return SupportCaseCreatedResponse(
                    message="El ID proporcionado no es válido",
                    success=False,
                    case=None
                )
            
            # Construir la consulta
            query = "SELECT * FROM support_cases WHERE id = %s"
            params = (case_id,)
            
            # Ejecutar la consulta
            case_data = await execute(query, params, fetch_one=True)
            print(case_data)
            
            # Si no se encuentra el caso
            if not case_data:
                return SupportCaseCreatedResponse(
                    message=f"No se encontró ningún caso con ID {case_id}",
                    success=False,
                    case=None
                )
            
            # Mapear los datos a un objeto SupportCase
            case = SupportCase(
                id=case_data[0],
                title=case_data[1],
                description=case_data[2],
                database_name=case_data[3],
                schema_name=case_data[4],
                sql_query=case_data[5],
                executed_by=case_data[6],
                status=case_data[7],
                priority=case_data[8],
                created_at=case_data[9],
                updated_at=case_data[10],
                execution_result=case_data[11] if len(case_data) > 11 else None
            )
            
            return SupportCaseCreatedResponse(
                message="Caso encontrado exitosamente",
                success=True,
                case=case
            )
            
        except Exception as e:
            return SupportCaseCreatedResponse(
                message=f"Error al buscar el caso: {str(e)}",
                success=False,
                case=None
            )
    
    @staticmethod
    async def get_paginated_cases(
        id: Optional[str] = None,
        page: int = 1, 
        size: int = 10,
        status: Optional[str] = None,
        database_name: Optional[str] = None,
        schema_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        executed_by: Optional[str] = None,
        priority: Optional[str] = None
    ) -> PaginatedResponse:
        try:
            # Validación de parámetros
            if page < 1:
                return PaginatedResponse(
                    message="El número de página debe ser positivo",
                    success=False,
                    items=[],
                    total=0,
                    page=page,
                    size=size,
                    total_pages=0
                )
            
            if size < 1 or size > 100:
                return PaginatedResponse(
                    message="El tamaño de página debe estar entre 1 y 100",
                    success=False,
                    items=[],
                    total=0,
                    page=page,
                    size=size,
                    total_pages=0
                )
            
            # Construcción de la consulta base
            base_query = "SELECT * FROM support_cases WHERE 1=1"
            count_query = "SELECT COUNT(*) FROM support_cases WHERE 1=1"
            params = []
            count_params = []
            
            # Añadir filtros condicionales
            filters = [
                (status, "status"),
                (database_name, "database_name"),
                (schema_name, "schema_name"),
                (executed_by, "executed_by"),
                (id, "id"),
                (priority, "priority")
            ]
            
            date_filters = [
                (start_date, "created_at >= %s"),
                (end_date, "created_at <= %s")
            ]
            
            for value, field in filters:
                if value is not None:
                    base_query += f" AND {field} = %s"
                    count_query += f" AND {field} = %s"
                    params.append(value)
                    count_params.append(value)
            
            for value, condition in date_filters:
                if value is not None:
                    base_query += f" AND {condition}"
                    count_query += f" AND {condition}"
                    params.append(value)
                    count_params.append(value)
            
            # Añadir ordenación y paginación
            base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([size, (page - 1) * size])
            
            # Ejecutar consultas
            cases_data = await execute(base_query, tuple(params), fetch_all=True)
            total_records = await execute(count_query, tuple(count_params), fetch_one=True)
            
            # Procesar resultados
            if not cases_data:
                cases_data = []
            
            if not total_records or not isinstance(total_records, Tuple):
                return PaginatedResponse(
                    message="Error en el formato de datos recibidos",
                    success=False,
                    items=[],
                    total=0,
                    page=page,
                    size=size,
                    total_pages=0
                )
            
            cases = [
                SupportCase(
                    id=case[0],
                    title=case[1],
                    description=case[2],
                    database_name=case[3],
                    schema_name=case[4],
                    sql_query=case[5],
                    executed_by=case[6],
                    status=case[7],
                    priority=case[8],
                    created_at=case[9],
                    updated_at=case[10],
                    execution_result=case[11],
                ) for case in cases_data
            ]
            
            return PaginatedResponse(
                message=f"Se obtuvieron {len(cases)} casos",
                success=True,
                items=cases,
                total=total_records[0],
                page=page,
                size=size,
                total_pages=(total_records[0] // size) + (1 if total_records[0] % size > 0 else 0),
            )
            
        except Exception as e:
            return PaginatedResponse(
                message=f"Error al obtener casos: {str(e)}",
                success=False,
                items=[],
                total=0,
                page=page,
                size=size,
                total_pages=0
            )
    
    @staticmethod
    async def create_support_case(
        title: str,
        description: str,
        database_name: str,
        schema_name: str,
        sql_query: str,
        executed_by: str,
        priority: str
    ) -> SupportCaseCreatedResponse:
        try:
        
            # Validate required fields
            if not all([title, description, database_name, schema_name, sql_query, executed_by, priority]):
                return SupportCaseCreatedResponse(
                    success=False,
                    message="Todos los campos son obligatorios",
                    case=None
                )
            # Generate case data
            case_id = uuid.uuid4()
            current_time = datetime.utcnow()
            initial_status = "pendiente"  # Default status for new cases

            # Insert into database
            query = """
                INSERT INTO support_cases (
                    id, title, description, database_name, schema_name,
                    sql_query, executed_by, status, created_at, updated_at, priority
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            params = (
                str(case_id), title, description, database_name, schema_name,
                sql_query, executed_by, initial_status, current_time, current_time, priority
            )

            # Execute the query
            result = await execute(query, params, fetch_one=True)

            if not result:
                return SupportCaseCreatedResponse(
                    success=False,
                    message="Error al crear el caso de soporte",
                    case=None,
                )

            # Return success response
            return SupportCaseCreatedResponse(
                success=True,
                message="Caso de soporte creado exitosamente",
                case=SupportCase(
                    id=case_id,
                    title=title,
                    description=description,
                    database_name=database_name,
                    schema_name=schema_name,
                    sql_query=sql_query,
                    executed_by=executed_by,
                    status=initial_status,
                    created_at=current_time,
                    updated_at=current_time,
                    priority=priority
                )
            )
        except Exception as e:
            return SupportCaseCreatedResponse(
                success=False,
                message=f"Error al crear el caso de soporte: {str(e)}",
                case=None,
            )