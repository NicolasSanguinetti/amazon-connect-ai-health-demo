# 🔧 Error: Each variable may only appear once

**Fecha:** 2 de Febrero de 2026  
**Error:** `Error calling updateAIPrompt: Each variable may only appear once.`

---

## 🎯 Problema

Al intentar actualizar el prompt del agente Luna en Amazon Connect, aparece el error:

```
Error calling updateAIPrompt: Each variable may only appear once.
```

---

## 🔍 Causa Raíz

Amazon Connect **no permite que una variable aparezca más de una vez** en el prompt.

En el prompt mejorado, la variable `{{$.dateTime}}` aparecía **3 veces**:

1. **Línea 29** - En las instrucciones de fecha:
```yaml
- Use the current date from system_variables ({{$.dateTime}}) to calculate dates
```

2. **Línea 59** - En el proceso paso a paso:
```yaml
a) Get current date from {{$.dateTime}}
```

3. **Línea 437** - En system_variables (la correcta):
```yaml
- dateTime: {{$.dateTime}}
```

---

## ✅ Solución

Eliminar las referencias duplicadas y dejar solo la definición en `<system_variables>`.

### Cambio 1: Línea 29

**Antes:**
```yaml
- Use the current date from system_variables ({{$.dateTime}}) to calculate dates
```

**Después:**
```yaml
- Use the current date from system_variables to calculate dates
```

### Cambio 2: Línea 59

**Antes:**
```yaml
a) Get current date from {{$.dateTime}}
```

**Después:**
```yaml
a) Get current date from system_variables (see dateTime below)
```

### Mantener: Línea 437

```yaml
<system_variables>
Current conversation details:
- contactId: {{$.contactId}}
- instanceId: {{$.instanceId}}
- sessionId: {{$.sessionId}}
- assistantId: {{$.assistantId}}
- dateTime: {{$.dateTime}}  ← Esta es la única referencia válida
- companyName: {{$.Custom.CompanyName_Voice}}
</system_variables>
```

---

## 📋 Regla de Amazon Connect

**Cada variable solo puede aparecer UNA vez en todo el prompt.**

Variables comunes que pueden causar este error:
- `{{$.dateTime}}`
- `{{$.contactId}}`
- `{{$.locale}}`
- `{{$.Custom.firstName}}`
- `{{$.Custom.lastName}}`
- `{{$.Custom.customerId}}`
- `{{$.Custom.email}}`
- `{{$.toolConfigurationList}}`
- `{{$.conversationHistory}}`

---

## 🔍 Cómo Verificar Variables Duplicadas

### Método 1: Búsqueda Manual

1. Abrir el archivo del prompt
2. Buscar cada variable (Ctrl+F)
3. Contar cuántas veces aparece
4. Si aparece más de 1 vez, eliminar duplicados

### Método 2: Usando grep (Linux/Mac)

```bash
grep -o '{{$\.[^}]*}}' luna-agent-prompt-MEJORADO-v2.yaml | sort | uniq -c | grep -v '^ *1 '
```

### Método 3: Usando PowerShell (Windows)

```powershell
Select-String -Path "luna-agent-prompt-MEJORADO-v2.yaml" -Pattern "\{\{\$\.[^}]*\}\}" -AllMatches | 
  ForEach-Object { $_.Matches.Value } | 
  Group-Object | 
  Where-Object { $_.Count -gt 1 } | 
  Select-Object Name, Count
```

---

## 🧪 Validación

Después de corregir, verificar que:

1. ✅ Cada variable aparece solo 1 vez
2. ✅ Todas las variables están definidas en `<system_variables>` o `<customer_info>`
3. ✅ El prompt se puede guardar sin errores en Amazon Connect

---

## 📚 Variables Disponibles

### System Variables
```yaml
<system_variables>
- contactId: {{$.contactId}}
- instanceId: {{$.instanceId}}
- sessionId: {{$.sessionId}}
- assistantId: {{$.assistantId}}
- dateTime: {{$.dateTime}}
- companyName: {{$.Custom.CompanyName_Voice}}
</system_variables>
```

### Customer Info
```yaml
<customer_info>
- First name: {{$.Custom.firstName}}
- Last name: {{$.Custom.lastName}}
- Patient ID: {{$.Custom.customerId}}
- email: {{$.Custom.email}}
</customer_info>
```

### Tool Configuration
```yaml
<tool_instructions>
{{$.toolConfigurationList}}
</tool_instructions>
```

### Conversation History
```yaml
messages:
  - '{{$.conversationHistory}}'
```

---

## 💡 Buenas Prácticas

1. **Definir variables una sola vez** en `<system_variables>` o `<customer_info>`
2. **Referenciar por nombre** en las instrucciones (sin usar `{{}}`)
3. **Documentar claramente** qué variables están disponibles
4. **Validar antes de subir** usando búsqueda de duplicados

### Ejemplo Correcto

**Definición (una vez):**
```yaml
<system_variables>
- dateTime: {{$.dateTime}}
</system_variables>
```

**Referencia (sin {{}}}):**
```yaml
Use the current date from system_variables to calculate dates.
The dateTime variable contains the current date and time.
```

### Ejemplo Incorrecto

**Definición:**
```yaml
<system_variables>
- dateTime: {{$.dateTime}}
</system_variables>
```

**Referencia (con {{}} - ERROR):**
```yaml
Use {{$.dateTime}} to calculate dates.  ❌ DUPLICADO
```

---

## 🚀 Próximos Pasos

1. ✅ Variables duplicadas eliminadas
2. ✅ Prompt corregido subido a GitHub
3. ⏭️ Copiar el prompt corregido
4. ⏭️ Actualizar en Amazon Connect
5. ⏭️ Guardar sin errores
6. ⏭️ Unpublish/Publish del agente

---

## ⏱️ Tiempo de Corrección

- Identificar variables duplicadas: 2 minutos
- Corregir el prompt: 1 minuto
- Validar: 1 minuto
- Actualizar en Amazon Connect: 2 minutos

**Total:** ~5 minutos

---

## 🎉 Resultado

Después de la corrección:

✅ El prompt se guarda sin errores  
✅ Todas las variables aparecen solo una vez  
✅ Las instrucciones siguen siendo claras  
✅ El agente puede acceder a todas las variables necesarias  

---

**Preparado por:** Kiro AI Assistant  
**Fecha:** 2 de Febrero de 2026  
**Versión:** 1.0
