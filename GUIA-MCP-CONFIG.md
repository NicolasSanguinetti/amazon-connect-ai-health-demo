# 🔍 Guía: Cómo Encontrar la Configuración del MCP Server en Amazon Connect

**Fecha:** 2 de Febrero de 2026  
**Objetivo:** Localizar y actualizar la URL del OpenAPI en el MCP Server del agente Luna

---

## 📍 Paso a Paso con Capturas Visuales

### Paso 1: Acceder a Amazon Connect Console

1. Ir a: **https://console.aws.amazon.com/connect/**
2. Verás una lista de tus instancias de Amazon Connect
3. Click en el **nombre de tu instancia** (no en "Access URL")

```
┌─────────────────────────────────────────────┐
│ Amazon Connect Instances                    │
├─────────────────────────────────────────────┤
│ Instance Name          | Access URL         │
│ ✓ tu-instancia-connect | https://...       │  ← Click aquí
└─────────────────────────────────────────────┘
```

---

### Paso 2: Navegar a AI Agents

En el menú lateral izquierdo, buscar la sección **"Agent applications"** o **"AI agents"**:

```
┌─────────────────────────┐
│ Amazon Connect          │
├─────────────────────────┤
│ Dashboard               │
│ Routing                 │
│ Users                   │
│ Contact flows           │
│ ▼ Agent applications    │  ← Expandir esta sección
│   • AI agents           │  ← Click aquí
│   • Flows               │
│   • Prompts             │
└─────────────────────────┘
```

**Alternativa:** Si no ves "AI agents", busca:
- **"Amazon Q in Connect"**
- **"Agents"**
- **"Generative AI"**

---

### Paso 3: Seleccionar el Agente Luna

Verás una lista de agentes configurados:

```
┌──────────────────────────────────────────────────┐
│ AI Agents                                        │
├──────────────────────────────────────────────────┤
│ Name    | Status  | Last Modified              │
│ Luna    | Active  | 2026-01-30 14:18:56       │  ← Click aquí
│ Agent2  | Draft   | 2026-01-15 10:30:00       │
└──────────────────────────────────────────────────┘
```

Click en **"Luna"** para abrir la configuración del agente.

---

### Paso 4: Ir a la Sección "Tools"

Dentro de la configuración del agente Luna, verás varias pestañas o secciones:

```
┌────────────────────────────────────────────────────┐
│ Agent: Luna                                        │
├────────────────────────────────────────────────────┤
│ [Overview] [Instructions] [Tools] [Settings]      │
│                              ↑                     │
│                         Click aquí                 │
└────────────────────────────────────────────────────┘
```

Click en la pestaña **"Tools"**.

---

### Paso 5: Localizar el MCP Server

En la sección Tools, verás los servicios/herramientas configuradas:

```
┌──────────────────────────────────────────────────────┐
│ Tools                                                │
├──────────────────────────────────────────────────────┤
│                                                      │
│ ┌──────────────────────────────────────────────┐   │
│ │ MCP Server                                   │   │
│ │ Type: OpenAPI                                │   │
│ │ URL: https://salud-api-stack-openapi...      │   │
│ │                                              │   │
│ │ [Edit] [Remove]                              │   │
│ └──────────────────────────────────────────────┘   │
│                                                      │
│ [+ Add tool]                                         │
└──────────────────────────────────────────────────────┘
```

**Busca:**
- Un bloque que diga **"MCP Server"** o **"OpenAPI"**
- Puede tener un nombre personalizado como **"Turnos API"** o **"Medical Appointments"**
- Verás una URL que apunta a S3 o a un archivo OpenAPI

---

### Paso 6: Editar la Configuración del MCP Server

Click en el botón **"Edit"** o **"Configure"** del MCP Server:

```
┌──────────────────────────────────────────────────────┐
│ Edit MCP Server                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Name: Turnos API                                     │
│ ┌──────────────────────────────────────────────┐   │
│ │ Turnos API                                   │   │
│ └──────────────────────────────────────────────┘   │
│                                                      │
│ OpenAPI Specification URL: *                         │
│ ┌──────────────────────────────────────────────┐   │
│ │ https://salud-api-stack-openapibucket-...    │   │ ← Actualizar aquí
│ └──────────────────────────────────────────────┘   │
│                                                      │
│ API Key (optional):                                  │
│ ┌──────────────────────────────────────────────┐   │
│ │ Y9xhqWXzTuacBXpqjgQvG35HWfDE7roo6P3S4pCm     │   │
│ └──────────────────────────────────────────────┘   │
│                                                      │
│ [Cancel] [Save]                                      │
└──────────────────────────────────────────────────────┘
```

---

### Paso 7: Actualizar la URL del OpenAPI

