# 🔄 Pasos para Actualizar el Prompt del Agente Luna

**Fecha:** 2 de Febrero de 2026  
**Problema Actual:** El agente NO ejecuta el tool crearTurno y cierra la conversación

---

## 🎯 Problema

El agente dice "Voy a confirmar tu turno ahora" pero:
- ❌ NO ejecuta el tool `salud_api__crearTurno`
- ❌ NO crea el turno en DynamoDB
- ❌ Cierra la conversación abruptamente

**Causa:** Estás usando el **prompt viejo** que no tiene las instrucciones de confirmación.

---

## ✅ Solución: Actualizar el Prompt

### Paso 1: Abrir el Archivo del Prompt Corregido

**Archivo:** `documentos_salud_connect_ia/luna-agent-prompt-MEJORADO-v2.yaml`

Este archivo tiene:
- ✅ Instrucciones de confirmación post-acción
- ✅ Instrucciones de manejo de fechas mejoradas
- ✅ Variables sin duplicados (corregido)

### Paso 2: Copiar TODO el Contenido

1. Abrir el archivo `luna-agent-prompt-MEJORADO-v2.yaml`
2. Seleccionar TODO el contenido (Ctrl+A)
3. Copiar (Ctrl+C)

**IMPORTANTE:** Copiar TODO el archivo, desde la primera línea hasta la última.

### Paso 3: Ir a Amazon Connect

1. Abrir: https://console.aws.amazon.com/connect/
2. Seleccionar tu instancia de Connect
3. Ir a: **AI agents**
4. Click en el agente **Luna**
5. Click en **Edit** (botón arriba a la derecha)

### Paso 4: Reemplazar el Prompt

1. Buscar la sección **"Instructions"** o **"Prompt"**
2. **Seleccionar TODO** el contenido actual del prompt
3. **Eliminar** el contenido actual
4. **Pegar** el nuevo prompt (Ctrl+V)
5. Verificar que se pegó correctamente

### Paso 5: Guardar

1. Click en **Save** (abajo a la derecha)
2. **ESPERAR** a que aparezca el mensaje de confirmación
3. Si aparece un error, revisar que no haya variables duplicadas

### Paso 6: Unpublish/Publish

1. Click en **Unpublish** (arriba a la derecha)
2. **ESPERAR 15 SEGUNDOS**
3. Click en **Publish**
4. Verificar que el estado sea **"Active"**

---

## 🧪 Validación

### Test 1: Verificar que el Prompt se Actualizó

1. Ir a Amazon Connect → AI agents → Luna
2. Click en **Edit**
3. Buscar en el prompt la sección `<appointment_confirmation_instructions>`
4. Debe estar presente con las instrucciones de confirmación

### Test 2: Probar Crear un Turno

1. Iniciar una conversación con el agente
2. Solicitar un turno con un cardiólogo
3. Proporcionar todos los datos
4. Confirmar la creación

**Resultado esperado:**
```
Cliente: "Perfecto, confirmo"
BOT: "Excelente, voy a confirmar tu turno ahora."
[El turno se crea en DynamoDB]
BOT: "¡Perfecto! Tu turno ha sido confirmado exitosamente. Tu número de turno es TURNO-XYZ789. Tienes tu cita con la Dra. Karina Perez el lunes 16 de febrero a las 11 de la mañana en nuestra sede de Palermo. ¿Hay algo más en lo que pueda ayudarte?"
```

### Test 3: Verificar en DynamoDB

```bash
aws dynamodb scan --table-name salud-api-stack-TurnosTable-1LLEZVIWYG3RI --region us-east-1 --max-items 10
```

Debe aparecer el turno recién creado con:
- nombrePaciente: "Marta Pini" (o el nombre que usaste)
- fechaTurno: "2026-02-16"
- horaTurno: "11:00"
- estado: "confirmado"

### Test 4: Verificar en Logs

```bash
aws logs tail /aws/apigateway/salud-api-stack --since 5m --filter-pattern "POST /turnos" --region us-east-1
```

Debe aparecer un POST /turnos con status 201.

