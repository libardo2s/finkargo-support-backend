from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from models.support_responses import ErrorResponse, ErrorDetail

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "unknown_field"
        msg = error["msg"]
        error_type = error["type"]
        
        # Traducción de mensajes al español
        if error_type == "missing":
            msg = "Campo requerido"
        elif error_type == "value_error.missing":
            msg = "Campo requerido"
        elif error_type == "int_parsing":
            msg = "Debe ser un número entero"
        elif error_type == "string_too_short":
            msg = f"El texto debe tener al menos {error['ctx']['min_length']} caracteres"
        elif error_type == "string_too_long":
            msg = f"El texto no puede exceder los {error['ctx']['max_length']} caracteres"
        elif error_type == "greater_than":
            msg = f"Debe ser mayor que {error['ctx']['gt']}"
        elif error_type == "less_than_equal":
            msg = f"Debe ser menor o igual a {error['ctx']['le']}"
        elif error_type == "value_error.email":
            msg = "El email no tiene un formato válido"
        elif error_type == "type_error.integer":
            msg = "Se esperaba un valor entero"
        elif error_type == "type_error.float":
            msg = "Se esperaba un número decimal"
        elif error_type == "value_error.number.not_gt":
            msg = f"El valor debe ser mayor que {error['ctx']['gt']}"
        elif error_type == "value_error.number.not_lt":
            msg = f"El valor debe ser menor que {error['ctx']['lt']}"
        
        errors.append(ErrorDetail(
            field=field,
            message=msg,
            error_type=error_type
        ))
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            success=False,
            message="Error de validación en los parámetros",
            errors=errors,
            error_code="VALIDATION_ERROR"
        ).dict()
    )