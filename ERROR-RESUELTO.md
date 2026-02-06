# ✅ Error Resuelto: Server URL must use HTTPS

**Fecha:** 2 de Febrero de 2026  
**Error:** "Server URL must use HTTPS protocol"  
**Estado:** ✅ RESUELTO

---

## 🔴 Problema Encontrado

Cuando guardaste los cambios en AgentCore Gateway, apareció este error:

```
Gateway updated successfully, but there was an error processing targets:
Gateway target update failed or timed out:
Found 1 validation error(s) in OpenAPI schema:
["Server URL (located at: servers) must use HTTPS protocol."]
```

### Causa:

El OpenAPI tenía un placeholder:
```yaml
servers:
  - url: ${API_GATEWAY_URL}  # ← Placeholder sin protocolo
```

AgentCore Gateway valida el OpenAPI antes de procesarlo y rechazó el placeholder porque no especifica HTTPS explícitamente.

---

## ✅ Solución Aplicada

Actualicé el OpenAPI con la URL real de tu API Gateway:

```yaml
servers:
  - url: https://wldr2xok2d.execute-api.us-east-1.amazonaws.com/dev
    description: AWS API Gateway endpoint
```

Y subí los archivos corregidos a S3:
- ✅ `openapi.yaml` → Actualizado con URL HTTPS
- ✅ `turnos-api.yaml` → Actualizado con URL HTTPS
- ✅ `turnos-medicos-api-openapi-v3.yaml` → Actualizado con URL HTTPS

---

## 🎯 Próximos Pasos

### Paso 1: Volver a Guardar en AgentCore Gateway

1. **Ir a la configuración del gateway** en AgentCore
2. **Verificar que la URL sea:**
   ```
   https://salud-api-stack-openapibucket-korvxxrkhifa.s3.us-east-1.amazonaws.com/turnos-medicos-api-openapi-v3.yaml
   ```
3. **Click en "Save"** nuevamente
4. **Esta vez NO debería dar error** ✅

### Paso 2: Forzar Recarga del Caché

Después de guardar exitosamente:

1. **Ir a Amazon Connect** → AI agents → Luna
2. **Click en "Unpublish"**
3. **Esperar 10-15 segundos**
4. **Click en "Publish"**
5. **Verificar que el estado sea "Active"**

---

## 🧪 Validar que Funcionó

### Test 1: Verificar que no hay errores

En la configuración del gateway, deberías ver:
```
✅ Gateway updated successfully
✅ No validation errors
```

### Test 2: Ver los tools actualizados

1. Ir a Amazon Connect → AI agents → Luna → Tools
2. Click en "salud_api__modificarTurno"
3. Expandir "Input Schema"
4. Deberías ver los nuevos campos:
   - `fecha` (además de `fechaTurno`)
   - `hora` (además de `horaTurno`)
   - `motivoConsulta`
   - `telefono` y `telefonoPaciente`

### Test 3: Probar con el agente

1. Llamar al sistema
2. Decir: "Quiero cambiar mi turno para el próximo miércoles a las 3 de la tarde"
3. Verificar que funcione correctamente

---

## 📊 Archivos Actualizados en S3

```bash
# Ver archivos actuales
aws s3 ls s3://salud-api-stack-openapibucket-korvxxrkhifa/

# Todos ahora tienen:
# - URL HTTPS explícita
# - Todos los campos documentados (OpenAPI v3)
```

---

## 🔍 Verificar el Contenido del OpenAPI

Si quieres verificar que el archivo tiene la URL correcta:

```bash
# Descargar y ver las primeras líneas
aws s3 cp s3://salud-api-stack-openapibucket-korvxxrkhifa/turnos-medicos-api-openapi-v3.yaml - | Select-String -Pattern "servers:" -Context 0,3
```

Deberías ver:
```yaml
servers:
  - url: https://wldr2xok2d.execute-api.us-east-1.amazonaws.com/dev
    description: AWS API Gateway endpoint
```

---

## ❓ Si Sigue Dando Error

### Error: "Server URL must use HTTPS"

**Causa:** El archivo en S3 no se actualizó correctamente.

**Solución:**
```bash
# Forzar actualización del archivo
aws s3 cp documentos_salud_connect_ia\turnos-medicos-api-openapi-CORREGIDO.yaml s3://salud-api-stack-openapibucket-korvxxrkhifa/turnos-medicos-api-openapi-v3.yaml --metadata-directive REPLACE --cache-control "no-cache"
```

### Error: "Gateway target update failed"

**Causa:** AgentCore no puede acceder al archivo en S3.

**Solución:**
1. Verificar que el bucket tenga los permisos correctos
2. Verificar que la URL del archivo sea accesible
3. Intentar con una URL diferente (openapi.yaml o turnos-api.yaml)

---

## 📝 Resumen de Cambios

### Antes:
```yaml
servers:
  - url: ${API_GATEWAY_URL}  # ❌ Placeholder sin protocolo
```

### Después:
```yaml
servers:
  - url: https://wldr2xok2d.execute-api.us-east-1.amazonaws.com/dev  # ✅ URL HTTPS explícita
```

---

## 🎉 Conclusión

El error estaba en el placeholder `${API_GATEWAY_URL}` que no especificaba el protocolo HTTPS. Lo reemplacé con la URL real de tu API Gateway y subí los archivos corregidos a S3.

**Ahora puedes:**
1. Volver a guardar en AgentCore Gateway (sin errores)
2. Hacer Unpublish/Publish del agente Luna
3. Probar que la modificación de turnos funcione correctamente

---

**¿Listo para continuar?** Vuelve a guardar en AgentCore Gateway y luego haz Unpublish/Publish 🚀
