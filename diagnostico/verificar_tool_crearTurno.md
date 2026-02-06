# 🔍 Diagnóstico: Tool crearTurno No Se Ejecuta

**Fecha:** 2 de Febrero de 2026  
**Problema:** El agente dice que va a crear el turno pero NO lo hace

---

## 📊 Evidencia del Problema

### Conversación del Usuario:
```
Cliente: "si si esta perfecto"
BOT: "Excelente, Ernesto. Voy a confirmar tu turno ahora."
El chat finalizó.
```

### Verificación en DynamoDB:
```bash
# Turnos en la tabla:
- TURNO-3U40P2 (2026-01-30) - Test Usuario
- TURNO-AD0OI6 (2026-02-02) - Carlos Cevallos
- TURNO-HBOAB3 (sin fecha creación) - Diego Borra
- TURNO-JXN1HO (2026-01-30) - Carlo Amerino
- TURNO-V7T8KY (2026-01-30) - Carlos Pérez

❌ NO hay turno de "Ernesto Sabato"
```

### Logs del API Gateway:
```
15:16:08 - POST /medicos/buscar - 200 ✅ (Funcionó)
❌ NO hay POST /turnos (No se llamó)
```

### Logs de Lambda:
```
❌ NO hay logs de CreateTurnoFunction
```

---

## 🎯 Causa Raíz Identificada

El agente **NO está ejecutando el tool `salud_api__crearTurno`**.

Posibles razones:

### 1. Tool No Habilitado o Sin Permisos

El tool puede estar configurado pero no habilitado para ejecución automática.

**Verificar:**
1. Ir a Amazon Connect → AI agents → Luna → Tools
2. Click en "salud_api__crearTurno"
3. Verificar:
   - ✅ "User Confirmation" debe estar **DESACTIVADO** (o el agente pedirá confirmación)
   - ✅ "Permissions" debe ser "Sufficient"
   - ✅ El tool debe estar **habilitado**

### 2. Agente en Modo Simulación

El agente puede estar configurado para NO ejecutar acciones reales.

**Verificar:**
1. En la configuración del agente Luna
2. Buscar "Action execution" o "Tool execution"
3. Verificar que esté en modo "Execute" no "Simulate"

### 3. Error en el Input Schema

El agente puede estar intentando llamar al tool pero con parámetros incorrectos.

**Verificar:**
1. Ver los logs del agente en CloudWatch
2. Buscar errores de validación de schema

### 4. Timeout o Error Silencioso

El agente puede estar intentando llamar pero fallando silenciosamente.

**Verificar:**
1. Logs de CloudWatch del agente
2. Logs de AgentCore Gateway

---

## 🔧 Solución Paso a Paso

### Paso 1: Verificar Configuración del Tool

1. **Ir a:** Amazon Connect → AI agents → Luna → Tools
2. **Click en:** "salud_api__crearTurno"
3. **Verificar:**

```
Tool Properties:
  Name: salud_api__crearTurno
  Title: gateway_salud-mcp-server-odybaqqqx2__salud-api__crearTurno
  
  User Confirmation: ❌ DESACTIVADO
  ↑ Si está activado, el agente pedirá confirmación antes de ejecutar
  
  Tool Safety Status: ⚠️ Unspecified
  ↑ Debería ser "Safe" o "Approved"
  
  Permissions: ✅ Sufficient
```

### Paso 2: Habilitar Ejecución Automática

Si "User Confirmation" está activado:

1. **Desactivar** el toggle "Require user confirmation before tool invocation"
2. **Guardar** cambios
3. **Hacer Unpublish/Publish** del agente

### Paso 3: Verificar Permisos del Tool

1. En la configuración del tool
2. Verificar que "Permissions" sea "Sufficient"
3. Si no lo es, revisar los permisos del agente en IAM

### Paso 4: Verificar el Prompt del Agente

El prompt del agente debe incluir instrucciones para ejecutar el tool:

```yaml
<instructions>
When the user confirms they want to create an appointment:
1. Call the salud_api__crearTurno tool with all required parameters
2. Wait for the response
3. Confirm the appointment was created successfully
4. Provide the turnoId to the user
</instructions>
```

### Paso 5: Ver Logs del Agente

```bash
# Buscar logs del agente en CloudWatch
aws logs tail /aws/connect/[instance-id] --since 1h --filter-pattern "crearTurno"

# O buscar por el contact ID
aws logs tail /aws/connect/[instance-id] --since 1h --filter-pattern "[contact-id]"
```

---

## 🧪 Test de Validación

### Test 1: Verificar que el Tool Se Puede Ejecutar

1. En la configuración del tool "salud_api__crearTurno"
2. Buscar un botón "Test" o "Try it"
3. Ejecutar con parámetros de prueba:

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

4. Verificar que retorne 201 Created

### Test 2: Probar con el Agente

1. Iniciar una nueva conversación
2. Solicitar un turno
3. **Observar si el agente:**
   - ❌ Dice "Voy a confirmar" pero no hace nada
   - ❌ Pide confirmación adicional
   - ✅ Ejecuta el tool y confirma con el turnoId

---

## 📋 Checklist de Verificación

- [ ] Tool "salud_api__crearTurno" está habilitado
- [ ] "User Confirmation" está DESACTIVADO
- [ ] "Permissions" es "Sufficient"
- [ ] "Tool Safety Status" es "Safe" o "Approved"
- [ ] El agente NO está en modo simulación
- [ ] El prompt incluye instrucciones para ejecutar el tool
- [ ] El OpenAPI v3 está cargado correctamente
- [ ] Se hizo Unpublish/Publish después de los cambios

---

## 🎯 Próximos Pasos

1. **Verificar la configuración del tool** (User Confirmation, Permissions)
2. **Desactivar "User Confirmation"** si está activado
3. **Hacer Unpublish/Publish** del agente
4. **Probar nuevamente** con una conversación de prueba
5. **Ver los logs** para identificar errores específicos

---

## 📞 Información Adicional Necesaria

Para diagnosticar mejor, necesitamos:

1. **Captura de pantalla** de la configuración del tool "salud_api__crearTurno"
2. **Logs del agente** durante la conversación
3. **Contact ID** de la conversación que falló
4. **Configuración del prompt** del agente (sección de tools/actions)

---

**Preparado por:** Diego Borra - CloudHesive LATAM  
**Fecha:** 2 de Febrero de 2026