**URL ACTUAL (probablemente):**
```
https://salud-api-stack-openapibucket-korvxxrkhifa.s3.us-east-1.amazonaws.com/openapi.yaml
```
o
```
https://salud-api-stack-openapibucket-korvxxrkhifa.s3.us-east-1.amazonaws.com/turnos-api.yaml
```

**URL NUEVA (OpenAPI v3 corregido):**
```
https://salud-api-stack-openapibucket-korvxxrkhifa.s3.us-east-1.amazonaws.com/turnos-medicos-api-openapi-v3.yaml
```

**Pasos:**
1. Seleccionar todo el texto en el campo "OpenAPI Specification URL"
2. Borrar
3. Pegar la URL nueva
4. Click en **"Save"**

---

### Paso 8: Forzar Recarga del Caché (CRÍTICO)

Después de guardar, **DEBES** forzar la recarga del caché:

```
┌──────────────────────────────────────────────────────┐
│ Agent: Luna                                          │
├──────────────────────────────────────────────────────┤
│ Status: Active                                       │
│                                                      │
│ [Unpublish] [Edit] [Delete]                         │
│     ↑                                                │
│  Click aquí primero                                  │
└──────────────────────────────────────────────────────┘
```

**Secuencia:**
1. Click en **"Unpublish"**
2. Confirmar la acción
3. **Esperar 10 segundos** (importante para limpiar el caché)
4. Click en **"Publish"**
5. Confirmar la acción
6. Verificar que el estado sea **"Active"**

---

## 🔍 Alternativas para Encontrar la Configuración

### Opción A: Buscar en "Action groups"

Si no ves "Tools", busca **"Action groups"**:

```
┌────────────────────────────────────────────────────┐
│ Agent: Luna                                        │
├────────────────────────────────────────────────────┤
│ [Overview] [Instructions] [Action groups]         │
│                              ↑                     │
│                         Click aquí                 │
└────────────────────────────────────────────────────┘
```

### Opción B: Buscar en "Knowledge bases and tools"

Puede estar en una sección combinada:

```
┌────────────────────────────────────────────────────┐
│ Agent: Luna                                        │
├────────────────────────────────────────────────────┤
│ [Overview] [Instructions] [Knowledge & Tools]     │
│                              ↑                     │
│                         Click aquí                 │
└────────────────────────────────────────────────────┘
```

### Opción C: Buscar en la configuración del Flow

Si el agente está integrado en un Contact Flow:

1. Ir a **"Contact flows"** en el menú lateral
2. Buscar el flow que usa el agente Luna
3. Abrir el flow
4. Buscar el bloque **"Invoke agent"** o **"Get customer input"**
5. Click en el bloque
6. Buscar la configuración del agente

---

## 🧪 Verificar la Configuración Actual

Para ver qué URL está configurada actualmente, puedes:

### Método 1: Ver en la consola de Connect

En la sección Tools/Action groups, verás la URL actual del OpenAPI.

### Método 2: Revisar los logs de CloudWatch

```bash
# Ver logs del agente
aws logs tail /aws/connect/[tu-instancia-id] --since 30m --follow
```

Busca líneas que mencionen "OpenAPI" o "MCP Server".

### Método 3: Verificar archivos en S3

```bash
# Listar archivos en el bucket
aws s3 ls s3://salud-api-stack-openapibucket-korvxxrkhifa/

# Deberías ver:
# openapi.yaml                    ← Versión antigua
# turnos-api.yaml                 ← Versión antigua
# turnos-medicos-api-openapi-v3.yaml  ← Versión nueva (corregida)
```

---

## ❓ Troubleshooting

### No encuentro la sección "AI agents"

**Posibles razones:**
1. Tu usuario no tiene permisos para ver agentes
2. La instancia no tiene agentes configurados
3. La interfaz puede tener un nombre diferente según la versión

**Solución:**
- Busca en el menú: "Amazon Q", "Agents", "Generative AI"
- Contacta al administrador de la cuenta para verificar permisos

### No veo ningún MCP Server configurado

**Posibles razones:**
1. El agente no tiene herramientas configuradas
2. La configuración está en otro lugar (Action groups, Knowledge bases)

**Solución:**
- Revisa todas las pestañas del agente
- Busca "OpenAPI", "API", "External service"

### El botón "Unpublish" no está disponible

**Posibles razones:**
1. El agente ya está en estado "Draft"
2. No tienes permisos para modificar el agente

**Solución:**
- Si está en "Draft", solo necesitas "Publish" después de guardar
- Contacta al administrador para verificar permisos

---

## 📞 Contacto

Si tienes problemas para encontrar la configuración, comparte:
1. Captura de pantalla de la página del agente Luna
2. Captura de las pestañas/secciones disponibles
3. Versión de Amazon Connect que estás usando

**Preparado por:** Diego Borra - CloudHesive LATAM  
**Email:** diego@cloudhesive.com  
**Fecha:** 2 de Febrero de 2026
