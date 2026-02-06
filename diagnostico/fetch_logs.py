"""
Script para obtener logs de CloudWatch y analizarlos.

Este script obtiene logs recientes de las funciones Lambda y los analiza
para identificar problemas.
"""

import subprocess
import json
from cloudwatch_analyzer import analyze_cloudwatch_logs, print_log_analysis


def get_cloudwatch_logs(log_group: str, minutes: int = 30) -> list:
    """
    Obtiene logs de CloudWatch usando AWS CLI.
    
    Args:
        log_group: Nombre del log group
        minutes: Minutos hacia atrás para buscar logs
        
    Returns:
        Lista de líneas de log
    """
    try:
        # Comando para obtener logs
        cmd = f'aws logs tail {log_group} --since {minutes}m --format short'
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout.split('\n')
        else:
            print(f"Error obteniendo logs: {result.stderr}")
            return []
    
    except subprocess.TimeoutExpired:
        print("Timeout al obtener logs de CloudWatch")
        return []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []


def main():
    """Función principal."""
    print("\n🔍 OBTENIENDO LOGS DE CLOUDWATCH")
    print("="*80)
    
    # Obtener logs de ModifyTurnoFunction
    print("\n📋 Obteniendo logs de ModifyTurnoFunction...")
    modify_logs = get_cloudwatch_logs('/aws/lambda/salud-api-stack-ModifyTurnoFunction*', 60)
    
    if modify_logs:
        print(f"✓ Se obtuvieron {len(modify_logs)} líneas de log")
        analysis = analyze_cloudwatch_logs(modify_logs, 'ModifyTurnoFunction')
        print_log_analysis(analysis)
    else:
        print("⚠️  No se pudieron obtener logs o no hay logs recientes")
        print("   Esto puede ser normal si no ha habido actividad reciente")
    
    # Obtener logs de CreateTurnoFunction
    print("\n📋 Obteniendo logs de CreateTurnoFunction...")
    create_logs = get_cloudwatch_logs('/aws/lambda/salud-api-stack-CreateTurnoFunction*', 60)
    
    if create_logs:
        print(f"✓ Se obtuvieron {len(create_logs)} líneas de log")
        analysis = analyze_cloudwatch_logs(create_logs, 'CreateTurnoFunction')
        print_log_analysis(analysis)
    else:
        print("⚠️  No se pudieron obtener logs o no hay logs recientes")
    
    print("\n💡 NOTA: Si no hay logs recientes, puedes:")
    print("   1. Hacer una llamada de prueba al sistema")
    print("   2. Usar curl para probar los endpoints directamente")
    print("   3. Revisar logs manualmente en la consola de AWS")


if __name__ == '__main__':
    main()
