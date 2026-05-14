from flask import Flask, render_template, request, abort, Response, jsonify
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import os
from datetime import datetime
from registro import registro_global

app = Flask(__name__)
BACKEND_URL = os.getenv('BACKEND_URL') or os.getenv('BACKEND_API_URL', 'http://backend:8000')

def crear_estilos_personalizados():
    """Crea estilos personalizados para el PDF con diseño profesional"""
    estilos = getSampleStyleSheet()
    
    # Estilo para el título principal
    estilos.add(ParagraphStyle(
        name='TituloPrincipal',
        parent=estilos['Heading1'],
        fontSize=40,
        textColor=colors.HexColor('#ffffff'),
        spaceAfter=6,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        leading=45,
    ))
    
    # Estilo para subtítulo
    estilos.add(ParagraphStyle(
        name='Subtitulo',
        parent=estilos['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#9ca3af'),
        spaceAfter=2,
        fontName='Helvetica',
        alignment=TA_CENTER,
    ))
    
    # Estilo para encabezados de sección con fondo
    estilos.add(ParagraphStyle(
        name='EncabezadoSeccion',
        parent=estilos['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#ffffff'),
        spaceAfter=4,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        leading=14,
    ))
    
    # Estilo para texto normal
    estilos.add(ParagraphStyle(
        name='TextoNormal',
        parent=estilos['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=3,
        leading=13,
    ))
    
    # Estilo para labels
    estilos.add(ParagraphStyle(
        name='Label',
        parent=estilos['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#ffffff'),
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
    ))
    
    # Estilo para datos empresariales
    estilos.add(ParagraphStyle(
        name='DatosEmpresa',
        parent=estilos['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=2,
        leading=12,
    ))
    
    # Estilo para encabezado de número de factura
    estilos.add(ParagraphStyle(
        name='NumeroFactura',
        parent=estilos['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#2563eb'),
        fontName='Helvetica-Bold',
        spaceAfter=2,
        alignment=TA_LEFT,
    ))
    
    # Estilo para pie de página
    estilos.add(ParagraphStyle(
        name='PieStyle',
        parent=estilos['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=0,
    ))
    
    return estilos


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/historial')
def historial():
    """Página de historial de descargas"""
    return render_template('historial.html')

@app.route('/generar-pdf', methods=['POST'])
def generar_pdf():
    try:
        id_factura = request.form.get('id_factura', '').strip()
        
        # Validación del ID de factura
        if not id_factura:
            abort(400, description="ID de factura es requerido")
            
        response = requests.get(f'{BACKEND_URL}/facturas/v1/{id_factura}')
        
        if response.status_code != 200:
            abort(404, description="Factura no encontrada")
            
        factura = response.json()
        
        # Validación de estructura de factura
        required_keys = ['numero_factura', 'fecha_emision', 'empresa', 'cliente', 'detalle', 'subtotal', 'impuesto', 'total']
        if not all(key in factura for key in required_keys):
            abort(500, description="Estructura de factura inválida")
        
        # Crear buffer y doc para la creación del PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )
        
        # Obtener estilos personalizados
        estilos = crear_estilos_personalizados()
        elements = []

        # ========== ENCABEZADO CON GRADIENTE ==========
        encabezado_tabla = Table(
            [[Paragraph('FACTURA', estilos['TituloPrincipal'])]], 
            colWidths=[170 * mm]
        )
        encabezado_tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2563eb')),
            ('TOPPADDING', (0, 0), (-1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(encabezado_tabla)
        
        # Línea decorativa
        linea_decorator = Table([['']], colWidths=[170 * mm])
        linea_decorator.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(linea_decorator)
        elements.append(Spacer(1, 8 * mm))

        # Información de factura en tres columnas
        info_data = [
            [
                Paragraph(f'<b>Nº Factura:</b><br/><font size="14" color="#2563eb" face="Helvetica-Bold">{factura["numero_factura"]}</font>', estilos['DatosEmpresa']),
                Paragraph(f'<b>Fecha de Emisión:</b><br/><font size="11">{factura["fecha_emision"]}</font>', estilos['DatosEmpresa']),
                Paragraph(f'<b>Estado:</b><br/><font size="11" color="#10b981"><b>Emitida</b></font>', estilos['DatosEmpresa']),
            ]
        ]
        info_tabla = Table(info_data, colWidths=[55 * mm, 55 * mm, 55 * mm])
        info_tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bfdbfe')),
        ]))
        elements.append(info_tabla)
        elements.append(Spacer(1, 10 * mm))

        # ========== INFORMACIÓN DE EMPRESA Y CLIENTE ==========
        empresa_cliente = [
            [
                Paragraph('<b>DATOS DE LA EMPRESA</b>', estilos['EncabezadoSeccion']),
                Paragraph('<b>DATOS DEL CLIENTE</b>', estilos['EncabezadoSeccion']),
            ]
        ]
        
        empresa_text = f"""
        <font size="11"><b>{factura['empresa']['nombre']}</b></font><br/>
        <font size="9">{factura['empresa']['direccion']}</font><br/>
        <font size="9">📞 {factura['empresa']['telefono']}</font><br/>
        <font size="9">📧 {factura['empresa']['email']}</font><br/>
        <font size="8" color="#6b7280">CIF: {factura['empresa'].get('cif', 'N/A')}</font>
        """
        
        cliente_text = f"""
        <font size="11"><b>{factura['cliente']['nombre']}</b></font><br/>
        <font size="9">{factura['cliente']['direccion']}</font><br/>
        <font size="9">📞 {factura['cliente']['telefono']}</font><br/>
        <font size="8" color="#6b7280">NIF: {factura['cliente'].get('nif', 'N/A')}</font>
        """
        
        empresa_cliente.append([
            Paragraph(empresa_text, estilos['DatosEmpresa']),
            Paragraph(cliente_text, estilos['DatosEmpresa']),
        ])
        
        empresa_cliente_table = Table(empresa_cliente, colWidths=[85 * mm, 85 * mm])
        empresa_cliente_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ]))
        elements.append(empresa_cliente_table)
        elements.append(Spacer(1, 10 * mm))

        # ========== DETALLE DE ITEMS ==========
        elements.append(Paragraph('DETALLE DE ARTÍCULOS', estilos['EncabezadoSeccion']))
        elements.append(Spacer(1, 4 * mm))
        
        detalle_data = [[
            Paragraph('QTY', estilos['Label']),
            Paragraph('DESCRIPCIÓN', estilos['Label']),
            Paragraph('PRECIO UNIT.', estilos['Label']),
            Paragraph('DESCUENTO', estilos['Label']),
            Paragraph('TOTAL', estilos['Label']),
        ]]
        
        subtotal_items = 0
        for idx, item in enumerate(factura['detalle']):
            descuento = item.get('descuento', 0)
            detalle_data.append([
                Paragraph(f"<b>{item['cantidad']}</b>", estilos['TextoNormal']),
                Paragraph(item['descripcion'][:35], estilos['TextoNormal']),
                Paragraph(f"€{item['precio_unitario']:.2f}", estilos['TextoNormal']),
                Paragraph(f"€{descuento:.2f}", estilos['TextoNormal']),
                Paragraph(f"<b>€{item['total']:.2f}</b>", estilos['TextoNormal']),
            ])
            subtotal_items += 1

        detalle_tabla = Table(detalle_data, colWidths=[15 * mm, 75 * mm, 30 * mm, 25 * mm, 25 * mm], hAlign='LEFT')
        detalle_tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(detalle_tabla)
        elements.append(Spacer(1, 10 * mm))

        # ========== TOTALES ==========
        totales_data = [
            [
                Paragraph('<b style="font-size: 11">Subtotal</b>', estilos['Label']),
                Paragraph(f'<font size="11">€ {factura["subtotal"]:.2f}</font>', estilos['Label']),
            ],
            [
                Paragraph('<b style="font-size: 11">Descuento (si aplica)</b>', estilos['Label']),
                Paragraph(f'<font size="11">€ 0.00</font>', estilos['Label']),
            ],
            [
                Paragraph('<b style="font-size: 11">Impuesto (21%)</b>', estilos['Label']),
                Paragraph(f'<font size="11">€ {factura["impuesto"]:.2f}</font>', estilos['Label']),
            ],
            [
                Paragraph('<b style="font-size: 13">TOTAL</b>', estilos['Label']),
                Paragraph(f'<font size="14" color="#ffffff"><b>€ {factura["total"]:.2f}</b></font>', estilos['Label']),
            ],
        ]
        
        totales_tabla = Table(totales_data, colWidths=[120 * mm, 50 * mm])
        totales_tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 2), colors.HexColor("#4783f3")),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 2), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 2), 11),
            ('FONTSIZE', (0, 3), (-1, 3), 13),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, 2), 1, colors.HexColor("#040f21")),
            ('GRID', (0, 3), (-1, 3), 2, colors.HexColor('#059669')),
        ]))
        elements.append(totales_tabla)
        elements.append(Spacer(1, 12 * mm))

        # Separador final
        linea_final = Table([['']], colWidths=[170 * mm])
        linea_final.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e5e7eb')),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        elements.append(linea_final)
        elements.append(Spacer(1, 8 * mm))
        
        # Pie de página con información
        pie_text = f"<b>Condiciones de Pago:</b> Contado | <b>Fecha de Emisión:</b> {datetime.now().strftime('%d/%m/%Y')}<br/><font size='8' color='#9ca3af'>Factura generada automáticamente el {datetime.now().strftime('%H:%M')} - Gracias por su confianza.</font>"
        elements.append(Paragraph(pie_text, estilos['PieStyle']))

        # Generar el doc y limpiar el buffer
        doc.build(elements)
        buffer.seek(0)
        
        # Obtener IP del cliente
        ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        # Registrar la descarga
        detalles = {
            "empresa": factura.get('empresa', {}).get('nombre', 'N/A'),
            "cliente": factura.get('cliente', {}).get('nombre', 'N/A'),
            "total": factura.get('total', 0)
        }
        registro_global.registrar_descarga(
            id_factura=id_factura,
            ip_cliente=ip_cliente,
            estado='exitosa',
            detalles=detalles
        )
        
        # Retornar el PDF como respuesta directa para que se muestre en el iframe
        response = Response(buffer.getvalue(), mimetype='application/pdf')
        response.headers['Content-Disposition'] = 'inline; filename=factura_{}.pdf'.format(id_factura)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except requests.exceptions.ConnectionError:
        abort(503, description="Error de conexión con el servidor backend")
    except Exception as e:
        abort(500, description=str(e))

@app.route('/api/historial', methods=['GET'])
def obtener_historial():
    """Retorna el historial completo de descargas en formato JSON"""
    try:
        historial = registro_global.obtener_historial()
        return jsonify({
            "success": True,
            "total": len(historial),
            "descargas": historial
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/resumen', methods=['GET'])
def obtener_resumen():
    """Retorna un resumen estadístico del registro de descargas"""
    try:
        resumen = registro_global.obtener_resumen()
        return jsonify({
            "success": True,
            "resumen": resumen
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/historial/<id_factura>', methods=['GET'])
def obtener_historial_factura(id_factura):
    """Retorna el historial de descargas de una factura específica"""
    try:
        historial = registro_global.obtener_historial_por_factura(id_factura)
        return jsonify({
            "success": True,
            "id_factura": id_factura,
            "total": len(historial),
            "descargas": historial
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
