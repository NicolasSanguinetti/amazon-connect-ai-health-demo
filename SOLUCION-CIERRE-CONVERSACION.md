# 🔧 Solución: Agente Cierra Conversación Abruptamente

**Fecha:** 2 de Febrero de 2026  
**Problema:** El agente crea el turno correctamente pero no confirma y cierra la conversación

---

## 🎯 Problema Identificado

**Síntomas:**
- ✅ El turno SE crea correctamente en DynamoDB
- ✅ El tool `salud_api__crearTurno` SE ejecuta
- ❌ El agente NO confirma que el turno se creó
- ❌ El agente NO proporciona el turnoId
- ❌ El agente NO pregunta si necesita algo más
- ❌ La conversación se cierra abruptamente

**Ejemplo de conversación:**
```
Cliente: "si si esta perfecto"
BOT: "Excelente, voy a confirmar tu turno ahora."
[El turno se crea en DynamoDB]
El chat finalizó. ❌ (Sin confirmación)
```

---

## 🔍 Causa Raíz

El **prompt del agente Luna** no tiene instrucciones específicas sobre qué hacer **después de ejecutar el tool de crear turno**.

El prompt actual tiene:
- ✅ Instrucciones generales de comportamiento
- ✅ Instrucciones de manejo de fechas
- ✅ Instrucciones de seguridad
- ❌ NO tiene instrucciones de confirmación post-acción

---

## ✅ Solución

Agregar una sección específica en el prompt con instrucciones de confirmación:

```yaml
<appointment_confirmation_instructions>
CRITICAL: After successfully creating or modifying an appointment, you MUST:

1. CONFIRM the action was successful
2. PROVIDE the turnoId (appointment ID) to the patient
3. SUMMARIZE the appointment details (doctor, date, time, location)
4. ASK if they need anything else

Example - After creating appointment:
<message>
¡Perfecto! Tu turno ha sido confirmado exitosamente. Tu número de turno es TURNO-ABC123. Tienes tu cita con el Dr. Juan Pérez el lunes 3 de febrero a las 10 de la mañana en nuestra sede de Palermo. ¿Hay algo más en lo que pueda ayudarte?
</message>

NEVER end the conversation abruptly after completing an action. ALWAYS ask if the patient needs additional help.
</appointment_confirmation_instructions>
```

---

## 📄 Archivo Actualizado

**Archivo creado:** `documentos_salud_connect_ia/luna-agent-prompt-MEJORADO-v2.yaml`

**Cambios aplicados:**
1. ✅ Agregada sección `<appointment_confirmation_instructions>`
2. ✅ Ejemplos específicos para crear, modificar y cancelar turnos
3. ✅ Instrucción explícita de NUNCA cerrar abruptamente
4. ✅ Instrucción de SIEMPRE preguntar si necesita algo más
5. ✅ Agregada instrucción CRITICAL en la sección `<instructions>` final

---

## 🚀 Pasos para Aplicar la Solución

### Paso 1: Subir el Prompt Actualizado

El prompt actualizado está en:
```
documentos_salud_connect_ia/luna-agent-prompt-MEJORADO-v2.yaml
```

### Paso 2: Actualizar el Agente Luna en Amazon Connect

```
1. Ir a: Amazon Connect → AI agents → Luna
2. Click en "Edit"
3. Ir a la sección "Instructions" o "Prompt"
4. Reemplazar el prompt actual con el contenido de luna-agent-prompt-MEJORADO-v2.yaml
5. Click en "Save"
```

### Paso 3: Unpublish/Publish del Agente

```
1. Click en "Unpublish"
2. ESPERAR 15 SEGUNDOS
3. Click en "Publish"
4. Verificar estado: "Active"
```

### Paso 4: Test de Validación

1. Iniciar una conversación con el agente
2. Solicitar un turno
3. Confirmar la creación

**Resultado esperado:**
```
Cliente: "si si esta perfecto"
BOT: "Excelente, voy a confirmar tu turno ahora."
[El turno se crea en DynamoDB]
BOT: "¡Perfecto! Tu turno ha sido confirmado exitosamente. Tu número de turno es TURNO-XYZ789. Tienes tu cita con la Dra. María González el viernes 6 de febrero a las 11 de la mañana en nuestra sede de Palermo. ¿Hay algo más en lo que pueda ayudarte?"
```

---

## 📊 Comparación Antes vs Después

### Antes (Prompt Original)
```yaml
<instructions>
You're Luna, the warm AI medical assistant. The patient has already been greeted in the contact flow, so DO NOT greet them again. Start directly by understanding their needs and helping them book appointments with excellent medical professionals. Keep it caring, friendly, and natural. Use your tools to assist patients efficiently. Always respond in the configured locale language.
</instructions>
```

**Problema:** No hay instrucciones sobre qué hacer después de crear un turno.

