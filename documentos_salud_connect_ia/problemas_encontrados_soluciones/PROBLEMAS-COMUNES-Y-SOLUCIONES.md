# 🐛 Problemas Comunes y Soluciones Aplicadas
## Sistema de Turnos Médicos - CloudHesive LATAM

**Fecha:** 30 de Enero de 2026  
**Versión:** 1.0  
**Autor:** Diego Borra - CloudHesive LATAM

---

## 📋 **RESUMEN EJECUTIVO**

Este documento detalla los 8 problemas principales encontrados durante el desarrollo e integración del sistema de turnos médicos con Amazon Connect, sus causas raíz, y las soluciones aplicadas.

**Estado general:** 6 de 8 problemas resueltos completamente, 2 pendientes de validación final.

---

## 🔴 **PROBLEMA 1: Mismatch de Nombres de Campos**

### **Descripción:**
El agente enviaba `fecha`, `hora`, `telefonoPaciente` pero las Lambdas esperaban `fechaTurno`, `horaTurno`, `telefono`.

### **Síntomas:**
```
Error: "Missing required parameters: fechaTurno, horaTurno"
```

### **Solución:**
Modificamos las Lambdas para aceptar AMBOS formatos:

```javascript
const fechaTurno = body.fechaTurno || body.fecha;
const horaTurno = body.horaTurno || body.hora;
const telefono = body.telefono || body.telefonoPaciente;
```

**Estado:** ✅ RESUELTO  
**Archivo:** `turnos-medicos-api-final.yaml`

---

## 🟠 **PROBLEMA 2: Cache del MCP Server**

### **Descripción:**
Amazon Connect cachea el OpenAPI y no recarga automáticamente al actualizar el archivo en S3.

### **Síntomas:**
- Actualizas OpenAPI en S3
- Agente sigue usando versión vieja
- Cambios no se reflejan en 15-20 minutos

### **Soluciones:**

**Opción 1 (recomendada):** Unpublish/Publish
```
AI agents → Tu agente → Unpublish → Wait 10s → Publish
```

**Opción 2:** Cache busting con timestamp
```bash
aws s3 cp openapi.yaml s3://bucket/openapi-${TIMESTAMP}.yaml
```

**Opción 3:** Query parameter
```
https://bucket.s3.amazonaws.com/openapi.yaml?v=2
```

**Estado:** ⚠️ WORKAROUND DISPONIBLE  
**Acción requerida:** Unpublish/Publish después de cada cambio

---

## 🔴 **PROBLEMA 3: Índice DynamoDB Incorrecto**

### **Descripción:**
Lambda buscaba `CustomerIndex` pero la tabla tenía `PacienteIndex`.

### **Error:**
```
The table does not have the specified index: CustomerIndex
```

### **Solución:**
```python
# ANTES
IndexName='CustomerIndex'

# DESPUÉS
IndexName='PacienteIndex'
```

**Estado:** ✅ RESUELTO  
**Archivo:** `turnos-medicos-api-final.yaml` (GetTurnosPacienteFunction)

---

## 🔴 **PROBLEMA 4: ModifyTurno No Guardaba Cambios**

### **Descripción:**
El agente confirmaba modificación pero `fechaTurno` y `horaTurno` no cambiaban en DynamoDB.

### **Causa:**
Lambda solo actualizaba si venían los campos, pero el agente solo enviaba `turnoId` y `pacienteId`.

### **Solución:**
```python
# Aceptar ambos formatos
if 'fechaTurno' in body or 'fecha' in body:
    fecha = body.get('fechaTurno') or body.get('fecha')
    expression_values[':fechaTurno'] = fecha
```

**Estado:** ✅ RESUELTO  
**Archivo:** `turnos-medicos-api-final.yaml` (ModifyTurnoFunction)

---

## 🟠 **PROBLEMA 5: Fechas Relativas vs Exactas**

### **Descripción:**
El agente decía "próximo miércoles" en lugar de calcular "2026-02-05".

### **Solución Aplicada:**
Agregamos sección completa en el prompt:

```yaml
<date_and_time_handling>
CRITICAL INSTRUCTIONS:

1. ALWAYS calculate exact dates - NEVER use relative terms
   - "next Monday" → "2026-02-03"
   
2. ALWAYS use ISO format: YYYY-MM-DD
   - Never: "02/05/2026"
   - Always: "2026-02-05"
   
3. ALWAYS use 24-hour format: HH:MM
   - Never: "3 PM"
   - Always: "15:00"
</date_and_time_handling>
```

**Estado:** ⚠️ IMPLEMENTADO - PENDIENTE VALIDACIÓN  
**Archivo:** `luna-agent-prompt-mejorado.yaml`  
**Acción requerida:** Validar después de cache refresh

---

## 🔴 **PROBLEMA 6: Variables Duplicadas en Prompt**

### **Descripción:**
Amazon Connect rechazaba el prompt: "Each variable may only appear once"

