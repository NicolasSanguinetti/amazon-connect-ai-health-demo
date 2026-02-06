# Implementation Plan: Diagnóstico y Corrección de Actualización de Turnos

## Overview

Este plan implementa un proceso sistemático para diagnosticar y resolver el problema de actualización de turnos en el sistema médico. El enfoque es incremental: primero diagnosticar, luego corregir, validar, y finalmente desplegar. Cada tarea construye sobre las anteriores y valida la funcionalidad antes de proceder.

## Tasks

- [x] 1. Crear herramientas de diagnóstico
  - [x] 1.1 Implementar analizador de código Lambda
    - Crear función `analyze_lambda_code()` que extraiga campos procesados del código
    - Crear función `extract_update_expression_fields()` que identifique campos en UpdateExpression
    - Validar con el código actual de ModifyTurnoFunction
    - _Requirements: 1.1, 1.2_

  - [x] 1.2 Implementar comparador de lambdas
    - Crear función `compare_field_handling()` que compare ModifyTurno vs CreateTurno
    - Identificar diferencias en procesamiento de fechaTurno/horaTurno
    - Generar reporte de diferencias
    - _Requirements: 1.2_

  - [x] 1.3 Implementar analizador de logs de CloudWatch
    - Crear función `analyze_cloudwatch_logs()` que busque patrones en logs
    - Extraer request bodies de logs para verificar campos recibidos
    - Identificar si fechaTurno/horaTurno llegan a la lambda
    - _Requirements: 1.3_

  - [x] 1.4 Escribir property test para analizador de código
    - **Property 1: UpdateExpression Field Detection**
    - **Validates: Requirements 1.1**

- [-] 2. Crear validador de consistencia OpenAPI-Lambda
  - [x] 2.1 Implementar extractor de campos de OpenAPI
    - Parsear turnos-medicos-api-openapi.yaml
    - Extraer campos del requestBody para /turnos/modificar
    - Crear función `extract_request_fields()`
    - _Requirements: 2.1, 2.2_

  - [x] 2.2 Implementar validador de consistencia
    - Crear función `validate_openapi_lambda_consistency()`
    - Comparar campos de OpenAPI vs campos procesados en lambda
    - Generar ConsistencyReport con discrepancias
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ] 2.3 Escribir property test para validador de consistencia
    - **Property 6: OpenAPI-Lambda Consistency Detection**
    - **Validates: Requirements 2.1, 2.2**

- [ ] 3. Checkpoint - Ejecutar diagnóstico completo
  - Ejecutar todas las herramientas de diagnóstico contra el sistema actual
  - Revisar reportes generados
  - Documentar hallazgos específicos del problema
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implementar Enhanced Logger para Lambda
  - [ ] 4.1 Crear clase EnhancedLogger
    - Implementar `log_request()` para registrar body completo
    - Implementar `log_update_expression()` para registrar expresión y valores
    - Implementar `log_update_result()` para registrar atributos actualizados
    - Implementar `log_error()` con stack trace y contexto
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ] 4.2 Escribir unit tests para EnhancedLogger
    - Test log_request con diferentes event structures
    - Test log_update_expression con diferentes expresiones
    - Test log_error con diferentes tipos de excepciones
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ] 4.3 Escribir property test para requestId consistency
    - **Property 13: RequestId Consistency**
    - **Validates: Requirements 3.5**

- [ ] 5. Implementar validador de disponibilidad de horarios
  - [ ] 5.1 Crear función check_availability
    - Implementar query a DynamoDB para buscar turnos conflictivos
    - Implementar lógica de exclusión del turno actual
    - Retornar AvailabilityResult con detalles del conflicto
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ] 5.2 Integrar validación en el flujo de modificación
    - Llamar check_availability antes de ejecutar update
    - Retornar 409 si hay conflicto
    - Registrar detalles del conflicto en logs
    - _Requirements: 4.1, 4.2, 4.4_

  - [ ] 5.3 Escribir property test para detección de conflictos
    - **Property 14: Availability Conflict Detection**
    - **Validates: Requirements 4.1, 4.2**

  - [ ] 5.4 Escribir property test para auto-exclusión
    - **Property 15: Self-Exclusion in Availability Check**
    - **Validates: Requirements 4.3**

