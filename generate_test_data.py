import uuid
from datetime import datetime, timedelta
import random
from faker import Faker
import asyncio
from enum import Enum
from database.connection import execute, create_database, drop_database

# Configure Faker for Spanish data
fake = Faker('es_ES')

# Status Enum
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

# Configuration
DATABASE_NAME = "finkargo_support_cases"
DATABASES = ["finkargo_transacciones", "finkargo_clientes", "finkargo_facturacion"]
SCHEMAS = ["operaciones", "clientes", "facturas", "envios"]
STATUSES = [status.value for status in CaseStatus]
PRIORITY = [priority.value for priority in PriorityLevel]
USERS = [
    "juan.perez@finkargo.com",
    "maria.gonzalez@finkargo.com",
    "carlos.rodriguez@finkargo.com",
    "ana.martinez@finkargo.com"
]

CASE_TYPES = {
    "update": [
        "Actualizar estado de envío",
        "Corregir dirección cliente",
        "Actualizar teléfono contacto",
        "Modificar monto factura"
    ],
    "insert": [
        "Nuevo registro de envío",
        "Crear factura manual",
        "Registrar devolución"
    ],
    "delete": [
        "Eliminar datos temporales",
        "Borrar registros antiguos",
        "Limpiar datos de prueba"
    ]
}

async def setup_database():
    """Drop and recreate the database with all necessary tables"""
    print(f"Eliminando base de datos '{DATABASE_NAME}' si existe...")
    await drop_database(DATABASE_NAME)
    
    print(f"Creando nueva base de datos '{DATABASE_NAME}'...")
    await create_database(DATABASE_NAME)
    
    print("Creando tablas...")
    # First ensure the table doesn't exist
    await execute("DROP TABLE IF EXISTS support_cases")
    
    # Then create it with the new schema
    await execute(f"""
    CREATE TABLE support_cases (
        id UUID PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        database_name VARCHAR(100),
        schema_name VARCHAR(100),
        sql_query TEXT NOT NULL,
        executed_by VARCHAR(255) NOT NULL,
        status VARCHAR(50) NOT NULL,
        priority VARCHAR(50) NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        execution_result TEXT
    )
    """)
    print("Estructura de base de datos creada exitosamente")

def generate_sql_query(case_type: str) -> str:
    """Generate realistic SQL queries in Spanish"""
    if case_type == "update":
        table = random.choice(["operaciones", "clientes", "facturas"])
        field = random.choice(["estado", "direccion", "telefono", "monto"])
        value = f"'{fake.word()}'" if field != "monto" else random.randint(1, 1000)
        id_value = random.randint(1000, 9999)
        return f"UPDATE {table} SET {field} = {value} WHERE id = {id_value}"
    
    elif case_type == "insert":
        table = random.choice(["envios", "pedidos"])
        columns = ["estado", "fecha_creacion", "fecha_actualizacion"]
        values = [f"'{random.choice([CaseStatus.PENDING, CaseStatus.IN_PROGRESS])}'", 
                 f"'{datetime.now().isoformat()}'",
                 f"'{datetime.now().isoformat()}'"]
        return f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)})"
    
    else:  # delete
        table = random.choice(["registros_temporales", "datos_prueba"])
        return f"DELETE FROM {table} WHERE fecha_creacion < '{datetime.now() - timedelta(days=30)}'"

def generate_description(title: str) -> str:
    """Generate realistic Spanish descriptions"""
    common_issues = [
        "El cliente reportó que la información está incorrecta",
        "Error detectado durante el proceso de reconciliación",
        "Solicitud del equipo de atención al cliente",
        "Problema identificado en auditoría interna",
        "Requiere actualización por cambios en políticas",
        "Inconsistencia encontrada durante revisión de calidad"
    ]
    
    actions = [
        "Se requiere actualización manual de los registros",
        "Necesita corrección inmediata para continuar el proceso",
        "Debe modificarse antes del cierre del día",
        "Urgente: afecta proceso de facturación",
        "Prioridad alta: impacto en experiencia del cliente"
    ]
    
    return f"{random.choice(common_issues)}. {random.choice(actions)}."

async def insert_test_case(case_data: dict):
    """Insert a test case into the database"""
    query = """
    INSERT INTO support_cases (
        id, title, description, database_name, schema_name, 
        sql_query, executed_by, status, priority, created_at, 
        updated_at, execution_result
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        str(case_data["id"]),
        case_data["title"],
        case_data["description"],
        case_data["database_name"],
        case_data["schema_name"],
        case_data["sql_query"],
        case_data["executed_by"],
        case_data["status"],
        case_data["priority"],
        case_data["created_at"],
        case_data["updated_at"],
        case_data["execution_result"]
    )
    await execute(query, values)

async def generate_test_cases(num_cases: int = 100):
    """Generate and insert test cases in Spanish"""
    for i in range(num_cases):
        case_type = random.choice(["update", "insert", "delete"])
        title = random.choice(CASE_TYPES[case_type])
        created_at = fake.date_time_between(start_date="-6m", end_date="now")
        
        case_data = {
            "id": uuid.uuid4(),
            "title": title,
            "description": generate_description(title),
            "database_name": random.choice(DATABASES),
            "schema_name": random.choice(SCHEMAS),
            "sql_query": generate_sql_query(case_type),
            "executed_by": random.choice(USERS),
            "status": random.choice(STATUSES),
            "priority": random.choice(PRIORITY),
            "created_at": created_at,
            "updated_at": created_at + timedelta(minutes=random.randint(0, 120)),
            "execution_result": random.choice([
                None,
                f"{random.randint(1, 5)} registros afectados",
                "Error: " + fake.sentence(nb_words=5),
                "Completado satisfactoriamente",
                "Requiere revisión adicional"
            ])
        }
        
        await insert_test_case(case_data)
        print(f"Generated case {i+1}/{num_cases}: {case_data['title']} - Status: {case_data['status']} - Priority: {case_data['priority']}")

async def main():
    print("Iniciando proceso de generación de datos de prueba...")
    
    # Step 1: Recreate database structure
    await setup_database()
    
    # Step 2: Generate test cases
    print("\nGenerando casos de prueba...")
    await generate_test_cases(100)
    
    print("\nProceso completado exitosamente!")
    print(f"Se generaron 100 casos de prueba en la base de datos '{DATABASE_NAME}'")

if __name__ == "__main__":
    asyncio.run(main())