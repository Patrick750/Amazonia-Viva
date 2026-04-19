import csv
import io
import json
from datetime import date
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import PaqueteTuristico, ReservaFecha, Detalles_Venta, Agencia
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class ExportarManifiestoAgenciaAPIView(APIView):
    """
    POST /api/gestion-agencia/logistica/exportar/
    Exporta el manifiesto de pasajeros para agencias.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        paquete_id = request.data.get('paquete_id')
        fecha = request.data.get('fecha')
        formato = request.data.get('formato', 'XLS').upper()

        if not paquete_id or not fecha:
            return HttpResponse(json.dumps({'error': 'Paquete y fecha son requeridos.'}), status=400, content_type='application/json')

        paquete = get_object_or_404(PaqueteTuristico, pk=paquete_id, agencia_id=request.user.pk)
        reservas_fecha = ReservaFecha.objects.filter(paquete=paquete, fecha=fecha).select_related('venta', 'venta__usuario')
        
        if not reservas_fecha.exists():
            return HttpResponse(json.dumps({'error': 'No hay pasajeros registrados para esta fecha.'}), status=404, content_type='application/json')

        turistas_data = []
        for res in reservas_fecha:
            novedades = res.venta.novedades_turistas
            if isinstance(novedades, str):
                try: novedades = json.loads(novedades)
                except: novedades = []
            
            if not isinstance(novedades, list) or not novedades:
                novedades = [{'nombres': res.venta.usuario.first_name, 'apellidos': res.venta.usuario.last_name, 'num_doc': 'N/A'}]

            for i, nov in enumerate(novedades):
                usr = res.venta.usuario
                telefono = None
                if hasattr(usr, 'agencia'): telefono = usr.agencia.numero_telefonico
                elif hasattr(usr, 'proveedor'): telefono = usr.proveedor.numero_telefonico
                elif hasattr(usr, 'turista'): telefono = usr.turista.numero_telefonico
                
                if not telefono: telefono = nov.get('telefono') or nov.get('celular')
                
                turistas_data.append({
                    'nombre': f"{nov.get('nombres', '')} {nov.get('apellidos', '')}".strip() or usr.username,
                    'identificacion': nov.get('num_doc', 'N/A'),
                    'correo': usr.email if i == 0 else 'S/R', 
                    'telefono': telefono or 'S/R',
                    'rol': 'Titular' if i == 0 else 'Pasajero',
                    'referencia': f"TRX-{res.venta.id}"
                })

        filename = f"Manifiesto_{paquete.nombre.replace(' ', '_')}_{fecha}"
        return self._generar_reporte(turistas_data, filename, formato, paquete.nombre, fecha)

    def _generar_reporte(self, data, filename, formato, service_name, fecha):
        if formato == 'CSV': return ExportarManifiestoBase()._export_csv(data, filename)
        elif formato == 'XLS': return ExportarManifiestoBase()._export_xlsx(data, filename, service_name, fecha)
        elif formato == 'PDF': return ExportarManifiestoBase()._export_pdf(data, filename, service_name, fecha)
        return HttpResponse(json.dumps({'error': 'Formato no soportado.'}), status=400, content_type='application/json')

class ExportarDespachoProveedorAPIView(APIView):
    """
    POST /api/gestion-proveedor/logistica/exportar/
    Exporta el reporte de despacho para proveedores.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        producto_id = request.data.get('paquete_id') # Mantenemos el nombre del campo por compatibilidad con el front
        fecha = request.data.get('fecha')
        formato = request.data.get('formato', 'XLS').upper()

        if not producto_id or not fecha:
            return HttpResponse(json.dumps({'error': 'Producto y fecha son requeridos.'}), status=400, content_type='application/json')

        producto = get_object_or_404(Productos, pk=producto_id, proveedor_id=request.user.pk)
        detalles = Detalles_Venta.objects.filter(producto=producto_id, venta__fecha__date=fecha).select_related('venta', 'venta__usuario')

        if not detalles.exists():
            return HttpResponse(json.dumps({'error': 'No hay pedidos para esta fecha.'}), status=404, content_type='application/json')

        clientes_data = []
        for det in detalles:
            usr = det.venta.usuario
            clientes_data.append({
                'nombre': f"{usr.first_name} {usr.last_name}".strip() or usr.username,
                'identificacion': 'N/A',
                'correo': usr.email,
                'telefono': usr.proveedor.numero_telefonico if hasattr(usr, 'proveedor') else 'S/R',
                'rol': 'Cliente',
                'referencia': f"TRX-{det.venta.id} (Cant: {det.cantidad})"
            })

        filename = f"Despacho_{producto.nombre.replace(' ', '_')}_{fecha}"
        return self._generar_reporte(clientes_data, filename, formato, producto.nombre, fecha)

    def _generar_reporte(self, data, filename, formato, service_name, fecha):
        if formato == 'CSV': return ExportarManifiestoBase()._export_csv(data, filename)
        elif formato == 'XLS': return ExportarManifiestoBase()._export_xlsx(data, filename, service_name, fecha)
        elif formato == 'PDF': return ExportarManifiestoBase()._export_pdf(data, filename, service_name, fecha)
        return HttpResponse(json.dumps({'error': 'Formato no soportado.'}), status=400, content_type='application/json')

