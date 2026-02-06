# 🏥 Sistema de Turnos Médicos - Resumen Ejecutivo del Proyecto
## CloudHesive LATAM + KIRO

**Fecha:** 30 de Enero de 2026  
**Cliente:** CloudHesive LATAM  
**Partner Desarrollo:** KIRO  
**Proyecto:** Sistema de Gestión de Turnos Médicos con IA Conversacional

---

## 📋 **RESUMEN EJECUTIVO**

Sistema completo de gestión de turnos médicos integrado con Amazon Connect que permite a los pacientes:
- Buscar médicos por especialidad
- Agendar turnos médicos por teléfono usando IA conversacional
- Consultar turnos existentes
- Modificar y cancelar turnos

**Tecnologías:** Amazon Connect, API Gateway, Lambda (Node.js/Python), DynamoDB, Bedrock, MCP Servers

---

## 🎯 **ESTADO ACTUAL DEL PROYECTO**

### ✅ **COMPLETADO**

1. **Infraestructura Backend (CloudFormation):**
   - ✅ API Gateway REST con 5 endpoints
   - ✅ 5 Lambda Functions (buscar médicos, crear/obtener/modificar/cancelar turnos)
   - ✅ 2 Tablas DynamoDB (Médicos y Turnos)
   - ✅ Seed data con médicos de muestra
   - ✅ API Key para autenticación

2. **Integración con Amazon Connect:**
   - ✅ MCP Server configurado con OpenAPI
   - ✅ 5 herramientas disponibles para el agente
   - ✅ Agente de IA "Luna" con prompt optimizado
   - ✅ Contact Flow básico configurado

3. **Funcionalidades Probadas:**
   - ✅ Búsqueda de médicos funciona correctamente
   - ✅ Creación de turnos funciona vía API (curl)
   - ✅ Consulta de turnos funciona
   - ✅ Modificación de turnos funciona vía API
   - ✅ Datos se guardan correctamente en DynamoDB

### ⚠️ **PENDIENTE DE RESOLVER**

1. **Cache del MCP Server:**
   - El agente de IA no está llamando a `crearTurno` correctamente
   - Causa: MCP Server tiene OpenAPI en cache
   - Solución necesaria: Forzar recarga del cache (Unpublish/Publish del agente)

2. **Prompt del Agente:**
   - El agente no está calculando fechas exactas (dice "próximo miércoles" en lugar de "2026-02-05")
   - Solución: Prompt ya incluye instrucciones específicas para fechas ISO y formato 24h
   - Necesita validación post-recarga de cache

3. **Testing End-to-End:**
   - Falta probar flujo completo: llamada → búsqueda médico → creación turno → confirmación
   - Una vez resuelto el cache, esto debería funcionar

---

## 📦 **ARCHIVOS DEL PROYECTO**

### **ARCHIVO 1: turnos-medicos-api-final.yaml** (CloudFormation Template - 60KB)
**Descripción:** Template principal que crea toda la infraestructura AWS
**Contiene:**
- 5 Lambda Functions (Node.js para APIs, Python para consultas)
- 2 DynamoDB Tables con GSI
- API Gateway REST API
- IAM Roles y Policies
- S3 Bucket para OpenAPI
- Custom Resources para seed data

**Parámetros:**
- `SeedDataUrl`: URL del JSON con datos de médicos
- `OpenApiSpecUrl`: URL del archivo OpenAPI para MCP Server

**Outputs:**
- `TurnosApiUrl`: URL base del API Gateway
- `ApiKey`: API Key para autenticación
- `TurnosTableName`: Nombre de la tabla de turnos
- `MedicosTableName`: Nombre de la tabla de médicos

---

### **ARCHIVO 2: turnos-medicos-api-openapi.yaml** (OpenAPI Spec - 18KB)
**Descripción:** Especificación OpenAPI 3.0 para el MCP Server de Amazon Connect
**Define:**
- 5 operaciones (buscarMedicos, crearTurno, obtenerTurnosPaciente, modificarTurno, cancelarTurno)
- Schemas de request/response
- Autenticación con API Key
- Ejemplos de uso

**Endpoints:**
```
POST /medicos/buscar
POST /turnos
POST /turnos/paciente
POST /turnos/modificar
POST /turnos/cancelar
```

