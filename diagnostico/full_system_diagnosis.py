"""
Diagnóstico completo del sistema de turnos médicos.

Este script analiza:
1. Todas las funciones Lambda
2. La especificación OpenAPI
3. El prompt del agente Luna
4. La consistencia entre todos los componentes
"""

import yaml
import re
from lambda_analyzer import analyze_lambda_code, compare_field_handling, extract_processed_fields
from openapi_validator import (
    extract_request_fields,
    validate_openapi_lambda_consistency,
    print_consistency_report
)


def extract_lambda_code_from_cloudformation(template_path: str, lambda_name: str) -> str:
    """Extrae el código de una función Lambda del template de CloudFormation."""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = rf'{lambda_name}:.*?ZipFile:\s*\|(.+?)(?=\n\s{{0,2}}\w+:|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1)
    else:
        raise ValueError(f"No se encontró la función Lambda {lambda_name} en el template")


def analyze_prompt_date_handling(prompt_path: str) -> dict:
    """
    Analiza el prompt del agente para verificar manejo de fechas.
    
    Args:
        prompt_path: Ruta al archivo del prompt
        
    Returns:
        Diccionario con análisis del prompt
    """
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
    except FileNotFoundError:
        return {
            'found': False,
            'error': f'Archivo no encontrado: {prompt_path}'
        }
    
    analysis = {
        'found': True,
        'has_date_handling_section': False,
        'mentions_iso_format': False,
        'mentions_24h_format': False,
        'mentions_exact_dates': False,
        'has_date_examples': False,
        'issues': [],
        'recommendations': []
    }
    
    # Buscar sección de manejo de fechas
    if 'date_and_time_handling' in prompt_content.lower() or 'date handling' in prompt_content.lower():
        analysis['has_date_handling_section'] = True
    else:
        analysis['issues'].append('No se encontró sección específica para manejo de fechas')
        analysis['recommendations'].append(
            'Agregar sección <date_and_time_handling> con instrucciones específicas'
        )
    
    # Verificar formato ISO
    if 'YYYY-MM-DD' in prompt_content or 'ISO' in prompt_content:
        analysis['mentions_iso_format'] = True
    else:
        analysis['issues'].append('No menciona formato ISO para fechas (YYYY-MM-DD)')
        analysis['recommendations'].append(
            'Especificar que las fechas deben estar en formato ISO: YYYY-MM-DD'
        )
    
    # Verificar formato 24h
    if 'HH:MM' in prompt_content or '24-hour' in prompt_content or '24 hour' in prompt_content:
        analysis['mentions_24h_format'] = True
    else:
        analysis['issues'].append('No menciona formato 24 horas para tiempo (HH:MM)')
        analysis['recommendations'].append(
            'Especificar que las horas deben estar en formato 24h: HH:MM'
        )
    
    # Verificar instrucciones sobre fechas exactas
    if 'exact date' in prompt_content.lower() or 'calculate' in prompt_content.lower():
        analysis['mentions_exact_dates'] = True
    else:
        analysis['issues'].append('No instruye calcular fechas exactas (evitar "próximo miércoles")')
        analysis['recommendations'].append(
            'Agregar instrucción: ALWAYS calculate exact dates - NEVER use relative terms'
        )
    
    # Buscar ejemplos de fechas
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    if re.search(date_pattern, prompt_content):
        analysis['has_date_examples'] = True
    else:
        analysis['recommendations'].append(
            'Agregar ejemplos de fechas en formato correcto (2026-02-05)'
        )
    
    return analysis


