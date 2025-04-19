from datetime import datetime
from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse
from services.support_service import SupportService
from models.support_responses import PaginatedResponse, SupportCaseCreateRequest, CaseResponse
from models.support_schema import PaginationParams
from utils.exceptions_handler import ErrorResponse


router = APIRouter(
    prefix="/api/support-cases",
    tags=["Support Cases"],
)


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get paginated support cases",
    description="Returns a paginated list of support cases with metadata",
    responses={
        400: {"model": ErrorResponse, "description": "Error en la solicitud"},
        422: {"model": ErrorResponse, "description": "Error de validación"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"},
    },
)
async def get_support_cases(pagination: PaginationParams = Depends()):
    """
    Get paginated support cases with filters

    Parameters:
    - id: Filter by case ID (optional)
    - page: Page number (default: 1)
    - size: Items per page (default: 10, max: 100)
    - status: Filter by status (optional)
    - database_name: Filter by database name (optional)
    - schema_name: Filter by schema name (optional)
    - start_date: Filter cases created after this date (optional)
    - end_date: Filter cases created before this date (optional)
    - executed_by: Filter by user who executed the case (optional)

    Returns:
    - Paginated list of filtered cases
    """
    try:
        response = await SupportService.get_paginated_cases(
            id=pagination.id,
            page=pagination.page,
            size=pagination.size,
            status=pagination.status,
            database_name=pagination.database_name,
            schema_name=pagination.schema_name,
            start_date=pagination.start_date,
            end_date=pagination.end_date,
            executed_by=pagination.executed_by,
            priority=pagination.priority,
        )

        if not response.success:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": response.message,
                    "error_code": "INVALID_REQUEST",
                },
            )

        return response

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Error interno del servidor",
                "error_code": "INTERNAL_SERVER_ERROR",
                "detail": str(e),
            },
        )

@router.get(
    "/case/{case_id}",
    response_model=CaseResponse,  # Now matches our return structure
    summary="Get a support case by ID",
    description="Returns a single support case by its ID",
    responses={
        400: {"model": ErrorResponse, "description": "Error en la solicitud"},
        404: {"model": ErrorResponse, "description": "Case not found"},
        422: {"model": ErrorResponse, "description": "Error de validación"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"},
    },
)
async def get_case_by_id(case_id: str):
    """
    Get a single support case by ID

    Parameters:
    - case_id: The ID of the case to retrieve (required)
    """
    try:
        response = await SupportService.get_case_by_id(case_id)
        
        if not response or not response.success:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Case not found",
                    "error_code": "NOT_FOUND",
                },
            )
            
        # Ensure the response matches our CaseResponse model
        return {
            "success": response.success,
            "message": response.message,
            "case": response.case
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Error interno del servidor",
                "error_code": "INTERNAL_SERVER_ERROR",
                "detail": str(e),
            },
        )

@router.post(
    "/",
    summary="Create a new support case",
    description="Creates a new support case with the provided data",
    responses={
        201: {"description": "Caso creado exitosamente"},
        400: {"model": ErrorResponse, "description": "Error en la solicitud"},
        422: {"model": ErrorResponse, "description": "Error de validación"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"},
    },
)
async def create_support_case(case_data: SupportCaseCreateRequest = Body(...)):
    """
    Create a new support case

    Parameters:
    - title: Case title (max 100 chars)
    - description: Detailed description (max 500 chars)
    - database_name: Target database name
    - schema_name: Target schema name
    - sql_query: SQL query to be executed
    - executed_by: User who executed the query
    - priority: Case priority (baja/media/alta)

    Returns:
    - Created case information with success status
    """
    try:
        response = await SupportService.create_support_case(
            title=case_data.title,
            description=case_data.description,
            database_name=case_data.database_name,
            schema_name=case_data.schema_name,
            sql_query=case_data.sql_query,
            executed_by=case_data.executed_by,
            priority=case_data.priority,
        )

        if not response.success:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": response.message,
                    "error_code": "INVALID_REQUEST",
                },
            )

        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Error interno del servidor",
                "error_code": "INTERNAL_SERVER_ERROR",
                "detail": str(e),
            },
        )
