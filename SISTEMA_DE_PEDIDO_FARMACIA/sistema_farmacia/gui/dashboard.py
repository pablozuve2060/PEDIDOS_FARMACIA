import os
import subprocess
import sys
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from gui.estilos import (
    centrar_ventana,
    cargar_logo_uleam,
    FUENTE_TITULO,
    FUENTE_NORMAL,
    FUENTE_SUBTITULO,
    TarjetaKPI,
    TarjetaMenu,
    NF_FONDO,
    NF_TARJETA,
    NF_BORDE,
    NF_ROJO,
    NF_VERDE,
    NF_AMBAR,
    NF_AZUL,
    NF_GRIS_TEXTO,
    NF_BLANCO,
)
from services.lista_enlazada import ListaEnlazadaMedicamentos
from services.arbol_busqueda import ArbolBusquedaMedicamentos
from services.cola_pedidos import ColaPedidos
from services import persistencia, recursividad, reportes_pdf
from gui.ventana_catalogo import VentanaCatalogo
from gui.ventana_pedidos import VentanaPedidos
from gui.ventana_busqueda import VentanaBusqueda
from gui.ventana_usuarios import VentanaUsuarios
from gui.ventana_reporte_ventas import VentanaReporteVentas
from gui.ventana_alertas_vencimiento import VentanaAlertasVencimiento
from gui.ventana_kardex import VentanaKardex
from gui.ventana_estanterias import VentanaEstanterias

ANCHO_VENTANA = 800
ALTO_VENTANA = 800