---

## ⚠️ Errores Comunes

### Error: "Each variable may only appear once"

**Causa:** Copiaste el prompt viejo que tenía variables duplicadas

**Solución:** Asegúrate de copiar el archivo `luna-agent-prompt-MEJORADO-v2.yaml` (v2, no v1)

### Error: El agente sigue sin ejecutar el tool

**Causa:** No hiciste Unpublish/Publish después de guardar

**Solución:**
1. Unpublish del agente
2. Esperar 15 segundos
3. Publish
4. Probar nuevamente

### Error: El agente ejecuta el tool pero no confirma

**Causa:** El prompt se actualizó pero falta la sección de confirmación

**Solución:**
1. Verificar que el prompt tenga `<appointment_confirmation_instructions>`
2. Verificar que la sección `<instructions>` final tenga la línea:
```yaml
CRITICAL: After completing any appointment action (create, modify, cancel), ALWAYS confirm the action was successful, provide relevant details (like turnoId), and ask if the patient needs anything else. NEVER end the conversation abruptly.
```

---

## 📋 Checklist Completo

Antes de probar:

- [ ] Abrí el archivo `luna-agent-prompt-MEJORADO-v2.yaml`
- [ ] Copié TODO el contenido del archivo
- [ ] Fui a Amazon Connect → AI agents → Luna → Edit
- [ ] Reemplacé el prompt completo
- [ ] Guardé los cambios
- [ ] Esperé a que aparezca el mensaje de confirmación
- [ ] Hice Unpublish del agente
- [ ] Esperé 15 segundos
- [ ] Hice Publish del agente
- [ ] Verifiqué que el estado sea "Active"

Después de probar:

- [ ] El agente ejecuta el tool crearTurno
- [ ] El turno aparece en DynamoDB
- [ ] El agente confirma con el turnoId
- [ ] El agente pregunta si necesito algo más
- [ ] La conversación NO se cierra abruptamente

---

## 🔍 Diagnóstico si Sigue Fallando

Si después de seguir todos los pasos el agente sigue sin ejecutar el tool:

### 1. Verificar Tool Safety Status

```
Amazon Connect → AI agents → Luna → Tools → salud_api__crearTurno
Tool Safety Status debe ser: "Destructive"
```

Si está en "Unspecified", revisar `SOLUCION-TOOL-SAFETY-STATUS.md`

### 2. Verificar User Confirmation

```
Amazon Connect → AI agents → Luna → Tools → salud_api__crearTurno
"Require user confirmation before tool invocation" debe estar: DESACTIVADO
```

### 3. Ver Logs del Agente

```bash
aws logs tail /aws/connect/[instance-id] --since 30m --follow
```

Buscar errores de tool execution o validación de schema.

### 4. Ver Logs del Gateway

```bash
aws logs tail /aws/lambda/gateway_salud-mcp-server --since 30m --follow
```

Buscar errores al generar los tools desde el OpenAPI.

---

## ⏱️ Tiempo Estimado

- Copiar prompt: 1 minuto
- Actualizar en Amazon Connect: 3 minutos
- Unpublish/Publish: 1 minuto
- Test de validación: 5 minutos

**Total:** ~10 minutos

---

## 🎉 Resultado Esperado

Después de actualizar el prompt:

✅ El agente ejecuta el tool `salud_api__crearTurno`  
✅ El turno se crea en DynamoDB  
✅ El agente confirma con el turnoId  
✅ El agente proporciona detalles del turno  
✅ El agente pregunta si necesita algo más  
✅ La conversación NO se cierra abruptamente  

---

## 📞 Soporte

Si después de seguir todos los pasos sigue sin funcionar:

1. Compartir captura de pantalla del prompt en Amazon Connect
2. Compartir el Contact ID de la conversación fallida
3. Compartir los logs del agente
4. Verificar que el OpenAPI tenga `x-amazon-connect-tool-safety: destructive`

---

**Preparado por:** Kiro AI Assistant  
**Fecha:** 2 de Febrero de 2026  
**Versión:** 1.0
