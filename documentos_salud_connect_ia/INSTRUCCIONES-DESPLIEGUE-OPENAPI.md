# 🚀 Instrucciones de Despliegue - OpenAPI Corregido

**Fecha:** 2 de Febrero de 2026  
**Stack:** salud-api-stack  
**Objetivo:** Actualizar el OpenAPI en Amazon Connect para que el agente Luna conozca todos los campos disponibles

---

## ✅ Paso 1: Subir OpenAPI a S3 (COMPLETADO)

El archivo OpenAPI corregido ya fue subido exitosamente:

```bash
✅ Archivo: turnos-medicos-api-openapi-v3.yaml
✅ Bucket: salud-api-stack-openapibucket-korvxxrkhifa
✅ Región: us-east-1
✅ URL: https://salud-api-stack-openapibucket-korvxxrkhifa.s3.us-east-1.amazonaws.com/turnos-medicos-api-openapi-v3.yaml
```

**Verificación:**
```bash
aws s3 ls s3://salud-api-stack-openapibucket-korvxxrkhifa/
# Debe mostrar: turnos-medicos-api-openapi-v3.yaml
```

---

## 📋 Paso 2: Actualizar MCP Server en Amazon Connect

### 2.1 Acceder a la Configuración del Agente

1. Ir a **Amazon Connect Console**: https://console.aws.amazon.com/connect/
2. Seleccionar tu instancia de Connect
3. En el menú lateral, ir a **AI agents**
4. Buscar y seleccionar el agente **Luna**

### 2.2 Actualizar la URL del OpenAPI

1. En la configuración del agente Luna, ir a la sección **Tools**
2. Buscar el **MCP Server** configurado
3. Click en **Edit** o **Configure**
4. Actualizar la URL del OpenAPI a:
   ```
   https://salud-api-stack-openapibucket-korvxxrkhifa.s3.us-east-1.amazonaws.com/turnos-medicos-api-openapi-v3.yaml
   ```
5. Click en **Save**

---

## 🔄 Paso 3: Forzar Recarga del Caché del MCP Server

**CRÍTICO:** Amazon Connect cachea el OpenAPI agresivamente. Debes forzar la recarga:

### Opción A: Unpublish/Publish (RECOMENDADO)

1. En la configuración del agente Luna, buscar el botón **Unpublish**
2. Click en **Unpublish**
3. **Esperar 10 segundos** (importante para que se limpie el caché)
4. Click en **Publish**
5. Verificar que el agente esté **Active**

### Opción B: Reiniciar el Agente

Si Unpublish/Publish no está disponible:

1. Ir a **AI agents** → **Luna**
2. Click en **Stop** o **Disable**
3. Esperar 10 segundos
4. Click en **Start** o **Enable**

---

## 🧪 Paso 4: Validación End-to-End

### 4.1 Probar con el Agente

1. Llamar al sistema de turnos
2. Solicitar modificar un turno existente
3. Usar lenguaje natural con fechas relativas:
   - "Quiero cambiar mi turno para la semana próxima"
   - "Cambiar mi turno al próximo miércoles a las 3 de la tarde"
   - "Modificar mi turno para el 15 de febrero a las 10 de la mañana"

### 4.2 Verificar en CloudWatch Logs

```bash
# Ver logs del API Gateway en tiempo real
aws logs tail /aws/apigateway/salud-api-stack --since 5m --follow

# Buscar el request body del POST /turnos/modificar
# Debe contener:
# {
#   "turnoId": "TURNO-XXX",
#   "pacienteId": "PAC-123",
#   "fechaTurno": "2026-02-12",  # Fecha calculada en formato ISO
#   "horaTurno": "15:00"          # Hora en formato 24h
# }
```

### 4.3 Verificar en DynamoDB

```bash
# Obtener el nombre de la tabla
TABLE_NAME=$(aws cloudformation describe-stacks \
  --stack-name salud-api-stack \
  --query "Stacks[0].Outputs[?OutputKey=='TurnosTableName'].OutputValue" \
  --output text)

# Ver los últimos turnos modificados
aws dynamodb scan \
  --table-name $TABLE_NAME \
  --filter-expression "attribute_exists(modifiedAt)" \
  --max-items 5 \
  | jq '.Items[] | {turnoId: .turnoId.S, fechaTurno: .fechaTurno.S, horaTurno: .horaTurno.S, modifiedAt: .modifiedAt.S}'
```

---

## ✅ Checklist de Validación

