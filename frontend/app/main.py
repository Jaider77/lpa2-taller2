from flask import Flask, render_template, request, send_file, abort
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
import os
from datetime import datetime

app = Flask(__name__)
BACKEND_URL = os.getenv('BACKEND_URL') or os.getenv('BACKEND_API_URL', 'http://backend:8000')

def crear_estilos_personalizados():
    """Crea estilos personalizados para el PDF"""
    estilos = getSampleStyleSheet()
    
    # Estilo para el título principal
    estilos.add(ParagraphStyle(
        name='TituloPrincipal',
        parent=estilos['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=6,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
    ))
    
    # Estilo para encabezados de sección
    estilos.add(ParagraphStyle(
        name='EncabezadoSeccion',
        parent=estilos['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=4,
        fontName='Helvetica-Bold',
        borderBottomWidth=2,
        borderBottomColor=colors.HexColor('#2563eb'),
        borderBottomPadding=4,
    ))
    
    # Estilo para texto normal
    estilos.add(ParagraphStyle(
        name='TextoNormal',
        parent=estilos['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=3,
        leading=12,
    ))
    
    # Estilo para labels
    estilos.add(ParagraphStyle(
        name='Label',
        parent=estilos['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        fontName='Helvetica-Bold',
    ))
    
    return estilos

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar-pdf', methods=['POST'])
def generar_pdf():
    try:
        id_factura = request.form['id_factura']
        response = requests.get(f'{BACKEND_URL}/facturas/v1/{id_factura}')
        
        if response.status_code != 200:
            abort(404, description="Factura no encontrada")
            
        factura = response.json()
        
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

        # ========== ENCABEZADO ==========
        # Título principal
        elements.append(Paragraph('FACTURA', estilos['TituloPrincipal']))
        elements.append(Spacer(1, 2 * mm))
        
        # Línea decorativa
        encabezado_table = Table([['']], colWidths=[170 * mm])
        encabezado_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#dbeafe')),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        elements.append(encabezado_table)
        elements.append(Spacer(1, 6 * mm))
        
        # Número y fecha
        info_data = [
            ['Nº Factura:', factura["numero_factura"], 'Fecha:', factura["fecha_emision"]],
        ]
        info_table = Table(info_data, colWidths=[35 * mm, 50 * mm, 35 * mm, 50 * mm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 6 * mm))

        # ========== INFORMACIÓN DE EMPRESA Y CLIENTE ==========
        empresa_cliente = [
            [
                Paragraph('<b>Datos de la Empresa</b>', estilos['EncabezadoSeccion']),
                Paragraph('<b>Datos del Cliente</b>', estilos['EncabezadoSeccion']),
            ]
        ]
        
        empresa_text = f"""
        <font size="10"><b>{factura['empresa']['nombre']}</b></font><br/>
        {factura['empresa']['direccion']}<br/>
        Tel: {factura['empresa']['telefono']}<br/>
        Email: {factura['empresa']['email']}
        """
        
        cliente_text = f"""
        <font size="10"><b>{factura['cliente']['nombre']}</b></font><br/>
        {factura['cliente']['direccion']}<br/>
        Tel: {factura['cliente']['telefono']}
        """
        
        empresa_cliente.append([
            Paragraph(empresa_text, estilos['TextoNormal']),
            Paragraph(cliente_text, estilos['TextoNormal']),
        ])
        
        empresa_cliente_table = Table(empresa_cliente, colWidths=[85 * mm, 85 * mm])
        empresa_cliente_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(empresa_cliente_table)
        elements.append(Spacer(1, 8 * mm))

        # ========== DETALLE DE ITEMS ==========
        elements.append(Paragraph('Detalle de Factura', estilos['EncabezadoSeccion']))
        elements.append(Spacer(1, 3 * mm))
        
        detalle_data = [[
            Paragraph('<b>Cantidad</b>', estilos['Label']),
            Paragraph('<b>Descripción</b>', estilos['Label']),
            Paragraph('<b>P. Unitario</b>', estilos['Label']),
            Paragraph('<b>Total</b>', estilos['Label']),
        ]]
        
        for idx, item in enumerate(factura['detalle']):
            color_fondo = colors.HexColor('#f3f4f6') if idx % 2 == 0 else colors.white
            detalle_data.append([
                Paragraph(str(item['cantidad']), estilos['TextoNormal']),
                Paragraph(item['descripcion'][:40], estilos['TextoNormal']),
                Paragraph(f'€ {item["precio_unitario"]:.2f}', estilos['TextoNormal']),
                Paragraph(f'€ {item["total"]:.2f}', estilos['TextoNormal']),
            ])

        detalle_tabla = Table(detalle_data, colWidths=[25 * mm, 85 * mm, 35 * mm, 35 * mm], hAlign='LEFT')
        detalle_tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (2, -1), 'RIGHT'),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(detalle_tabla)
        elements.append(Spacer(1, 10 * mm))

        # ========== TOTALES ==========
        totales_data = [
            [Paragraph('<b>Subtotal:</b>', estilos['Label']), Paragraph(f'€ {factura["subtotal"]:.2f}', estilos['TextoNormal'])],
            [Paragraph('<b>Impuesto (21%):</b>', estilos['Label']), Paragraph(f'€ {factura["impuesto"]:.2f}', estilos['TextoNormal'])],
            [Paragraph('<b>TOTAL:</b>', estilos['Label']), Paragraph(f'<font size="12" color="#2563eb"><b>€ {factura["total"]:.2f}</b></font>', estilos['TextoNormal'])],
        ]
        
        totales_tabla = Table(totales_data, colWidths=[135 * mm, 35 * mm], hAlign='RIGHT')
        totales_tabla.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#dbeafe')),
            ('GRID', (0, 1), (-1, 2), 1, colors.HexColor('#2563eb')),
        ]))
        elements.append(totales_tabla)
        elements.append(Spacer(1, 10 * mm))

        # ========== PIE DE PÁGINA ==========
        pie_table = Table([['']], colWidths=[170 * mm])
        pie_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(pie_table)
        
        elements.append(Spacer(1, 2 * mm))
        pie_text = f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} | Gracias por tu compra"
        elements.append(Paragraph(pie_text, estilos['TextoNormal']))

        # Generar el doc y limpiar el buffer
        doc.build(elements)
        buffer.seek(0)
        
        # Retornar a la página el PDF para visualizar y descargar
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'factura_{id_factura}.pdf'
        )
    except requests.exceptions.ConnectionError:
        abort(503, description="Error de conexión con el servidor")
    except Exception as e:
        abort(500, description=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)