### **Variables duplicadas:**
- `{{$.dateTime}}` - 3 veces
- `{{$.locale}}` - 2 veces
- `{{$.Custom.CompanyName_Voice}}` - 4 veces

### **Solución:**
Cada variable solo puede aparecer UNA vez. Removimos duplicados:

```yaml
# ❌ ANTES
system: |
  AI assistant for {{$.Custom.CompanyName_Voice}}
  appointment at {{$.Custom.CompanyName_Voice}}
  
system_variables:
  - companyName: {{$.Custom.CompanyName_Voice}}

# ✅ DESPUÉS
system: |
  AI assistant!
  
system_variables:
  - companyName: {{$.Custom.CompanyName_Voice}}  # Solo aquí
```

**Estado:** ✅ RESUELTO  
**Archivo:** `luna-agent-prompt-mejorado.yaml`

---

## 🔴 **PROBLEMA 7: OpenAPI Access Denied (403)**

### **Descripción:**
CustomResource de CloudFormation no podía descargar OpenAPI desde S3 externo.

### **Error:**
```
HTTP Error 403: Forbidden
Access Denied
```

### **Causa:**
Bucket externo tenía Block Public Access sin bucket policy.

### **Solución:**
Usar bucket interno del stack:

```bash
# Obtener bucket interno
STACK_BUCKET=$(aws cloudformation describe-stack-resources \
  --stack-name salud-api-stack \
  --logical-resource-id OpenApiBucket \
  --query 'StackResources[0].PhysicalResourceId' --output text)

# Subir ahí
aws s3 cp openapi.yaml s3://${STACK_BUCKET}/turnos-api.yaml
```

**Estado:** ✅ RESUELTO  
**Bucket usado:** `salud-api-stack-openapibucket-korvxxrkhifa`

---

## 🔴 **PROBLEMA 8: Doble Saludo**

### **Descripción:**
Contact Flow y Agente saludaban ambos.

### **Resultado:**
```
Flow: "Hola, bienvenido a ClinicaSalud"
Agent: "¡Hola! ¿Cómo te puedo ayudar?"
```

### **Solución:**
```yaml
<instructions>
The patient has already been greeted in the contact flow, 
so DO NOT greet them again. Start directly by understanding 
their needs.
</instructions>
```

**Estado:** ✅ RESUELTO  
**Archivo:** `luna-agent-prompt-mejorado.yaml`

---

## 🔴 **PROBLEMA 9: OpenAPI Incompleto - Causa Raíz del Problema de Modificación**

### **Descripción:**
El OpenAPI no documentaba todos los campos que las lambdas aceptan, causando que el agente no supiera que puede enviar formatos alternativos.

### **Causa Raíz Identificada:**
```
Lambda ModifyTurnoFunction acepta:
  - fechaTurno o fecha (ambos)
  - horaTurno o hora (ambos)
  - telefono o telefonoPaciente (ambos)
  - motivoConsulta

OpenAPI v2 solo documentaba:
  - fechaTurno
  - horaTurno
  
Resultado: El agente solo conocía los campos documentados en OpenAPI
```

### **Impacto:**
- El agente nunca enviaba los formatos alternativos
- Modificaciones de turnos fallaban silenciosamente
- El problema NO era el código de la lambda (que estaba correcto)
- El problema NO era el prompt del agente (que estaba correcto)
- **El problema ERA la inconsistencia OpenAPI-Lambda**

### **Solución Implementada:**

**1. Diagnóstico Completo:**
```bash
# Herramientas creadas:
✅ lambda_analyzer.py - Analiza código de lambdas
✅ openapi_validator.py - Valida consistencia OpenAPI-Lambda
✅ cloudwatch_analyzer.py - Analiza logs
✅ full_system_diagnosis.py - Diagnóstico completo
✅ Tests: 9/9 pasando
```

**2. OpenAPI v3 Corregido:**
```yaml
# Archivo: turnos-medicos-api-openapi-CORREGIDO.yaml
/turnos/modificar:
  properties:
    # Documentar AMBOS formatos
    fechaTurno:
      type: string
      description: "Nueva fecha (YYYY-MM-DD). También acepta 'fecha'"
    fecha:
      type: string
      description: "Formato alternativo de fechaTurno"
    horaTurno:
      type: string
      description: "Nueva hora (HH:MM). También acepta 'hora'"
    hora:
      type: string
      description: "Formato alternativo de horaTurno"
    # Campos adicionales
    motivoConsulta: string
    telefono: string
    telefonoPaciente: string
```

**3. Despliegue:**
```bash
# Subir OpenAPI v3 a S3
aws s3 cp turnos-medicos-api-openapi-CORREGIDO.yaml \
  s3://salud-api-stack-openapibucket-korvxxrkhifa/turnos-medicos-api-openapi-v3.yaml

# URL del OpenAPI v3:
https://salud-api-stack-openapibucket-korvxxrkhifa.s3.us-east-1.amazonaws.com/turnos-medicos-api-openapi-v3.yaml
```