class Dashboard(tb.Frame):

    def __init__(self, parent, usuario):
        super().__init__(parent, padding=0)
        self.parent = parent
        self.usuario = usuario
        self.lista_medicamentos = ListaEnlazadaMedicamentos()
        self.arbol_medicamentos = ArbolBusquedaMedicamentos()
        self.cola_pedidos = ColaPedidos()
        persistencia.cargar_medicamentos(self.lista_medicamentos, self.arbol_medicamentos)
        persistencia.cargar_cola_pedidos(self.cola_pedidos)
        self.pack(fill="both", expand=True)
        self._construir_ui()
        centrar_ventana(parent, ANCHO_VENTANA, ALTO_VENTANA)

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _construir_ui(self):
        contenedor = tb.Frame(self, padding=(30, 22, 30, 22))
        contenedor.pack(fill="both", expand=True)

        self._construir_header(contenedor)
        tb.Separator(contenedor).pack(fill="x", pady=(16, 22))
        self._construir_kpis(contenedor)
        self._construir_menu(contenedor)

    def _construir_header(self, parent):
        header = tb.Frame(parent)
        header.pack(fill="x")

        izquierda = tb.Frame(header)
        izquierda.pack(side="left")
        logo_uleam = cargar_logo_uleam(alto_deseado=42)
        if logo_uleam is not None:
            label_logo = tb.Label(izquierda, image=logo_uleam, background=NF_FONDO)
            label_logo.image = logo_uleam
            label_logo.pack(side="left", padx=(0, 12))
        else:
            badge = tk.Canvas(izquierda, width=42, height=42, bg=NF_FONDO,
                               highlightthickness=0, bd=0)
            badge.pack(side="left", padx=(0, 12))
            badge.create_oval(2, 2, 40, 40, fill=NF_ROJO, outline="")
            badge.create_text(21, 21, text="💊", font=("Segoe UI", 16))
        titulos = tb.Frame(izquierda)
        titulos.pack(side="left")
        tb.Label(titulos, text="Panel Principal", font=FUENTE_TITULO,
                 bootstyle="light").pack(anchor="w")
        tb.Label(titulos, text="Sistema de Farmacia · ULEAM", font=FUENTE_NORMAL,
                 bootstyle="secondary").pack(anchor="w")

        derecha = tb.Frame(header)
        derecha.pack(side="right")
        tb.Label(derecha, text=f"👤 {self.usuario['nombre']}", font=FUENTE_NORMAL,
                 bootstyle="light").pack(anchor="e")
        tb.Label(derecha, text=self.usuario["rol"].capitalize(), font=("Segoe UI", 9),
                 bootstyle="secondary").pack(anchor="e")

    def _construir_kpis(self, parent):
        fila = tb.Frame(parent)
        fila.pack(fill="x", pady=(0, 26))
        for i in range(4):
            fila.columnconfigure(i, weight=1)

        bajo_stock = recursividad.contar_medicamentos_bajo_stock_recursivo(
            self.lista_medicamentos.a_lista(), umbral=10
        )
        alertas_vencimiento = sum(
            1 for med in self.lista_medicamentos.a_lista()
            if med.estado_vencimiento() in ("vencido", "por_vencer")
        )

        datos_kpi = [
            ("📦", "Medicamentos", str(len(self.lista_medicamentos)), NF_AZUL),
            ("🧾", "Pedidos en cola", str(len(self.cola_pedidos)), NF_AZUL),
            ("⚠️", "Stock bajo (<10)", str(bajo_stock),
             NF_ROJO if bajo_stock > 0 else NF_VERDE),
            ("⏰", "Por vencer / vencidos", str(alertas_vencimiento),
             NF_ROJO if alertas_vencimiento > 0 else NF_VERDE),
        ]
        self._tarjetas_kpi = []
        for i, (icono, titulo, valor, color) in enumerate(datos_kpi):
            tarjeta = TarjetaKPI(fila, icono, titulo, valor, color_acento=color,
                                  ancho=168, alto=92)
            tarjeta.grid(row=0, column=i, sticky="nsew", padx=6)
            self._tarjetas_kpi.append(tarjeta)

    def _construir_menu(self, parent):
        tb.Label(parent, text="MENÚ PRINCIPAL", font=("Segoe UI", 10, "bold"),
                 bootstyle="secondary").pack(anchor="w", pady=(0, 10))

        rejilla = tb.Frame(parent)
        rejilla.pack(fill="x")
        rejilla.columnconfigure(0, weight=1)
        rejilla.columnconfigure(1, weight=1)

        opciones = [
            ("📦", "Catálogo de Medicamentos", "Alta, edición y stock", NF_AZUL, self._abrir_catalogo),
            ("🧾", "Cola de Pedidos", "Atención FIFO de ventas", "#B084F2", self._abrir_pedidos),
            ("🔎", "Búsqueda de Medicamentos", "Búsqueda binaria por código", NF_GRIS_TEXTO, self._abrir_busqueda),
            ("⏰", "Alertas de Vencimiento", "Próximos a caducar", NF_AMBAR, self._abrir_alertas_vencimiento),
            ("📋", "Kardex de Movimientos", "Historial de entradas/salidas", "#8C8C8C", self._abrir_kardex),
            ("🗄️", "Estanterías del Almacén", "Ubicación física por categoría", "#B084F2", self._abrir_estanterias),
        ]
        if self.usuario["rol"] == "admin":
            opciones += [
                ("🧾", "Reporte General PDF", "Resumen exportable", NF_VERDE, self._generar_reporte),
                ("📊", "Reporte de Ventas por Fecha", "Historial de ventas", NF_VERDE, self._abrir_reporte_ventas),
                ("👥", "Gestión de Usuarios", "Roles y accesos", NF_AZUL, self._abrir_usuarios),
            ]

        fila = col = 0
        for icono, titulo, subtitulo, color, comando in opciones:
            tarjeta = TarjetaMenu(rejilla, icono, titulo, subtitulo, color, comando,
                                   ancho=320, alto=76)
            tarjeta.grid(row=fila, column=col, padx=6, pady=6, sticky="w")
            col += 1
            if col > 1:
                col = 0
                fila += 1

        pie = tb.Frame(parent)
        pie.pack(fill="x", pady=(24, 0))
        tb.Button(pie, text="🚪  Cerrar Sesión", bootstyle="danger", width=22,
                  command=self._cerrar_sesion).pack(anchor="center", ipady=6)

    # ------------------------------------------------------------------
    # Refresco de datos
    # ------------------------------------------------------------------
    def _refrescar_resumen(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._construir_ui()

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------
    def _abrir_catalogo(self):
        VentanaCatalogo(self.parent, self.lista_medicamentos, self.arbol_medicamentos,
                         al_cerrar=self._refrescar_resumen, rol=self.usuario["rol"],
                         usuario_nombre=self.usuario["nombre"])

    def _abrir_pedidos(self):
        VentanaPedidos(self.parent, self.cola_pedidos, self.lista_medicamentos,
                        al_cerrar=self._refrescar_resumen, usuario_nombre=self.usuario["nombre"])

    def _abrir_busqueda(self):
        VentanaBusqueda(self.parent, self.arbol_medicamentos, self.lista_medicamentos)

    def _abrir_alertas_vencimiento(self):
        VentanaAlertasVencimiento(self.parent, self.lista_medicamentos)

    def _abrir_kardex(self):
        VentanaKardex(self.parent, self.lista_medicamentos, al_cerrar=self._refrescar_resumen)

    def _abrir_estanterias(self):
        VentanaEstanterias(self.parent, self.lista_medicamentos)

    def _abrir_usuarios(self):
        VentanaUsuarios(self.parent, self.usuario)

    def _abrir_reporte_ventas(self):
        VentanaReporteVentas(self.parent, generado_por=self.usuario["nombre"],
                              al_generar=self._abrir_archivo)

    def _generar_reporte(self):
        try:
            ruta = reportes_pdf.generar_reporte(
                self.lista_medicamentos, self.arbol_medicamentos, self.cola_pedidos,
                generado_por=self.usuario["nombre"]
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte:\n{e}")
            return
        ruta_absoluta = os.path.abspath(ruta)
        respuesta = messagebox.askyesno(
            "Reporte generado", f"Reporte guardado en:\n{ruta_absoluta}\n\n¿Deseas abrirlo ahora?"
        )
        if respuesta:
            self._abrir_archivo(ruta_absoluta)

    def _abrir_archivo(self, ruta):
        try:
            if sys.platform.startswith("win"):
                os.startfile(ruta)
            elif sys.platform == "darwin":
                subprocess.run(["open", ruta])
            else:
                subprocess.run(["xdg-open", ruta])
        except Exception:
            messagebox.showinfo("Abrir manualmente", f"No se pudo abrir automáticamente.\nRuta: {ruta}")

    def _cerrar_sesion(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        from gui.login import VentanaLogin
        VentanaLogin(self.parent, al_iniciar_sesion=lambda u: Dashboard(self.parent, u))
