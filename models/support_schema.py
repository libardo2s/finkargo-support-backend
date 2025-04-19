from pydantic import BaseModel, Field, conint, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class CaseStatus(str, Enum):
    PENDING = "pendiente"
    COMPLETED = "completado"
    IN_PROGRESS = "en_proceso"
    REJECTED = "rechazado"
    ON_HOLD = "en_pausa"


class PriorityLevel(str, Enum):
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"


class SupportCase(BaseModel):
    id: UUID
    status: CaseStatus
    created_at: datetime
    updated_at: datetime
    execution_result: Optional[str] = None
    title: str = Field(
        max_length=100, description="Title of the support case", required=True
    )
    description: str = Field(
        max_length=500, description="Description of the support case", required=True
    )
    database_name: str = Field(max_length=50, required=True)
    schema_name: str = Field(max_length=50, required=True)
    sql_query: str
    executed_by: str = Field(max_length=50, required=True)
    priority: PriorityLevel

    @validator("status")
    def validate_status(cls, v):
        allowed_statuses = [
            "pendiente",
            "completado",
            "en_proceso",
            "rechazado",
            "en_pausa",
        ]
        if v not in allowed_statuses:
            raise ValueError(
                f"Estado inválido. Debe ser uno de: {', '.join(allowed_statuses)}"
            )
        return v

    @validator("priority")
    def validate_priority(cls, v):
        allowed_priorities = ["baja", "media", "alta"]
        if v not in allowed_priorities:
            raise ValueError(
                f"Prioridad inválida. Debe ser uno de: {', '.join(allowed_priorities)}"
            )
        return v

    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    id: Optional[str] = None
    page: conint(gt=0) = 1
    size: conint(gt=0, le=100) = 10
    status: Optional[str] = None
    database_name: Optional[str] = None
    schema_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    executed_by: Optional[str] = None
    priority: Optional[str] = None

    @validator("page", "size", pre=True)
    def validate_numbers(cls, v):
        if not isinstance(v, int):
            raise ValueError("must be an integer")
        return v
