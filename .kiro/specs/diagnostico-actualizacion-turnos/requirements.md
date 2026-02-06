# Requirements Document

## Introduction

Este documento especifica los requisitos para diagnosticar y resolver problemas en el sistema de turnos médicos desplegado en AWS. El sistema utiliza Amazon Connect + API Gateway + Lambda + DynamoDB y tiene un agente de IA "Luna" integrado con MCP Server. El problema principal es que la lambda de modificar turnos no actualiza correctamente los campos `fechaTurno` y `horaTurno` en DynamoDB, aunque la lambda de crear turnos funciona correctamente.

## Glossary

- **Sistema**: El conjunto completo de componentes del sistema de turnos médicos (CloudFormation stack, lambdas, DynamoDB, API Gateway, Amazon Connect, agente Luna)
- **Lambda_Modificar**: La función Lambda `ModifyTurnoFunction` que actualiza turnos existentes
- **Lambda_Crear**: La función Lambda `CreateTurnoFunction` que crea nuevos turnos
- **DynamoDB_Turnos**: La tabla DynamoDB `TurnosTable` que almacena los turnos médicos
- **Agente_Luna**: El agente de IA integrado con Amazon Connect que interactúa con los pacientes
- **MCP_Server**: El servidor MCP que expone la especificación OpenAPI al agente
- **OpenAPI_Spec**: La especificación OpenAPI que define los endpoints y contratos de la API
- **CloudFormation_Stack**: El stack de CloudFormation `salud-api-stack` que despliega toda la infraestructura
- **Cache_MCP**: El sistema de caché de Amazon Connect que almacena la especificación OpenAPI

## Requirements

### Requirement 1: Diagnóstico de Actualización de Turnos

**User Story:** Como desarrollador, quiero diagnosticar por qué la Lambda_Modificar no actualiza correctamente los campos de fecha y hora, para que pueda identificar la causa raíz del problema.

#### Acceptance Criteria

1. WHEN se analiza el código de Lambda_Modificar, THE Sistema SHALL identificar si los campos `fechaTurno` y `horaTurno` están siendo procesados correctamente en el UpdateExpression
2. WHEN se comparan Lambda_Modificar y Lambda_Crear, THE Sistema SHALL identificar diferencias en el manejo de campos de fecha y hora
3. WHEN se revisan los logs de CloudWatch, THE Sistema SHALL identificar si los valores de `fechaTurno` y `horaTurno` están llegando al handler de la lambda
4. WHEN se examina el request body recibido, THE Sistema SHALL verificar si el Agente_Luna está enviando los nombres de campos correctos
5. WHEN se valida la estructura del UpdateExpression, THE Sistema SHALL verificar que la sintaxis de DynamoDB sea correcta

### Requirement 2: Validación de Consistencia OpenAPI-Lambda

**User Story:** Como desarrollador, quiero verificar la consistencia entre la OpenAPI_Spec y las implementaciones de las lambdas, para que el Agente_Luna y las lambdas usen los mismos nombres de campos.

#### Acceptance Criteria

1. WHEN se compara OpenAPI_Spec con Lambda_Modificar, THE Sistema SHALL identificar discrepancias en nombres de campos entre la especificación y la implementación
2. WHEN se compara OpenAPI_Spec con Lambda_Crear, THE Sistema SHALL verificar que los nombres de campos sean consistentes
3. WHEN se detectan inconsistencias, THE Sistema SHALL generar un reporte con los campos que no coinciden
4. WHEN se valida el endpoint `/turnos/modificar`, THE Sistema SHALL verificar que todos los campos del requestBody estén siendo procesados por la lambda

### Requirement 3: Mejora de Logging y Debugging

**User Story:** Como desarrollador, quiero mejorar el logging en las lambdas, para que pueda diagnosticar problemas más fácilmente en el futuro.

#### Acceptance Criteria

1. WHEN Lambda_Modificar recibe un request, THE Sistema SHALL registrar en logs el body completo recibido con nivel INFO
2. WHEN Lambda_Modificar construye el UpdateExpression, THE Sistema SHALL registrar la expresión completa y los valores antes de ejecutar la actualización
3. WHEN Lambda_Modificar completa la actualización, THE Sistema SHALL registrar los atributos actualizados retornados por DynamoDB
4. WHEN ocurre un error en Lambda_Modificar, THE Sistema SHALL registrar el stack trace completo y el contexto del error
5. WHEN se ejecuta cualquier lambda, THE Sistema SHALL incluir el requestId en todos los mensajes de log para trazabilidad