### Después (Prompt Mejorado v2)
```yaml
<appointment_confirmation_instructions>
CRITICAL: After successfully creating or modifying an appointment, you MUST:
1. CONFIRM the action was successful
2. PROVIDE the turnoId (appointment ID) to the patient
3. SUMMARIZE the appointment details
4. ASK if they need anything else

NEVER end the conversation abruptly after completing an action.
</appointment_confirmation_instructions>

<instructions>
You're Luna, the warm AI medical assistant. The patient has already been greeted in the contact flow, so DO NOT greet them again. Start directly by understanding their needs and helping them book appointments with excellent medical professionals. Keep it caring, friendly, and natural. Use your tools to assist patients efficiently. Always respond in the configured locale language.

CRITICAL: After completing any appointment action (create, modify, cancel), ALWAYS confirm the action was successful, provide relevant details (like turnoId), and ask if the patient needs anything else. NEVER end the conversation abruptly.
</instructions>
```

**Solución:** Instrucciones explícitas con ejemplos y recordatorio en la sección final.

---

## 🧪 Validación

### Test 1: Crear Turno
```
Usuario: "Quiero sacar un turno con un cardiólogo"
Agente: [Busca médicos]
Usuario: "Con la Dra. María González el viernes 6 de febrero a las 11am"
Agente: [Solicita datos]
Usuario: "Pablo Imanof, pablo@gmail.com, 45452323"
Agente: "¿Confirmas que quieres crear este turno?"
Usuario: "Sí, perfecto"
Agente: ✅ "¡Perfecto! Tu turno ha sido confirmado exitosamente. Tu número de turno es TURNO-ABC123. Tienes tu cita con la Dra. María González el viernes 6 de febrero a las 11 de la mañana en nuestra sede de Palermo. ¿Hay algo más en lo que pueda ayudarte?"
```

### Test 2: Modificar Turno
```
Usuario: "Quiero cambiar mi turno para el próximo miércoles a las 3pm"
Agente: [Modifica el turno]
Agente: ✅ "¡Listo! He modificado tu turno exitosamente. Tu nuevo turno es para el miércoles 12 de febrero a las 3 de la tarde. Tu número de turno sigue siendo TURNO-ABC123. ¿Necesitas algo más?"
```

### Test 3: Cancelar Turno
```
Usuario: "Necesito cancelar mi turno"
Agente: "¿Confirmas que quieres cancelar tu turno?"
Usuario: "Sí"
Agente: ✅ "Tu turno ha sido cancelado correctamente. Si necesitas agendar uno nuevo en el futuro, estaré encantada de ayudarte. ¿Hay algo más que pueda hacer por ti hoy?"
```

---

## 📋 Checklist de Implementación

- [ ] Revisar el prompt actualizado (luna-agent-prompt-MEJORADO-v2.yaml)
- [ ] Copiar el contenido del prompt
- [ ] Ir a Amazon Connect → AI agents → Luna → Edit
- [ ] Reemplazar el prompt en la sección "Instructions"
- [ ] Guardar cambios
- [ ] Unpublish del agente
- [ ] Esperar 15 segundos
- [ ] Publish del agente
- [ ] Test de creación de turno
- [ ] Verificar que confirma con turnoId
- [ ] Verificar que pregunta si necesita algo más
- [ ] Verificar que NO cierra abruptamente

---

## 🔍 Troubleshooting

### El agente sigue cerrando abruptamente

**Posibles causas:**
1. El prompt no se actualizó correctamente
2. No se hizo Unpublish/Publish
3. Hay una configuración de timeout en el contact flow

**Solución:**
1. Verificar que el prompt en Amazon Connect tenga la sección `<appointment_confirmation_instructions>`
2. Hacer Unpublish/Publish nuevamente
3. Revisar el contact flow para ver si hay un timeout configurado

### El agente confirma pero no proporciona el turnoId

**Causa:** El tool no está retornando el turnoId en la respuesta

**Solución:**
1. Verificar los logs de la lambda CreateTurnoFunction
2. Verificar que la respuesta incluya el campo `turnoId`
3. Actualizar el OpenAPI para documentar el campo `turnoId` en la respuesta

---

## 📚 Documentación Relacionada

- **Prompt original:** `documentos_salud_connect_ia/luna-agent-prompt-mejorado.yaml`
- **Prompt actualizado:** `documentos_salud_connect_ia/luna-agent-prompt-MEJORADO-v2.yaml`
- **Guía de AgentCore:** `GUIA-AGENTCORE-GATEWAY.md`
- **FAQ Tool Safety:** `FAQ-TOOL-SAFETY-STATUS.md`

---

## ⏱️ Tiempo Estimado

- Copiar prompt: 2 minutos
- Actualizar en Amazon Connect: 3 minutos
- Unpublish/Publish: 1 minuto
- Test de validación: 5 minutos

**Total:** ~10 minutos

---

**Preparado por:** Kiro AI Assistant  
**Fecha:** 2 de Febrero de 2026  
**Versión:** 1.0