- [ ] 6. Corregir y mejorar ModifyTurnoFunction
  - [ ] 6.1 Integrar EnhancedLogger en el handler
    - Reemplazar print statements con EnhancedLogger
    - Agregar logging de request, update expression, y resultados
    - Mantener formato JSON estructurado
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ] 6.2 Verificar procesamiento de campos alternativos
    - Confirmar que acepta fechaTurno/fecha y horaTurno/hora
    - Verificar que ambos formatos se incluyen en UpdateExpression
    - Agregar logging explícito de campos procesados
    - _Requirements: 5.1, 5.2_

  - [ ] 6.3 Integrar validación de disponibilidad
    - Agregar llamada a check_availability antes de update
    - Implementar manejo de conflictos con respuesta 409
    - Agregar logging de validación
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ] 6.4 Mejorar manejo de respuestas
    - Asegurar que ReturnValues='ALL_NEW' esté configurado
    - Incluir turno completo actualizado en respuesta
    - Verificar statusCode 200 para éxito
    - _Requirements: 5.3, 5.5_

  - [ ] 6.5 Escribir property test para aceptación de nombres alternativos
    - **Property 17: Alternative Field Name Acceptance**
    - **Validates: Requirements 5.1, 5.2**

  - [ ] 6.6 Escribir property test para preservación de campos
    - **Property 18: Field Preservation Invariant**
    - **Validates: Requirements 5.4**

  - [ ] 6.7 Escribir property test para formato de respuesta
    - **Property 19: Successful Update Response Format**
    - **Validates: Requirements 5.3, 5.5**

- [ ] 7. Checkpoint - Validar lambda corregida localmente
  - Ejecutar todos los tests unitarios y property tests
  - Simular requests con diferentes combinaciones de campos
  - Verificar logs generados
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Actualizar template de CloudFormation
  - [ ] 8.1 Actualizar código de ModifyTurnoFunction en template
    - Reemplazar ZipFile con código corregido
    - Mantener configuración existente (Runtime, Role, Environment)
    - Verificar que no se cambien nombres de recursos
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ] 8.2 Validar template de CloudFormation
    - Ejecutar `aws cloudformation validate-template`
    - Verificar que no hay errores de sintaxis
    - Confirmar que recursos existentes no se reemplazan
    - _Requirements: 6.1, 6.2_

  - [ ] 8.3 Crear changeset para preview
    - Ejecutar `aws cloudformation create-change-set`
    - Revisar cambios propuestos
    - Verificar que solo ModifyTurnoFunction se actualiza
    - _Requirements: 6.1, 6.3_

- [ ] 9. Actualizar especificación OpenAPI si necesario
  - [ ] 9.1 Revisar consistencia de campos en OpenAPI
    - Verificar que /turnos/modificar incluya fechaTurno y horaTurno
    - Verificar descripciones y ejemplos
    - Confirmar que tipos de datos sean correctos
    - _Requirements: 2.1, 2.2_

  - [ ] 9.2 Actualizar OpenAPI en S3 si hay cambios
    - Subir archivo actualizado al bucket del stack
    - Usar timestamp para cache busting si necesario
    - Documentar cambios realizados
    - _Requirements: 6.5, 7.2_

