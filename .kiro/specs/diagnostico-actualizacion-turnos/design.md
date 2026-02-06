# Design Document

## Overview

Este diseño especifica la solución para diagnosticar y resolver problemas en el sistema de turnos médicos desplegado en AWS. El sistema actual tiene un problema donde la lambda `ModifyTurnoFunction` no actualiza correctamente los campos `fechaTurno` y `horaTurno` en DynamoDB, aunque el código ya incluye lógica para aceptar ambos formatos de nombres de campos.

El diseño se enfoca en:
1. Diagnóstico sistemático del problema mediante análisis de logs y código
2. Validación de consistencia entre OpenAPI, lambdas y el agente de IA
3. Mejoras en logging para facilitar debugging futuro
4. Implementación de validación de disponibilidad de horarios
5. Correcciones en el código de la lambda
6. Proceso de actualización del stack de CloudFormation
7. Gestión del caché del MCP Server
8. Documentación completa del proceso

## Architecture

### System Components

```
┌─────────────────┐
│  Amazon Connect │
│   + Agente Luna │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MCP Server    │
│  (OpenAPI Spec) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Gateway    │
│   /turnos/*     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         Lambda Functions            │
│  ┌──────────────────────────────┐  │
│  │ ModifyTurnoFunction (Python) │  │
│  │ CreateTurnoFunction (Node.js)│  │
│  │ GetTurnosPacienteFunction    │  │
│  │ CancelTurnoFunction          │  │
│  │ SearchMedicosFunction        │  │
│  └──────────────────────────────┘  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│    DynamoDB     │
│  TurnosTable    │
│  MedicosTable   │
└─────────────────┘
```

### Data Flow for Modify Turno

```
1. Patient → Amazon Connect → Agente Luna
2. Agente Luna → MCP Server (reads OpenAPI spec)
3. Agente Luna → API Gateway POST /turnos/modificar
4. API Gateway → ModifyTurnoFunction
5. ModifyTurnoFunction → DynamoDB UpdateItem
6. DynamoDB → ModifyTurnoFunction (updated attributes)
7. ModifyTurnoFunction → API Gateway → Agente Luna
```

## Components and Interfaces

### 1. Diagnostic Module

**Purpose:** Analizar el sistema para identificar la causa raíz del problema

**Functions:**

```python
def analyze_lambda_code(lambda_function_name: str) -> DiagnosticReport:
    """
    Analiza el código de una lambda para identificar problemas
    
    Args:
        lambda_function_name: Nombre de la función Lambda
        
    Returns:
        DiagnosticReport con hallazgos y recomendaciones
    """
    pass

def compare_field_handling(modify_lambda_code: str, create_lambda_code: str) -> ComparisonReport:
    """
    Compara cómo dos lambdas manejan los campos de fecha y hora
    
    Args:
        modify_lambda_code: Código de ModifyTurnoFunction
        create_lambda_code: Código de CreateTurnoFunction
        
    Returns:
        ComparisonReport con diferencias identificadas
    """
    pass

def analyze_cloudwatch_logs(log_group: str, time_range: TimeRange) -> LogAnalysis:
    """
    Analiza logs de CloudWatch para identificar patrones de error
    
    Args:
        log_group: Nombre del log group
        time_range: Rango de tiempo a analizar
        
    Returns:
        LogAnalysis con patrones identificados
    """
    pass
```

### 2. Consistency Validator

**Purpose:** Validar consistencia entre OpenAPI, lambdas y el agente

**Functions:**

