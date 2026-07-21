import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from services import recursividad

CARPETA_REPORTES = "reportes"
UMBRAL_STOCK_BAJO = 10


def _estilos():
    base = getSampleStyleSheet()
    estilos = {
        "titulo": ParagraphStyle(
            "titulo",
            parent=base["Title"],
            fontSize=18,
            textColor=colors.HexColor("#2E8B57"),
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo",
            parent=base["Heading2"],
            fontSize=13,
            spaceBefore=14,
            spaceAfter=6,
        ),
        "normal": base["Normal"],
        "pie": ParagraphStyle(
            "pie",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_RIGHT,
        ),
        "meta": ParagraphStyle(
            "meta",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER,
        ),
    }
    return estilos


def generar_reporte(
    lista_medicamentos, arbol_medicamentos, cola_pedidos, generado_por="Sistema"
):
    os.makedirs(CARPETA_REPORTES, exist_ok=True)
    fecha_hora = datetime.now()
    nombre_archivo = f"reporte_farmacia_{fecha_hora.strftime('%Y%m%d_%H%M%S')}.pdf"
    ruta = os.path.join(CARPETA_REPORTES, nombre_archivo)
    estilos = _estilos()
    doc = SimpleDocTemplate(
        ruta,
        pagesize=letter,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
    )
    story = []
    story.append(Paragraph("Sistema de Farmacia", estilos["titulo"]))
    story.append(Paragraph("Reporte General de Operación", estilos["subtitulo"]))
    story.append(
        Paragraph(
            f"Generado el {fecha_hora.strftime('%d/%m/%Y %H:%M')} · Usuario: {generado_por}",
            estilos["meta"],
        )
    )
    story.append(Spacer(1, 10))
    story.append(
        HRFlowable(width="100%", color=colors.HexColor("#2E8B57"), thickness=1)
    )
    story.append(Spacer(1, 14))
    todos_medicamentos = arbol_medicamentos.recorrido_inorden()
    total_medicamentos = len(todos_medicamentos)
    bajo_stock = recursividad.contar_medicamentos_bajo_stock_recursivo(
        todos_medicamentos, umbral=UMBRAL_STOCK_BAJO
    )
    total_pedidos_cola = len(cola_pedidos)
    story.append(Paragraph("1. Resumen General", estilos["subtitulo"]))
    tabla_resumen = Table(
        [
            ["Medicamentos en catálogo", str(total_medicamentos)],
            [f"Medicamentos con stock < {UMBRAL_STOCK_BAJO}", str(bajo_stock)],
            ["Pedidos actualmente en cola", str(total_pedidos_cola)],
        ],
        colWidths=[10 * cm, 5 * cm],
    )
    tabla_resumen.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2F7F4")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(tabla_resumen)
    story.append(Spacer(1, 18))
    story.append(Paragraph("2. Medicamentos con Stock Bajo", estilos["subtitulo"]))
    criticos = [m for m in todos_medicamentos if m.stock < UMBRAL_STOCK_BAJO]
    if criticos:
        filas = [["Código", "Nombre", "Stock", "Categoría"]]
        for med in criticos:
            filas.append([med.codigo, med.nombre, str(med.stock), med.categoria])
        tabla_criticos = Table(filas, colWidths=[3 * cm, 6.5 * cm, 2.5 * cm, 3 * cm])
        tabla_criticos.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9534F")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#FBEAEA")],
                    ),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(tabla_criticos)
    else:
        story.append(
            Paragraph("No hay medicamentos con stock bajo. ✅", estilos["normal"])
        )
    story.append(Spacer(1, 18))
    story.append(Paragraph("3. Cola de Pedidos Actual", estilos["subtitulo"]))
    pedidos = cola_pedidos.a_lista()
    if pedidos:
        filas = [["#", "Cliente", "Ítems", "Total", "Estado"]]
        for pedido in pedidos:
            filas.append(
                [
                    str(pedido.numero_pedido),
                    pedido.cliente or "—",
                    str(len(pedido.items)),
                    f"${pedido.total:.2f}",
                    pedido.estado,
                ]
            )
        tabla_pedidos = Table(
            filas, colWidths=[1.5 * cm, 5 * cm, 2 * cm, 2.5 * cm, 3.5 * cm]
        )
        tabla_pedidos.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E8B57")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#EAF3EE")],
                    ),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(tabla_pedidos)
    else:
        story.append(
            Paragraph("No hay pedidos en cola actualmente.", estilos["normal"])
        )
    story.append(Spacer(1, 24))
    story.append(
        HRFlowable(width="100%", color=colors.HexColor("#CCCCCC"), thickness=0.5)
    )
    story.append(
        Paragraph(
            "Sistema de Farmacia · Reporte generado automáticamente", estilos["pie"]
        )
    )
    doc.build(story)
    return ruta


