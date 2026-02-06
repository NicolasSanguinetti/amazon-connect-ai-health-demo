"""
Property tests para el analizador de código Lambda.

Feature: diagnostico-actualizacion-turnos
Property 1: UpdateExpression Field Detection
Validates: Requirements 1.1
"""

import unittest
from lambda_analyzer import (
    extract_update_expression_fields,
    extract_processed_fields,
    analyze_lambda_code
)


class TestLambdaAnalyzer(unittest.TestCase):
    """Tests unitarios para el analizador de Lambda."""
    
    def test_extract_update_expression_basic(self):
        """Test básico de extracción de campos de UpdateExpression."""
        code = """
        update_expression = 'SET modifiedAt = :modifiedAt'
        update_expression += ', fechaTurno = :fechaTurno'
        update_expression += ', horaTurno = :horaTurno'
        """
        
        fields = extract_update_expression_fields(code)
        
        self.assertIn('fechaTurno', fields)
        self.assertIn('horaTurno', fields)
    
    def test_extract_processed_fields_python(self):
        """Test de extracción de campos procesados en Python."""
        code = """
        fecha = body.get('fechaTurno') or body.get('fecha')
        hora = body.get('horaTurno') or body.get('hora')
        if 'motivoConsulta' in body:
            motivo = body['motivoConsulta']
        """
        
        fields = extract_processed_fields(code)
        
        self.assertIn('fechaTurno', fields)
        self.assertIn('fecha', fields)
        self.assertIn('horaTurno', fields)
        self.assertIn('hora', fields)
        self.assertIn('motivoConsulta', fields)
    
    def test_extract_processed_fields_javascript(self):
        """Test de extracción de campos procesados en JavaScript."""
        code = """
        const { medicoId, pacienteId, fechaTurno, horaTurno } = body;
        const fecha = body.fechaTurno || body.fecha;
        """
        
        fields = extract_processed_fields(code)
        
        self.assertIn('medicoId', fields)
        self.assertIn('pacienteId', fields)
        self.assertIn('fechaTurno', fields)
        self.assertIn('horaTurno', fields)
    
    def test_analyze_lambda_detects_missing_fecha(self):
        """Test que detecta cuando falta fechaTurno en UpdateExpression."""
        code = """
        def handler(event, context):
            body = json.loads(event['body'])
            update_expression = 'SET modifiedAt = :modifiedAt'
            # No incluye fechaTurno
            table.update_item(UpdateExpression=update_expression)
        """
        
        report = analyze_lambda_code('TestFunction', code)
        
        # Debe encontrar que falta fechaTurno
        fecha_findings = [f for f in report.findings 
                         if 'fecha' in f.description.lower()]
        self.assertTrue(len(fecha_findings) > 0)
    
    def test_analyze_lambda_detects_missing_hora(self):
        """Test que detecta cuando falta horaTurno en UpdateExpression."""
        code = """
        def handler(event, context):
            body = json.loads(event['body'])
            update_expression = 'SET modifiedAt = :modifiedAt'
            # No incluye horaTurno
            table.update_item(UpdateExpression=update_expression)
        """
        
        report = analyze_lambda_code('TestFunction', code)
        
        # Debe encontrar que falta horaTurno
        hora_findings = [f for f in report.findings 
                        if 'hora' in f.description.lower()]
        self.assertTrue(len(hora_findings) > 0)
    
    def test_analyze_lambda_accepts_both_formats(self):
        """Test que verifica detección de aceptación de ambos formatos."""
        code = """
        def handler(event, context):
            body = json.loads(event['body'])
            
            if 'fechaTurno' in body or 'fecha' in body:
                fecha = body.get('fechaTurno') or body.get('fecha')
                update_expression += ', fechaTurno = :fechaTurno'
            
            if 'horaTurno' in body or 'hora' in body:
                hora = body.get('horaTurno') or body.get('hora')
                update_expression += ', horaTurno = :horaTurno'
        """
        
        report = analyze_lambda_code('TestFunction', code)
        
        # No debe tener findings críticos sobre fecha/hora
        critical_fecha_hora = [f for f in report.findings 
                               if f.severity == 'critical' and 
                               ('fecha' in f.description.lower() or 
                                'hora' in f.description.lower())]
        self.assertEqual(len(critical_fecha_hora), 0)


# Property-Based Test usando hypothesis (si está disponible)
try:
    from hypothesis import given, strategies as st
    
    class TestLambdaAnalyzerProperties(unittest.TestCase):
        """Property-based tests para el analizador."""
        
        @given(st.text(min_size=10))
        def test_property_extract_fields_returns_list(self, code):
            """
            Property 1: UpdateExpression Field Detection
            
            Para cualquier código Lambda, extract_update_expression_fields
            debe retornar una lista (posiblemente vacía).
            """
            result = extract_update_expression_fields(code)
            self.assertIsInstance(result, list)
        
        @given(st.text(min_size=10))
        def test_property_extract_processed_returns_list(self, code):
            """
            Para cualquier código Lambda, extract_processed_fields
            debe retornar una lista (posiblemente vacía).
            """
            result = extract_processed_fields(code)
            self.assertIsInstance(result, list)
        
        @given(st.text(min_size=10))
        def test_property_analyze_returns_report(self, code):
            """
            Para cualquier código Lambda, analyze_lambda_code
            debe retornar un DiagnosticReport válido.
            """
            report = analyze_lambda_code('TestFunction', code)
            
            self.assertIsNotNone(report)
            self.assertIsNotNone(report.lambda_name)
            self.assertIsInstance(report.findings, list)
            self.assertIsInstance(report.summary, str)
            self.assertIsInstance(report.requires_code_change, bool)

except ImportError:
    print("hypothesis no está instalado, saltando property-based tests")
    print("Para instalar: pip install hypothesis")


if __name__ == '__main__':
    unittest.main()