```python
def validate_openapi_lambda_consistency(
    openapi_spec: dict,
    lambda_code: str,
    endpoint: str
) -> ConsistencyReport:
    """
    Valida que los campos en OpenAPI coincidan con los procesados en la lambda
    
    Args:
        openapi_spec: Especificación OpenAPI parseada
        lambda_code: Código de la función Lambda
        endpoint: Endpoint a validar (ej: /turnos/modificar)
        
    Returns:
        ConsistencyReport con discrepancias encontradas
    """
    pass

def extract_request_fields(openapi_spec: dict, endpoint: str) -> list[str]:
    """
    Extrae los campos del requestBody de un endpoint en OpenAPI
    
    Args:
        openapi_spec: Especificación OpenAPI parseada
        endpoint: Endpoint a analizar
        
    Returns:
        Lista de nombres de campos
    """
    pass

def extract_processed_fields(lambda_code: str) -> list[str]:
    """
    Extrae los campos que la lambda procesa del request body
    
    Args:
        lambda_code: Código de la función Lambda
        
    Returns:
        Lista de nombres de campos procesados
    """
    pass
```

### 3. Enhanced Logger

**Purpose:** Mejorar el logging en las lambdas para facilitar debugging

**Implementation:**

```python
import json
import traceback
from typing import Any, Dict

class EnhancedLogger:
    """Logger mejorado para lambdas con contexto estructurado"""
    
    def __init__(self, request_id: str):
        self.request_id = request_id
    
    def log_request(self, event: Dict[str, Any]) -> None:
        """Registra el request completo recibido"""
        print(json.dumps({
            'level': 'INFO',
            'message': 'Request received',
            'requestId': self.request_id,
            'event': event,
            'body': json.loads(event.get('body', '{}'))
        }))
    
    def log_update_expression(
        self,
        update_expression: str,
        expression_values: Dict[str, Any]
    ) -> None:
        """Registra el UpdateExpression antes de ejecutarlo"""
        print(json.dumps({
            'level': 'INFO',
            'message': 'Executing DynamoDB update',
            'requestId': self.request_id,
            'updateExpression': update_expression,
            'expressionValues': expression_values
        }))
    
    def log_update_result(self, attributes: Dict[str, Any]) -> None:
        """Registra los atributos actualizados retornados por DynamoDB"""
        print(json.dumps({
            'level': 'INFO',
            'message': 'Update completed successfully',
            'requestId': self.request_id,
            'updatedAttributes': attributes
        }))
    
    def log_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Registra errores con stack trace completo"""
        print(json.dumps({
            'level': 'ERROR',
            'message': 'Error occurred',
            'requestId': self.request_id,
            'error': str(error),
            'errorType': type(error).__name__,
            'stack': traceback.format_exc(),
            'context': context
        }))
```

### 4. Availability Validator

**Purpose:** Validar disponibilidad de horarios al modificar turnos

**Functions:**

```python
def check_availability(
    medico_id: str,
    fecha_turno: str,
    hora_turno: str,
    exclude_turno_id: str = None
) -> AvailabilityResult:
    """
    Verifica si un horario está disponible para un médico
    
    Args:
        medico_id: ID del médico
        fecha_turno: Fecha en formato YYYY-MM-DD
        hora_turno: Hora en formato HH:MM
        exclude_turno_id: ID del turno actual (para excluirlo de la búsqueda)
        
    Returns:
        AvailabilityResult indicando si está disponible y detalles del conflicto
    """
    pass

def find_conflicting_turno(
    medico_id: str,
    fecha_turno: str,
    hora_turno: str,
    exclude_turno_id: str = None
) -> Optional[Dict[str, Any]]:
    """
    Busca un turno que conflictúe con el horario solicitado
    
    Args:
        medico_id: ID del médico
        fecha_turno: Fecha en formato YYYY-MM-DD
        hora_turno: Hora en formato HH:MM
        exclude_turno_id: ID del turno actual
        
    Returns:
        Turno conflictivo o None si no hay conflicto
    """
    pass
```

### 5. Modified Lambda Handler

**Purpose:** Lambda corregida con logging mejorado y validación de disponibilidad

**Implementation:**

