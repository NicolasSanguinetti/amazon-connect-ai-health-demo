# ❓ Preguntas Frecuentes: Tool Safety Status

**Fecha:** 2 de Febrero de 2026

---

## 1. ¿Por qué el Tool Safety Status está en "Unspecified"?

**Respuesta:** Porque el OpenAPI no tiene la extensión `x-amazon-connect-tool-safety` configurada.

Amazon Connect lee esta extensión del OpenAPI para determinar si un tool es:
- **safe** - Solo lee datos, no modifica nada
- **destructive** - Modifica o elimina datos
- **unspecified** - No se especificó (default)

Cuando está en "unspecified", Amazon Connect puede decidir NO ejecutar el tool automáticamente.

---

## 2. ¿Por qué no puedo cambiar el Tool Safety Status desde la UI?

**Respuesta:** Porque el Tool Safety Status NO se configura desde la UI de Amazon Connect.

Se define en el OpenAPI con:
```yaml
x-amazon-connect-tool-safety: destructive
```

La UI solo **muestra** el valor que viene del OpenAPI, no permite editarlo.

**Para cambiarlo:**
1. Editar el OpenAPI
2. Subir a S3
3. Forzar recarga del gateway
4. Unpublish/Publish del agente

---

## 3. ¿Ya subí el OpenAPI corregido a S3, por qué sigue en "Unspecified"?

**Respuesta:** Porque el gateway y el agente tienen el OpenAPI en caché.

**Solución:**
1. Forzar recarga del gateway (Edit → Save → 30s)
2. Unpublish/Publish del agente (15s)

El gateway cachea el OpenAPI para mejorar el rendimiento. Al hacer Edit → Save, fuerza la recarga desde S3.

---

## 4. ¿Cuánto tiempo tarda en actualizarse el Tool Safety Status?

**Respuesta:** Aproximadamente 1 minuto después de Unpublish/Publish.

**Timeline:**
- Gateway Edit → Save: 30 segundos
- Agente Unpublish → Publish: 15 segundos
- Verificación del Tool Safety Status: Inmediato

**Total:** ~1 minuto

---

## 5. ¿El agente pedirá confirmación antes de ejecutar el tool?

**Respuesta:** Depende de la configuración de "User Confirmation".

**Si "User Confirmation" está ACTIVADO:**
- El agente pedirá confirmación explícita antes de ejecutar
- Ejemplo: "¿Confirmas que quieres crear este turno?"

**Si "User Confirmation" está DESACTIVADO:**
- El agente ejecutará el tool automáticamente
- Ejemplo: "Voy a confirmar tu turno ahora" → Ejecuta inmediatamente

**Recomendación:** Desactivar "User Confirmation" para una experiencia más fluida.

---

## 6. ¿Qué diferencia hay entre "safe" y "destructive"?

**Respuesta:**

### safe
- El tool solo **lee** datos
- No modifica ni elimina nada
- Ejemplos: buscarMedicos, obtenerTurnosPaciente
- Amazon Connect lo ejecuta sin restricciones

### destructive
- El tool **modifica o elimina** datos
- Ejemplos: crearTurno, modificarTurno, cancelarTurno
- Amazon Connect puede requerir confirmación adicional
- Requiere permisos especiales

---

## 7. ¿Debo configurar todos los endpoints como "destructive"?

**Respuesta:** NO. Solo los que modifican o eliminan datos.

**Configuración recomendada:**

```yaml
# Solo lectura → safe
/medicos/buscar:
  post:
    x-amazon-connect-tool-safety: safe

/turnos/paciente:
  post:
    x-amazon-connect-tool-safety: safe

# Modifican datos → destructive
/turnos:
  post:
    x-amazon-connect-tool-safety: destructive

/turnos/modificar:
  post:
    x-amazon-connect-tool-safety: destructive

/turnos/cancelar:
  post:
    x-amazon-connect-tool-safety: destructive
```

---

## 8. ¿Qué pasa si no configuro x-amazon-connect-tool-safety?

**Respuesta:** El tool quedará en "Unspecified" y puede NO ejecutarse.

**Comportamiento:**
- Amazon Connect no sabe si es seguro ejecutar el tool
- Puede decidir NO ejecutarlo automáticamente
- El agente dirá que va a hacer algo pero no lo hará
- No habrá errores en los logs, simplemente no se ejecuta

**Solución:** Siempre configurar `x-amazon-connect-tool-safety` en todos los endpoints.

---

## 9. ¿Cómo verifico que el OpenAPI en S3 tiene la configuración correcta?

**Respuesta:** Ejecutar el script de verificación:

```powershell
.\diagnostico\verificar_tool_safety.ps1
```

**O manualmente:**

```bash
# Descargar el OpenAPI desde S3
aws s3 cp s3://salud-api-stack-openapibucket-korvxxrkhifa/openapi.yaml openapi-temp.yaml

# Buscar x-amazon-connect-tool-safety
grep -A 2 "x-amazon-connect-tool-safety" openapi-temp.yaml
```

Debe mostrar:
```yaml
x-amazon-connect-tool-safety: destructive
```

---

## 10. ¿Por qué el agente dice "Voy a confirmar tu turno" pero no lo hace?

