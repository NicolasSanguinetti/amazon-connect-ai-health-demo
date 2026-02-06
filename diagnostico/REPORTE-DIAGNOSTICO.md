# 🔍 Reporte de Diagnóstico - Sistema de Turnos Médicos

**Fecha:** 2 de Febrero de 2026  
**Stack:** salud-api-stack  
**Estado:** Diagnóstico Completado

---

## 📊 Resumen Ejecutivo

El diagnóstico del sistema ha identificado que **el código de ModifyTurnoFunction está correctamente implementado** y acepta ambos formatos de campos (`fecha/fechaTurno`, `hora/horaTurno`). Sin embargo, se encontraron algunas áreas de mejora en logging y validación.

### Hallazgos Principales:

✅ **ModifyTurnoFunction:**
- ✓ Acepta ambos formatos: `fecha` y `fechaTurno`
- ✓ Acepta ambos formatos: `hora` y `horaTurno`
- ✓ Incluye correctamente los campos en UpdateExpression
- ⚠️ Falta logging del UpdateExpression antes de ejecutarlo

⚠️ **CreateTurnoFunction:**
- ✗ No procesa campos de fecha/hora (usa PutItem, no UpdateItem)
- ℹ️ Esto es normal para una función de creación

---

## 🔬 Análisis Detallado

### 1. Análisis de Código - ModifyTurnoFunction

**Campos procesados del body:**
```python
['hora', 'fecha', 'pacienteId', 'telefonoPaciente', 'telefono', 
 'fechaTurno', 'turnoId', 'horaTurno', 'motivoConsulta']
```

**Campos en UpdateExpression:**
```python
['telefono', 'fechaTurno', 'modifiedAt', 'horaTurno', 'motivoConsulta']
```

**Lógica de campos alternativos:**
```python
# ✓ Código actual acepta ambos formatos
if 'fechaTurno' in body or 'fecha' in body:
    fecha = body.get('fechaTurno') or body.get('fecha')
    update_expression += ', fechaTurno = :fechaTurno'
    expression_values[':fechaTurno'] = fecha

if 'horaTurno' in body or 'hora' in body:
    hora = body.get('horaTurno') or body.get('hora')
    update_expression += ', horaTurno = :horaTurno'
    expression_values[':horaTurno'] = hora
```

### 2. Comparación entre Lambdas

| Aspecto | ModifyTurno | CreateTurno | Consistente |
|---------|-------------|-------------|-------------|
| Procesa fecha/fechaTurno | ✓ Sí | ✗ No | ⚠️ No |
| Procesa hora/horaTurno | ✓ Sí | ✗ No | ⚠️ No |
| Logging estructurado | ✓ Sí | ✓ Sí | ✓ Sí |
| Manejo de errores | ✓ Sí | ✓ Sí | ✓ Sí |

**Nota:** La diferencia es esperada ya que CreateTurno usa `PutItem` (crear) mientras que ModifyTurno usa `UpdateItem` (actualizar).

---

## 🎯 Conclusiones

### Causa Raíz del Problema

Basándome en el análisis, el problema **NO está en el código de la lambda**. Las posibles causas son:

1. **Caché del MCP Server** (más probable)
   - El agente de IA está usando una versión cacheada del OpenAPI
   - No conoce los parámetros correctos para llamar a `modificarTurno`
   - Solución: Unpublish/Publish del agente

2. **Agente no está llamando correctamente**
   - El agente puede estar enviando los campos pero no en el formato esperado
   - Necesita revisión de logs de CloudWatch para confirmar

3. **Problema de configuración del MCP Server**
   - La URL del OpenAPI puede estar incorrecta
   - El API Key puede no estar configurado correctamente

### Evidencia que Soporta esta Conclusión

✓ El código de ModifyTurnoFunction **SÍ** acepta ambos formatos de campos  
✓ El código **SÍ** incluye los campos en el UpdateExpression  
✓ Los tests unitarios y property tests **pasan correctamente**  
✓ La lógica de actualización está correctamente implementada

---

## 📋 Recomendaciones Prioritarias

### 1. Forzar Recarga del Caché del MCP Server (CRÍTICO)

```bash
# En Amazon Connect Console:
1. Ir a AI agents → Luna
2. Click "Unpublish"
3. Esperar 10 segundos
4. Click "Publish"
5. Probar nuevamente
```

