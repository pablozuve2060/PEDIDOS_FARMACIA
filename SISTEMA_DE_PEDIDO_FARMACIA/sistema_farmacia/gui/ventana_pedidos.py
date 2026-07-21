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
from services import persistencia, kardex


class VentanaPedidos(tb.Toplevel):

    def __init__(self, parent, cola_pedidos, lista_medicamentos, al_cerrar=None, usuario_nombre="Sistema"):
        super().__init__(parent)
        self.title("Cola de Pedidos")
        aplicar_favicon(self)
        self.cola = cola_pedidos
        self.lista_medicamentos = lista_medicamentos
        self.al_cerrar = al_cerrar
        self.usuario_nombre = usuario_nombre
        self.pedido_actual = None
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self._construir_ui()
        self._refrescar_cola()
        centrar_ventana(self, 880, 580)

    def _construir_ui(self):
        tb.Label(self, text="🧾 Gestión de Pedidos", font=FUENTE_TITULO).pack(
            pady=(15, 10)
        )
        cuerpo = tb.Frame(self)
        cuerpo.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        panel_izq = tb.Labelframe(
            cuerpo, text="Nuevo Pedido", padding=15, bootstyle="primary"
        )
        panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tb.Label(panel_izq, text="Cliente (opcional)", font=FUENTE_NORMAL).pack(
            anchor="w"
        )
        self.entry_cliente = tb.Entry(panel_izq, width=30)
        self.entry_cliente.pack(fill="x", pady=(2, 10))
        tb.Label(panel_izq, text="Código medicamento", font=FUENTE_NORMAL).pack(
            anchor="w"
        )
        self.combo_codigo = tb.Combobox(
            panel_izq,
            values=valores_combo_medicamentos(self.lista_medicamentos, solo_con_stock=True),
            width=28,
            state="readonly",
        )
        self.combo_codigo.pack(fill="x", pady=(2, 8))
        tb.Label(panel_izq, text="Cantidad", font=FUENTE_NORMAL).pack(anchor="w")
        self.entry_cantidad = tb.Entry(panel_izq, width=10)
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.pack(anchor="w", pady=(2, 8))
        tb.Button(
            panel_izq,
            text="➕ Agregar ítem al pedido",
            bootstyle="info",
            command=self._agregar_item,
        ).pack(fill="x", pady=(0, 10))
        self.lista_items = tb.Treeview(
            panel_izq,
            columns=("nombre", "cant", "subtotal"),
            show="headings",
            height=8,
            bootstyle="info",
        )
        for col, txt, w in [
            ("nombre", "Medicamento", 140),
            ("cant", "Cant.", 50),
            ("subtotal", "Subtotal", 70),
        ]:
            self.lista_items.heading(col, text=txt)
            self.lista_items.column(col, width=w, anchor="center")
        self.lista_items.pack(fill="both", expand=True, pady=(0, 10))
        self.label_total = tb.Label(
            panel_izq, text="Total: $0.00", font=("Segoe UI", 12, "bold")
        )
        self.label_total.pack(anchor="e", pady=(0, 10))
        tb.Button(
            panel_izq,
            text="✅ Encolar Pedido",
            bootstyle="success",
            command=self._encolar_pedido,
        ).pack(fill="x", ipady=4)
        panel_der = tb.Labelframe(
            cuerpo, text="Cola de Atención (FIFO)", padding=15, bootstyle="secondary"
        )
        panel_der.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.tabla_cola = tb.Treeview(
            panel_der,
            columns=("numero", "cliente", "items", "total", "estado"),
            show="headings",
            height=14,
            bootstyle="secondary",
        )
        encabezados = [
            ("numero", "#", 40),
            ("cliente", "Cliente", 110),
            ("items", "Ítems", 50),
            ("total", "Total", 70),
            ("estado", "Estado", 90),
        ]
        for col, txt, w in encabezados:
            self.tabla_cola.heading(col, text=txt)
            self.tabla_cola.column(col, width=w, anchor="center")
        self.tabla_cola.pack(fill="both", expand=True, pady=(0, 10))
        tb.Button(
            panel_der,
            text="▶️ Atender siguiente (frente de la cola)",
            bootstyle="success",
            command=self._atender_pedido,
        ).pack(fill="x", pady=(0, 6), ipady=4)
        tb.Button(
            panel_der,
            text="❌ Cancelar pedido seleccionado",
            bootstyle="danger",
            command=self._cancelar_pedido,
        ).pack(fill="x", ipady=4)

    def _agregar_item(self):
        codigo = codigo_desde_valor_combo(self.combo_codigo.get())
        if not codigo:
            messagebox.showwarning("Sin selección", "Selecciona un medicamento de la lista.")
            return
        try:
            cantidad = int(self.entry_cantidad.get().strip())
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return
        if cantidad <= 0:
            messagebox.showerror("Error", "La cantidad debe ser mayor a 0.")
            return
        med = self.lista_medicamentos.buscar_por_codigo(codigo)
        if med is None:
            messagebox.showwarning(
                "No encontrado", f"No existe medicamento con código '{codigo}'."
            )
            return
        if med.stock < cantidad:
            messagebox.showwarning(
                "Stock insuficiente", f"Stock disponible: {med.stock}"
            )
            return
        if self.pedido_actual is None:
            cliente = self.entry_cliente.get().strip() or None
            from models.pedido import Pedido

            self.pedido_actual = Pedido(numero_pedido=0, cliente=cliente)
        self.pedido_actual.agregar_item(med.codigo, med.nombre, cantidad, med.precio)
        self._refrescar_items_pedido_actual()
        self.combo_codigo.set("")
        self.entry_cantidad.delete(0, "end")
        self.entry_cantidad.insert(0, "1")
        self._refrescar_combo_medicamentos()

    def _refrescar_combo_medicamentos(self):
        self.combo_codigo["values"] = valores_combo_medicamentos(
            self.lista_medicamentos, solo_con_stock=True
        )

    def _refrescar_items_pedido_actual(self):
        for fila in self.lista_items.get_children():
            self.lista_items.delete(fila)
        for item in self.pedido_actual.items:
            self.lista_items.insert(
                "",
                "end",
                values=(
                    item.nombre_medicamento,
                    item.cantidad,
                    f"${item.subtotal:.2f}",
                ),
            )
        self.label_total.config(text=f"Total: ${self.pedido_actual.total:.2f}")

    def _encolar_pedido(self):
        if self.pedido_actual is None or not self.pedido_actual.items:
            messagebox.showwarning(
                "Pedido vacío", "Agrega al menos un ítem antes de encolar."
            )
            return
        cliente = self.entry_cliente.get().strip() or None
        nuevo_pedido = self.cola.encolar(cliente=cliente)
        nuevo_pedido.items = self.pedido_actual.items
        for item in nuevo_pedido.items:
            nuevo_stock = (
                self.lista_medicamentos.buscar_por_codigo(
                    item.codigo_medicamento
                ).stock
                - item.cantidad
            )
            self.lista_medicamentos.actualizar(
                item.codigo_medicamento,
                stock=nuevo_stock,
            )
            kardex.registrar_movimiento(
                item.codigo_medicamento,
                item.nombre_medicamento,
                "salida",
                item.cantidad,
                nuevo_stock,
                usuario=self.usuario_nombre,
                motivo=f"Venta - Pedido #{nuevo_pedido.numero_pedido}",
            )
        persistencia.guardar_medicamentos(self.lista_medicamentos)
        persistencia.guardar_cola_pedidos(self.cola)
        messagebox.showinfo(
            "Pedido encolado",
            f"Pedido #{nuevo_pedido.numero_pedido} agregado a la cola.",
        )
        self.pedido_actual = None
        self.entry_cliente.delete(0, "end")
        self._refrescar_items_pedido_actual_vacio()
        self._refrescar_cola()
        self._refrescar_combo_medicamentos()

    def _refrescar_items_pedido_actual_vacio(self):
        for fila in self.lista_items.get_children():
            self.lista_items.delete(fila)
        self.label_total.config(text="Total: $0.00")

    def _refrescar_cola(self):
        for fila in self.tabla_cola.get_children():
            self.tabla_cola.delete(fila)
        for pedido in self.cola.a_lista():
            self.tabla_cola.insert(
                "",
                "end",
                values=(
                    pedido.numero_pedido,
                    pedido.cliente or "—",
                    len(pedido.items),
                    f"${pedido.total:.2f}",
                    pedido.estado,
                ),
            )

    def _atender_pedido(self):
        if self.cola.esta_vacia():
            messagebox.showinfo("Cola vacía", "No hay pedidos pendientes.")
            return
        pedido = self.cola.atender()
        persistencia.agregar_a_historial(pedido)
        persistencia.guardar_cola_pedidos(self.cola)
        messagebox.showinfo(
            "Pedido atendido",
            f"Pedido #{pedido.numero_pedido} despachado.\nTotal: ${pedido.total:.2f}",
        )
        self._refrescar_cola()
        if self.al_cerrar:
            self.al_cerrar()

    def _cancelar_pedido(self):
        seleccion = self.tabla_cola.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona un pedido de la tabla.")
            return
        numero = self.tabla_cola.item(seleccion[0])["values"][0]
        pedido_cancelado = self.cola.cancelar(numero)
        if pedido_cancelado is not None:
            for item in pedido_cancelado.items:
                med = self.lista_medicamentos.buscar_por_codigo(item.codigo_medicamento)
                if med is not None:
                    nuevo_stock = med.stock + item.cantidad
                    self.lista_medicamentos.actualizar(
                        item.codigo_medicamento,
                        stock=nuevo_stock,
                    )
                    kardex.registrar_movimiento(
                        item.codigo_medicamento,
                        item.nombre_medicamento,
                        "entrada",
                        item.cantidad,
                        nuevo_stock,
                        usuario=self.usuario_nombre,
                        motivo=f"Cancelación - Pedido #{numero}",
                    )
            persistencia.guardar_medicamentos(self.lista_medicamentos)
            persistencia.guardar_cola_pedidos(self.cola)
            messagebox.showinfo(
                "Cancelado", f"Pedido #{numero} cancelado y stock restaurado."
            )
            self._refrescar_cola()
            self._refrescar_combo_medicamentos()
            if self.al_cerrar:
                self.al_cerrar()

    def _cerrar(self):
        if self.al_cerrar:
            self.al_cerrar()
        self.destroy()
