"""
Analizador de código Lambda para diagnosticar problemas en funciones Lambda.

Este módulo proporciona herramientas para analizar el código de funciones Lambda
y extraer información sobre cómo procesan campos, especialmente fechaTurno y horaTurno.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


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


def extract_update_expression_fields(lambda_code: str) -> List[str]:
    """
    Extrae los campos que están siendo incluidos en UpdateExpression de DynamoDB.
    
    Args:
        lambda_code: Código fuente de la función Lambda
        
    Returns:
        Lista de nombres de campos encontrados en UpdateExpression
    """
    fields = []
    
    # Buscar patrones de UpdateExpression
    # Patrón 1: update_expression += ', campo = :campo'
    pattern1 = r"update_expression\s*\+=\s*['\"],\s*(\w+)\s*="
    matches1 = re.findall(pattern1, lambda_code, re.IGNORECASE)
    fields.extend(matches1)
    
    # Patrón 2: UpdateExpression='SET campo = :valor'
    pattern2 = r"UpdateExpression\s*=\s*['\"]SET\s+(\w+)\s*="
    matches2 = re.findall(pattern2, lambda_code, re.IGNORECASE)
    fields.extend(matches2)
    
    # Patrón 3: 'SET campo = :valor, campo2 = :valor2'
    pattern3 = r"['\"]SET\s+(?:[\w\s=:,]+?)(\w+)\s*=\s*:\w+"
    matches3 = re.findall(pattern3, lambda_code, re.IGNORECASE)
    fields.extend(matches3)
    
    return list(set(fields))  # Eliminar duplicados


def extract_processed_fields(lambda_code: str) -> List[str]:
    """
    Extrae los campos que la lambda procesa del request body.
    
    Args:
        lambda_code: Código fuente de la función Lambda
        
    Returns:
        Lista de nombres de campos procesados
    """
    fields = []
    
    # Patrón 1: body.get('campo') o body['campo']
    pattern1 = r"body\.get\(['\"](\w+)['\"]\)|body\[['\"](\w+)['\"]\]"
    matches1 = re.findall(pattern1, lambda_code)
    for match in matches1:
        fields.extend([f for f in match if f])
    
    # Patrón 2: 'campo' in body
    pattern2 = r"['\"](\w+)['\"]\s+in\s+body"
    matches2 = re.findall(pattern2, lambda_code)
    fields.extend(matches2)
    
    # Patrón 3: const { campo } = body (JavaScript)
    pattern3 = r"const\s*\{\s*(\w+(?:\s*,\s*\w+)*)\s*\}\s*=\s*body"
    matches3 = re.findall(pattern3, lambda_code)
    for match in matches3:
        # Separar múltiples campos
        campo_list = [c.strip() for c in match.split(',')]
        fields.extend(campo_list)
    
    return list(set(fields))  # Eliminar duplicados


def analyze_lambda_code(lambda_name: str, lambda_code: str) -> DiagnosticReport:
    """
    Analiza el código de una lambda para identificar problemas.
    
    Args:
        lambda_name: Nombre de la función Lambda
        lambda_code: Código fuente de la función Lambda
        
    Returns:
        DiagnosticReport con hallazgos y recomendaciones
    """
    findings = []
    
    # Extraer campos procesados y campos en UpdateExpression
    processed_fields = extract_processed_fields(lambda_code)
    update_fields = extract_update_expression_fields(lambda_code)
    
    # Verificar si fechaTurno y horaTurno están en UpdateExpression
    fecha_in_update = any('fecha' in f.lower() for f in update_fields)
    hora_in_update = any('hora' in f.lower() for f in update_fields)
    
    if not fecha_in_update:
        findings.append(Finding(
            severity='critical',
            category='code',
            description='Campo fechaTurno no encontrado en UpdateExpression',
            location='UpdateExpression construction',
            recommendation='Verificar que el código incluya fechaTurno en el UpdateExpression cuando se recibe en el body'
        ))
    
    if not hora_in_update:
        findings.append(Finding(
            severity='critical',
            category='code',
            description='Campo horaTurno no encontrado en UpdateExpression',
            location='UpdateExpression construction',
            recommendation='Verificar que el código incluya horaTurno en el UpdateExpression cuando se recibe en el body'
        ))
    
    # Verificar si se procesan nombres alternativos (fecha/fechaTurno, hora/horaTurno)
    fecha_variants = [f for f in processed_fields if 'fecha' in f.lower()]
    hora_variants = [f for f in processed_fields if 'hora' in f.lower()]
    
    if len(fecha_variants) < 2:
        findings.append(Finding(
            severity='warning',
            category='code',
            description=f'Solo se procesa una variante de fecha: {fecha_variants}',
            location='Request body processing',
            recommendation='Considerar aceptar ambos formatos: fecha y fechaTurno para compatibilidad'
        ))
    
    if len(hora_variants) < 2:
        findings.append(Finding(
            severity='warning',
            category='code',
            description=f'Solo se procesa una variante de hora: {hora_variants}',
            location='Request body processing',
            recommendation='Considerar aceptar ambos formatos: hora y horaTurno para compatibilidad'
        ))
    
    # Verificar logging
    has_logging = 'print(' in lambda_code or 'console.log(' in lambda_code or 'logger.' in lambda_code
    if not has_logging:
        findings.append(Finding(
            severity='warning',
            category='code',
            description='No se encontró logging en el código',
            location='Handler function',
            recommendation='Agregar logging para facilitar debugging'
        ))
    
    # Verificar si se registra el UpdateExpression antes de ejecutarlo
    logs_update_expression = bool(re.search(r'(print|console\.log|logger).*update.*expression', lambda_code, re.IGNORECASE))
    if not logs_update_expression:
        findings.append(Finding(
            severity='info',
            category='code',
            description='No se registra el UpdateExpression antes de ejecutarlo',
            location='DynamoDB update operation',
            recommendation='Agregar logging del UpdateExpression y expression_values antes de ejecutar update_item'
        ))
    
    # Generar resumen
    critical_count = sum(1 for f in findings if f.severity == 'critical')
    warning_count = sum(1 for f in findings if f.severity == 'warning')
    
    if critical_count > 0:
        summary = f'Se encontraron {critical_count} problemas críticos y {warning_count} advertencias'
    elif warning_count > 0:
        summary = f'Se encontraron {warning_count} advertencias'
    else:
        summary = 'No se encontraron problemas críticos'
    
    return DiagnosticReport(
        lambda_name=lambda_name,
        findings=findings,
        summary=summary,
        requires_code_change=critical_count > 0,
        requires_config_change=False
    )


def compare_field_handling(modify_lambda_code: str, create_lambda_code: str) -> Dict[str, Any]:
    """
    Compara cómo dos lambdas manejan los campos de fecha y hora.
    
    Args:
        modify_lambda_code: Código de ModifyTurnoFunction
        create_lambda_code: Código de CreateTurnoFunction
        
    Returns:
        Diccionario con diferencias identificadas
    """
    modify_fields = extract_processed_fields(modify_lambda_code)
    create_fields = extract_processed_fields(create_lambda_code)
    
    modify_update_fields = extract_update_expression_fields(modify_lambda_code)
    
    # Campos de fecha y hora
    modify_fecha = [f for f in modify_fields if 'fecha' in f.lower()]
    create_fecha = [f for f in create_fields if 'fecha' in f.lower()]
    
    modify_hora = [f for f in modify_fields if 'hora' in f.lower()]
    create_hora = [f for f in create_fields if 'hora' in f.lower()]
    
    differences = {
        'modify_processes_fecha': modify_fecha,
        'create_processes_fecha': create_fecha,
        'modify_processes_hora': modify_hora,
        'create_processes_hora': create_hora,
        'modify_update_fields': modify_update_fields,
        'fecha_handling_differs': set(modify_fecha) != set(create_fecha),
        'hora_handling_differs': set(modify_hora) != set(create_hora),
        'recommendations': []
    }
    
    if differences['fecha_handling_differs']:
        differences['recommendations'].append(
            'Las lambdas manejan campos de fecha de manera diferente. '
            'Considerar estandarizar para aceptar ambos formatos.'
        )
    
    if differences['hora_handling_differs']:
        differences['recommendations'].append(
            'Las lambdas manejan campos de hora de manera diferente. '
            'Considerar estandarizar para aceptar ambos formatos.'
        )
    
    return differences


if __name__ == '__main__':
    # Ejemplo de uso
    print("Analizador de código Lambda inicializado")
    print("Use las funciones analyze_lambda_code() y compare_field_handling() para analizar código")
