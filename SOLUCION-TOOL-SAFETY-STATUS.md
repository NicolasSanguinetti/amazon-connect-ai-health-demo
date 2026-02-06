# 🔧 Solución: Tool Safety Status "Unspecified"

**Fecha:** 2 de Febrero de 2026  
**Problema:** El tool `salud_api__crearTurno` no se ejecuta - Tool Safety Status en "Unspecified"

---

## ✅ Lo Que Ya Está Hecho

1. ✅ OpenAPI v3 corregido con `x-amazon-connect-tool-safety: destructive`
2. ✅ Archivos subidos a S3
3. ✅ Gateway configurado correctamente

**El problema:** El agente tiene el OpenAPI en caché y no ve los cambios.

---

## 🎯 Solución en 3 Pasos

### Paso 1: Forzar Recarga del Gateway

El gateway necesita recargar el OpenAPI desde S3:

```
1. Ir a: Amazon Bedrock → AgentCore → Gateways
2. Buscar: gateway_salud-mcp-server-odybaqqqx2
3. Click en el gateway
4. Click en "Edit"
5. NO cambies nada
6. Click en "Save"
7. ESPERAR 30 segundos (el gateway recarga el OpenAPI)
```

### Paso 2: Unpublish/Publish del Agente Luna

El agente necesita recargar los tools desde el gateway:

```
1. Ir a: Amazon Connect → AI agents → Luna
2. Click en "Unpublish"
3. ESPERAR 15 segundos
4. Click en "Publish"
5. Verificar que el estado sea "Active"
```

### Paso 3: Verificar el Tool Safety Status

```
1. Ir a: Amazon Connect → AI agents → Luna → Tools
2. Click en "salud_api__crearTurno"
3. Verificar que ahora diga:
   Tool Safety Status: Destructive ✅
```

---

## 🔍 Por Qué No Se Puede Cambiar desde la UI

El "Tool Safety Status" NO se configura desde la UI de Amazon Connect.

Se define en el OpenAPI con la extensión:
```yaml
x-amazon-connect-tool-safety: destructive
```

La UI solo **muestra** el valor, no permite editarlo.

Para cambiarlo:
1. Editar el OpenAPI
2. Subir a S3
3. Forzar recarga del gateway
4. Unpublish/Publish del agente

---

## 🧪 Validar que Funcionó

### Test 1: Verificar Tool Safety Status

```
1. Amazon Connect → AI agents → Luna → Tools
2. Click en "salud_api__crearTurno"
3. Debe decir: "Tool Safety Status: Destructive"
```

### Test 2: Probar Crear un Turno

1. Iniciar una conversación con el agente
2. Solicitar un turno con un cardiólogo
3. Proporcionar todos los datos
4. Confirmar la creación

**Resultado esperado:**
- ✅ El agente ejecuta el tool
- ✅ Aparece un nuevo turno en DynamoDB
- ✅ El agente confirma con el turnoId

### Test 3: Verificar en DynamoDB

```bash
aws dynamodb scan \
  --table-name salud-api-stack-TurnosTable-1LLEZVIWYG3RI \
  --region us-east-1 \
  --max-items 10
```

Debe aparecer el turno recién creado.

---

## 📊 Qué Hace el x-amazon-connect-tool-safety

Esta extensión le dice a Amazon Connect cómo tratar el tool:

### Valores posibles:

1. **safe** - El tool solo lee datos, no modifica nada
   - Ejemplo: buscarMedicos, obtenerTurnosPaciente
   - El agente puede ejecutarlo sin restricciones

2. **destructive** - El tool modifica o elimina datos
   - Ejemplo: crearTurno, modificarTurno, cancelarTurno
   - El agente puede requerir confirmación adicional

3. **unspecified** (default) - No se especificó
   - Amazon Connect no sabe si es seguro o no
   - Puede causar que el agente NO ejecute el tool

---

## 🔧 Configuración Actual en el OpenAPI

```yaml
/turnos:
  post:
    operationId: crearTurno
    x-amazon-connect-tool-safety: destructive  # ← Esto define el Tool Safety Status
    
/turnos/modificar:
  post:
    operationId: modificarTurno
    x-amazon-connect-tool-safety: destructive  # ← Esto define el Tool Safety Status
    
/turnos/cancelar:
  post:
    operationId: cancelarTurno
    x-amazon-connect-tool-safety: destructive  # ← Esto define el Tool Safety Status
```

---

## ⚠️ Importante: User Confirmation

Además del Tool Safety Status, verifica que "User Confirmation" esté DESACTIVADO:

```
1. Amazon Connect → AI agents → Luna → Tools
2. Click en "salud_api__crearTurno"
3. Buscar: "Require user confirmation before tool invocation"
4. Debe estar: ❌ DESACTIVADO
```

Si está activado, el agente pedirá confirmación explícita antes de ejecutar el tool.

---

## 📋 Checklist Completo

- [ ] OpenAPI tiene `x-amazon-connect-tool-safety: destructive` en los 3 endpoints
- [ ] OpenAPI está subido a S3
- [ ] Gateway recargado (Edit → Save → Esperar 30s)
- [ ] Agente Unpublish/Publish (Esperar 15s)
- [ ] Tool Safety Status cambió de "Unspecified" a "Destructive"
- [ ] User Confirmation está DESACTIVADO
- [ ] Test de creación de turno exitoso
- [ ] Turno aparece en DynamoDB

---

## 🎉 Resultado Final Esperado

Después de seguir estos pasos:

✅ Tool Safety Status: **Destructive** (ya no "Unspecified")  
✅ El agente ejecuta `salud_api__crearTurno` automáticamente  
✅ Los turnos se crean correctamente en DynamoDB  
✅ El agente confirma con el turnoId generado  

---

## 📞 Si Aún No Funciona

Si después de estos pasos el tool sigue sin ejecutarse:

1. **Ver logs del agente:**
```bash
aws logs tail /aws/connect/[instance-id] --since 30m --follow
```

2. **Ver logs del gateway:**
```bash
aws logs tail /aws/lambda/gateway_salud-mcp-server --since 30m --follow
```

3. **Verificar permisos IAM:**
   - El agente debe tener permisos para invocar el gateway
   - El gateway debe tener permisos para llamar al API Gateway

4. **Revisar el prompt del agente:**
   - Debe incluir instrucciones para ejecutar tools
   - No debe tener restricciones que impidan la ejecución

---

**Preparado por:** Kiro AI Assistant  
**Fecha:** 2 de Febrero de 2026  
**Versión:** 1.0
