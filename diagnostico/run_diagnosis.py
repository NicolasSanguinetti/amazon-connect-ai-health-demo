"""
Script para ejecutar el diagnóstico completo del sistema de turnos médicos.

Este script analiza el código de las lambdas ModifyTurnoFunction y CreateTurnoFunction
para identificar problemas y diferencias en el manejo de campos.
"""

import yaml
import re
from lambda_analyzer import (
    analyze_lambda_code,
    compare_field_handling,
    extract_update_expression_fields,
    extract_processed_fields
)


def extract_lambda_code_from_cloudformation(template_path: str, lambda_name: str) -> str:
    """
    Extrae el código de una función Lambda del template de CloudFormation.
    
    Args:
        template_path: Ruta al archivo YAML de CloudFormation
        lambda_name: Nombre lógico de la función Lambda en el template
        
    Returns:
        Código de la función Lambda
    """
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la sección de la lambda específica
    pattern = rf'{lambda_name}:.*?ZipFile:\s*\|(.+?)(?=\n\s{{0,2}}\w+:|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1)
    else:
        raise ValueError(f"No se encontró la función Lambda {lambda_name} en el template")


def print_report(report):
    """Imprime un reporte de diagnóstico de forma legible."""
    print(f"\n{'='*80}")
    print(f"REPORTE DE DIAGNÓSTICO: {report.lambda_name}")
    print(f"{'='*80}")
    print(f"\nResumen: {report.summary}")
    print(f"Requiere cambios en código: {'Sí' if report.requires_code_change else 'No'}")
    print(f"Requiere cambios en configuración: {'Sí' if report.requires_config_change else 'No'}")
    
    if report.findings:
        print(f"\n{'─'*80}")
        print("HALLAZGOS:")
        print(f"{'─'*80}")
        
        for i, finding in enumerate(report.findings, 1):
            severity_icon = {
                'critical': '🔴',
                'warning': '⚠️',
                'info': 'ℹ️'
            }.get(finding.severity, '•')
            
            print(f"\n{i}. {severity_icon} [{finding.severity.upper()}] {finding.category}")
            print(f"   Descripción: {finding.description}")
            print(f"   Ubicación: {finding.location}")
            print(f"   Recomendación: {finding.recommendation}")
    
    print(f"\n{'='*80}\n")


def print_comparison(comparison):
    """Imprime el resultado de la comparación entre lambdas."""
    print(f"\n{'='*80}")
    print("COMPARACIÓN: ModifyTurnoFunction vs CreateTurnoFunction")
    print(f"{'='*80}")
    
    print("\n📋 Campos de FECHA procesados:")
    print(f"   ModifyTurno: {comparison['modify_processes_fecha']}")
    print(f"   CreateTurno: {comparison['create_processes_fecha']}")
    print(f"   ¿Difieren?: {'Sí ⚠️' if comparison['fecha_handling_differs'] else 'No ✓'}")
    
    print("\n📋 Campos de HORA procesados:")
    print(f"   ModifyTurno: {comparison['modify_processes_hora']}")
    print(f"   CreateTurno: {comparison['create_processes_hora']}")
    print(f"   ¿Difieren?: {'Sí ⚠️' if comparison['hora_handling_differs'] else 'No ✓'}")
    
    print("\n📋 Campos en UpdateExpression (ModifyTurno):")
    print(f"   {comparison['modify_update_fields']}")
    
    if comparison['recommendations']:
        print(f"\n{'─'*80}")
        print("RECOMENDACIONES:")
        print(f"{'─'*80}")
        for i, rec in enumerate(comparison['recommendations'], 1):
            print(f"{i}. {rec}")
    
    print(f"\n{'='*80}\n")


def main():
    """Función principal que ejecuta el diagnóstico completo."""
    print("\n🔍 INICIANDO DIAGNÓSTICO DEL SISTEMA DE TURNOS MÉDICOS")
    print("="*80)
    
    template_path = 'documentos_salud_connect_ia/turnos-medicos-api-final.yaml'
    
    try:
        # Extraer código de las lambdas
        print("\n📂 Extrayendo código de las funciones Lambda...")
        modify_code = extract_lambda_code_from_cloudformation(template_path, 'ModifyTurnoFunction')
        create_code = extract_lambda_code_from_cloudformation(template_path, 'CreateTurnoFunction')
        print("✓ Código extraído exitosamente")
        
        # Analizar ModifyTurnoFunction
        print("\n🔬 Analizando ModifyTurnoFunction...")
        modify_report = analyze_lambda_code('ModifyTurnoFunction', modify_code)
        print_report(modify_report)
        
        # Analizar CreateTurnoFunction
        print("\n🔬 Analizando CreateTurnoFunction...")
        create_report = analyze_lambda_code('CreateTurnoFunction', create_code)
        print_report(create_report)
        
        # Comparar ambas lambdas
        print("\n🔄 Comparando manejo de campos entre lambdas...")
        comparison = compare_field_handling(modify_code, create_code)
        print_comparison(comparison)
        
        # Análisis detallado de ModifyTurnoFunction
        print("\n🔍 ANÁLISIS DETALLADO: ModifyTurnoFunction")
        print("="*80)
        
        processed = extract_processed_fields(modify_code)
        update_fields = extract_update_expression_fields(modify_code)
        
        print(f"\n✓ Campos procesados del body: {processed}")
        print(f"✓ Campos en UpdateExpression: {update_fields}")
        
        # Verificar lógica de campos alternativos
        has_fecha_or_fechaturno = "'fechaTurno' in body or 'fecha' in body" in modify_code
        has_hora_or_horaturno = "'horaTurno' in body or 'hora' in body" in modify_code
        
        print(f"\n📝 Lógica de campos alternativos:")
        print(f"   Acepta fecha/fechaTurno: {'Sí ✓' if has_fecha_or_fechaturno else 'No ⚠️'}")
        print(f"   Acepta hora/horaTurno: {'Sí ✓' if has_hora_or_horaturno else 'No ⚠️'}")
        
        # Verificar si se incluyen en UpdateExpression
        includes_fecha_in_update = "update_expression += ', fechaTurno = :fechaTurno'" in modify_code
        includes_hora_in_update = "update_expression += ', horaTurno = :horaTurno'" in modify_code
        
        print(f"\n📝 Inclusión en UpdateExpression:")
        print(f"   Incluye fechaTurno: {'Sí ✓' if includes_fecha_in_update else 'No ⚠️'}")
        print(f"   Incluye horaTurno: {'Sí ✓' if includes_hora_in_update else 'No ⚠️'}")
        
        # Resumen final
        print(f"\n{'='*80}")
        print("📊 RESUMEN DEL DIAGNÓSTICO")
        print(f"{'='*80}")
        
        total_critical = sum(1 for f in modify_report.findings + create_report.findings if f.severity == 'critical')
        total_warnings = sum(1 for f in modify_report.findings + create_report.findings if f.severity == 'warning')
        
        print(f"\n🔴 Problemas críticos encontrados: {total_critical}")
        print(f"⚠️  Advertencias encontradas: {total_warnings}")
        
        if total_critical == 0 and total_warnings == 0:
            print("\n✅ El código parece estar correctamente implementado.")
            print("   Si hay problemas, pueden ser de configuración o caché del MCP Server.")
        else:
            print("\n⚠️  Se requieren correcciones en el código.")
        
        print(f"\n{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