```python
import json
import boto3
import os
import traceback
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TURNOS_TABLE_NAME'])

def decimal_default(obj):
    """Helper para serializar Decimal a JSON"""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError

def check_availability(
    medico_id: str,
    fecha_turno: str,
    hora_turno: str,
    exclude_turno_id: Optional[str] = None
) -> tuple[bool, Optional[Dict[str, Any]]]:
    """
    Verifica disponibilidad de horario
    
    Returns:
        (is_available, conflicting_turno)
    """
    # Query turnos for the medico on the specified date
    response = table.scan(
        FilterExpression='medicoId = :medicoId AND fechaTurno = :fechaTurno AND horaTurno = :horaTurno AND #status <> :cancelled',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':medicoId': medico_id,
            ':fechaTurno': fecha_turno,
            ':horaTurno': hora_turno,
            ':cancelled': 'cancelled'
        }
    )
    
    # Filter out the current turno if provided
    conflicting_turnos = [
        t for t in response['Items']
        if exclude_turno_id is None or t['turnoId'] != exclude_turno_id
    ]
    
    if conflicting_turnos:
        return False, conflicting_turnos[0]
    return True, None

def handler(event, context):
    """Handler mejorado con logging y validación"""
    request_id = event.get('requestContext', {}).get('requestId', 'unknown')
    logger = EnhancedLogger(request_id)
    
    try:
        # Log request completo
        logger.log_request(event)
        
        # Parse body
        if 'body' in event and event['body']:
            body = json.loads(event['body'])
        else:
            body = event
        
        # Extract required fields
        turno_id = body.get('turnoId')
        paciente_id = body.get('pacienteId')
        
        if not turno_id or not paciente_id:
            missing = []
            if not turno_id:
                missing.append('turnoId')
            if not paciente_id:
                missing.append('pacienteId')
            
            logger.log_error(
                ValueError(f'Missing parameters: {missing}'),
                {'body': body}
            )
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Missing required parameters: {", ".join(missing)}'
                })
            }
        
        # Get current turno to extract medicoId
        current_turno = table.get_item(Key={'turnoId': turno_id})
        if 'Item' not in current_turno:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Turno not found'})
            }
        
        medico_id = current_turno['Item']['medicoId']
        
        # Build update expression
        update_expression = 'SET modifiedAt = :modifiedAt'
        expression_values = {':modifiedAt': datetime.utcnow().isoformat()}
        
        # Handle fecha - accept both fechaTurno and fecha
        if 'fechaTurno' in body or 'fecha' in body:
            fecha = body.get('fechaTurno') or body.get('fecha')
            update_expression += ', fechaTurno = :fechaTurno'
            expression_values[':fechaTurno'] = fecha
        
        # Handle hora - accept both horaTurno and hora
        if 'horaTurno' in body or 'hora' in body:
            hora = body.get('horaTurno') or body.get('hora')
            update_expression += ', horaTurno = :horaTurno'
            expression_values[':horaTurno'] = hora
        
        # Validate availability if fecha or hora changed
        if 'fechaTurno' in expression_values or 'horaTurno' in expression_values:
            new_fecha = expression_values.get(':fechaTurno', current_turno['Item']['fechaTurno'])
            new_hora = expression_values.get(':horaTurno', current_turno['Item']['horaTurno'])
            
            is_available, conflicting_turno = check_availability(
                medico_id,
                new_fecha,
                new_hora,
                exclude_turno_id=turno_id
            )
            
            if not is_available:
                logger.log_error(
                    ValueError('Horario no disponible'),
                    {
                        'medicoId': medico_id,
                        'fechaTurno': new_fecha,
                        'horaTurno': new_hora,
                        'conflictingTurno': conflicting_turno
                    }
                )
                return {
                    'statusCode': 409,
                    'body': json.dumps({
                        'error': 'Horario no disponible',
                        'conflictingTurno': conflicting_turno['turnoId']
                    }, default=decimal_default)
                }
        
        # Handle other optional fields
        if 'motivoConsulta' in body:
            update_expression += ', motivoConsulta = :motivoConsulta'
            expression_values[':motivoConsulta'] = body['motivoConsulta']
        
        if 'telefono' in body or 'telefonoPaciente' in body:
            telefono = body.get('telefono') or body.get('telefonoPaciente')
            update_expression += ', telefono = :telefono'
            expression_values[':telefono'] = telefono
        
        # Log update expression before execution
        logger.log_update_expression(update_expression, expression_values)
        
        # Execute update
        response = table.update_item(
            Key={'turnoId': turno_id},
            UpdateExpression=update_expression,
            ConditionExpression='pacienteId = :pacienteId',
            ExpressionAttributeValues={
                **expression_values,
                ':pacienteId': paciente_id
            },
            ReturnValues='ALL_NEW'
        )
        
        # Log successful update
        logger.log_update_result(response['Attributes'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'Reservation modified successfully',
                'reservation': response['Attributes']
            }, default=decimal_default)
        }
        
    except Exception as e:
        logger.log_error(e, {'body': body if 'body' in locals() else {}})
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'success': False
            }, default=decimal_default)
        }
```

