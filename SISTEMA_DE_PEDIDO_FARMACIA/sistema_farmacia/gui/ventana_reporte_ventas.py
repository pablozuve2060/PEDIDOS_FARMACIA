import os
from datetime import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from gui.estilos import aplicar_favicon, centrar_ventana, FUENTE_TITULO, FUENTE_NORMAL
from services import persistencia, reportes_pdf


class VentanaReporteVentas(tb.Toplevel):

    def __init__(self, parent, generado_por, al_generar=None):
        super().__init__(parent)
        self.title("Reporte de Ventas por Fecha")
        aplicar_favicon(self)
        self.generado_por = generado_por
        self.al_generar = al_generar
        self._construir_ui()
        centrar_ventana(self, 420, 280)

    def _construir_ui(self):
        tb.Label(
            self,
            text="📊 Reporte de Ventas",
            font=FUENTE_TITULO,
        ).pack(pady=(15, 0))
        tb.Label(
            self,
            text="Ventas reales según el historial de pedidos despachados",
            font=FUENTE_NORMAL,
            bootstyle="secondary",
            wraplength=380,
            justify="center",
        ).pack(pady=(2, 15))
        contenedor = tb.Frame(self, padding=(20, 0))
        contenedor.pack(fill="x")
        hoy = datetime.now()
        inicio_de_mes = hoy.replace(day=1)
        tb.Label(contenedor, text="Desde", font=FUENTE_NORMAL).pack(anchor="w")
        self.fecha_inicio = tb.DateEntry(
            contenedor, dateformat="%Y-%m-%d", startdate=inicio_de_mes
        )
        self.fecha_inicio.pack(fill="x", pady=(2, 12))
        tb.Label(contenedor, text="Hasta", font=FUENTE_NORMAL).pack(anchor="w")
        self.fecha_fin = tb.DateEntry(
            contenedor, dateformat="%Y-%m-%d", startdate=hoy
        )
        self.fecha_fin.pack(fill="x", pady=(2, 20))
        tb.Button(
            contenedor,
            text="📄 Generar PDF",
            bootstyle="success",
            command=self._generar,
        ).pack(fill="x", ipady=6)

    def _generar(self):
        try:
            fecha_inicio = self.fecha_inicio.get_date().strftime("%Y-%m-%d")
            fecha_fin = self.fecha_fin.get_date().strftime("%Y-%m-%d")
        except Exception:
            messagebox.showerror("Error", "Selecciona un rango de fechas válido.")
            return
        if fecha_inicio > fecha_fin:
            messagebox.showwarning(
                "Rango inválido", "La fecha 'Desde' no puede ser posterior a 'Hasta'."
            )
            return
        historial = persistencia.cargar_historial()
        try:
            ruta = reportes_pdf.generar_reporte_ventas(
                historial, fecha_inicio, fecha_fin, generado_por=self.generado_por
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte:\n{e}")
            return
        ruta_absoluta = os.path.abspath(ruta)
        respuesta = messagebox.askyesno(
            "Reporte generado",
            f"Reporte guardado en:\n{ruta_absoluta}\n\n¿Deseas abrirlo ahora?",
        )
        if respuesta and self.al_generar:
            self.al_generar(ruta_absoluta)
        self.destroy()