### Requirement 4: Validación de Disponibilidad de Horarios

**User Story:** Como desarrollador, quiero implementar validación de disponibilidad de horarios al modificar turnos, para que no se permitan modificaciones a horarios ya ocupados.

#### Acceptance Criteria

1. WHEN se modifica un turno a una nueva fecha y hora, THE Sistema SHALL verificar que el horario esté disponible para el médico especificado
2. WHEN el horario solicitado ya está ocupado, THE Sistema SHALL retornar un error 409 con mensaje descriptivo
3. WHEN se valida disponibilidad, THE Sistema SHALL excluir el turno actual de la búsqueda de conflictos
4. WHEN la validación falla, THE Sistema SHALL registrar en logs el turnoId conflictivo y los detalles del conflicto

### Requirement 5: Corrección de Lambda de Modificación

**User Story:** Como desarrollador, quiero corregir el código de Lambda_Modificar, para que actualice correctamente todos los campos solicitados en DynamoDB_Turnos.

#### Acceptance Criteria

1. WHEN Lambda_Modificar recibe `fechaTurno` o `fecha`, THE Sistema SHALL incluir el campo en el UpdateExpression con el valor correcto
2. WHEN Lambda_Modificar recibe `horaTurno` o `hora`, THE Sistema SHALL incluir el campo en el UpdateExpression con el valor correcto
3. WHEN Lambda_Modificar ejecuta la actualización, THE Sistema SHALL retornar los atributos actualizados en la respuesta
4. WHEN se actualiza un turno, THE Sistema SHALL preservar todos los campos existentes que no fueron modificados
5. WHEN la actualización es exitosa, THE Sistema SHALL retornar statusCode 200 con el turno actualizado completo

### Requirement 6: Actualización del Stack de CloudFormation

**User Story:** Como desarrollador, quiero actualizar el CloudFormation_Stack con las correcciones, para que los cambios se desplieguen en el ambiente de producción.

#### Acceptance Criteria

1. WHEN se actualiza el template de CloudFormation, THE Sistema SHALL preservar todos los recursos existentes sin reemplazos innecesarios
2. WHEN se ejecuta el update del stack, THE Sistema SHALL completar sin errores de validación
3. WHEN el stack se actualiza, THE Sistema SHALL mantener las mismas URLs de API Gateway y nombres de recursos
4. WHEN la actualización completa, THE Sistema SHALL verificar que las nuevas versiones de las lambdas estén desplegadas
5. WHEN se despliegan cambios en OpenAPI_Spec, THE Sistema SHALL actualizar el archivo en S3 y forzar la recarga del Cache_MCP

### Requirement 7: Gestión de Caché del MCP Server

**User Story:** Como desarrollador, quiero implementar un proceso para forzar la recarga del Cache_MCP, para que los cambios en OpenAPI_Spec se reflejen inmediatamente en el Agente_Luna.

#### Acceptance Criteria

1. WHEN se actualiza OpenAPI_Spec en S3, THE Sistema SHALL documentar el proceso de Unpublish/Publish del agente
2. WHEN se requiere cache busting, THE Sistema SHALL proporcionar comandos para agregar timestamps a la URL del OpenAPI
3. WHEN se actualiza el agente, THE Sistema SHALL esperar al menos 10 segundos entre Unpublish y Publish
4. WHEN se completa el proceso, THE Sistema SHALL validar que el agente esté usando la nueva versión del OpenAPI

### Requirement 8: Documentación de Proceso de Actualización

**User Story:** Como desarrollador, quiero documentar el proceso completo de actualización del sistema, para que futuros cambios puedan realizarse de manera consistente y sin errores.

#### Acceptance Criteria

1. WHEN se documenta el proceso, THE Sistema SHALL incluir todos los pasos necesarios para actualizar lambdas
2. WHEN se documenta el proceso, THE Sistema SHALL incluir comandos específicos de AWS CLI para cada operación
3. WHEN se documenta el proceso, THE Sistema SHALL incluir el proceso de validación post-despliegue
4. WHEN se documenta el proceso, THE Sistema SHALL incluir troubleshooting para problemas comunes identificados
5. WHEN se actualiza la documentación, THE Sistema SHALL incluir ejemplos de requests y responses esperados para cada endpoint
