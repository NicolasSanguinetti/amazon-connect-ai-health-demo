# 🔧 Guía: Actualizar OpenAPI en AgentCore Gateway

**Fecha:** 2 de Febrero de 2026  
**Gateway:** gateway_salud-mcp-server-odybaqqqx2  
**Servicio:** AWS AgentCore

---

## 📊 Situación Actual

Tu arquitectura es:

```
Amazon Connect (Agente Luna)
    ↓
AgentCore Gateway (gateway_salud-mcp-server-odybaqqqx2)
    ↓ Lee OpenAPI desde S3
    ↓ Genera tools automáticamente
    ↓
Tools en Connect:
  - salud_api__crearTurno
  - salud_api__modificarTurno
  - salud_api__obtenerTurnosPaciente
  etc.
```

---

## 🎯 Solución Implementada

Ya actualicé los archivos OpenAPI en S3:

✅ **Archivo 1:** `openapi.yaml` → Reemplazado con OpenAPI v3
✅ **Archivo 2:** `turnos-api.yaml` → Reemplazado con OpenAPI v3
✅ **Archivo 3:** `turnos-medicos-api-openapi-v3.yaml` → Nuevo archivo

---

## 📋 Cómo Acceder a la Configuración de AgentCore

### Opción 1: Desde la Consola de AWS

1. **Ir a AWS Console**: https://console.aws.amazon.com/
2. **Buscar "AgentCore"** en la barra de búsqueda superior
3. **O ir directamente a**: https://console.aws.amazon.com/agentcore/

### Opción 2: Desde Amazon Connect

1. En la configuración del agente Luna
2. Buscar una sección que diga:
   - "External services"
   - "Gateways"
   - "MCP Servers"
3. Deberías ver: `gateway_salud-mcp-server-odybaqqqx2`
4. Click para ver/editar la configuración

### Opción 3: Usando AWS CLI

```bash
# Listar gateways de AgentCore
aws agentcore list-gateways

# Ver configuración del gateway específico
aws agentcore describe-gateway --gateway-id gateway_salud-mcp-server-odybaqqqx2
```

---

## 🔍 Qué Buscar en la Configuración del Gateway

Cuando encuentres la configuración del gateway, busca:

```yaml
Gateway Configuration:
  Name: gateway_salud-mcp-server-odybaqqqx2
  Type: MCP Server
  
  OpenAPI Configuration:
    URL: https://salud-api-stack-openapibucket-korvxxrkhifa.s3.us-east-1.amazonaws.com/openapi.yaml
    # ↑ Esta es la URL que el gateway está usando
    
  Authentication:
    Type: API Key
    Header: X-API-Key
    Value: Y9xhqWXzTuacBXpqjgQvG35HWfDE7roo6P3S4pCm
```

---

## ✅ Opciones para Actualizar

### Opción A: Cambiar la URL en AgentCore (Si necesitas)

Si quieres que el gateway use el archivo `turnos-medicos-api-openapi-v3.yaml`:

1. En la configuración del gateway
2. Cambiar la URL de:
   ```
   https://...amazonaws.com/openapi.yaml
   ```
   a:
   ```
   https://...amazonaws.com/turnos-medicos-api-openapi-v3.yaml
   ```
3. Guardar cambios

### Opción B: Ya Está Actualizado (Recomendado)

Como ya reemplacé los archivos `openapi.yaml` y `turnos-api.yaml` en S3 con el contenido del OpenAPI v3, **el gateway ya está usando la versión corregida**.

No necesitas cambiar la URL, solo necesitas **forzar la recarga del caché**.

---

## 🔄 Forzar Recarga del Caché (CRÍTICO)

AgentCore cachea el OpenAPI agresivamente. Debes forzar la recarga:

### Método 1: Unpublish/Publish del Agente (Más Fácil)

1. Ir a Amazon Connect → AI agents → Luna
2. Click en **"Unpublish"**
3. **Esperar 10-15 segundos**
4. Click en **"Publish"**
5. Verificar que el estado sea "Active"

### Método 2: Reiniciar el Gateway (Si disponible)

Si en la configuración del gateway hay una opción de "Restart" o "Reload":
1. Click en "Restart Gateway"
2. Esperar a que el estado sea "Active"

### Método 3: Usando AWS CLI

```bash
# Forzar recarga del gateway
aws agentcore update-gateway \
  --gateway-id gateway_salud-mcp-server-odybaqqqx2 \
  --force-reload
```

---

## 🧪 Validar que el Cambio Funcionó

### Test 1: Ver los Tools Actualizados