def print_prompt_analysis(analysis: dict):
    """Imprime el análisis del prompt."""
    print(f"\n{'='*80}")
    print("ANÁLISIS DEL PROMPT DEL AGENTE LUNA")
    print(f"{'='*80}")
    
    if not analysis['found']:
        print(f"\n❌ {analysis['error']}")
        return
    
    print("\n📋 Verificaciones:")
    checks = [
        ('Sección de manejo de fechas', analysis['has_date_handling_section']),
        ('Menciona formato ISO (YYYY-MM-DD)', analysis['mentions_iso_format']),
        ('Menciona formato 24h (HH:MM)', analysis['mentions_24h_format']),
        ('Instruye calcular fechas exactas', analysis['mentions_exact_dates']),
        ('Incluye ejemplos de fechas', analysis['has_date_examples'])
    ]
    
    for check_name, passed in checks:
        icon = '✅' if passed else '❌'
        print(f"  {icon} {check_name}")
    
    if analysis['issues']:
        print(f"\n{'─'*80}")
        print("⚠️  PROBLEMAS ENCONTRADOS:")
        print(f"{'─'*80}")
        for i, issue in enumerate(analysis['issues'], 1):
            print(f"{i}. {issue}")
    
    if analysis['recommendations']:
        print(f"\n{'─'*80}")
        print("💡 RECOMENDACIONES:")
        print(f"{'─'*80}")
        for i, rec in enumerate(analysis['recommendations'], 1):
            print(f"{i}. {rec}")
    
    print(f"\n{'='*80}\n")