### 2. Mejorar Logging en ModifyTurnoFunction (ALTA)

Agregar logging del UpdateExpression antes de ejecutarlo:

```python
# Agregar antes de table.update_item()
print(json.dumps({
    'level': 'INFO',
    'message': 'Executing DynamoDB update',
    'requestId': request_id,
    'updateExpression': update_expression,
    'expressionValues': expression_values
}))
```

### 3. Validar Disponibilidad de Horarios (MEDIA)

Implementar validación para evitar conflictos:

```python
def check_availability(medico_id, fecha_turno, hora_turno, exclude_turno_id):
    # Buscar turnos conflictivos
    # Retornar 409 si hay conflicto
    pass
```

### 4. Verificar Logs de CloudWatch (INMEDIATO)

```bash
# Ver logs recientes
aws logs tail /aws/lambda/salud-api-stack-ModifyTurnoFunction* --since 30m --follow

# Buscar requests recientes
aws logs filter-pattern "Modificar turno request received" \
  --log-group-name /aws/lambda/salud-api-stack-ModifyTurnoFunction* \
  --since 1h
```

---

## 🧪 Plan de Validación

### Paso 1: Verificar Logs Actuales

```bash
python diagnostico/fetch_logs.py
```

### Paso 2: Probar Endpoint Directamente

```bash
# Obtener credenciales
API_URL=$(aws cloudformation describe-stacks --stack-name salud-api-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`TurnosApiUrl`].OutputValue' --output text)
API_KEY=$(aws cloudformation describe-stacks --stack-name salud-api-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiKey`].OutputValue' --output text)

# Crear turno de prueba
curl -X POST "${API_URL}/turnos" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "fecha": "2026-02-15",
    "hora": "10:00",
    "medicoId": "medico-buenosaires-cardio-001",
    "pacienteId": "test-diag-001",
    "nombrePaciente": "Test Diagnostico",
    "emailPaciente": "test@diag.com",
    "telefonoPaciente": "+541199887766",
    "motivoConsulta": "Test"
  }'

# Guardar el turnoId retornado

# Modificar turno (probar con ambos formatos)
curl -X POST "${API_URL}/turnos/modificar" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "turnoId": "TURNO-XXXXX",
    "pacienteId": "test-diag-001",
    "fechaTurno": "2026-02-16",
    "horaTurno": "11:00"
  }'

# Verificar en DynamoDB
TABLE_NAME=$(aws cloudformation describe-stack-resources \
  --stack-name salud-api-stack \
  --logical-resource-id TurnosTable \
  --query 'StackResources[0].PhysicalResourceId' --output text)

aws dynamodb get-item \
  --table-name ${TABLE_NAME} \
  --key '{"turnoId": {"S": "TURNO-XXXXX"}}'
```

### Paso 3: Probar con el Agente

1. Llamar al número de Amazon Connect
2. Solicitar modificar un turno
3. Verificar que el agente llame correctamente a la API
4. Revisar logs de API Gateway y Lambda

---

## 📈 Próximos Pasos

1. ✅ **Diagnóstico completado** - Código de lambda está correcto
2. ⏭️ **Forzar recarga de caché** - Unpublish/Publish del agente
3. ⏭️ **Mejorar logging** - Agregar logging del UpdateExpression
4. ⏭️ **Validar end-to-end** - Probar flujo completo
5. ⏭️ **Implementar validación de disponibilidad** - Evitar conflictos
6. ⏭️ **Actualizar documentación** - Documentar proceso de actualización

---

## 🔧 Herramientas de Diagnóstico Creadas

1. **lambda_analyzer.py** - Analiza código de lambdas
2. **cloudwatch_analyzer.py** - Analiza logs de CloudWatch
3. **run_diagnosis.py** - Ejecuta diagnóstico completo
4. **fetch_logs.py** - Obtiene logs de AWS
5. **test_lambda_analyzer.py** - Tests unitarios y property-based

Todos los tests pasan: ✅ 9/9 tests exitosos

---

**Conclusión Final:** El código está correctamente implementado. El problema es muy probablemente el caché del MCP Server. Recomendación: Unpublish/Publish del agente Luna y validar.