- [ ] 10. Desplegar actualización del stack
  - [ ] 10.1 Ejecutar update del stack de CloudFormation
    - Aplicar changeset creado anteriormente
    - Monitorear eventos del stack durante actualización
    - Verificar que UPDATE_COMPLETE sin errores
    - _Requirements: 6.2, 6.3, 6.4_

  - [ ] 10.2 Verificar despliegue de nueva versión de lambda
    - Confirmar que ModifyTurnoFunction tiene nueva versión
    - Verificar código actualizado en AWS Console
    - Revisar configuración de la lambda
    - _Requirements: 6.4_

  - [ ] 10.3 Forzar recarga de caché del MCP Server
    - Ejecutar Unpublish del agente Luna en Amazon Connect
    - Esperar 10 segundos
    - Ejecutar Publish del agente Luna
    - Verificar que agente esté activo
    - _Requirements: 6.5, 7.1, 7.3, 7.4_

- [ ] 11. Validación end-to-end
  - [ ] 11.1 Probar modificación de turno con fechaTurno/horaTurno
    - Crear turno de prueba
    - Modificar usando nombres estándar (fechaTurno, horaTurno)
    - Verificar actualización en DynamoDB
    - Revisar logs de CloudWatch
    - _Requirements: 5.1, 5.2, 5.3, 5.5_

  - [ ] 11.2 Probar modificación de turno con fecha/hora
    - Modificar turno usando nombres alternativos (fecha, hora)
    - Verificar actualización en DynamoDB
    - Confirmar que ambos formatos funcionan
    - _Requirements: 5.1, 5.2_

  - [ ] 11.3 Probar validación de disponibilidad
    - Crear dos turnos para el mismo médico
    - Intentar modificar uno al horario del otro
    - Verificar respuesta 409 con detalles del conflicto
    - Revisar logs de conflicto
    - _Requirements: 4.1, 4.2, 4.4_

  - [ ] 11.4 Probar preservación de campos
    - Modificar solo fecha de un turno
    - Verificar que hora y otros campos se preserven
    - Modificar solo hora
    - Verificar que fecha y otros campos se preserven
    - _Requirements: 5.4_

  - [ ] 11.5 Verificar logging mejorado
    - Revisar logs de CloudWatch para ejecuciones recientes
    - Confirmar presencia de request body completo
    - Confirmar logging de UpdateExpression
    - Confirmar logging de resultados
    - Verificar requestId en todos los logs
    - _Requirements: 3.1, 3.2, 3.3, 3.5_

- [ ] 12. Documentar proceso de actualización
  - [ ] 12.1 Crear guía de actualización de lambdas
    - Documentar pasos para modificar código en template
    - Incluir comandos AWS CLI específicos
    - Documentar proceso de validación y despliegue
    - _Requirements: 8.1, 8.2_

  - [ ] 12.2 Documentar proceso de actualización de OpenAPI
    - Documentar cómo actualizar spec en S3
    - Incluir proceso de cache busting
    - Documentar Unpublish/Publish del agente
    - _Requirements: 8.2, 8.3_

  - [ ] 12.3 Crear guía de troubleshooting
    - Documentar problemas comunes identificados
    - Incluir comandos para diagnóstico
    - Agregar ejemplos de logs de error y éxito
    - _Requirements: 8.4_

  - [ ] 12.4 Documentar ejemplos de requests/responses
    - Incluir ejemplos para cada endpoint
    - Mostrar ambos formatos de nombres de campos
    - Incluir ejemplos de respuestas de error
    - _Requirements: 8.5_

  - [ ] 12.5 Actualizar PROBLEMAS-COMUNES-Y-SOLUCIONES.md
    - Agregar sección sobre este problema específico
    - Documentar causa raíz identificada
    - Documentar solución implementada
    - Incluir lecciones aprendidas
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 13. Checkpoint final - Validación completa
  - Revisar todos los tests (unitarios y property-based)
  - Confirmar que validación end-to-end pasó
  - Verificar documentación completa
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- El código de ModifyTurnoFunction ya incluye lógica para aceptar ambos formatos de campos, pero necesita mejoras en logging y validación
- La actualización del stack debe ser cuidadosa para no reemplazar recursos innecesariamente
- El proceso de Unpublish/Publish es crítico para forzar recarga del caché del MCP Server