---

### **ARCHIVO 3: medicos_seed_data_converted.json** (Datos Iniciales - 14KB)
**Descripción:** Datos de muestra de médicos para inicializar el sistema
**Contiene:**
- 15 médicos de ejemplo
- 10 especialidades médicas
- 3 ciudades (Buenos Aires, Córdoba, Rosario)
- Obras sociales argentinas (OSDE, Swiss Medical, Galeno)

**Estructura:**
```json
{
  "medicoId": "medico-buenosaires-cardio-001",
  "nombreCompleto": "Dra. María González",
  "especialidad": "Cardiología",
  "ciudad": "Buenos Aires",
  "diasAtencion": ["Lunes", "Miércoles", "Viernes"],
  "obrasSociales": [...],
  "valorConsulta": 15000
}
```

---

### **ARCHIVO 4: luna-agent-prompt-mejorado.yaml** (Prompt del Agente - 17KB)
**Descripción:** Prompt completo y optimizado para el agente de IA "Luna"
**Características:**
- Instrucciones específicas para manejo de fechas (formato ISO: YYYY-MM-DD)
- Instrucciones para formato de hora 24h (HH:MM)
- Guías para uso correcto de herramientas
- Ejemplos de conversaciones
- Configuración de variables dinámicas
- Solo inglés y español (sin francés)
- No saluda al inicio (el saludo se hace en el contact flow)

**Variables del sistema:**
```yaml
- companyName: {{$.Custom.CompanyName_Voice}}
- firstName: {{$.Custom.firstName}}
- lastName: {{$.Custom.lastName}}
- customerId: {{$.Custom.customerId}}
- email: {{$.Custom.email}}
```

---

### **ARCHIVO 5: README-DESPLIEGUE-COMPLETO.md** (Documentación - 15KB)
**Descripción:** Guía completa de despliegue paso a paso
**Incluye:**
- Instrucciones para crear el stack desde cero
- Configuración del agente en Amazon Connect
- Configuración del MCP Server
- Configuración del Contact Flow
- Comandos para testing
- Troubleshooting
- Scripts para actualización
- Scripts para eliminación completa del sistema

---

## 🔧 **ARQUITECTURA DEL SISTEMA**

```
┌─────────────────┐
│   Teléfono      │
│   del Paciente  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   Amazon Connect        │
│   - Contact Flow        │
│   - AI Agent (Luna)     │
│   - MCP Server          │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   API Gateway           │
│   + API Key Auth        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Lambda Functions      │
│   - buscarMedicos       │
│   - crearTurno          │
│   - obtenerTurnos       │
│   - modificarTurno      │
│   - cancelarTurno       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   DynamoDB              │
│   - Tabla Médicos       │
│   - Tabla Turnos        │
└─────────────────────────┘
```

---

## 🚀 **INSTRUCCIONES DE DESPLIEGUE RÁPIDO**

### **Prerequisitos:**
- Cuenta AWS con permisos de CloudFormation, Lambda, DynamoDB, API Gateway, S3
- AWS CLI configurado
- Bucket S3 existente
- Amazon Connect instance configurada

### **Despliegue en 5 pasos:**

```bash
# 1. Subir archivos a S3
BUCKET="tu-bucket-name"
aws s3 cp medicos_seed_data_converted.json s3://${BUCKET}/medicos_seed_data_ok.json
aws s3 cp turnos-medicos-api-openapi.yaml s3://${BUCKET}/turnos-medicos-api-openapi-v2.yaml

# 2. Crear stack
aws cloudformation create-stack \
  --stack-name salud-api-stack \
  --template-body file://turnos-medicos-api-final.yaml \
  --parameters \
    ParameterKey=SeedDataUrl,ParameterValue="https://${BUCKET}.s3.us-east-1.amazonaws.com/medicos_seed_data_ok.json" \
    ParameterKey=OpenApiSpecUrl,ParameterValue="https://${BUCKET}.s3.us-east-1.amazonaws.com/turnos-medicos-api-openapi-v2.yaml" \
  --capabilities CAPABILITY_IAM

# 3. Esperar creación
aws cloudformation wait stack-create-complete --stack-name salud-api-stack

# 4. Obtener credenciales
API_URL=$(aws cloudformation describe-stacks --stack-name salud-api-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`TurnosApiUrl`].OutputValue' --output text)
API_KEY=$(aws cloudformation describe-stacks --stack-name salud-api-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiKey`].OutputValue' --output text)

