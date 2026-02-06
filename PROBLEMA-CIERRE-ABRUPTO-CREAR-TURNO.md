# Problema: Agente cierra conversación después de crear turno

## Fecha
2026-02-02

## Problema Reportado
El agente Luna crea turnos correctamente en DynamoDB pero NO confirma al paciente y cierra la conversación abruptamente sin preguntar si necesita algo más.

### Comportamiento Observado
- ✅ **Modificar turno**: Confirma y pregunta si necesita algo más
- ✅ **Cancelar turno**: Confirma y pregunta si necesita algo más  
- ❌ **Crear turno**: NO confirma y cierra la conversación

### Ejemplo de Conversación Problemática
```
User: "quiero reservar un turno"
Bot: [Busca médicos, pide datos, etc.]
User: "mancha en la piel"
Bot: [Ejecuta crearTurno tool]
[El chat finalizó] ❌ <- PROBLEMA: No confirma ni pregunta si necesita algo más
```

## Causa Raíz Identificada

El prompt tenía instrucciones de confirmación pero **NO tenía ejemplos completos de conversación** que mostraran el flujo completo de crear un turno.

Los LLMs aprenden mejor con ejemplos concretos. Sin ejemplos completos que muestren:
1. Cómo ejecutar el tool
2. Cómo procesar la respuesta del tool
3. Cómo confirmar con el turnoId
4. Cómo preguntar si necesita algo más

El agente no sabía exactamente qué hacer después de ejecutar el tool `crearTurno`.

## Soluciones Implementadas

### 1. Schema de Respuesta en OpenAPI (Implementado anteriormente)
Agregado schema completo de respuesta 201 para POST /turnos:
```yaml
responses:
  '201':
    description: Turno creado exitosamente
    content:
      application/json:
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Turno creado exitosamente
            turnoId:
              type: string
              example: TURNO-ABC123
            reservation:
              type: object
              description: Detalles completos del turno creado
```

### 2. Ejemplos Completos de Conversación (Implementado HOY)
Agregada nueva sección `<complete_conversation_examples>` al prompt con 3 ejemplos completos:

#### Ejemplo 1: Crear Turno (FLUJO COMPLETO)
- Muestra cómo buscar médicos
- Muestra cómo recopilar datos del paciente
- Muestra cómo ejecutar el tool `crearTurno`
- **Muestra cómo confirmar con el turnoId**
- **Muestra cómo preguntar si necesita algo más**

#### Ejemplo 2: Modificar Turno (FLUJO COMPLETO)
- Muestra cómo buscar turnos existentes
- Muestra cómo ejecutar el tool `modificarTurno`
- Muestra cómo confirmar la modificación
- Muestra cómo preguntar si necesita algo más

#### Ejemplo 3: Cancelar Turno (FLUJO COMPLETO)
- Muestra cómo buscar turnos existentes
- Muestra cómo pedir confirmación antes de cancelar
- Muestra cómo ejecutar el tool `cancelarTurno`
- Muestra cómo confirmar la cancelación
- Muestra cómo preguntar si necesita algo más

### Lecciones Críticas Incluidas en los Ejemplos
```yaml
CRITICAL LESSONS FROM THESE EXAMPLES:
1. ALWAYS confirm after tool execution with the turnoId
2. ALWAYS summarize the appointment details
3. ALWAYS ask if they need anything else
4. NEVER end the conversation abruptly after creating/modifying/canceling
5. ALWAYS use exact dates (YYYY-MM-DD) and times (HH:MM) in tool calls
6. ALWAYS show date calculation in <thinking> tags
```

## Archivos Modificados
- `documentos_salud_connect_ia/luna-agent-prompt-MEJORADO-v2.yaml`
  - Agregada sección `<complete_conversation_examples>` con 3 ejemplos completos
  - 195 líneas agregadas

## Próximos Pasos

### 1. Actualizar el Prompt en Amazon Connect
```bash
# El prompt ya está actualizado en GitHub
# Ahora debes copiarlo a Amazon Connect
```