def generar_reporte_ventas(historial_pedidos, fecha_inicio, fecha_fin, generado_por="Sistema"):
    os.makedirs(CARPETA_REPORTES, exist_ok=True)
    fecha_hora = datetime.now()
    nombre_archivo = f"reporte_ventas_{fecha_hora.strftime('%Y%m%d_%H%M%S')}.pdf"
    ruta = os.path.join(CARPETA_REPORTES, nombre_archivo)
    estilos = _estilos()
    doc = SimpleDocTemplate(
        ruta,
        pagesize=letter,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
    )
    pedidos_filtrados = [
        p
        for p in historial_pedidos
        if p.get("hora_despacho")
        and fecha_inicio <= p["hora_despacho"][:10] <= fecha_fin
    ]
    total_pedidos = len(pedidos_filtrados)
    total_vendido = sum(
        sum(item["cantidad"] * item["precio_unitario"] for item in p["items"])
        for p in pedidos_filtrados
    )
    promedio_pedido = total_vendido / total_pedidos if total_pedidos else 0
    ventas_por_medicamento = {}
    for p in pedidos_filtrados:
        for item in p["items"]:
            clave = item["codigo_medicamento"]
            if clave not in ventas_por_medicamento:
                ventas_por_medicamento[clave] = {
                    "nombre": item["nombre_medicamento"],
                    "cantidad": 0,
                    "monto": 0.0,
                }
            ventas_por_medicamento[clave]["cantidad"] += item["cantidad"]
            ventas_por_medicamento[clave]["monto"] += (
                item["cantidad"] * item["precio_unitario"]
            )
    top_medicamentos = sorted(
        ventas_por_medicamento.items(), key=lambda x: x[1]["cantidad"], reverse=True
    )[:10]
    story = []
    story.append(Paragraph("Sistema de Farmacia", estilos["titulo"]))
    story.append(Paragraph("Reporte de Ventas por Rango de Fecha", estilos["subtitulo"]))
    story.append(
        Paragraph(
            f"Del {fecha_inicio} al {fecha_fin} · Generado el "
            f"{fecha_hora.strftime('%d/%m/%Y %H:%M')} · Usuario: {generado_por}",
            estilos["meta"],
        )
    )
    story.append(Spacer(1, 10))
    story.append(
        HRFlowable(width="100%", color=colors.HexColor("#2E8B57"), thickness=1)
    )
    story.append(Spacer(1, 14))
    story.append(Paragraph("1. Resumen de Ventas", estilos["subtitulo"]))
    tabla_resumen = Table(
        [
            ["Pedidos despachados en el rango", str(total_pedidos)],
            ["Total vendido", f"${total_vendido:.2f}"],
            ["Promedio por pedido", f"${promedio_pedido:.2f}"],
        ],
        colWidths=[10 * cm, 5 * cm],
    )
    tabla_resumen.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2F7F4")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(tabla_resumen)
    story.append(Spacer(1, 18))
    story.append(Paragraph("2. Medicamentos Más Vendidos", estilos["subtitulo"]))
    if top_medicamentos:
        filas = [["Código", "Nombre", "Cantidad", "Monto"]]
        for codigo, datos in top_medicamentos:
            filas.append(
                [codigo, datos["nombre"], str(datos["cantidad"]), f"${datos['monto']:.2f}"]
            )
        tabla_top = Table(filas, colWidths=[3 * cm, 6.5 * cm, 2.5 * cm, 3 * cm])
        tabla_top.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E8B57")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#EAF3EE")],
                    ),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(tabla_top)
    else:
        story.append(
            Paragraph("No hay ventas registradas en este rango.", estilos["normal"])
        )
    story.append(Spacer(1, 18))
    story.append(Paragraph("3. Detalle de Pedidos Despachados", estilos["subtitulo"]))
    if pedidos_filtrados:
        filas = [["#", "Cliente", "Fecha despacho", "Ítems", "Total"]]
        for p in pedidos_filtrados:
            total_pedido = sum(
                item["cantidad"] * item["precio_unitario"] for item in p["items"]
            )
            filas.append(
                [
                    str(p["numero_pedido"]),
                    p.get("cliente") or "—",
                    p.get("hora_despacho", "—"),
                    str(len(p["items"])),
                    f"${total_pedido:.2f}",
                ]
            )
        tabla_detalle = Table(
            filas, colWidths=[1.3 * cm, 4 * cm, 4 * cm, 1.7 * cm, 3 * cm]
        )
        tabla_detalle.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E8B57")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#EAF3EE")],
                    ),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(tabla_detalle)
    else:
        story.append(
            Paragraph("No hay pedidos despachados en este rango.", estilos["normal"])
        )
    story.append(Spacer(1, 24))
    story.append(
        HRFlowable(width="100%", color=colors.HexColor("#CCCCCC"), thickness=0.5)
    )
    story.append(
        Paragraph(
            "Sistema de Farmacia · Reporte generado automáticamente", estilos["pie"]
        )
    )
    doc.build(story)
    return ruta
