GET_PAGINATED_CASES = """
SELECT 
    id, title, description, database_name, schema_name, 
    sql_query, executed_by, status, created_at, updated_at, execution_result
FROM support_cases
ORDER BY created_at DESC
LIMIT %s OFFSET %s
"""

GET_TOTAL_CASES = """
SELECT COUNT(*) FROM support_cases
"""

CREATE_CASE_TABLE = """
CREATE TABLE IF NOT EXISTS support_cases (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    database_name VARCHAR(100),
    schema_name VARCHAR(100),
    sql_query TEXT NOT NULL,
    executed_by VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    execution_result TEXT,
    priority VARCHAR(50) NOT NULL
)
"""