1. Ir a Amazon Connect → AI agents → Luna → Tools
2. Click en **"salud_api__modificarTurno"**
3. Expandir **"Input Schema"**
4. Deberías ver los nuevos campos:
   - `fecha` (además de `fechaTurno`)
   - `hora` (además de `horaTurno`)
   - `motivoConsulta`
   - `telefono` y `telefonoPaciente`

### Test 2: Probar con el Agente

1. Llamar al sistema
2. Decir: "Quiero cambiar mi turno para el próximo miércoles a las 3 de la tarde"
3. El agente debería:
   - Calcular la fecha exacta (2026-02-12)
   - Enviar `fechaTurno: "2026-02-12"` y `horaTurno: "15:00"`
   - Actualizar correctamente en DynamoDB

### Test 3: Ver Logs de CloudWatch

```bash
# Ver logs del API Gateway
aws logs tail /aws/apigateway/salud-api-stack --since 5m --follow

# Buscar el POST /turnos/modificar
# Verificar que el body contenga fechaTurno y horaTurno
```

---

## 📊 Estado Actual de los Archivos en S3

```bash
# Ver archivos actuales
aws s3 ls s3://salud-api-stack-openapibucket-korvxxrkhifa/

# Resultado:
# openapi.yaml                         ← ACTUALIZADO con OpenAPI v3
# turnos-api.yaml                      ← ACTUALIZADO con OpenAPI v3
# turnos-medicos-api-openapi-v3.yaml   ← NUEVO (OpenAPI v3)
```

Todos los archivos ahora contienen el OpenAPI v3 corregido con todos los campos documentados.

---

## 🔍 Troubleshooting

### No veo cambios después de Unpublish/Publish

**Causa:** El caché de AgentCore puede tardar más en limpiarse.

**Solución:**
1. Esperar 2-3 minutos adicionales
2. Hacer Unpublish/Publish nuevamente
3. Si persiste, contactar a AWS Support para limpiar el caché del gateway

### Los tools siguen mostrando el schema antiguo

**Causa:** El gateway no ha recargado el OpenAPI.

**Solución:**
1. Verificar que el archivo en S3 esté actualizado:
   ```bash
   aws s3 cp s3://salud-api-stack-openapibucket-korvxxrkhifa/openapi.yaml - | head -50
   ```
2. Buscar la línea que dice `version: 2.0.0` (debería estar en el OpenAPI v3)
3. Si no está actualizado, volver a subir el archivo

### El agente sigue sin enviar los campos correctos

**Causa:** El prompt del agente puede necesitar actualización.

**Solución:**
1. Verificar que el prompt incluya instrucciones sobre fechas ISO
2. Agregar ejemplos explícitos de cómo enviar fechaTurno y horaTurno

---

## 📝 Comandos Útiles

```bash
# Ver configuración del stack
aws cloudformation describe-stacks --stack-name salud-api-stack

# Ver archivos en S3
aws s3 ls s3://salud-api-stack-openapibucket-korvxxrkhifa/

# Descargar y ver el OpenAPI actual
aws s3 cp s3://salud-api-stack-openapibucket-korvxxrkhifa/openapi.yaml - | head -100

# Ver logs del API Gateway
aws logs tail /aws/apigateway/salud-api-stack --since 10m --follow

# Ver logs de Lambda ModifyTurno
aws logs tail /aws/lambda/salud-api-stack-ModifyTurnoFunction --since 10m
```

---

## 🎯 Resumen de Acciones

✅ **Completado:**
1. OpenAPI v3 corregido creado
2. Archivos en S3 actualizados (`openapi.yaml`, `turnos-api.yaml`)
3. Nuevo archivo `turnos-medicos-api-openapi-v3.yaml` subido

⏭️ **Pendiente (Tu acción):**
1. Ir a Amazon Connect → AI agents → Luna
2. Click en "Unpublish"
3. Esperar 10-15 segundos
4. Click en "Publish"
5. Probar con una llamada de prueba

---

## 📞 Contacto

Si necesitas ayuda para encontrar la configuración de AgentCore o tienes problemas:
- Comparte capturas de la consola de AgentCore
- Comparte los logs de CloudWatch
- Verifica que el agente esté en estado "Active"

**Preparado por:** Diego Borra - CloudHesive LATAM  
**Email:** diego@cloudhesive.com  
**Fecha:** 2 de Febrero de 2026

---

## 🎉 Conclusión

El OpenAPI v3 corregido ya está en S3 y los archivos que AgentCore Gateway está usando han sido actualizados. Solo necesitas **forzar la recarga del caché** haciendo Unpublish/Publish del agente Luna.

Una vez hecho esto, el agente conocerá todos los campos disponibles y podrá modificar turnos correctamente.