### 6. CloudFormation Update Manager

**Purpose:** Gestionar la actualización del stack de CloudFormation

**Functions:**

```python
def update_lambda_code(
    stack_name: str,
    lambda_logical_id: str,
    new_code: str
) -> UpdateResult:
    """
    Actualiza el código de una lambda en el template de CloudFormation
    
    Args:
        stack_name: Nombre del stack
        lambda_logical_id: ID lógico de la lambda en el template
        new_code: Nuevo código de la lambda
        
    Returns:
        UpdateResult con status de la actualización
    """
    pass

def validate_template(template_path: str) -> ValidationResult:
    """
    Valida un template de CloudFormation antes de desplegarlo
    
    Args:
        template_path: Ruta al template
        
    Returns:
        ValidationResult con errores si los hay
    """
    pass

def deploy_stack_update(
    stack_name: str,
    template_path: str,
    parameters: Dict[str, str]
) -> DeploymentResult:
    """
    Despliega una actualización del stack
    
    Args:
        stack_name: Nombre del stack
        template_path: Ruta al template actualizado
        parameters: Parámetros del stack
        
    Returns:
        DeploymentResult con status del despliegue
    """
    pass
```

### 7. MCP Cache Manager

**Purpose:** Gestionar el caché del MCP Server

**Functions:**

```python
def force_cache_reload(agent_id: str) -> CacheReloadResult:
    """
    Fuerza la recarga del caché mediante Unpublish/Publish
    
    Args:
        agent_id: ID del agente en Amazon Connect
        
    Returns:
        CacheReloadResult con status de la operación
    """
    pass

def add_cache_busting_timestamp(openapi_url: str) -> str:
    """
    Agrega un timestamp a la URL del OpenAPI para cache busting
    
    Args:
        openapi_url: URL original del OpenAPI
        
    Returns:
        URL con timestamp agregado
    """
    pass

def upload_openapi_to_s3(
    bucket: str,
    openapi_content: str,
    use_timestamp: bool = False
) -> S3UploadResult:
    """
    Sube la especificación OpenAPI a S3
    
    Args:
        bucket: Nombre del bucket
        openapi_content: Contenido del OpenAPI
        use_timestamp: Si debe agregar timestamp al nombre del archivo
        
    Returns:
        S3UploadResult con la URL del archivo subido
    """
    pass
```

## Data Models

### DiagnosticReport

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Finding:
    """Un hallazgo del diagnóstico"""
    severity: str  # 'critical', 'warning', 'info'
    category: str  # 'code', 'configuration', 'data'
    description: str
    location: str  # Ubicación en el código o configuración
    recommendation: str

@dataclass
class DiagnosticReport:
    """Reporte de diagnóstico del sistema"""
    lambda_name: str
    findings: List[Finding]
    summary: str
    requires_code_change: bool
    requires_config_change: bool
```

### ConsistencyReport

```python
@dataclass
class FieldDiscrepancy:
    """Discrepancia en un campo"""
    field_name: str
    in_openapi: bool
    in_lambda: bool
    openapi_type: Optional[str]
    lambda_processing: Optional[str]

