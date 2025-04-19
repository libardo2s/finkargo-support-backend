import uvicorn

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware  # Add this import

from database.connection import db
from routes.support_cases import router as support_cases_router
from utils.exceptions_handler import validation_exception_handler

app = FastAPI(
    title="Finkargo Support Tracker API",
    description="API para el sistema de trazabilidad de casos de soporte",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

@app.on_event("startup")
async def startup():
    pass

@app.on_event("shutdown")
async def shutdown():
    db.close_all_connections()

app.include_router(support_cases_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)