# 5. Configurar agente en Amazon Connect Console (manual)
# - Crear AI agent
# - Agregar MCP Server con OpenAPI URL y API Key
# - Pegar prompt de luna-agent-prompt-mejorado.yaml
# - Publicar agente
```

---

## 🐛 **PROBLEMAS CONOCIDOS Y SOLUCIONES**

### **PROBLEMA 1: El agente no crea turnos**

**Síntomas:**
- El agente dice "voy a confirmar tu turno" pero no lo crea
- No aparecen logs de POST /turnos en API Gateway
- Solo se ven llamadas a /medicos/buscar

**Causa:**
MCP Server tiene el OpenAPI en cache y no conoce los parámetros correctos

**Solución:**
1. Ir a Amazon Connect Console → AI agents → Tu agente
2. Click **Unpublish**
3. Esperar 10 segundos
4. Click **Publish**
5. Probar nuevamente

**Alternativa:**
Editar el MCP Server y agregar `?v=2` al final de la OpenAPI URL para romper el cache

---

### **PROBLEMA 2: El agente usa fechas relativas**

**Síntomas:**
- El agente dice "próximo miércoles" en lugar de "2026-02-05"
- El agente dice "3 de la tarde" en lugar de "15:00"

**Causa:**
El prompt no se actualizó después de los cambios

**Solución:**
1. Verificar que el prompt en Connect tiene la sección `<date_and_time_handling>`
2. Unpublish y Publish el agente para recargar el prompt

---

### **PROBLEMA 3: Lambda Functions reciben campos incorrectos**

**Síntomas:**
- Error: "Missing required parameters: fechaTurno, horaTurno"
- Los logs muestran que llega `fecha` y `hora` en lugar de `fechaTurno` y `horaTurno`

**Causa:**
Las Lambdas ya están corregidas para aceptar AMBOS formatos

**Estado:**
✅ Resuelto - Las Lambdas aceptan tanto `fecha/hora` como `fechaTurno/horaTurno`

---

## 📊 **TESTING Y VALIDACIÓN**

### **Test 1: API Gateway (Manual)**

```bash
# Buscar médicos
curl -X POST "${API_URL}/medicos/buscar" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{"especialidad": "Cardiología"}' | jq

# Crear turno
curl -X POST "${API_URL}/turnos" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "fecha": "2026-02-10",
    "hora": "14:00",
    "medicoId": "medico-buenosaires-cardio-001",
    "pacienteId": "test-001",
    "nombrePaciente": "Juan Perez",
    "emailPaciente": "juan@test.com",
    "telefonoPaciente": "+541199887766",
    "motivoConsulta": "Consulta general"
  }' | jq
```

**Resultado Esperado:** 
- Status 200/201
- JSON con datos del turno creado
- `turnoId` generado (ej: "TURNO-ABC123")

---

### **Test 2: Agente de IA (End-to-End)**

**Flujo de conversación esperado:**

```
Usuario: "Hola, quiero un turno"
Luna: "¿Qué especialidad necesitas?"

Usuario: "Cardiología"
Luna: [Busca médicos y muestra opciones]

Usuario: "Con la Dra. González"
Luna: "¿Cuál es tu nombre completo?"

Usuario: "María Rodríguez"
Luna: "¿Cuál es tu email y teléfono?"

Usuario: "maria@test.com y 1122334455"
Luna: "¿Qué día y hora prefieres?"

Usuario: "El 5 de febrero a las 3 de la tarde"
Luna: [Confirma: "María Rodríguez, 2026-02-05 a las 15:00 con Dra. González"]

Usuario: "Sí, confirmo"
Luna: [Crea el turno] "Tu turno está confirmado con código TURNO-XYZ123"
```

**Validación:**
1. ✅ El agente debe calcular "5 de febrero" → "2026-02-05"
2. ✅ El agente debe convertir "3 de la tarde" → "15:00"
3. ✅ Debe aparecer POST /turnos en los logs de API Gateway
4. ✅ El turno debe aparecer en DynamoDB

---

### **Test 3: Verificación en DynamoDB**

```bash
# Obtener nombre de tabla
TABLE_NAME=$(aws cloudformation describe-stack-resources \
  --stack-name salud-api-stack \
  --logical-resource-id TurnosTable \
  --query 'StackResources[0].PhysicalResourceId' \
  --output text)

