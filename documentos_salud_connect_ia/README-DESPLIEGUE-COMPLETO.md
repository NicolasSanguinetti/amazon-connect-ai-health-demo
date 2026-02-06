# 🏥 Sistema de Turnos Médicos - ClinicaSalud
## Despliegue Completo desde Cero

Este documento contiene las instrucciones completas para desplegar todo el sistema de gestión de turnos médicos con Amazon Connect, API Gateway, Lambda y DynamoDB.

---

## 📋 **ARCHIVOS NECESARIOS**

Necesitás estos 4 archivos para el despliegue completo:

1. **turnos-medicos-api-final.yaml** - Template de CloudFormation (Stack principal)
2. **turnos-medicos-api-openapi.yaml** - Especificación OpenAPI para MCP Server
3. **medicos_seed_data_converted.json** - Datos iniciales de médicos
4. **luna-agent-prompt-mejorado.yaml** - Prompt del agente de IA

---

## 🚀 **PASO 1: PREPARAR S3 BUCKET**

```bash
# Crear o usar un bucket existente
BUCKET_NAME="tu-bucket-name"  # Cambiá esto por tu bucket
REGION="us-east-1"

# Subir archivos necesarios
aws s3 cp medicos_seed_data_converted.json s3://${BUCKET_NAME}/medicos_seed_data_ok.json
aws s3 cp turnos-medicos-api-openapi.yaml s3://${BUCKET_NAME}/turnos-medicos-api-openapi-v2.yaml

echo "✅ Archivos subidos a S3"
```

---

## 🏗️ **PASO 2: DESPLEGAR STACK DE CLOUDFORMATION**

```bash
# Parámetros del stack
STACK_NAME="salud-api-stack"
SEED_DATA_URL="https://${BUCKET_NAME}.s3.${REGION}.amazonaws.com/medicos_seed_data_ok.json"
OPENAPI_URL="https://${BUCKET_NAME}.s3.${REGION}.amazonaws.com/turnos-medicos-api-openapi-v2.yaml"

# Crear el stack
aws cloudformation create-stack \
  --stack-name ${STACK_NAME} \
  --template-body file://turnos-medicos-api-final.yaml \
  --parameters \
    ParameterKey=SeedDataUrl,ParameterValue="${SEED_DATA_URL}" \
    ParameterKey=OpenApiSpecUrl,ParameterValue="${OPENAPI_URL}" \
  --capabilities CAPABILITY_IAM

echo "⏳ Esperando que el stack se cree..."
aws cloudformation wait stack-create-complete --stack-name ${STACK_NAME}

echo "✅ Stack creado exitosamente!"

# Obtener outputs del stack
aws cloudformation describe-stacks \
  --stack-name ${STACK_NAME} \
  --query 'Stacks[0].Outputs' \
  --output table
```

---

## 🔑 **PASO 3: OBTENER CREDENCIALES**

```bash
# Guardar API URL y API Key
API_URL=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_NAME} \
  --query 'Stacks[0].Outputs[?OutputKey==`TurnosApiUrl`].OutputValue' \
  --output text)

API_KEY=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_NAME} \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiKey`].OutputValue' \
  --output text)

echo "API URL: ${API_URL}"
echo "API Key: ${API_KEY:0:20}..."

# Guardar en archivo para referencia
cat > api-credentials.txt << EOF
API URL: ${API_URL}
API Key: ${API_KEY}
Fecha de creación: $(date)
EOF

echo "✅ Credenciales guardadas en api-credentials.txt"
```

---

## 🤖 **PASO 4: CONFIGURAR AGENTE EN AMAZON CONNECT**

### 4.1 Crear MCP Server

1. Ir a **Amazon Connect Console** → **AI agents**
2. Click **Create AI agent**
3. Nombre: `Luna - Asistente de Turnos Médicos`
4. Descripción: `Agente de IA para gestión de turnos médicos`
5. Click **Create**

### 4.2 Configurar Tools (MCP Server)

1. En el agente creado, ir a pestaña **Tools**
2. Click **Add tool** → **MCP Server**
3. Configurar:
   - **Name**: `salud-api`
   - **OpenAPI Specification URL**: `https://tu-bucket.s3.us-east-1.amazonaws.com/turnos-medicos-api-openapi-v2.yaml`
   - **API Key Header**: `X-API-Key`
   - **API Key Value**: `[El API_KEY obtenido en Paso 3]`
