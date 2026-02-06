"""
Validador de consistencia entre OpenAPI y Lambdas.

Este módulo verifica que los campos definidos en OpenAPI coincidan con
los que procesan las lambdas, y viceversa.
"""

import yaml
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from lambda_analyzer import extract_processed_fields


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
    lambda_name: str
    is_consistent: bool
    discrepancies: List[FieldDiscrepancy]
    missing_in_lambda: List[str]
    missing_in_openapi: List[str]
    recommendations: List[str]


def extract_request_fields(openapi_spec: dict, endpoint: str, method: str = 'post') -> Dict[str, Any]:
    """
    Extrae los campos del requestBody de un endpoint en OpenAPI.
    
    Args:
        openapi_spec: Especificación OpenAPI parseada
        endpoint: Endpoint a analizar (ej: /turnos/modificar)
        method: Método HTTP (default: post)
        
    Returns:
        Diccionario con información de campos
    """
    fields_info = {
        'required': [],
        'optional': [],
        'all_fields': {},
        'endpoint': endpoint
    }
    
    try:
        # Navegar a la definición del endpoint
        path_item = openapi_spec.get('paths', {}).get(endpoint, {})
        operation = path_item.get(method, {})
        
        # Obtener requestBody
        request_body = operation.get('requestBody', {})
        content = request_body.get('content', {})
        json_content = content.get('application/json', {})
        schema = json_content.get('schema', {})
        
        # Extraer campos requeridos
        required_fields = schema.get('required', [])
        fields_info['required'] = required_fields
        
        # Extraer todas las propiedades
        properties = schema.get('properties', {})
        
        for field_name, field_spec in properties.items():
            fields_info['all_fields'][field_name] = {
                'type': field_spec.get('type', 'unknown'),
                'description': field_spec.get('description', ''),
                'required': field_name in required_fields,
                'format': field_spec.get('format', None),
                'example': field_spec.get('example', None)
            }
            
            if field_name not in required_fields:
                fields_info['optional'].append(field_name)
    
    except Exception as e:
        print(f"Error extrayendo campos de {endpoint}: {str(e)}")
    
    return fields_info


def validate_openapi_lambda_consistency(
    openapi_spec: dict,
    lambda_code: str,
    endpoint: str,
    lambda_name: str
) -> ConsistencyReport:
    """
    Valida que los campos en OpenAPI coincidan con los procesados en la lambda.
    
    Args:
        openapi_spec: Especificación OpenAPI parseada
        lambda_code: Código de la función Lambda
        endpoint: Endpoint a validar (ej: /turnos/modificar)
        lambda_name: Nombre de la lambda
        
    Returns:
        ConsistencyReport con discrepancias encontradas
    """
    # Extraer campos de OpenAPI
    openapi_fields = extract_request_fields(openapi_spec, endpoint)
    openapi_field_names = set(openapi_fields['all_fields'].keys())
    
    # Extraer campos procesados por la lambda
    lambda_fields = set(extract_processed_fields(lambda_code))
    
    # Identificar discrepancias
    missing_in_lambda = openapi_field_names - lambda_fields
    missing_in_openapi = lambda_fields - openapi_field_names
    
    # Crear lista de discrepancias detalladas
    discrepancies = []
    
    for field in openapi_field_names | lambda_fields:
        in_openapi = field in openapi_field_names
        in_lambda = field in lambda_fields
        
        if in_openapi != in_lambda:
            openapi_type = None
            if in_openapi:
                openapi_type = openapi_fields['all_fields'][field].get('type')
            
            discrepancies.append(FieldDiscrepancy(
                field_name=field,
                in_openapi=in_openapi,
                in_lambda=in_lambda,
                openapi_type=openapi_type,
                lambda_processing='processed' if in_lambda else 'not_processed'
            ))
    
    # Generar recomendaciones
    recommendations = []
    
    if missing_in_lambda:
        recommendations.append(
            f"Campos definidos en OpenAPI pero no procesados en lambda: {list(missing_in_lambda)}. "
            "Considerar agregar procesamiento o remover de OpenAPI si no son necesarios."
        )
    
    if missing_in_openapi:
        recommendations.append(
            f"Campos procesados en lambda pero no definidos en OpenAPI: {list(missing_in_openapi)}. "
            "Considerar agregar a OpenAPI para documentación completa."
        )
    
    # Verificar campos de fecha/hora específicamente
    fecha_fields_openapi = [f for f in openapi_field_names if 'fecha' in f.lower()]
    hora_fields_openapi = [f for f in openapi_field_names if 'hora' in f.lower()]
    
    fecha_fields_lambda = [f for f in lambda_fields if 'fecha' in f.lower()]
    hora_fields_lambda = [f for f in lambda_fields if 'hora' in f.lower()]
    
    if fecha_fields_openapi and not fecha_fields_lambda:
        recommendations.append(
            f"⚠️ CRÍTICO: OpenAPI define campos de fecha {fecha_fields_openapi} "
            "pero la lambda no los procesa."
        )
    
    if hora_fields_openapi and not hora_fields_lambda:
        recommendations.append(
            f"⚠️ CRÍTICO: OpenAPI define campos de hora {hora_fields_openapi} "
            "pero la lambda no los procesa."
        )
    
    is_consistent = len(discrepancies) == 0
    
    return ConsistencyReport(
        endpoint=endpoint,
        lambda_name=lambda_name,
        is_consistent=is_consistent,
        discrepancies=discrepancies,
        missing_in_lambda=list(missing_in_lambda),
        missing_in_openapi=list(missing_in_openapi),
        recommendations=recommendations
    )


def print_consistency_report(report: ConsistencyReport):
    """Imprime un reporte de consistencia de forma legible."""
    print(f"\n{'='*80}")
    print(f"REPORTE DE CONSISTENCIA: {report.endpoint}")
    print(f"Lambda: {report.lambda_name}")
    print(f"{'='*80}")
    
    status_icon = '✅' if report.is_consistent else '⚠️'
    status_text = 'CONSISTENTE' if report.is_consistent else 'INCONSISTENTE'
    print(f"\nEstado: {status_icon} {status_text}")
    
    if report.missing_in_lambda:
        print(f"\n🔴 Campos en OpenAPI pero NO en Lambda:")
        for field in report.missing_in_lambda:
            print(f"   - {field}")
    
    if report.missing_in_openapi:
        print(f"\n⚠️  Campos en Lambda pero NO en OpenAPI:")
        for field in report.missing_in_openapi:
            print(f"   - {field}")
    
    if report.discrepancies:
        print(f"\n{'─'*80}")
        print("DISCREPANCIAS DETALLADAS:")
        print(f"{'─'*80}")
        
        for disc in report.discrepancies:
            openapi_status = '✓' if disc.in_openapi else '✗'
            lambda_status = '✓' if disc.in_lambda else '✗'
            
            print(f"\n  Campo: {disc.field_name}")
            print(f"    OpenAPI: {openapi_status} | Lambda: {lambda_status}")
            if disc.openapi_type:
                print(f"    Tipo en OpenAPI: {disc.openapi_type}")
    
    if report.recommendations:
        print(f"\n{'─'*80}")
        print("RECOMENDACIONES:")
        print(f"{'─'*80}")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"{i}. {rec}")
    
    print(f"\n{'='*80}\n")


if __name__ == '__main__':
    print("Validador de consistencia OpenAPI-Lambda inicializado")
    print("Use validate_openapi_lambda_consistency() para validar endpoints")
