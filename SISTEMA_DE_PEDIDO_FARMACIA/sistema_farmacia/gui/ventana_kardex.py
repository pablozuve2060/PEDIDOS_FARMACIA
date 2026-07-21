from datetime import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from gui.estilos import (
    aplicar_favicon,
    centrar_ventana,
    FUENTE_TITULO,
    FUENTE_NORMAL,
    valores_combo_medicamentos,
    codigo_desde_valor_combo,
)
from services import kardex, persistencia


class VentanaKardex(tb.Toplevel):

    def __init__(self, parent, lista_medicamentos=None, al_cerrar=None):
        super().__init__(parent)
        self.title("Kardex de Movimientos")
        aplicar_favicon(self)
        self.lista_medicamentos = lista_medicamentos
        self.al_cerrar = al_cerrar
        self._construir_ui()
        self._refrescar()
        centrar_ventana(self, 920, 640)

    def _construir_ui(self):
        tb.Label(self, text="📋 Kardex de Movimientos", font=FUENTE_TITULO).pack(
            pady=(15, 10)
        )
        filtros = tb.Frame(self)
        filtros.pack(fill="x", padx=15, pady=(0, 10))
        tb.Label(filtros, text="Código", font=FUENTE_NORMAL).grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )
        valores_meds = ["Todos"] + valores_combo_medicamentos(self.lista_medicamentos) \
            if self.lista_medicamentos is not None else ["Todos"]
        self.combo_codigo = tb.Combobox(
            filtros, values=valores_meds, width=22, state="readonly"
        )
        self.combo_codigo.set("Todos")
        self.combo_codigo.grid(row=1, column=0, padx=(0, 10))
        tb.Label(filtros, text="Tipo", font=FUENTE_NORMAL).grid(
            row=0, column=1, sticky="w", padx=(0, 5)
        )
        self.combo_tipo = tb.Combobox(
            filtros,
            values=["Todos", "entrada", "salida", "ajuste"],
            width=12,
            state="readonly",
        )
        self.combo_tipo.set("Todos")
        self.combo_tipo.grid(row=1, column=1, padx=(0, 10))
        hoy = datetime.now()
        inicio_de_mes = hoy.replace(day=1)
        tb.Label(filtros, text="Desde", font=FUENTE_NORMAL).grid(
            row=0, column=2, sticky="w", padx=(0, 5)
        )
        self.fecha_inicio = tb.DateEntry(
            filtros, dateformat="%Y-%m-%d", startdate=inicio_de_mes, width=12
        )
        self.fecha_inicio.grid(row=1, column=2, padx=(0, 10))
        tb.Label(filtros, text="Hasta", font=FUENTE_NORMAL).grid(
            row=0, column=3, sticky="w", padx=(0, 5)
        )
        self.fecha_fin = tb.DateEntry(
            filtros, dateformat="%Y-%m-%d", startdate=hoy, width=12
        )
        self.fecha_fin.grid(row=1, column=3, padx=(0, 10))
        tb.Button(
            filtros, text="🔍 Filtrar", bootstyle="primary", command=self._refrescar
        ).grid(row=1, column=4, padx=(5, 5))
        tb.Button(
            filtros,
            text="🧹 Limpiar filtros",
            bootstyle="secondary",
            command=self._limpiar_filtros,
        ).grid(row=1, column=5)
        columnas = ("fecha", "codigo", "nombre", "tipo", "cantidad", "stock_resultante", "usuario", "motivo")
        self.tabla = tb.Treeview(
            self, columns=columnas, show="headings", bootstyle="primary", height=18
        )
        encabezados = [
            ("fecha", "Fecha", 130),
            ("codigo", "Código", 65),
            ("nombre", "Medicamento", 150),
            ("tipo", "Tipo", 70),
            ("cantidad", "Cantidad", 70),
            ("stock_resultante", "Stock resultante", 100),
            ("usuario", "Usuario", 100),
            ("motivo", "Motivo", 180),
        ]
        for col, txt, w in encabezados:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor="center")
        self.tabla.column("motivo", anchor="w")
        self.tabla.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.tabla.tag_configure("entrada", foreground="#2E8B57")
        self.tabla.tag_configure("salida", foreground="#D9534F")
        self.tabla.tag_configure("ajuste", foreground="#B8860B")
        self.label_resumen = tb.Label(self, text="", font=FUENTE_NORMAL, bootstyle="secondary")
        self.label_resumen.pack(pady=(0, 4))

        panel_deshacer = tb.Frame(self)
        panel_deshacer.pack(fill="x", padx=15, pady=(0, 12))
        self.label_pila = tb.Label(
            panel_deshacer, text="", font=FUENTE_NORMAL, bootstyle="secondary"
        )
        self.label_pila.pack(side="left")
        self.boton_deshacer = tb.Button(
            panel_deshacer,
            text="↩️ Deshacer último movimiento",
            bootstyle="warning",
            command=self._deshacer_ultimo,
        )
        self.boton_deshacer.pack(side="right")

    def _deshacer_ultimo(self):
        if not kardex.hay_movimiento_para_deshacer():
            messagebox.showinfo(
                "Pila vacía", "No hay movimientos registrados en esta sesión para deshacer."
            )
            return
        pendiente = kardex.ver_movimiento_pendiente_deshacer()
        if not messagebox.askyesno(
            "Confirmar",
            f"¿Deshacer el movimiento de '{pendiente['nombre_medicamento']}' "
            f"({pendiente['tipo']}, cantidad {pendiente['cantidad']})?",
        ):
            return
        try:
            movimiento, stock_restaurado = kardex.deshacer_ultimo_movimiento(
                self.lista_medicamentos
            )
        except (IndexError, ValueError) as error:
            messagebox.showerror("No se pudo deshacer", str(error))
            return
        persistencia.guardar_medicamentos(self.lista_medicamentos)
        messagebox.showinfo(
            "Movimiento deshecho",
            f"Se revirtió el movimiento de '{movimiento['nombre_medicamento']}'. "
            f"Stock restaurado a {stock_restaurado}.",
        )
        self._refrescar()
        if self.al_cerrar:
            self.al_cerrar()

    def _limpiar_filtros(self):
        self.combo_codigo.set("Todos")
        self.combo_tipo.set("Todos")
        self._refrescar()

    def _refrescar(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        valor_codigo = self.combo_codigo.get()
        codigo = None if valor_codigo in ("", "Todos") else codigo_desde_valor_combo(valor_codigo)
        tipo = self.combo_tipo.get()
        tipo = None if tipo == "Todos" else tipo
        try:
            fecha_inicio = self.fecha_inicio.get_date().strftime("%Y-%m-%d")
            fecha_fin = self.fecha_fin.get_date().strftime("%Y-%m-%d")
        except Exception:
            fecha_inicio = fecha_fin = None
        movimientos = kardex.cargar_movimientos()
        movimientos = kardex.filtrar_movimientos(
            movimientos, codigo=codigo, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, tipo=tipo
        )
        movimientos.sort(key=lambda m: m["fecha"], reverse=True)
        for m in movimientos:
            self.tabla.insert(
                "",
                "end",
                values=(
                    m["fecha"],
                    m["codigo_medicamento"],
                    m["nombre_medicamento"],
                    m["tipo"],
                    m["cantidad"],
                    m["stock_resultante"],
                    m["usuario"],
                    m["motivo"],
                ),
                tags=(m["tipo"],),
            )
        self.label_resumen.config(text=f"Total de movimientos mostrados: {len(movimientos)}")
        pendientes = kardex.cantidad_pendientes_deshacer()
        if pendientes:
            self.label_pila.config(
                text=f"🧱 Pila de deshacer: {pendientes} movimiento(s) disponible(s)"
            )
            self.boton_deshacer.config(state="normal")
        else:
            self.label_pila.config(text="🧱 Pila de deshacer: vacía")
            self.boton_deshacer.config(state="disabled")