@dataclass
class ConsistencyReport:
    """Reporte de consistencia OpenAPI-Lambda"""
    endpoint: str
    is_consistent: bool
    discrepancies: List[FieldDiscrepancy]
    missing_in_lambda: List[str]
    missing_in_openapi: List[str]
```

### AvailabilityResult

```python
@dataclass
class AvailabilityResult:
    """Resultado de validación de disponibilidad"""
    is_available: bool
    medico_id: str
    fecha_turno: str
    hora_turno: str
    conflicting_turno_id: Optional[str]
    conflicting_turno_details: Optional[Dict[str, Any]]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: UpdateExpression Field Detection

*For any* Lambda code that processes date and time fields, the diagnostic analyzer should correctly identify whether `fechaTurno` and `horaTurno` are being included in the UpdateExpression.

**Validates: Requirements 1.1**

### Property 2: Lambda Comparison Accuracy

*For any* pair of Lambda functions that handle similar operations, the comparison tool should identify all differences in how they process date and time fields.

**Validates: Requirements 1.2**

### Property 3: Log Field Extraction

*For any* CloudWatch log entry from a Lambda execution, the log analyzer should correctly identify whether `fechaTurno` and `horaTurno` values are present in the logged request body.

**Validates: Requirements 1.3**

### Property 4: Request Body Validation

*For any* request body received by the Lambda, the validator should correctly determine whether it contains the expected field names (`fechaTurno`/`fecha`, `horaTurno`/`hora`).

**Validates: Requirements 1.4**

### Property 5: DynamoDB Syntax Validation

*For any* UpdateExpression string, the validator should correctly classify it as syntactically valid or invalid according to DynamoDB rules.

**Validates: Requirements 1.5**

### Property 6: OpenAPI-Lambda Consistency Detection

*For any* endpoint defined in OpenAPI and its corresponding Lambda implementation, the consistency validator should identify all field name discrepancies between the specification and the code.

**Validates: Requirements 2.1, 2.2**

### Property 7: Consistency Report Completeness

*For any* set of detected inconsistencies between OpenAPI and Lambda, the generated report should include all fields that don't match.

**Validates: Requirements 2.3**

### Property 8: Field Processing Completeness

*For any* endpoint with a requestBody in OpenAPI, the validator should identify all fields that are defined in the spec but not processed by the Lambda.

**Validates: Requirements 2.4**

### Property 9: Request Logging Completeness

*For any* request received by the Lambda, a log entry with level INFO should be generated containing the complete request body.

**Validates: Requirements 3.1**

### Property 10: UpdateExpression Logging

*For any* UpdateExpression constructed by the Lambda, a log entry should be generated before execution containing both the expression and the expression values.

**Validates: Requirements 3.2**

### Property 11: Update Result Logging

*For any* successful DynamoDB update operation, a log entry should be generated containing the updated attributes returned by DynamoDB.

**Validates: Requirements 3.3**

### Property 12: Error Logging Completeness

*For any* exception that occurs during Lambda execution, a log entry should be generated containing the error message, error type, stack trace, and execution context.

**Validates: Requirements 3.4**

### Property 13: RequestId Consistency

*For any* sequence of log entries from a single Lambda execution, all entries should contain the same requestId value.

**Validates: Requirements 3.5**

### Property 14: Availability Conflict Detection

*For any* modification request to a new date and time, if another turno exists for the same medico at that time (excluding the current turno), the system should detect the conflict and return a 409 status code.

**Validates: Requirements 4.1, 4.2**

### Property 15: Self-Exclusion in Availability Check

*For any* turno being modified to the same date and time it currently has, the availability check should not detect a conflict with itself.

**Validates: Requirements 4.3**

### Property 16: Conflict Logging

*For any* availability validation that fails due to a conflict, a log entry should be generated containing the conflicting turnoId and conflict details.

**Validates: Requirements 4.4**

### Property 17: Alternative Field Name Acceptance