**Respuesta:** Porque el tool NO se está ejecutando.

**Posibles causas:**

1. **Tool Safety Status en "Unspecified"** ← Causa más común
   - Solución: Configurar x-amazon-connect-tool-safety

2. **User Confirmation activado**
   - Solución: Desactivar "Require user confirmation"

3. **Permisos insuficientes**
   - Solución: Verificar permisos IAM del agente

4. **Error en el input schema**
   - Solución: Ver logs del agente para errores de validación

5. **Gateway no actualizado**
   - Solución: Forzar recarga del gateway

---

## 11. ¿Cómo sé si el tool se ejecutó correctamente?

**Respuesta:** Verificar en múltiples lugares:

### 1. Logs del API Gateway
```bash
aws logs tail /aws/apigateway/salud-api-stack --since 5m --follow
```

Debe aparecer:
```
POST /turnos - 201 Created
```

### 2. Logs de Lambda
```bash
aws logs tail /aws/lambda/CreateTurnoFunction --since 5m --follow
```

Debe aparecer:
```
Creating turno for patient: ...
Turno created successfully: TURNO-ABC123
```

### 3. DynamoDB
```bash
aws dynamodb scan --table-name salud-api-stack-TurnosTable-1LLEZVIWYG3RI --region us-east-1 --max-items 10
```

Debe aparecer el turno recién creado.

### 4. Respuesta del Agente
El agente debe confirmar con el turnoId:
```
"Tu turno ha sido confirmado. Tu número de turno es TURNO-ABC123"
```

---

## 12. ¿Qué hago si después de seguir todos los pasos sigue sin funcionar?

**Respuesta:** Revisar los logs para identificar el error específico.

### Paso 1: Ver logs del agente
```bash
aws logs tail /aws/connect/[instance-id] --since 30m --follow
```

Buscar:
- Errores de tool execution
- Errores de validación de schema
- Errores de permisos

### Paso 2: Ver logs del gateway
```bash
aws logs tail /aws/lambda/gateway_salud-mcp-server --since 30m --follow
```

Buscar:
- Errores al leer el OpenAPI
- Errores al generar los tools
- Errores de conexión con el API Gateway

### Paso 3: Verificar permisos IAM

El agente Luna debe tener permisos para:
- Invocar el gateway de AgentCore
- El gateway debe tener permisos para llamar al API Gateway

### Paso 4: Revisar el prompt del agente

El prompt debe incluir instrucciones para ejecutar tools:
```yaml
<instructions>
When the user confirms they want to create an appointment:
1. Call the salud_api__crearTurno tool
2. Wait for the response
3. Confirm with the turnoId
</instructions>
```

---

## 13. ¿Puedo probar el tool manualmente antes de probarlo con el agente?

**Respuesta:** Sí, desde la configuración del tool en Amazon Connect.

**Pasos:**
1. Amazon Connect → AI agents → Luna → Tools
2. Click en "salud_api__crearTurno"
3. Buscar un botón "Test" o "Try it"
4. Ejecutar con parámetros de prueba:

```json
{
  "medicoId": "medico-buenosaires-cardio-001",
  "pacienteId": "test-123",
  "nombrePaciente": "Test Usuario",
  "emailPaciente": "test@test.com",
  "fechaTurno": "2026-02-15",
  "horaTurno": "10:00",
  "telefono": "1234567890",
  "motivoConsulta": "Test"
}
```

Debe retornar:
```json
{
  "success": true,
  "turnoId": "TURNO-XYZ789",
  "message": "Turno creado exitosamente"
}
```

---

## 14. ¿Necesito hacer Unpublish/Publish cada vez que cambio el OpenAPI?

**Respuesta:** Sí, cada vez que cambies el OpenAPI en S3.

**Workflow:**
1. Editar el OpenAPI localmente
2. Subir a S3
3. Forzar recarga del gateway (Edit → Save)
4. Unpublish/Publish del agente

**Por qué:** El gateway y el agente cachean el OpenAPI para mejorar el rendimiento.

---

## 15. ¿Cuánto tiempo permanece el OpenAPI en caché?

**Respuesta:** Indefinidamente hasta que se fuerce la recarga.

El gateway NO recarga el OpenAPI automáticamente. Debes forzar la recarga manualmente:

**Método 1:** Edit → Save en el gateway
**Método 2:** Recrear el gateway (no recomendado)
**Método 3:** Esperar 24 horas (no confiable)

**Recomendación:** Siempre usar Edit → Save para forzar la recarga inmediata.

---

## 📚 Documentación de Referencia

- **SOLUCION-TOOL-SAFETY-STATUS.md** - Guía detallada del problema
- **ACCION-INMEDIATA.md** - Pasos inmediatos
- **RESUMEN-FINAL-SOLUCION.md** - Resumen completo
- **DIAGRAMA-SOLUCION-TOOL-SAFETY.txt** - Diagrama visual
- **GUIA-AGENTCORE-GATEWAY.md** - Configuración del gateway

---

**Preparado por:** Kiro AI Assistant  
**Fecha:** 2 de Febrero de 2026  
**Versión:** 1.0
