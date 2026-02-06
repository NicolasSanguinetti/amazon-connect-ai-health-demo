# 📅 Mejoras en el Manejo de Fechas Relativas

**Fecha:** 2 de Febrero de 2026  
**Versión del Prompt:** v2.1 (Mejorado)

---

## 🎯 Problema Original

El agente tenía instrucciones básicas para manejar fechas, pero le faltaban:
- ❌ Ejemplos específicos para "semana próxima"
- ❌ Instrucciones para expresiones en español
- ❌ Proceso paso a paso de cálculo de fechas
- ❌ Ejemplos de conversaciones completas

---

## ✅ Mejoras Implementadas

### 1. Proceso Paso a Paso de Cálculo

Agregado un proceso claro de 5 pasos:

```yaml
6. STEP-BY-STEP DATE CALCULATION PROCESS:
   a) Get current date from {{$.dateTime}}
   b) Identify what the user is asking for
   c) Calculate the exact date
   d) Format as YYYY-MM-DD
   e) Use this calculated date in the tool call
```

### 2. Ejemplos Extendidos de Cálculo de Fechas

Agregados ejemplos específicos con fecha actual de referencia:

```yaml
Examples of date calculations:
- Current date: 2026-02-02 (Sunday)
- User says "tomorrow" → Calculate: 2026-02-03 (Monday)
- User says "next Monday" → Calculate: 2026-02-09 (next Monday, not tomorrow)
- User says "next Wednesday" → Calculate: 2026-02-04 or 2026-02-11
- User says "next week" or "semana próxima" → Calculate: 2026-02-09 to 2026-02-15
- User says "próximo miércoles" → Calculate: 2026-02-04 or 2026-02-11
- User says "el viernes" → Calculate: 2026-02-06 or 2026-02-13
```

### 3. Expresiones Comunes en Español

Agregado un diccionario de expresiones:

```yaml
Common Spanish date expressions:
- "mañana" → tomorrow
- "pasado mañana" → day after tomorrow
- "la semana que viene" / "semana próxima" → next week
- "el próximo [día]" → next [day]
- "este [día]" → this [day] (this week)
- "dentro de una semana" → one week from today
- "dentro de dos semanas" → two weeks from today
```

### 4. Ejemplos de Conversaciones Completas

Agregada una nueva sección con 4 ejemplos de conversaciones:

#### Ejemplo 1: "Semana próxima"
```
User: "Quiero un turno para la semana próxima"
Agent: "Perfecto, puedo ayudarte con eso. ¿Qué día de la semana próxima prefieres?"
User: "El miércoles"
Agent: [Calcula: 2026-02-11]
Agent: "Excelente, entonces sería el miércoles 11 de febrero. ¿A qué hora?"
```

#### Ejemplo 2: "Próximo viernes"
```
User: "Necesito cambiar mi turno para el próximo viernes"
Agent: [Calcula: 2026-02-06]
Agent: "Perfecto, voy a cambiar tu turno para el viernes 6 de febrero. ¿A qué hora?"
```

#### Ejemplo 3: "Mañana"
```
User: "Quiero un turno para mañana a las 3 de la tarde"
Agent: [Calcula: 2026-02-03 at 15:00]
Agent: "Entendido, busco disponibilidad para mañana lunes 3 de febrero a las 3 de la tarde."
```

#### Ejemplo 4: "Dentro de dos semanas"
```
User: "Prefiero un turno dentro de dos semanas"
Agent: [Calcula: 2026-02-16]
Agent: "Perfecto, eso sería alrededor del 16 de febrero. ¿Qué día de esa semana prefieres?"
```

### 5. Instrucción de Usar <thinking> para Cálculos

Agregada instrucción crítica:

```yaml
CRITICAL: Always show your date calculation in <thinking> tags to ensure accuracy.
```

Esto hace que el agente muestre su razonamiento:

```yaml
<thinking>
Current date from system: 2026-02-02 (Sunday)
User wants "next week Wednesday"
Next week starts on 2026-02-09 (Monday)
Wednesday of next week is 2026-02-11
</thinking>
```

---

## 📊 Comparación Antes vs Después

### Antes (Prompt v2.0)
```yaml
Examples:
- User says "next Monday" → Calculate exact date: "2026-02-03"
- User says "3 PM" → Convert to 24-hour: "15:00"
- User says "tomorrow at 10 in the morning" → "2026-01-31" at "10:00"
```

**Limitaciones:**
- Solo 3 ejemplos básicos
- No cubre "semana próxima"
- No tiene expresiones en español
- No muestra el proceso de cálculo

### Después (Prompt v2.1)
```yaml
6. STEP-BY-STEP DATE CALCULATION PROCESS:
   [5 pasos claros]

Examples of date calculations:
   [10+ ejemplos con contexto]

Common Spanish date expressions:
   [7 expresiones comunes]

<date_handling_conversation_examples>
   [4 conversaciones completas con <thinking>]
```

