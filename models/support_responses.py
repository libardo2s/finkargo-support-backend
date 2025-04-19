from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID


class SupportCase(BaseModel):
    id: UUID
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    database_name: str
    schema_name: str
    sql_query: str
    executed_by: str
    status: str = Field("pending")
    created_at: datetime
    updated_at: datetime
    execution_result: Optional[str] = None
    priority: str = Field("baja")


class PaginatedResponse(BaseModel):
    message: str = Field(..., description="Response message in Spanish")
    success: bool
    items: List[SupportCase]
    total: int
    page: int
    size: int
    total_pages: int


class ErrorDetail(BaseModel):
    field: str
    message: str
    error_type: str


class ErrorResponse(BaseModel):
    success: bool = False
    message: str = "Validation error"
    errors: List[ErrorDetail]
    error_code: Optional[str] = None


class SupportCaseCreatedResponse(BaseModel):

    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo de la respuesta")
    case: Optional[SupportCase] = Field(
        None, description="Detalles completos del caso creado"
    )

class CaseResponse(BaseModel):
    success: bool
    message: str
    case: SupportCase


class SupportCaseCreateRequest(BaseModel):
    title: str = Field(..., max_length=100, description="Title of the support case")
    description: str = Field(
        ..., max_length=500, description="Description of the support case"
    )
    database_name: str = Field(..., max_length=50, description="Name of the database")
    schema_name: str = Field(..., max_length=50, description="Name of the schema")
    sql_query: str = Field(..., description="SQL query to be executed")
    executed_by: str = Field(..., max_length=50, description="Username of the executor")
    status: str = Field(
        "pending", description="Status of the support case (pendiente/completado)"
    )
    priority: str = Field(..., description="Priority level (baja/media/alta)")

    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = {'baja', 'media', 'alta'}
        if v not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(allowed_priorities)}")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = {'pendiente', 'completado', 'en_proceso', 'rechazado', 'en_pausa'}
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v