*For any* request containing either `fechaTurno` or `fecha` (and similarly `horaTurno` or `hora`), the Lambda should include the field in the UpdateExpression with the correct value.

**Validates: Requirements 5.1, 5.2**

### Property 18: Field Preservation Invariant

*For any* turno update operation, all fields that existed before the update and were not explicitly modified should remain unchanged in the updated turno.

**Validates: Requirements 5.4**

### Property 19: Successful Update Response Format

*For any* successful update operation, the response should have statusCode 200 and include the complete updated turno with all attributes.

**Validates: Requirements 5.3, 5.5**

### Property 20: Cache Busting Command Generation

*For any* OpenAPI URL, the cache busting function should generate a valid command that adds a timestamp query parameter to the URL.

**Validates: Requirements 7.2**

## Error Handling

### Error Categories

1. **Validation Errors (400)**
   - Missing required parameters (turnoId, pacienteId)
   - Invalid field formats
   - Response: JSON with descriptive error message

2. **Not Found Errors (404)**
   - Turno does not exist
   - Response: JSON with "Turno not found" message

3. **Conflict Errors (409)**
   - Horario already occupied by another turno
   - Response: JSON with conflict details and conflicting turnoId

4. **Authorization Errors (403)**
   - pacienteId does not match the turno owner
   - Response: JSON with "Unauthorized" message

5. **Internal Errors (500)**
   - DynamoDB errors
   - Unexpected exceptions
   - Response: JSON with error message and requestId for tracking

### Error Logging Strategy

All errors must be logged with:
- Error level (ERROR)
- Error message and type
- Full stack trace
- Request context (turnoId, pacienteId, etc.)
- RequestId for correlation

### Error Recovery

- **Transient DynamoDB errors**: Lambda will retry automatically (AWS SDK default behavior)
- **Validation errors**: No retry, immediate response to client
- **Conflict errors**: Client should query available slots and retry with different time

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples of valid and invalid requests
- Edge cases (empty fields, special characters, boundary dates)
- Error conditions (missing parameters, conflicts, not found)
- Integration points (DynamoDB operations, log formatting)

**Property-Based Tests** focus on:
- Universal properties across all inputs (see Correctness Properties section)
- Randomized input generation to discover edge cases
- Invariants that must hold regardless of input

### Property-Based Testing Configuration

- **Library**: Use `hypothesis` for Python lambdas, `fast-check` for Node.js lambdas
- **Iterations**: Minimum 100 iterations per property test
- **Test Tagging**: Each property test must reference its design document property

Tag format:
```python
# Feature: diagnostico-actualizacion-turnos, Property 17: Alternative Field Name Acceptance
```

### Test Coverage Requirements

1. **Diagnostic Module**
   - Unit tests for each analysis function with known good/bad inputs
   - Property tests for analyzer correctness across random code samples

2. **Consistency Validator**
   - Unit tests for specific OpenAPI-Lambda pairs
   - Property tests for consistency detection across random specs

3. **Enhanced Logger**
   - Unit tests for each log method with sample data
   - Property tests for requestId consistency and log completeness

4. **Availability Validator**
   - Unit tests for specific conflict scenarios
   - Property tests for conflict detection across random turno sets

5. **Modified Lambda Handler**
   - Unit tests for each request type and error condition
   - Property tests for field preservation and response format

### Integration Testing

Integration tests should verify:
1. End-to-end flow from API Gateway to DynamoDB
2. CloudWatch log generation and format
3. Error responses match OpenAPI specification
4. Cache reload process works correctly

### Manual Testing Checklist

After deployment:
1. ✅ Verify Lambda code updated in AWS Console
2. ✅ Test modify turno with `fechaTurno` and `horaTurno`
3. ✅ Test modify turno with `fecha` and `hora`
4. ✅ Verify DynamoDB shows updated values
5. ✅ Check CloudWatch logs for enhanced logging
6. ✅ Test conflict detection with overlapping turnos
7. ✅ Verify OpenAPI spec updated in S3
8. ✅ Unpublish/Publish agent and test end-to-end