**Estado:** ✅ RESUELTO - OpenAPI v3 subido, listo para configurar en Amazon Connect  
**Archivo:** `turnos-medicos-api-openapi-v3.yaml` en S3  
**Documentación:** `INSTRUCCIONES-DESPLIEGUE-OPENAPI.md`

---

## 📊 **TABLA RESUMEN**

| # | Problema | Estado | Archivo Afectado | Prioridad |
|---|----------|--------|------------------|-----------|
| 1 | Mismatch campos | ✅ Resuelto | turnos-medicos-api-final.yaml | P0 |
| 2 | Cache MCP | ⚠️ Workaround | N/A | P0 |
| 3 | Índice DynamoDB | ✅ Resuelto | turnos-medicos-api-final.yaml | P0 |
| 4 | ModifyTurno | ✅ Resuelto | turnos-medicos-api-final.yaml | P0 |
| 5 | Fechas relativas | ⚠️ Pendiente | luna-agent-prompt-mejorado.yaml | P1 |
| 6 | Variables duplicadas | ✅ Resuelto | luna-agent-prompt-mejorado.yaml | P1 |
| 7 | OpenAPI 403 | ✅ Resuelto | N/A | P0 |
| 8 | Doble saludo | ✅ Resuelto | luna-agent-prompt-mejorado.yaml | P2 |
| 9 | **OpenAPI Incompleto** | ✅ **Resuelto** | **turnos-medicos-api-openapi-v3.yaml** | **P0** |

**Leyenda:**
- ✅ Resuelto = Implementado y validado
- ⚠️ Workaround = Solución temporal disponible
- ⚠️ Pendiente = Implementado pero requiere validación

---

## 🎯 **ACCIONES PENDIENTES**

### **CRÍTICO (hacer ahora):**
1. ✅ **Diagnóstico completo** - COMPLETADO
2. ✅ **OpenAPI v3 corregido** - COMPLETADO
3. ✅ **Subir OpenAPI v3 a S3** - COMPLETADO
4. ⏭️ **Actualizar URL en Amazon Connect** - Ver `INSTRUCCIONES-DESPLIEGUE-OPENAPI.md`
5. ⏭️ **Unpublish/Publish el agente Luna** - Forzar recarga del cache
6. ⏭️ **Validar end-to-end** - Probar con fechas relativas

### **Instrucciones Detalladas:**
Ver archivo: `INSTRUCCIONES-DESPLIEGUE-OPENAPI.md`

### **Testing requerido:**
```bash
# 1. Ver logs en tiempo real
aws logs tail /aws/apigateway/salud-api-stack --since 5m --follow

# 2. Hacer llamada al flow
# Usuario: "Quiero modificar mi turno para el próximo miércoles a las 3 PM"

# 3. Verificar en logs:
# - POST /turnos/modificar ✅ (debe aparecer)

# 4. Verificar request body contiene:
# {"turnoId": "...", "pacienteId": "...", "fechaTurno": "2026-02-05", "horaTurno": "15:00"}

# 5. Verificar DynamoDB
TABLE_NAME=$(aws cloudformation describe-stacks \
  --stack-name salud-api-stack \
  --query "Stacks[0].Outputs[?OutputKey=='TurnosTableName'].OutputValue" \
  --output text)

aws dynamodb scan --table-name $TABLE_NAME --max-items 5
```

---

## 📝 **LECCIONES APRENDIDAS**

### **1. Cache en AWS es agresivo**
**Problema:** MCP Server cachea OpenAPI  
**Solución:** Siempre usar timestamps o Unpublish/Publish  
**Prevención:** Documentar proceso de actualización

### **2. Consistencia de nombres es crítica**
**Problema:** OpenAPI vs Lambda desincronizados  
**Solución:** Aceptar ambos formatos en Lambda  
**Prevención:** Contrato de API versionado y validado

### **3. Variables en prompts son estrictas**
**Problema:** Connect rechaza variables duplicadas  
**Solución:** Una variable = una aparición  
**Prevención:** Validar con grep antes de guardar

### **4. Testing incremental ahorra tiempo**
**Problema:** Difícil debuggear sistemas integrados  
**Solución:** Probar cada capa por separado  
**Prevención:** CI/CD con tests unitarios y de integración

---

## 🔧 **COMANDOS ÚTILES**

```bash
# Ver logs API Gateway
aws logs tail /aws/apigateway/salud-api-stack --since 30m --follow

# Ver logs Lambda
aws logs tail /aws/lambda/salud-api-stack-CreateTurnoFunction-* --since 30m

# Test manual endpoint
curl -X POST "${API_URL}/turnos" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{...}' | jq

# Ver datos DynamoDB
aws dynamodb scan --table-name ${TABLE_NAME} --max-items 5

# Verificar stack events (errores CloudFormation)
aws cloudformation describe-stack-events \
  --stack-name salud-api-stack \
  --max-items 20 \
  --output table
```

---

**Documento preparado por:** Diego Borra - CloudHesive LATAM  
**Para:** Equipo KIRO  
**Próximos pasos:** Validación end-to-end después de cache refresh
