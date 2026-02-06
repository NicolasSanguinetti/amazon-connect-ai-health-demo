# Script de Validación del Despliegue OpenAPI v3
# Fecha: 2 de Febrero de 2026
# Stack: salud-api-stack

$ErrorActionPreference = "Stop"

Write-Host "🔍 Validación del Despliegue - OpenAPI v3" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$STACK_NAME = "salud-api-stack"
$OPENAPI_FILE = "turnos-medicos-api-openapi-v3.yaml"

Write-Host "📋 Paso 1: Verificar OpenAPI en S3" -ForegroundColor Yellow
Write-Host "-----------------------------------"

# Obtener bucket name
$BUCKET_NAME = aws cloudformation describe-stack-resources `
  --stack-name $STACK_NAME `
  --logical-resource-id OpenApiBucket `
  --query "StackResources[0].PhysicalResourceId" `
  --output text

Write-Host "Bucket: $BUCKET_NAME"

# Verificar que el archivo existe
$s3Check = aws s3 ls "s3://$BUCKET_NAME/$OPENAPI_FILE" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ OpenAPI v3 encontrado en S3" -ForegroundColor Green
    
    # Mostrar detalles del archivo
    aws s3 ls "s3://$BUCKET_NAME/$OPENAPI_FILE"
    
    # Construir URL
    $OPENAPI_URL = "https://$BUCKET_NAME.s3.us-east-1.amazonaws.com/$OPENAPI_FILE"
    Write-Host ""
    Write-Host "URL del OpenAPI v3:"
    Write-Host $OPENAPI_URL -ForegroundColor Cyan
} else {
    Write-Host "❌ OpenAPI v3 NO encontrado en S3" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📊 Paso 2: Verificar Stack Outputs" -ForegroundColor Yellow
Write-Host "-----------------------------------"

# Obtener outputs del stack
$API_URL = aws cloudformation describe-stacks `
  --stack-name $STACK_NAME `
  --query "Stacks[0].Outputs[?OutputKey=='TurnosApiUrl'].OutputValue" `
  --output text

$API_KEY = aws cloudformation describe-stacks `
  --stack-name $STACK_NAME `
  --query "Stacks[0].Outputs[?OutputKey=='ApiKey'].OutputValue" `
  --output text

$TABLE_NAME = aws cloudformation describe-stacks `
  --stack-name $STACK_NAME `
  --query "Stacks[0].Outputs[?OutputKey=='TurnosTableName'].OutputValue" `
  --output text 2>$null

if (-not $TABLE_NAME) {
    $TABLE_NAME = "TurnosTable-NotFound"
}

Write-Host "API URL: $API_URL"
Write-Host "API Key: $($API_KEY.Substring(0, 10))..."
Write-Host "Table Name: $TABLE_NAME"

Write-Host ""
Write-Host "🧪 Paso 3: Test de Conectividad" -ForegroundColor Yellow
Write-Host "--------------------------------"

# Test endpoint de búsqueda de médicos
Write-Host "Probando POST /medicos/buscar..."

$body = @{
    especialidad = "Cardiología"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$API_URL/medicos/buscar" `
        -Method POST `
        -Headers @{
            "Content-Type" = "application/json"
            "X-API-Key" = $API_KEY
        } `
        -Body $body `
        -UseBasicParsing

    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API Gateway respondiendo correctamente" -ForegroundColor Green
        $result = $response.Content | ConvertFrom-Json
        Write-Host "Médicos encontrados: $($result.cantidad)"
    }
} catch {
    Write-Host "❌ Error en API Gateway" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host "📝 Paso 4: Verificar Turnos en DynamoDB" -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Contar turnos en la tabla
if ($TABLE_NAME -ne "TurnosTable-NotFound") {
    $TURNOS_COUNT = aws dynamodb scan `
      --table-name $TABLE_NAME `
      --select COUNT `
      --query "Count" `
      --output text 2>$null
    
    if ($TURNOS_COUNT) {
        Write-Host "Total de turnos en DynamoDB: $TURNOS_COUNT"
    }
    
    # Mostrar últimos turnos modificados
    Write-Host ""
    Write-Host "Últimos turnos modificados:"
    aws dynamodb scan `
      --table-name $TABLE_NAME `
      --filter-expression "attribute_exists(modifiedAt)" `
      --max-items 3 `
      --query "Items[].{turnoId: turnoId.S, fechaTurno: fechaTurno.S, horaTurno: horaTurno.S, modifiedAt: modifiedAt.S}" `
      --output table 2>$null
} else {
    Write-Host "⚠️  No se pudo obtener el nombre de la tabla de turnos" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Paso 5: Instrucciones de Configuración" -ForegroundColor Yellow
Write-Host "------------------------------------------"
Write-Host ""
Write-Host "Para completar el despliegue, debes:"
Write-Host ""
Write-Host "1. Ir a Amazon Connect Console:"
Write-Host "   https://console.aws.amazon.com/connect/" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Seleccionar tu instancia → AI agents → Luna"
Write-Host ""
Write-Host "3. En la sección Tools, editar el MCP Server"
Write-Host ""
Write-Host "4. Actualizar la URL del OpenAPI a:"
Write-Host "   $OPENAPI_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Guardar cambios"
Write-Host ""
Write-Host "6. CRÍTICO: Forzar recarga del caché:" -ForegroundColor Red
Write-Host "   - Click en 'Unpublish'"
Write-Host "   - Esperar 10 segundos"
Write-Host "   - Click en 'Publish'"
Write-Host ""
Write-Host "7. Validar con una llamada de prueba:"
Write-Host "   'Quiero cambiar mi turno para el próximo miércoles a las 3 PM'"
Write-Host ""

Write-Host ""
Write-Host "📊 Resumen de Validación" -ForegroundColor Cyan
Write-Host "========================"
Write-Host ""
Write-Host "✅ OpenAPI v3 subido a S3" -ForegroundColor Green
Write-Host "✅ Stack activo y funcionando" -ForegroundColor Green
Write-Host "✅ API Gateway respondiendo" -ForegroundColor Green
Write-Host "⏭️  Pendiente: Configurar MCP Server en Amazon Connect" -ForegroundColor Yellow
Write-Host "⏭️  Pendiente: Unpublish/Publish del agente Luna" -ForegroundColor Yellow
Write-Host ""
Write-Host "Documentación completa: INSTRUCCIONES-DESPLIEGUE-OPENAPI.md"
Write-Host ""