4. Click **Save**
5. Seleccionar todas las herramientas:
   - ✅ buscarMedicos
   - ✅ crearTurno
   - ✅ obtenerTurnosPaciente
   - ✅ modificarTurno
   - ✅ cancelarTurno

### 4.3 Configurar Prompt del Agente

1. En el agente, ir a pestaña **Instructions**
2. Copiar y pegar el contenido completo de `luna-agent-prompt-mejorado.yaml`
3. Click **Save**

### 4.4 Publicar el Agente

1. Click **Publish**
2. Confirmar publicación

---

## 📞 **PASO 5: CONFIGURAR CONTACT FLOW**

### 5.1 Crear Contact Flow

1. **Amazon Connect Console** → **Routing** → **Contact flows**
2. Click **Create contact flow**
3. Nombre: `Sistema de Turnos Médicos`

### 5.2 Agregar Bloques

**Estructura del flow:**

```
Entry → Set logging → Get customer input → Invoke AI agent → Disconnect
```

**Configuración del bloque "Invoke AI agent":**
- Agent: Luna - Asistente de Turnos Médicos
- Session attributes:
  - `firstName`: `$.CustomerEndpoint.Address` (o variable de perfil)
  - `lastName`: `$.CustomerEndpoint.Address`
  - `customerId`: `$.CustomerEndpoint.Address`
  - `email`: `$.CustomerEndpoint.Address`

### 5.3 Publicar y Asignar Número

1. Click **Publish**
2. Ir a **Phone numbers** → Seleccionar número
3. **Contact flow**: Seleccionar "Sistema de Turnos Médicos"
4. Click **Save**

---

## ✅ **PASO 6: PROBAR EL SISTEMA**

### Prueba Manual de APIs

```bash
# 1. Buscar médicos
curl -X POST "${API_URL}/medicos/buscar" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{"especialidad": "Cardiología"}' | jq

# 2. Crear turno
curl -X POST "${API_URL}/turnos" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "fecha": "2026-02-10",
    "hora": "14:00",
    "medicoId": "medico-buenosaires-cardio-001",
    "pacienteId": "test-123",
    "nombrePaciente": "Juan Perez",
    "emailPaciente": "juan@test.com",
    "telefonoPaciente": "+541199887766",
    "motivoConsulta": "Consulta general"
  }' | jq

# 3. Obtener turnos de paciente
curl -X POST "${API_URL}/turnos/paciente" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{"pacienteId": "test-123"}' | jq

# 4. Verificar datos en DynamoDB
TABLE_NAME=$(aws cloudformation describe-stack-resources \
  --stack-name ${STACK_NAME} \
  --logical-resource-id TurnosTable \
  --query 'StackResources[0].PhysicalResourceId' \
  --output text)

aws dynamodb scan --table-name ${TABLE_NAME} --max-items 5
```

### Prueba del Agente

1. Llamar al número asignado
2. Conversación de prueba:
   ```
   Usuario: "Hola, quiero un turno"
   Agente: "¡Hola! ¿Qué especialidad necesitas?"
   Usuario: "Cardiología"
   Agente: [Busca médicos]
   Usuario: "Con González"
   Agente: "¿Cuál es tu nombre?"
   Usuario: "Juan Perez"
   Agente: "¿Email y teléfono?"
   Usuario: "juan@test.com y 1122334455"
   Agente: "¿Qué día y hora?"
   Usuario: "Miércoles 5 de febrero a las 3 de la tarde"
   Agente: [Confirma y crea el turno]
   ```

---

## 🔍 **PASO 7: MONITOREO Y LOGS**

### Ver Logs de Lambdas

```bash
# Logs de CreateTurnoFunction
aws logs tail /aws/lambda/${STACK_NAME}-CreateTurnoFunction* --since 30m --follow

# Logs de API Gateway
aws logs tail /aws/apigateway/${STACK_NAME} --since 30m --follow
```

### Ver Datos en DynamoDB

```bash
# Ver todos los turnos
TABLE_NAME=$(aws cloudformation describe-stack-resources \
  --stack-name ${STACK_NAME} \
  --logical-resource-id TurnosTable \
  --query 'StackResources[0].PhysicalResourceId' \
  --output text)

aws dynamodb scan --table-name ${TABLE_NAME} | jq '.Items[] | {turnoId: .turnoId.S, fecha: .fechaTurno.S, hora: .horaTurno.S, paciente: .nombrePaciente.S}'

# Ver médicos
MEDICOS_TABLE=$(aws cloudformation describe-stack-resources \
  --stack-name ${STACK_NAME} \
  --logical-resource-id MedicosTable \
  --query 'StackResources[0].PhysicalResourceId' \
  --output text)

aws dynamodb scan --table-name ${MEDICOS_TABLE} | jq '.Items[] | {id: .medicoId.S, nombre: .nombreCompleto.S, especialidad: .especialidad.S}'
```