**Mejoras:**
- ✅ Proceso paso a paso
- ✅ 10+ ejemplos con contexto
- ✅ Expresiones en español
- ✅ Conversaciones completas
- ✅ Uso de <thinking> para transparencia

---

## 🧪 Casos de Prueba

### Test 1: "Semana próxima"
```
Input: "Quiero un turno para la semana próxima"
Expected: Agente pregunta qué día específico
Expected: Calcula fecha correcta (2026-02-09 a 2026-02-15)
```

### Test 2: "Próximo miércoles"
```
Input: "Necesito cambiar mi turno para el próximo miércoles"
Expected: Agente calcula 2026-02-04 o 2026-02-11 (según día actual)
Expected: Confirma fecha calculada con el usuario
```

### Test 3: "Mañana a las 3 de la tarde"
```
Input: "Quiero un turno para mañana a las 3 de la tarde"
Expected: Agente calcula fecha de mañana (2026-02-03)
Expected: Agente convierte "3 de la tarde" a "15:00"
Expected: Usa fecha="2026-02-03" y hora="15:00" en el tool
```

### Test 4: "Dentro de dos semanas"
```
Input: "Prefiero un turno dentro de dos semanas"
Expected: Agente calcula fecha +14 días (2026-02-16)
Expected: Agente pregunta qué día de esa semana prefiere
```

### Test 5: "Pasado mañana"
```
Input: "Quiero un turno para pasado mañana"
Expected: Agente calcula fecha +2 días (2026-02-04)
Expected: Confirma fecha calculada
```

---

## 📋 Checklist de Validación

Después de actualizar el prompt, verificar:

- [ ] El agente calcula fechas exactas (no usa términos relativos)
- [ ] El agente usa formato ISO (YYYY-MM-DD)
- [ ] El agente usa formato 24h (HH:MM)
- [ ] El agente pregunta día específico cuando dice "semana próxima"
- [ ] El agente muestra su cálculo en <thinking>
- [ ] El agente confirma la fecha calculada con el usuario
- [ ] El agente maneja expresiones en español correctamente
- [ ] La fecha en DynamoDB es la correcta

---

## 🔍 Troubleshooting

### El agente sigue usando fechas relativas

**Causa:** El prompt no se actualizó correctamente

**Solución:**
1. Verificar que el prompt tenga la sección `<date_and_time_handling>` completa
2. Verificar que tenga la sección `<date_handling_conversation_examples>`
3. Hacer Unpublish/Publish del agente

### El agente calcula fechas incorrectas

**Causa:** No está usando {{$.dateTime}} correctamente

**Solución:**
1. Verificar que {{$.dateTime}} esté disponible en system_variables
2. Revisar los logs del agente para ver qué fecha está usando
3. Agregar más ejemplos en el prompt

### El agente no pregunta día específico para "semana próxima"

**Causa:** Falta la instrucción específica

**Solución:**
1. Verificar que el prompt tenga:
```yaml
IMPORTANT: When user says "next week" or "semana próxima" without specifying a day:
- Ask which day of next week they prefer
```

---

## 📚 Archivos Actualizados

1. **documentos_salud_connect_ia/luna-agent-prompt-MEJORADO-v2.yaml**
   - Sección `<date_and_time_handling>` expandida
   - Nueva sección `<date_handling_conversation_examples>`
   - Proceso paso a paso de cálculo
   - Expresiones en español
   - 4 ejemplos de conversaciones completas

---

## 🚀 Próximos Pasos

1. Revisar el prompt actualizado
2. Copiar el contenido completo
3. Ir a Amazon Connect → AI agents → Luna → Edit
4. Reemplazar el prompt
5. Guardar cambios
6. Unpublish → Esperar 15s → Publish
7. Probar con diferentes expresiones de fecha:
   - "semana próxima"
   - "próximo miércoles"
   - "mañana a las 3"
   - "dentro de dos semanas"
   - "pasado mañana"

---

## ⏱️ Tiempo Estimado

- Revisar prompt: 5 minutos
- Actualizar en Amazon Connect: 3 minutos
- Unpublish/Publish: 1 minuto
- Tests de validación: 10 minutos

**Total:** ~20 minutos

---

## 🎉 Resultado Esperado

Después de aplicar estas mejoras:

✅ El agente entiende "semana próxima" y pregunta qué día  
✅ El agente calcula fechas exactas para todas las expresiones  
✅ El agente usa formato ISO (YYYY-MM-DD) en los tools  
✅ El agente confirma las fechas calculadas con el usuario  
✅ Las fechas en DynamoDB son correctas  
✅ El agente maneja expresiones en español naturalmente  

---

**Preparado por:** Kiro AI Assistant  
**Fecha:** 2 de Febrero de 2026  
**Versión:** 2.1
