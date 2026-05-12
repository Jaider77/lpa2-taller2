from flask import Flask, render_template, request, send_file, abort
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from io import BytesIO
import os

app = Flask(__name__)
BACKEND_URL = os.getenv('BACKEND_URL') or os.getenv('BACKEND_API_URL', 'http://backend:8000')

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
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = styles['Normal']
        header_style = styles['Heading2']
        elements = []

        # Adicionar el Título, ID
        elements.append(Paragraph('Factura', title_style))
        elements.append(Spacer(1, 4 * mm))
        elements.append(Paragraph(f'Número de factura: {factura["numero_factura"]}', normal_style))
        elements.append(Paragraph(f'Fecha de emisión: {factura["fecha_emision"]}', normal_style))
        elements.append(Spacer(1, 6 * mm))

        # Agregar Información de la Empresa
        elements.append(Paragraph('Información de la empresa', header_style))
        elements.append(Spacer(1, 2 * mm))
        elements.append(Paragraph(f'Nombre: {factura["empresa"]["nombre"]}', normal_style))
        elements.append(Paragraph(f'Dirección: {factura["empresa"]["direccion"]}', normal_style))
        elements.append(Paragraph(f'Teléfono: {factura["empresa"]["telefono"]}', normal_style))
        elements.append(Paragraph(f'Email: {factura["empresa"]["email"]}', normal_style))
        elements.append(Spacer(1, 6 * mm))

        # Agregar Información del Cliente
        elements.append(Paragraph('Información del cliente', header_style))
        elements.append(Spacer(1, 2 * mm))
        elements.append(Paragraph(f'Nombre: {factura["cliente"]["nombre"]}', normal_style))
        elements.append(Paragraph(f'Dirección: {factura["cliente"]["direccion"]}', normal_style))
        elements.append(Paragraph(f'Teléfono: {factura["cliente"]["telefono"]}', normal_style))
        elements.append(Spacer(1, 6 * mm))

        # Adicionar el Detalle de la Factura: cantidad, descripción, precio unitario y total
        detalle_data = [[
            'Cantidad',
            'Descripción',
            'Precio unitario',
            'Total'
        ]]
        for item in factura['detalle']:
            detalle_data.append([
                str(item['cantidad']),
                item['descripcion'],
                f'€ {item["precio_unitario"]:.2f}',
                f'€ {item["total"]:.2f}'
            ])

        detalle_tabla = Table(detalle_data, colWidths=[30 * mm, 85 * mm, 35 * mm, 35 * mm], hAlign='LEFT')
        detalle_tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d3d3d3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
        ]))
        elements.append(detalle_tabla)
        elements.append(Spacer(1, 6 * mm))

        # Adicionar Subtotal, impuesto y Total
        totales_data = [
            ['Subtotal', f'€ {factura["subtotal"]:.2f}'],
            ['Impuesto (21%)', f'€ {factura["impuesto"]:.2f}'],
            ['Total', f'€ {factura["total"]:.2f}'],
        ]
        totales_tabla = Table(totales_data, colWidths=[120 * mm, 65 * mm], hAlign='RIGHT')
        totales_tabla.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (-1, -2), colors.black),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(totales_tabla)
        elements.append(Spacer(1, 4 * mm))

        # Generar el doc y limpiar el buffer
        doc.build(elements)
        buffer.seek(0)
        
        # TODO: Retornar a la página el PDF para visualizar y descargar

        
    except requests.exceptions.ConnectionError:
        abort(503, description="Error de conexión con el servidor")
    except Exception as e:
        abort(500, description=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)