def main():
    """Función principal que ejecuta el diagnóstico completo del sistema."""
    print("\n" + "="*80)
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA DE TURNOS MÉDICOS")
    print("="*80)
    
    template_path = 'documentos_salud_connect_ia/turnos-medicos-api-final.yaml'
    openapi_path = 'documentos_salud_connect_ia/turnos-medicos-api-openapi.yaml'
    prompt_path = 'documentos_salud_connect_ia/luna-agent-prompt-mejorado.yaml'
    
    # Cargar OpenAPI
    print("\n📂 Cargando especificación OpenAPI...")
    try:
        with open(openapi_path, 'r', encoding='utf-8') as f:
            openapi_spec = yaml.safe_load(f)
        print("✓ OpenAPI cargado exitosamente")
    except Exception as e:
        print(f"❌ Error cargando OpenAPI: {str(e)}")
        return
    
    # Definir lambdas y sus endpoints correspondientes
    lambdas_to_check = [
        ('CreateTurnoFunction', '/turnos', 'Crear turno'),
        ('ModifyTurnoFunction', '/turnos/modificar', 'Modificar turno'),
        ('CancelTurnoFunction', '/turnos/cancelar', 'Cancelar turno'),
        ('GetTurnosPacienteFunction', '/turnos/paciente', 'Obtener turnos'),
        ('SearchMedicosFunction', '/medicos/buscar', 'Buscar médicos')
    ]
    
    print(f"\n{'='*80}")
    print("PARTE 1: ANÁLISIS DE LAMBDAS")
    print(f"{'='*80}")
    
    lambda_codes = {}
    lambda_reports = {}
    
    for lambda_name, endpoint, description in lambdas_to_check:
        print(f"\n🔬 Analizando {lambda_name} ({description})...")
        
        try:
            code = extract_lambda_code_from_cloudformation(template_path, lambda_name)
            lambda_codes[lambda_name] = code
            
            # Analizar código
            report = analyze_lambda_code(lambda_name, code)
            lambda_reports[lambda_name] = report
            
            # Mostrar resumen
            critical = sum(1 for f in report.findings if f.severity == 'critical')
            warnings = sum(1 for f in report.findings if f.severity == 'warning')
            
            if critical > 0:
                print(f"   🔴 {critical} problemas críticos")
            if warnings > 0:
                print(f"   ⚠️  {warnings} advertencias")
            if critical == 0 and warnings == 0:
                print(f"   ✅ Sin problemas")
            
            # Mostrar campos procesados
            processed = extract_processed_fields(code)
            fecha_fields = [f for f in processed if 'fecha' in f.lower()]
            hora_fields = [f for f in processed if 'hora' in f.lower()]
            
            if fecha_fields:
                print(f"   📅 Campos de fecha: {fecha_fields}")
            if hora_fields:
                print(f"   🕐 Campos de hora: {hora_fields}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n{'='*80}")
    print("PARTE 2: VALIDACIÓN DE CONSISTENCIA OPENAPI-LAMBDA")
    print(f"{'='*80}")
    
    consistency_reports = []
    
    for lambda_name, endpoint, description in lambdas_to_check:
        if lambda_name in lambda_codes:
            print(f"\n🔄 Validando consistencia: {endpoint} <-> {lambda_name}")
            
            try:
                report = validate_openapi_lambda_consistency(
                    openapi_spec,
                    lambda_codes[lambda_name],
                    endpoint,
                    lambda_name
                )
                consistency_reports.append(report)
                
                # Mostrar resumen
                if report.is_consistent:
                    print(f"   ✅ Consistente")
                else:
                    print(f"   ⚠️  Inconsistente")
                    if report.missing_in_lambda:
                        print(f"      Faltan en lambda: {report.missing_in_lambda}")
                    if report.missing_in_openapi:
                        print(f"      Faltan en OpenAPI: {report.missing_in_openapi}")
            
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    print(f"\n{'='*80}")
    print("PARTE 3: ANÁLISIS DEL PROMPT DEL AGENTE")
    print(f"{'='*80}")
    
    prompt_analysis = analyze_prompt_date_handling(prompt_path)
    print_prompt_analysis(prompt_analysis)
    
    print(f"\n{'='*80}")
    print("PARTE 4: ANÁLISIS DE CAMPOS EN OPENAPI")
    print(f"{'='*80}")
    
    for lambda_name, endpoint, description in lambdas_to_check:
        print(f"\n📋 Endpoint: {endpoint}")
        fields_info = extract_request_fields(openapi_spec, endpoint)
        
        if fields_info['required']:
            print(f"   Campos requeridos: {fields_info['required']}")
        if fields_info['optional']:
            print(f"   Campos opcionales: {fields_info['optional']}")
        
        # Verificar campos de fecha/hora
        all_fields = list(fields_info['all_fields'].keys())
        fecha_fields = [f for f in all_fields if 'fecha' in f.lower()]
        hora_fields = [f for f in all_fields if 'hora' in f.lower()]
        
        if fecha_fields:
            print(f"   📅 Campos de fecha en OpenAPI: {fecha_fields}")
        if hora_fields:
            print(f"   🕐 Campos de hora en OpenAPI: {hora_fields}")
    
    print(f"\n{'='*80}")
    print("📊 RESUMEN EJECUTIVO")
    print(f"{'='*80}")
    
    # Contar problemas totales
    total_critical = sum(
        sum(1 for f in report.findings if f.severity == 'critical')
        for report in lambda_reports.values()
    )
    total_warnings = sum(
        sum(1 for f in report.findings if f.severity == 'warning')
        for report in lambda_reports.values()
    )
    total_inconsistent = sum(1 for r in consistency_reports if not r.is_consistent)
    
    print(f"\n🔴 Problemas críticos en lambdas: {total_critical}")
    print(f"⚠️  Advertencias en lambdas: {total_warnings}")
    print(f"⚠️  Endpoints inconsistentes: {total_inconsistent}/{len(consistency_reports)}")
    
    # Análisis del prompt
    prompt_issues = len(prompt_analysis.get('issues', []))
    if prompt_issues > 0:
        print(f"⚠️  Problemas en prompt del agente: {prompt_issues}")
    else:
        print(f"✅ Prompt del agente: OK")
    
    # Conclusiones
    print(f"\n{'─'*80}")
    print("🎯 CONCLUSIONES:")
    print(f"{'─'*80}")
    
    if total_critical == 0 and total_inconsistent == 0 and prompt_issues == 0:
        print("\n✅ El sistema está correctamente configurado.")
        print("   Si hay problemas, verificar:")
        print("   1. Caché del MCP Server (Unpublish/Publish)")
        print("   2. Logs de CloudWatch para ver requests reales")
        print("   3. Configuración del agente en Amazon Connect")
    else:
        print("\n⚠️  Se encontraron problemas que requieren atención:")
        
        if total_critical > 0:
            print(f"\n   🔴 {total_critical} problemas críticos en código de lambdas")
        
        if total_inconsistent > 0:
            print(f"\n   ⚠️  {total_inconsistent} endpoints con inconsistencias OpenAPI-Lambda")
            print("      Revisar reportes detallados arriba")
        
        if prompt_issues > 0:
            print(f"\n   ⚠️  {prompt_issues} problemas en el prompt del agente")
            print("      El agente puede no estar calculando fechas correctamente")
    
    print(f"\n{'='*80}\n")
    
    # Generar reporte detallado si hay problemas
    if total_inconsistent > 0:
        print("\n📄 REPORTES DETALLADOS DE CONSISTENCIA:")
        print("="*80)
        for report in consistency_reports:
            if not report.is_consistent:
                print_consistency_report(report)


if __name__ == '__main__':
    main()