---

## 🔧 **ACTUALIZAR EL SISTEMA**

### Actualizar Lambda Functions

```bash
# Actualizar el stack con cambios
aws cloudformation update-stack \
  --stack-name ${STACK_NAME} \
  --template-body file://turnos-medicos-api-final.yaml \
  --parameters \
    ParameterKey=SeedDataUrl,UsePreviousValue=true \
    ParameterKey=OpenApiSpecUrl,UsePreviousValue=true \
  --capabilities CAPABILITY_IAM

aws cloudformation wait stack-update-complete --stack-name ${STACK_NAME}
```

### Actualizar OpenAPI

```bash
# Subir nueva versión
TIMESTAMP=$(date +%s)
aws s3 cp turnos-medicos-api-openapi.yaml \
  s3://${BUCKET_NAME}/turnos-medicos-api-openapi-v${TIMESTAMP}.yaml

# Actualizar en Connect Console:
# AI agents → Tools → Edit MCP Server → Cambiar URL
```

### Actualizar Prompt del Agente

```bash
# Editar manualmente en Connect Console:
# AI agents → Tu agente → Instructions → Pegar nuevo prompt → Save → Publish
```

---

## 🗑️ **ELIMINAR TODO EL SISTEMA**

```bash
# CUIDADO: Esto elimina TODO el stack y sus recursos

# Eliminar stack
aws cloudformation delete-stack --stack-name ${STACK_NAME}

# Esperar eliminación
aws cloudformation wait stack-delete-complete --stack-name ${STACK_NAME}

# Limpiar S3 (opcional)
aws s3 rm s3://${BUCKET_NAME}/medicos_seed_data_ok.json
aws s3 rm s3://${BUCKET_NAME}/turnos-medicos-api-openapi-v2.yaml

echo "✅ Sistema completamente eliminado"
```

---

## 📚 **RECURSOS DEL SISTEMA**

### Recursos de CloudFormation

- **DynamoDB Tables**: TurnosTable, MedicosTable
- **Lambda Functions**: 
  - CreateTurnoFunction
  - GetTurnosPacienteFunction
  - ModifyTurnoFunction
  - CancelTurnoFunction
  - SearchMedicosFunction
- **API Gateway**: REST API con 5 endpoints
- **S3 Bucket**: OpenApiBucket (interno)

### Endpoints de API

- `POST /medicos/buscar` - Buscar médicos por especialidad
- `POST /turnos` - Crear nuevo turno
- `POST /turnos/paciente` - Obtener turnos de un paciente
- `POST /turnos/modificar` - Modificar turno existente
- `POST /turnos/cancelar` - Cancelar turno

---

## 🐛 **TROUBLESHOOTING**

### Problema: El agente no crea turnos

**Solución:**
1. Verificar que todas las herramientas estén habilitadas en Tools
2. Unpublish y Publish el agente para recargar cache
3. Verificar logs del API Gateway: `aws logs tail /aws/apigateway/${STACK_NAME} --since 10m`

### Problema: Lambda Functions fallan

**Solución:**
```bash
# Ver logs específicos
aws logs tail /aws/lambda/${STACK_NAME}-CreateTurnoFunction* --since 30m

# Verificar que las tablas de DynamoDB existen
aws dynamodb list-tables | grep salud-api-stack
```

### Problema: MCP Server con 403 Forbidden

**Solución:**
- Verificar que el archivo OpenAPI sea accesible públicamente
- Usar el bucket interno del stack en lugar de bucket externo
- Verificar que el API Key sea correcto

---

## 📞 **SOPORTE**

Para problemas o preguntas:
- Email: diego@cloudhesive.com
- AWS CloudFormation Docs: https://docs.aws.amazon.com/cloudformation/
- Amazon Connect Docs: https://docs.aws.amazon.com/connect/

---

**Versión:** 1.0.0  
**Última actualización:** 30 de Enero de 2026  
**Creado por:** CloudHesive LATAM
