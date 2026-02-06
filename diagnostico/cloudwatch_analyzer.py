"""
Analizador de logs de CloudWatch para diagnosticar problemas en las lambdas.

Este módulo proporciona herramientas para analizar logs de CloudWatch y extraer
información sobre requests, errores y patrones de ejecución.
"""

import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class LogAnalysis:
    """Resultado del análisis de logs"""
    log_group: str
    time_range: str
    total_entries: int
    error_count: int
    request_bodies: List[Dict[str, Any]]
    patterns: Dict[str, int]
    recommendations: List[str]


def parse_log_entry(log_line: str) -> Optional[Dict[str, Any]]:
    """
    Parsea una línea de log y extrae información estructurada.
    
    Args:
        log_line: Línea de log de CloudWatch
        
    Returns:
        Diccionario con información parseada o None si no se puede parsear
    """
    try:
        # Intentar parsear como JSON
        if log_line.strip().startswith('{'):
            return json.loads(log_line)
    except json.JSONDecodeError:
        pass
    
    # Intentar extraer JSON embebido
    json_match = re.search(r'\{.*\}', log_line)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    return None


def extract_request_bodies(log_entries: List[str]) -> List[Dict[str, Any]]:
    """
    Extrae request bodies de los logs.
    
    Args:
        log_entries: Lista de líneas de log
        
    Returns:
        Lista de request bodies encontrados
    """
    request_bodies = []
    
    for entry in log_entries:
        parsed = parse_log_entry(entry)
        if parsed:
            # Buscar body en diferentes ubicaciones
            if 'body' in parsed:
                try:
                    if isinstance(parsed['body'], str):
                        body = json.loads(parsed['body'])
                    else:
                        body = parsed['body']
                    request_bodies.append(body)
                except (json.JSONDecodeError, TypeError):
                    pass
            
            # Buscar event.body
            if 'event' in parsed and isinstance(parsed['event'], dict):
                if 'body' in parsed['event']:
                    try:
                        if isinstance(parsed['event']['body'], str):
                            body = json.loads(parsed['event']['body'])
                        else:
                            body = parsed['event']['body']
                        request_bodies.append(body)
                    except (json.JSONDecodeError, TypeError):
                        pass
    
    return request_bodies