class ExportarManifiestoBase:
    """Clase base con utilidades de exportación para no repetir lógica."""

    def _export_csv(self, data, filename):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Nombre Completo', 'Identificación', 'Rol', 'Correo', 'Teléfono', 'Referencia TRX'])
        for row in data:
            writer.writerow([row['nombre'], row['identificacion'], row['rol'], row['correo'], row['telefono'], row['referencia']])
        
        response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        return response

    def _export_xlsx(self, data, filename, tour_name, fecha):
        from openpyxl.drawing.image import Image as XLImage
        import os
        from django.conf import settings

        wb = Workbook()
        ws = wb.active
        ws.title = "Manifiesto"

        # 1. Encabezado con Logo y Nombre
        logo_path = os.path.join(settings.BASE_DIR, 'frontend_project', 'src', 'assets', 'public', 'amazon_logo.png')
        if os.path.exists(logo_path):
            img = XLImage(logo_path)
            img.width = 40  # Ajustar tamaño
            img.height = 40
            ws.add_image(img, 'A1')
        
        ws.merge_cells('B1:F1')
        ws['B1'] = "AMAZONIA VIVA"
        ws['B1'].font = Font(size=16, bold=True, color="10B981")
        ws['B1'].alignment = Alignment(vertical='center')
        ws.row_dimensions[1].height = 40

        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid") # Emerald-600
        center_align = Alignment(horizontal='center')

        # Cabecera informativa
        ws.append([])
        ws.append(['MANIFIESTO DE PASAJEROS'])
        ws.append([f'Tour: {tour_name}'])
        ws.append([f'Fecha de Salida: {fecha}'])
        ws.append([])

        # Encabezados de tabla
        headers = ['Nombre Completo', 'Identificación', 'Rol', 'Correo', 'Teléfono', 'Referencia TRX']
        ws.append(headers)
        
        # El índice de la fila de encabezados ahora es 7 por las filas previas
        for cell in ws[7]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align

        # Datos
        for row in data:
            ws.append([row['nombre'], row['identificacion'], row['rol'], row['correo'], row['telefono'], row['referencia']])

        # Ajustar anchos
        for col in ws.columns:
            max_length = 0
            column = get_column_letter(col[0].column)
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except: pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        return response

    def _export_pdf(self, data, filename, tour_name, fecha):
        from reportlab.lib.pagesizes import landscape
        from reportlab.platypus import Image as PDFImage
        import os
        from django.conf import settings

        buffer = io.BytesIO()
        # Usamos landscape para dar más espacio horizontal
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        
        # Estilo para celdas con wrap
        style_cell = styles['Normal']
        style_cell.fontSize = 8
        style_cell.leading = 10

        elements = []

        # 1. Encabezado Corporativo (Logo + Nombre)
        logo_path = os.path.join(settings.BASE_DIR, 'frontend_project', 'src', 'assets', 'public', 'amazon_logo.png')
        
        header_data = []
        if os.path.exists(logo_path):
            img = PDFImage(logo_path, width=40, height=40)
            header_data = [[img, Paragraph("<font size=18 color='#10B981'><b>AMAZONIA VIVA</b></font>", styles['Normal'])]]
        else:
            header_data = [[Paragraph("<font size=18 color='#10B981'><b>AMAZONIA VIVA</b></font>", styles['Normal'])]]

        header_table = Table(header_data, colWidths=[50, 400])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))

        # Título del reporte
        elements.append(Paragraph(f"<b>MANIFIESTO DE OPERACIONES</b>", styles['Title']))
        elements.append(Paragraph(f"<b>Tour:</b> {tour_name}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fecha:</b> {fecha}", styles['Normal']))
        elements.append(Spacer(1, 15))

        # Tabla de datos
        table_data = [['Nombre Completo', 'Identificación', 'Rol', 'Correo', 'Teléfono', 'Referencia']]
        for row in data:
            table_data.append([
                Paragraph(row['nombre'], style_cell),
                row['identificacion'],
                row['rol'],
                Paragraph(row['correo'], style_cell),
                row['telefono'],
                row['referencia']
            ])

        # Anchos en Landscape (Total ~732 de contenido)
        # Nombre(180) + ID(90) + Rol(70) + Correo(180) + Tel(120) + Ref(80) = 720
        t = Table(table_data, colWidths=[180, 90, 70, 180, 120, 80], repeatRows=1)
        
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#10B981")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'), # ID y Rol centrados
            ('ALIGN', (4, 0), (5, -1), 'CENTER'), # Tel y Referencia centrada
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t)

        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        return response