- [ ] OpenAPI v3 subido a S3
- [ ] URL del MCP Server actualizada en Amazon Connect
- [ ] Agente Luna unpublished y published
- [ ] Agente Luna está en estado **Active**
- [ ] Prueba con fecha relativa ("semana próxima") funciona
- [ ] Logs muestran `fechaTurno` y `horaTurno` en formato ISO
- [ ] DynamoDB muestra los campos actualizados correctamente

---

## 🔍 Troubleshooting

### Problema: El agente sigue sin enviar los campos correctos

**Causa:** El caché del MCP Server no se limpió correctamente.

**Solución:**
1. Verificar que la URL del OpenAPI esté correcta
2. Hacer Unpublish/Publish nuevamente
3. Esperar 2-3 minutos antes de probar
4. Si persiste, agregar un query parameter a la URL:
   ```
   https://...openapi-v3.yaml?v=2
   ```

### Problema: Error 403 al acceder al OpenAPI

**Causa:** El bucket tiene Block Public Access activado.

**Solución:**
El bucket interno del stack ya tiene los permisos correctos. Verificar que estés usando la URL correcta:
```
https://salud-api-stack-openapibucket-korvxxrkhifa.s3.us-east-1.amazonaws.com/turnos-medicos-api-openapi-v3.yaml
```

### Problema: El agente calcula mal las fechas

**Causa:** El prompt del agente puede necesitar actualización.

**Solución:**
Verificar que el prompt incluya la sección `<date_and_time_handling>` con instrucciones claras sobre formato ISO.

---

## 📊 Cambios Implementados en el OpenAPI v3

### Endpoint: `/turnos/modificar`

**ANTES (OpenAPI v2):**
```yaml
properties:
  turnoId: string
  pacienteId: string
  fechaTurno: string  # Solo este
  horaTurno: string   # Solo este
```

**DESPUÉS (OpenAPI v3):**
```yaml
properties:
  turnoId: string
  pacienteId: string
  # Campos de fecha - acepta AMBOS formatos
  fechaTurno: string
    description: "Nueva fecha (YYYY-MM-DD). También acepta 'fecha'"
  fecha: string
    description: "Formato alternativo de fechaTurno"
  # Campos de hora - acepta AMBOS formatos
  horaTurno: string
    description: "Nueva hora (HH:MM). También acepta 'hora'"
  hora: string
    description: "Formato alternativo de horaTurno"
  # Campos adicionales
  motivoConsulta: string
  telefono: string
  telefonoPaciente: string
```

**Impacto:**
- El agente ahora conoce que puede enviar `fecha` o `fechaTurno`
- El agente ahora conoce que puede enviar `hora` o `horaTurno`
- El agente puede modificar `motivoConsulta` y `telefono`
- La lambda ya acepta ambos formatos (no requiere cambios)

---

## 📝 Próximos Pasos Opcionales

### 1. Actualizar el Stack con el OpenAPI v3 por defecto

Si quieres que el stack siempre use el OpenAPI v3:

```bash
# Actualizar el parámetro OpenApiSpecUrl
aws cloudformation update-stack \
  --stack-name salud-api-stack \
  --use-previous-template \
  --parameters \
    ParameterKey=OpenApiSpecUrl,ParameterValue=s3://salud-api-stack-openapibucket-korvxxrkhifa/turnos-medicos-api-openapi-v3.yaml \
    ParameterKey=SeedDataUrl,UsePreviousValue=true
```

### 2. Mejorar Logging en ModifyTurnoFunction

Agregar logging del UpdateExpression antes de ejecutarlo:

```python
print(json.dumps({
    'level': 'INFO',
    'message': 'Executing DynamoDB update',
    'requestId': request_id,
    'updateExpression': update_expression,
    'expressionValues': expression_values
}))
```

### 3. Agregar Validación de Disponibilidad

Implementar check de conflictos antes de modificar:

```python
# Verificar si el nuevo horario está disponible
response = table.query(
    IndexName='MedicoFechaIndex',
    KeyConditionExpression='medicoId = :medicoId AND fechaTurno = :fechaTurno',
    FilterExpression='horaTurno = :horaTurno AND turnoId <> :currentTurnoId'
)

if response['Items']:
    return {
        'statusCode': 409,
        'body': json.dumps({'error': 'Horario no disponible'})
    }
```

---

## 📞 Contacto

**Preparado por:** Diego Borra - CloudHesive LATAM  
**Email:** diego@cloudhesive.com  
**Fecha:** 2 de Febrero de 2026

---

**Estado:** ✅ OpenAPI v3 subido - Listo para configurar en Amazon Connect