def analyze_field_presence(request_bodies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analiza la presencia de campos en los request bodies.
    
    Args:
        request_bodies: Lista de request bodies
        
    Returns:
        Diccionario con estadísticas de campos
    """
    field_stats = {}
    
    for body in request_bodies:
        for field in body.keys():
            if field not in field_stats:
                field_stats[field] = {
                    'count': 0,
                    'sample_values': []
                }
            field_stats[field]['count'] += 1
            
            # Guardar valores de muestra para campos de fecha/hora
            if 'fecha' in field.lower() or 'hora' in field.lower():
                if len(field_stats[field]['sample_values']) < 3:
                    field_stats[field]['sample_values'].append(body[field])
    
    return field_stats


def identify_patterns(log_entries: List[str]) -> Dict[str, int]:
    """
    Identifica patrones comunes en los logs.
    
    Args:
        log_entries: Lista de líneas de log
        
    Returns:
        Diccionario con patrones y sus frecuencias
    """
    patterns = {
        'errors': 0,
        'missing_parameters': 0,
        'successful_updates': 0,
        'fecha_turno_present': 0,
        'hora_turno_present': 0,
        'fecha_present': 0,
        'hora_present': 0,
        'update_expression_logged': 0
    }
    
    for entry in log_entries:
        entry_lower = entry.lower()
        
        if 'error' in entry_lower or 'exception' in entry_lower:
            patterns['errors'] += 1
        
        if 'missing' in entry_lower and 'parameter' in entry_lower:
            patterns['missing_parameters'] += 1
        
        if 'successfully' in entry_lower or 'success' in entry_lower:
            patterns['successful_updates'] += 1
        
        if 'fechaturno' in entry_lower:
            patterns['fecha_turno_present'] += 1
        
        if 'horaturno' in entry_lower:
            patterns['hora_turno_present'] += 1
        
        if '"fecha"' in entry_lower or "'fecha'" in entry_lower:
            patterns['fecha_present'] += 1
        
        if '"hora"' in entry_lower or "'hora'" in entry_lower:
            patterns['hora_present'] += 1
        
        if 'updateexpression' in entry_lower or 'update_expression' in entry_lower:
            patterns['update_expression_logged'] += 1
    
    return patterns


def analyze_cloudwatch_logs(log_entries: List[str], log_group: str = 'unknown') -> LogAnalysis:
    """
    Analiza logs de CloudWatch para identificar patrones de error.
    
    Args:
        log_entries: Lista de líneas de log
        log_group: Nombre del log group
        
    Returns:
        LogAnalysis con patrones identificados
    """
    # Extraer request bodies
    request_bodies = extract_request_bodies(log_entries)
    
    # Identificar patrones
    patterns = identify_patterns(log_entries)
    
    # Analizar presencia de campos
    field_stats = analyze_field_presence(request_bodies)
    
    # Generar recomendaciones
    recommendations = []
    
    if patterns['errors'] > 0:
        recommendations.append(
            f"Se encontraron {patterns['errors']} errores en los logs. "
            "Revisar los mensajes de error para identificar problemas."
        )
    
    if patterns['missing_parameters'] > 0:
        recommendations.append(
            f"Se encontraron {patterns['missing_parameters']} errores de parámetros faltantes. "
            "Verificar que el agente esté enviando todos los campos requeridos."
        )
    
    # Verificar si llegan campos de fecha y hora
    fecha_fields = [f for f in field_stats.keys() if 'fecha' in f.lower()]
    hora_fields = [f for f in field_stats.keys() if 'hora' in f.lower()]
    
    if not fecha_fields:
        recommendations.append(
            "No se encontraron campos de fecha en los request bodies. "
            "Verificar que el agente esté enviando fechaTurno o fecha."
        )
    else:
        recommendations.append(
            f"Campos de fecha encontrados: {fecha_fields}. "
            f"Presentes en {field_stats[fecha_fields[0]]['count']} requests."
        )
    
    if not hora_fields:
        recommendations.append(
            "No se encontraron campos de hora en los request bodies. "
            "Verificar que el agente esté enviando horaTurno o hora."
        )
    else:
        recommendations.append(
            f"Campos de hora encontrados: {hora_fields}. "
            f"Presentes en {field_stats[hora_fields[0]]['count']} requests."
        )
    
    if patterns['update_expression_logged'] == 0:
        recommendations.append(
            "No se encontró logging del UpdateExpression. "
            "Agregar logging para facilitar debugging."
        )
    
    return LogAnalysis(
        log_group=log_group,
        time_range='last 30 minutes',
        total_entries=len(log_entries),
        error_count=patterns['errors'],
        request_bodies=request_bodies,
        patterns=patterns,
        recommendations=recommendations
    )


def print_log_analysis(analysis: LogAnalysis):
    """Imprime el análisis de logs de forma legible."""
    print(f"\n{'='*80}")
    print(f"ANÁLISIS DE LOGS: {analysis.log_group}")
    print(f"{'='*80}")
    print(f"\nRango de tiempo: {analysis.time_range}")
    print(f"Total de entradas: {analysis.total_entries}")
    print(f"Errores encontrados: {analysis.error_count}")
    
    print(f"\n{'─'*80}")
    print("PATRONES IDENTIFICADOS:")
    print(f"{'─'*80}")
    for pattern, count in analysis.patterns.items():
        icon = '✓' if count > 0 else '✗'
        print(f"  {icon} {pattern}: {count}")
    
    print(f"\n{'─'*80}")
    print(f"REQUEST BODIES ENCONTRADOS: {len(analysis.request_bodies)}")
    print(f"{'─'*80}")
    
    if analysis.request_bodies:
        # Mostrar campos únicos encontrados
        all_fields = set()
        for body in analysis.request_bodies:
            all_fields.update(body.keys())
        
        print(f"\nCampos únicos encontrados: {sorted(all_fields)}")
        
        # Mostrar un ejemplo de request body
        if analysis.request_bodies:
            print(f"\nEjemplo de request body:")
            print(json.dumps(analysis.request_bodies[0], indent=2))
    
    if analysis.recommendations:
        print(f"\n{'─'*80}")
        print("RECOMENDACIONES:")
        print(f"{'─'*80}")
        for i, rec in enumerate(analysis.recommendations, 1):
            print(f"{i}. {rec}")
    
    print(f"\n{'='*80}\n")


# Función de ejemplo para simular análisis con logs de muestra
def analyze_sample_logs():
    """Analiza logs de muestra para demostración."""
    sample_logs = [
        '{"level": "INFO", "message": "Modificar turno request received", "requestId": "abc123", "event": {"body": "{\\"turnoId\\": \\"TURNO-123\\", \\"pacienteId\\": \\"PAC-456\\", \\"fechaTurno\\": \\"2026-02-10\\", \\"horaTurno\\": \\"14:00\\"}"}}',
        '{"level": "INFO", "message": "Modifying reservation", "requestId": "abc123", "turnoId": "TURNO-123"}',
        '{"level": "ERROR", "message": "Missing required parameters", "requestId": "def456", "missingParameters": ["fechaTurno"]}',
        '{"level": "INFO", "message": "Reservation modified successfully", "requestId": "abc123"}',
    ]
    
    analysis = analyze_cloudwatch_logs(sample_logs, 'ModifyTurnoFunction')
    print_log_analysis(analysis)


if __name__ == '__main__':
    print("Analizador de logs de CloudWatch inicializado")
    print("\nEjecutando análisis con logs de muestra...")
    analyze_sample_logs()