**Pasos en la consola de Amazon Connect:**
1. Ir a Amazon Connect → Amazon Bedrock → Agents
2. Seleccionar el agente "Luna"
3. Click en "Edit"
4. Ir a la sección "Advanced prompts"
5. Click en "Edit" en "Orchestration"
6. Reemplazar el prompt completo con el contenido de `luna-agent-prompt-MEJORADO-v2.yaml`
7. Click en "Save and exit"
8. **Unpublish** el agente (si está publicado)
9. **Publish** el agente nuevamente
10. Esperar 15 segundos para que se propague

### 2. Probar la Solución
Crear un turno nuevo y verificar que:
- ✅ El turno se crea en DynamoDB
- ✅ El agente confirma con el turnoId
- ✅ El agente resume los detalles del turno
- ✅ El agente pregunta si necesita algo más
- ✅ La conversación NO se cierra abruptamente

### 3. Ejemplo de Conversación Esperada
```
User: "quiero reservar un turno"
Bot: "¡Hola! Claro que sí, con gusto te ayudo a reservar un turno. ¿Qué especialidad médica necesitas?"
User: "Dermatología"
Bot: [Busca médicos y muestra opciones]
User: "con carlos"
Bot: [Pide datos: fecha, hora, nombre, email, DNI/afiliado, teléfono, motivo]
User: "mancha en la piel"
Bot: [Ejecuta crearTurno tool]
Bot: "¡Perfecto! Tu turno ha sido confirmado exitosamente. Tu número de turno es TURNO-2026-02-06-ABC123. Tienes tu cita con el Dr. Carlos Rodríguez el jueves 6 de febrero a las 10:30 en Palermo. ¿Hay algo más en lo que pueda ayudarte?" ✅
User: "No, gracias"
Bot: "¡Perfecto! Nos vemos el jueves. Que tengas un excelente día."
```

## Diferencia Clave

### ANTES (Sin ejemplos completos)
```
Bot: [Ejecuta crearTurno tool]
[El chat finalizó] ❌
```

### DESPUÉS (Con ejemplos completos)
```
Bot: [Ejecuta crearTurno tool]
Bot: "¡Perfecto! Tu turno ha sido confirmado exitosamente. Tu número de turno es TURNO-2026-02-06-ABC123. Tienes tu cita con el Dr. Carlos Rodríguez el jueves 6 de febrero a las 10:30 en Palermo. ¿Hay algo más en lo que pueda ayudarte?" ✅
```

## Notas Técnicas

### Por qué los ejemplos son críticos
Los LLMs aprenden por imitación. Sin ejemplos concretos que muestren el flujo completo:
- El agente no sabe qué hacer con la respuesta del tool
- El agente no sabe cómo extraer el turnoId de la respuesta
- El agente no sabe que debe confirmar antes de terminar
- El agente puede asumir que ejecutar el tool es suficiente

Con ejemplos completos:
- El agente ve exactamente cómo procesar la respuesta
- El agente ve cómo extraer y usar el turnoId
- El agente ve que SIEMPRE debe confirmar y preguntar si necesita algo más
- El agente aprende el patrón completo de inicio a fin

### Instrucciones vs Ejemplos
- **Instrucciones**: "ALWAYS confirm after tool execution" → El agente entiende la regla
- **Ejemplos**: Muestra el flujo completo → El agente ve CÓMO aplicar la regla

Ambos son necesarios, pero los ejemplos son más poderosos para comportamientos complejos.

## Historial de Cambios

### 2026-02-02 - Solución Implementada
- Agregados 3 ejemplos completos de conversación al prompt
- Cada ejemplo muestra el flujo completo de inicio a fin
- Incluye lecciones críticas explícitas
- Cambios commiteados y subidos a GitHub

### 2026-02-01 - Primera Solución (Parcial)
- Agregado schema de respuesta al OpenAPI
- Agregadas instrucciones de confirmación al prompt
- Resultado: Mejoró pero no resolvió completamente el problema

## Referencias
- Archivo del prompt: `documentos_salud_connect_ia/luna-agent-prompt-MEJORADO-v2.yaml`
- Archivo del OpenAPI: `documentos_salud_connect_ia/turnos-medicos-api-openapi-CORREGIDO.yaml`
- Guía de actualización: `PASOS-ACTUALIZAR-PROMPT.md`
