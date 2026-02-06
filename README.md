# 🏥 Sistema de Turnos Médicos - Salud Connect IA

Sistema de gestión de turnos médicos integrado con Amazon Connect, AgentCore Gateway y AWS Lambda.

---

### Solución Implementada
✅ OpenAPI v3 corregido con `x-amazon-connect-tool-safety: destructive`  
✅ Archivos subidos a S3  
✅ Documentación completa creada  
⏳ Pendiente: Forzar recarga del gateway + Unpublish/Publish del agente

---

## 🚀 Inicio Rápido

### 1. Lee el Resumen
```bash
# Ver el resumen ejecutivo completo
cat RESUMEN-FINAL-SOLUCION.md
```

### 2. Ejecuta la Verificación
```powershell
# Verificar que el OpenAPI en S3 tenga la configuración correcta
.\diagnostico\verificar_tool_safety.ps1
```

### 3. Sigue los Pasos
```bash
# Ver los pasos inmediatos a seguir
cat SIGUIENTE-PASO.md
```

---

## 📚 Documentación

### Documentos Principales
- **[RESUMEN-FINAL-SOLUCION.md](RESUMEN-FINAL-SOLUCION.md)** - Resumen ejecutivo completo ⭐
- **[SIGUIENTE-PASO.md](SIGUIENTE-PASO.md)** - Pasos inmediatos a seguir ⭐
- **[ACCION-INMEDIATA.md](ACCION-INMEDIATA.md)** - Acción requerida urgente ⭐

### Guías de Solución
- **[SOLUCION-TOOL-SAFETY-STATUS.md](SOLUCION-TOOL-SAFETY-STATUS.md)** - Guía detallada del problema
- **[FAQ-TOOL-SAFETY-STATUS.md](FAQ-TOOL-SAFETY-STATUS.md)** - 15 preguntas frecuentes
- **[DIAGRAMA-SOLUCION-TOOL-SAFETY.txt](DIAGRAMA-SOLUCION-TOOL-SAFETY.txt)** - Diagrama visual

### Índice Completo
- **[INDICE-DOCUMENTACION.md](INDICE-DOCUMENTACION.md)** - Índice de toda la documentación

---

## 🏗️ Arquitectura

```
Usuario (Teléfono)
    ↓
Amazon Connect (Agente Luna)
    ↓
AgentCore Gateway (gateway_salud-mcp-server-odybaqqqx2)
    ↓ Lee OpenAPI desde S3
    ↓
API Gateway (https://wldr2xok2d.execute-api.us-east-1.amazonaws.com/dev)
    ↓
AWS Lambda (5 funciones)
    ↓
DynamoDB (salud-api-stack-TurnosTable-1LLEZVIWYG3RI)
```

---

## 🔧 Componentes

### Lambdas
1. **CreateTurnoFunction** - Crear turnos
2. **ModifyTurnoFunction** - Modificar turnos
3. **CancelTurnoFunction** - Cancelar turnos
4. **GetTurnosPacienteFunction** - Obtener turnos de un paciente
5. **BuscarMedicosFunction** - Buscar médicos por especialidad

### OpenAPI
- **Archivo:** `documentos_salud_connect_ia/turnos-medicos-api-openapi-CORREGIDO.yaml`
- **Versión:** 3.0.1
- **Ubicación S3:** `s3://salud-api-stack-openapibucket-korvxxrkhifa/openapi.yaml`

### Gateway
- **Nombre:** gateway_salud-mcp-server-odybaqqqx2
- **Tipo:** AgentCore Gateway
- **Función:** Genera tools automáticamente desde el OpenAPI

### Agente
- **Nombre:** Luna
- **Plataforma:** Amazon Connect
- **Función:** Asistente virtual para gestión de turnos

---

## 📋 Checklist de Validación

- [x] Diagnóstico completo ejecutado
- [x] OpenAPI v3 con x-amazon-connect-tool-safety
- [x] Archivos subidos a S3
- [x] Documentación completa creada
- [ ] Gateway recargado (Edit → Save → 30s)
- [ ] Agente Unpublish/Publish (15s)
- [ ] Tool Safety Status = "Destructive"
- [ ] Test de creación exitoso
- [ ] Turno en DynamoDB confirmado

---

## 🧪 Tests

### Ejecutar Diagnóstico Completo
```bash
python diagnostico/full_system_diagnosis.py
```

### Ejecutar Tests de Lambda Analyzer
```bash
python -m pytest diagnostico/test_lambda_analyzer.py -v
```

### Verificar Tool Safety
```powershell
.\diagnostico\verificar_tool_safety.ps1
```

### Validar Deployment
```powershell
.\diagnostico\validate_deployment.ps1
```

---

## 🔍 Troubleshooting

### El tool no se ejecuta
1. Verificar Tool Safety Status (debe ser "Destructive")
2. Verificar User Confirmation (debe estar DESACTIVADO)
3. Ver logs del agente
4. Ver logs del API Gateway

### Tool Safety Status en "Unspecified"
1. Verificar que el OpenAPI tenga x-amazon-connect-tool-safety
2. Forzar recarga del gateway (Edit → Save)
3. Unpublish/Publish del agente
4. Esperar 1 minuto

### Ver Logs
```bash
# Logs del API Gateway
aws logs tail /aws/apigateway/salud-api-stack --since 5m --follow

# Logs de Lambda
aws logs tail /aws/lambda/CreateTurnoFunction --since 5m --follow

# Ver turnos en DynamoDB
aws dynamodb scan --table-name salud-api-stack-TurnosTable-1LLEZVIWYG3RI --region us-east-1 --max-items 10
```

---

## 📞 Soporte

### Documentación
- Ver [FAQ-TOOL-SAFETY-STATUS.md](FAQ-TOOL-SAFETY-STATUS.md) para preguntas frecuentes
- Ver [INDICE-DOCUMENTACION.md](INDICE-DOCUMENTACION.md) para índice completo

### Logs
- Ejecutar `diagnostico/verificar_tool_safety.ps1` para verificación
- Revisar logs según [FAQ pregunta #12](FAQ-TOOL-SAFETY-STATUS.md#12-cómo-sé-si-el-tool-se-ejecutó-correctamente)

---

## 🔄 Historial

### 2026-02-06
- ✅ Diagnóstico completo del sistema
- ✅ Identificada causa raíz: Tool Safety Status "Unspecified"
- ✅ Creado OpenAPI v3 con x-amazon-connect-tool-safety
- ✅ Subidos archivos a S3
- ✅ Documentación completa creada
- ⏳ Pendiente: Validación del usuario

### 2026-01-30
- ✅ Diagnóstico inicial
- ✅ Identificada inconsistencia OpenAPI-Lambda
- ✅ Creadas herramientas de diagnóstico

---

## 📄 Licencia

MIT License

---

## 👥 Autores

- **Nicolas Sanguinetti** - CloudHesive LATAM

---

## 🔗 Enlaces Útiles

- [AWS Console](https://console.aws.amazon.com/)
- [Amazon Connect](https://console.aws.amazon.com/connect/)
- [Amazon Bedrock](https://console.aws.amazon.com/bedrock/)
- [S3 Bucket](https://s3.console.aws.amazon.com/s3/buckets/salud-api-stack-openapibucket-korvxxrkhifa)

---

**Última actualización:** 2 de Febrero de 2026  
**Versión:** 1.0  
**Estado:** Solución implementada - Pendiente validación
