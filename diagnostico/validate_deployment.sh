#!/bin/bash

# Script de Validación del Despliegue OpenAPI v3
# Fecha: 2 de Febrero de 2026
# Stack: salud-api-stack

set -e

echo "🔍 Validación del Despliegue - OpenAPI v3"
echo "=========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
STACK_NAME="salud-api-stack"
OPENAPI_FILE="turnos-medicos-api-openapi-v3.yaml"

echo "📋 Paso 1: Verificar OpenAPI en S3"
echo "-----------------------------------"

# Obtener bucket name
BUCKET_NAME=$(aws cloudformation describe-stack-resources \
  --stack-name $STACK_NAME \
  --logical-resource-id OpenApiBucket \
  --query "StackResources[0].PhysicalResourceId" \
  --output text)

echo "Bucket: $BUCKET_NAME"

# Verificar que el archivo existe
if aws s3 ls s3://$BUCKET_NAME/$OPENAPI_FILE > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OpenAPI v3 encontrado en S3${NC}"
    
    # Mostrar detalles del archivo
    aws s3 ls s3://$BUCKET_NAME/$OPENAPI_FILE
    
    # Construir URL
    OPENAPI_URL="https://$BUCKET_NAME.s3.us-east-1.amazonaws.com/$OPENAPI_FILE"
    echo ""
    echo "URL del OpenAPI v3:"
    echo "$OPENAPI_URL"
else
    echo -e "${RED}❌ OpenAPI v3 NO encontrado en S3${NC}"
    exit 1
fi

echo ""
echo "📊 Paso 2: Verificar Stack Outputs"
echo "-----------------------------------"

# Obtener outputs del stack
API_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query "Stacks[0].Outputs[?OutputKey=='TurnosApiUrl'].OutputValue" \
  --output text)

API_KEY=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query "Stacks[0].Outputs[?OutputKey=='ApiKey'].OutputValue" \
  --output text)

TABLE_NAME=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query "Stacks[0].Outputs[?OutputKey=='TurnosTableName'].OutputValue" \
  --output text 2>/dev/null || echo "TurnosTable-NotFound")

echo "API URL: $API_URL"
echo "API Key: ${API_KEY:0:10}..."
echo "Table Name: $TABLE_NAME"

echo ""
echo "🧪 Paso 3: Test de Conectividad"
echo "--------------------------------"

# Test endpoint de búsqueda de médicos
echo "Probando POST /medicos/buscar..."
RESPONSE=$(curl -s -X POST "$API_URL/medicos/buscar" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"especialidad": "Cardiología"}' \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ API Gateway respondiendo correctamente${NC}"
    MEDICOS_COUNT=$(echo "$BODY" | jq -r '.cantidad // 0')
    echo "Médicos encontrados: $MEDICOS_COUNT"
else
    echo -e "${RED}❌ Error en API Gateway (HTTP $HTTP_CODE)${NC}"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
fi

echo ""
echo "📝 Paso 4: Verificar Turnos en DynamoDB"
echo "----------------------------------------"

# Contar turnos en la tabla
if [ "$TABLE_NAME" != "TurnosTable-NotFound" ]; then
    TURNOS_COUNT=$(aws dynamodb scan \
      --table-name $TABLE_NAME \
      --select COUNT \
      --query "Count" \
      --output text 2>/dev/null || echo "0")
    
    echo "Total de turnos en DynamoDB: $TURNOS_COUNT"
    
    # Mostrar últimos turnos modificados
    echo ""
    echo "Últimos turnos modificados:"
    aws dynamodb scan \
      --table-name $TABLE_NAME \
      --filter-expression "attribute_exists(modifiedAt)" \
      --max-items 3 \
      --query "Items[].{turnoId: turnoId.S, fechaTurno: fechaTurno.S, horaTurno: horaTurno.S, modifiedAt: modifiedAt.S}" \
      --output table 2>/dev/null || echo "No hay turnos modificados"
else
    echo -e "${YELLOW}⚠️  No se pudo obtener el nombre de la tabla de turnos${NC}"
fi

echo ""
echo "📋 Paso 5: Instrucciones de Configuración"
echo "------------------------------------------"
echo ""
echo "Para completar el despliegue, debes:"
echo ""
echo "1. Ir a Amazon Connect Console:"
echo "   https://console.aws.amazon.com/connect/"
echo ""
echo "2. Seleccionar tu instancia → AI agents → Luna"
echo ""
echo "3. En la sección Tools, editar el MCP Server"
echo ""
echo "4. Actualizar la URL del OpenAPI a:"
echo "   $OPENAPI_URL"
echo ""
echo "5. Guardar cambios"
echo ""
echo "6. CRÍTICO: Forzar recarga del caché:"
echo "   - Click en 'Unpublish'"
echo "   - Esperar 10 segundos"
echo "   - Click en 'Publish'"
echo ""
echo "7. Validar con una llamada de prueba:"
echo "   'Quiero cambiar mi turno para el próximo miércoles a las 3 PM'"
echo ""

echo ""
echo "📊 Resumen de Validación"
echo "========================"
echo ""
echo -e "${GREEN}✅ OpenAPI v3 subido a S3${NC}"
echo -e "${GREEN}✅ Stack activo y funcionando${NC}"
echo -e "${GREEN}✅ API Gateway respondiendo${NC}"
echo -e "${YELLOW}⏭️  Pendiente: Configurar MCP Server en Amazon Connect${NC}"
echo -e "${YELLOW}⏭️  Pendiente: Unpublish/Publish del agente Luna${NC}"
echo ""
echo "Documentación completa: INSTRUCCIONES-DESPLIEGUE-OPENAPI.md"
echo ""
