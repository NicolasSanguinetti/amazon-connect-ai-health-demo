# Script de Verificación: Tool Safety Status
# Verifica que el OpenAPI tenga la configuración correcta y que esté en S3

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verificación: Tool Safety Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$bucket = "salud-api-stack-openapibucket-korvxxrkhifa"
$region = "us-east-1"

# 1. Verificar que el OpenAPI en S3 tenga x-amazon-connect-tool-safety
Write-Host "1. Verificando OpenAPI en S3..." -ForegroundColor Yellow

try {
    # Descargar el OpenAPI desde S3
    $tempFile = "$env:TEMP\openapi-temp.yaml"
    aws s3 cp "s3://$bucket/openapi.yaml" $tempFile --region $region 2>$null
    
    if (Test-Path $tempFile) {
        $content = Get-Content $tempFile -Raw
        
        # Buscar x-amazon-connect-tool-safety
        $matches = [regex]::Matches($content, "x-amazon-connect-tool-safety:\s*(\w+)")
        
        if ($matches.Count -gt 0) {
            Write-Host "   ✅ OpenAPI tiene x-amazon-connect-tool-safety configurado" -ForegroundColor Green
            Write-Host ""
            Write-Host "   Endpoints con tool-safety:" -ForegroundColor Cyan
            
            foreach ($match in $matches) {
                $value = $match.Groups[1].Value
                Write-Host "   - $value" -ForegroundColor White
            }
            
            # Verificar que crearTurno tenga destructive
            if ($content -match "/turnos:[\s\S]*?post:[\s\S]*?x-amazon-connect-tool-safety:\s*destructive") {
                Write-Host ""
                Write-Host "   ✅ /turnos (crearTurno) tiene 'destructive'" -ForegroundColor Green
            } else {
                Write-Host ""
                Write-Host "   ❌ /turnos (crearTurno) NO tiene 'destructive'" -ForegroundColor Red
            }
            
            # Verificar que modificarTurno tenga destructive
            if ($content -match "/turnos/modificar:[\s\S]*?post:[\s\S]*?x-amazon-connect-tool-safety:\s*destructive") {
                Write-Host "   ✅ /turnos/modificar tiene 'destructive'" -ForegroundColor Green
            } else {
                Write-Host "   ❌ /turnos/modificar NO tiene 'destructive'" -ForegroundColor Red
            }
            
            # Verificar que cancelarTurno tenga destructive
            if ($content -match "/turnos/cancelar:[\s\S]*?post:[\s\S]*?x-amazon-connect-tool-safety:\s*destructive") {
                Write-Host "   ✅ /turnos/cancelar tiene 'destructive'" -ForegroundColor Green
            } else {
                Write-Host "   ❌ /turnos/cancelar NO tiene 'destructive'" -ForegroundColor Red
            }
            
        } else {
            Write-Host "   ❌ OpenAPI NO tiene x-amazon-connect-tool-safety" -ForegroundColor Red
            Write-Host "   Necesitas subir el OpenAPI corregido a S3" -ForegroundColor Yellow
        }
        
        Remove-Item $tempFile -Force
    } else {
        Write-Host "   ❌ No se pudo descargar el OpenAPI desde S3" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Error al verificar OpenAPI: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "2. Próximos Pasos" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Si el OpenAPI está correcto:" -ForegroundColor White
Write-Host "1. Ir a Amazon Bedrock → AgentCore → Gateways" -ForegroundColor Cyan
Write-Host "2. Editar gateway_salud-mcp-server-odybaqqqx2" -ForegroundColor Cyan
Write-Host "3. Click en 'Save' (sin cambiar nada)" -ForegroundColor Cyan
Write-Host "4. ESPERAR 30 SEGUNDOS" -ForegroundColor Yellow
Write-Host ""
Write-Host "5. Ir a Amazon Connect → AI agents → Luna" -ForegroundColor Cyan
Write-Host "6. Click en 'Unpublish'" -ForegroundColor Cyan
Write-Host "7. ESPERAR 15 SEGUNDOS" -ForegroundColor Yellow
Write-Host "8. Click en 'Publish'" -ForegroundColor Cyan
Write-Host ""
Write-Host "9. Verificar en Luna → Tools → salud_api__crearTurno" -ForegroundColor Cyan
Write-Host "   Tool Safety Status debe decir: 'Destructive'" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "3. Test de Validación" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Después de Unpublish/Publish:" -ForegroundColor White
Write-Host "1. Iniciar una conversación con el agente" -ForegroundColor Cyan
Write-Host "2. Solicitar un turno" -ForegroundColor Cyan
Write-Host "3. Confirmar la creación" -ForegroundColor Cyan
Write-Host "4. Verificar que el turno aparezca en DynamoDB:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   aws dynamodb scan --table-name salud-api-stack-TurnosTable-1LLEZVIWYG3RI --region us-east-1 --max-items 10" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verificación Completa" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