# Ver todos los turnos
aws dynamodb scan --table-name ${TABLE_NAME} | \
  jq '.Items[] | {turnoId: .turnoId.S, fecha: .fechaTurno.S, hora: .horaTurno.S, paciente: .nombrePaciente.S}'
```

**Resultado Esperado:**
- Lista de turnos creados
- Campos: turnoId, fechaTurno, horaTurno, nombrePaciente, estado, etc.

---

## 🔍 **MONITOREO Y LOGS**

### **CloudWatch Logs Groups:**

```bash
# Logs de Lambda Functions
/aws/lambda/salud-api-stack-CreateTurnoFunction-*
/aws/lambda/salud-api-stack-SearchMedicosFunction-*
/aws/lambda/salud-api-stack-GetTurnosPacienteFunction-*
/aws/lambda/salud-api-stack-ModifyTurnoFunction-*
/aws/lambda/salud-api-stack-CancelTurnoFunction-*

# Logs de API Gateway
/aws/apigateway/salud-api-stack

# Ver logs en tiempo real
aws logs tail /aws/apigateway/salud-api-stack --since 30m --follow
```

### **Métricas Clave:**

- **API Gateway:** Número de requests, latencia, errores 4xx/5xx
- **Lambda:** Duración, errores, cold starts
- **DynamoDB:** Read/Write capacity, throttling

---

## 📈 **PRÓXIMOS PASOS CON KIRO**

### **Fase 1: Resolución de Issues Pendientes (1-2 días)**
1. Forzar recarga del cache del MCP Server
2. Validar que el agente crea turnos correctamente
3. Validar cálculo automático de fechas
4. Testing end-to-end completo

### **Fase 2: Mejoras y Optimizaciones (1 semana)**
1. Agregar validación de disponibilidad de médicos
2. Implementar manejo de conflictos de horarios
3. Agregar notificaciones por email/SMS
4. Mejorar manejo de errores y mensajes al usuario
5. Agregar soporte para obras sociales

### **Fase 3: Features Adicionales (2-3 semanas)**
1. Integración con sistemas externos (HIS/EMR)
2. Dashboard de administración
3. Reportes y analytics
4. Multi-sede y multi-especialidad avanzado
5. Recordatorios automáticos de turnos

### **Fase 4: Producción (1 semana)**
1. Security review y hardening
2. Performance testing y optimización
3. Documentación técnica completa
4. Capacitación de usuarios
5. Go-live y monitoreo

---

## 💰 **COSTOS ESTIMADOS AWS**

**Estimación mensual para 1000 llamadas/mes:**

| Servicio | Costo Mensual |
|----------|---------------|
| Amazon Connect | ~$30 (incluye AI agent) |
| API Gateway | ~$3.50 |
| Lambda | ~$5 |
| DynamoDB | ~$2.50 |
| CloudWatch Logs | ~$5 |
| S3 | ~$1 |
| **TOTAL** | **~$47/mes** |

*Nota: Costos estimados. Pueden variar según región y uso real.*

---

## 📞 **CONTACTOS**

**CloudHesive LATAM:**
- Diego Borra - AWS Ambassador & Customer Engagement Lead
- Email: diego@cloudhesive.com

**KIRO (Partner Desarrollo):**
- [Agregar contacto técnico]
- [Agregar email]

---

## 📚 **RECURSOS ADICIONALES**

- [AWS CloudFormation Docs](https://docs.aws.amazon.com/cloudformation/)
- [Amazon Connect Docs](https://docs.aws.amazon.com/connect/)
- [Amazon Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [MCP Servers Guide](https://docs.aws.amazon.com/connect/latest/adminguide/mcp-servers.html)

---

**Documento preparado por:** CloudHesive LATAM  
**Versión:** 1.0.0  
**Última actualización:** 30 de Enero de 2026  
**Estado:** ✅ Backend completo, ⚠️ Agente pendiente de validación final
