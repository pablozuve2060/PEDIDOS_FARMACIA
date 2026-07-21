from datetime import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from gui.estilos import aplicar_favicon, centrar_ventana, FUENTE_TITULO, FUENTE_NORMAL
from models.medicamento import Medicamento
from services import persistencia, kardex, estanterias


class VentanaCatalogo(tb.Toplevel):

    def __init__(
        self,
        parent,
        lista_medicamentos,
        arbol_medicamentos,
        al_cerrar=None,
        rol="vendedor",
        usuario_nombre="Sistema",
    ):
        super().__init__(parent)
        self.title("Catálogo de Medicamentos")
        aplicar_favicon(self)
        self.lista = lista_medicamentos
        self.arbol = arbol_medicamentos
        self.al_cerrar = al_cerrar
        self.codigo_seleccionado = None
        self.rol = rol
        self.usuario_nombre = usuario_nombre
        self.puede_editar = rol == "admin"
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self._construir_ui()
        self._refrescar_tabla()
        centrar_ventana(self, 860, 600)

    def _construir_ui(self):
        tb.Label(self, text="📦 Catálogo de Medicamentos", font=FUENTE_TITULO).pack(
            pady=(15, 10)
        )
        if not self.puede_editar:
            tb.Label(
                self,
                text="🔒 Modo solo lectura — tu rol no permite editar el catálogo",
                font=FUENTE_NORMAL,
                bootstyle="warning",
            ).pack(pady=(0, 5))
        form = tb.Frame(self, padding=10)
        form.pack(fill="x", padx=15)
        self.entries = {}
        campos = [
            ("codigo", "Código"),
            ("nombre", "Nombre comercial"),
            ("principio_activo", "Principio activo"),
            ("precio", "Precio"),
            ("stock", "Stock"),
            ("categoria", "Categoría"),
            ("fecha_vencimiento", "Vencimiento (AAAA-MM-DD)"),
            ("ubicacion", "Ubicación (estante)"),
        ]
        for i, (clave, etiqueta) in enumerate(campos):
            fila, columna = (i // 3, i % 3 * 2)
            tb.Label(form, text=etiqueta, font=FUENTE_NORMAL).grid(
                row=fila * 2, column=columna, sticky="w", padx=5, pady=(5, 0)
            )
            entry = tb.Entry(form, width=20)
            entry.grid(row=fila * 2 + 1, column=columna, padx=5, pady=(0, 5))
            if clave == "ubicacion":
                # La ubicación se calcula sola según la categoría; nunca se
                # escribe a mano.
                entry.configure(state="readonly")
            elif not self.puede_editar:
                entry.configure(state="disabled")
            self.entries[clave] = entry
        self.entries["categoria"].bind(
            "<FocusOut>", lambda e: self._sugerir_ubicacion()
        )
        botones_form = tb.Frame(self)
        botones_form.pack(fill="x", padx=15, pady=(5, 10))
        estado_edicion = "normal" if self.puede_editar else "disabled"
        tb.Button(
            botones_form,
            text="➕ Agregar",
            bootstyle="success",
            command=self._agregar,
            state=estado_edicion,
        ).pack(side="left", padx=5)
        tb.Button(
            botones_form,
            text="✏️ Actualizar",
            bootstyle="warning",
            command=self._actualizar,
            state=estado_edicion,
        ).pack(side="left", padx=5)
        tb.Button(
            botones_form,
            text="🗑️ Eliminar",
            bootstyle="danger",
            command=self._eliminar,
            state=estado_edicion,
        ).pack(side="left", padx=5)
        tb.Button(
            botones_form,
            text="🧹 Limpiar",
            bootstyle="secondary",
            command=self._limpiar_formulario,
        ).pack(side="left", padx=5)
        tb.Separator(self).pack(fill="x", padx=15, pady=5)
        columnas = (
            "codigo",
            "nombre",
            "principio_activo",
            "precio",
            "stock",
            "categoria",
            "vencimiento",
            "ubicacion",
        )
        self.tabla = tb.Treeview(
            self, columns=columnas, show="headings", bootstyle="primary", height=14
        )
        encabezados = [
            "Código",
            "Nombre",
            "Principio Activo",
            "Precio",
            "Stock",
            "Categoría",
            "Vencimiento",
            "Estante",
        ]
        anchos = [70, 160, 130, 60, 50, 100, 95, 65]
        for col, enc, ancho in zip(columnas, encabezados, anchos):
            self.tabla.heading(col, text=enc)
            self.tabla.column(col, width=ancho, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_fila)

    def _fijar_texto_readonly(self, clave, texto):
        entry = self.entries[clave]
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, texto)
        entry.configure(state="readonly")

    def _sugerir_ubicacion(self):
        """Mientras se está dando de alta un medicamento nuevo (no hay
        ninguno seleccionado de la tabla), muestra en el campo Ubicación
        la próxima posición disponible según la categoría escrita."""
        if self.codigo_seleccionado is not None:
            return
        categoria = self.entries["categoria"].get().strip()
        if not categoria:
            self._fijar_texto_readonly("ubicacion", "")
            return
        sugerida = estanterias.generar_ubicacion(categoria, self.lista)
        self._fijar_texto_readonly("ubicacion", sugerida)

    def _refrescar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for med in self.lista.a_lista():
            estado_venc = med.estado_vencimiento()
            if estado_venc == "vencido":
                estilo_fila = ("vencido",)
            elif estado_venc == "por_vencer":
                estilo_fila = ("por_vencer",)
            elif med.stock < 10:
                estilo_fila = ("stock_bajo",)
            else:
                estilo_fila = ()
            self.tabla.insert(
                "",
                "end",
                values=(
                    med.codigo,
                    med.nombre,
                    med.principio_activo,
                    f"${med.precio:.2f}",
                    med.stock,
                    med.categoria,
                    med.fecha_vencimiento or "—",
                    med.ubicacion or "—",
                ),
                tags=estilo_fila,
            )
        self.tabla.tag_configure("stock_bajo", foreground="#D9534F")
        self.tabla.tag_configure("por_vencer", foreground="#B8860B")
        self.tabla.tag_configure("vencido", foreground="#FFFFFF", background="#D9534F")

    def _al_seleccionar_fila(self, event):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0])["values"]
        self.codigo_seleccionado = valores[0]
        med = self.lista.buscar_por_codigo(str(self.codigo_seleccionado))
        if med:
            self._llenar_formulario(med)

    def _llenar_formulario(self, med):
        self.entries["codigo"].delete(0, "end")
        self.entries["codigo"].insert(0, med.codigo)
        self.entries["nombre"].delete(0, "end")
        self.entries["nombre"].insert(0, med.nombre)
        self.entries["principio_activo"].delete(0, "end")
        self.entries["principio_activo"].insert(0, med.principio_activo)
        self.entries["precio"].delete(0, "end")
        self.entries["precio"].insert(0, str(med.precio))
        self.entries["stock"].delete(0, "end")
        self.entries["stock"].insert(0, str(med.stock))
        self.entries["categoria"].delete(0, "end")
        self.entries["categoria"].insert(0, med.categoria)
        self.entries["fecha_vencimiento"].delete(0, "end")
        self.entries["fecha_vencimiento"].insert(0, med.fecha_vencimiento or "")
        self._fijar_texto_readonly("ubicacion", med.ubicacion or "")

    def _limpiar_formulario(self):
        for clave, entry in self.entries.items():
            if clave == "ubicacion":
                continue
            entry.delete(0, "end")
        self._fijar_texto_readonly("ubicacion", "")
        self.codigo_seleccionado = None
        self.tabla.selection_remove(self.tabla.selection())

    def _leer_formulario(self):
        fecha_vencimiento = self.entries["fecha_vencimiento"].get().strip() or None
        if fecha_vencimiento:
            try:
                datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Error", "La fecha de vencimiento debe tener el formato AAAA-MM-DD."
                )
                return None
        try:
            return {
                "codigo": self.entries["codigo"].get().strip(),
                "nombre": self.entries["nombre"].get().strip(),
                "principio_activo": self.entries["principio_activo"].get().strip(),
                "precio": float(self.entries["precio"].get().strip()),
                "stock": int(self.entries["stock"].get().strip()),
                "categoria": self.entries["categoria"].get().strip() or "General",
                "fecha_vencimiento": fecha_vencimiento,
            }
        except ValueError:
            messagebox.showerror("Error", "Precio debe ser numérico y Stock un entero.")
            return None

    def _agregar(self):
        if not self.puede_editar:
            messagebox.showerror(
                "Acceso denegado", "Tu rol no tiene permiso para editar el catálogo."
            )
            return
        datos = self._leer_formulario()
        if datos is None:
            return
        if not datos["codigo"] or not datos["nombre"]:
            messagebox.showwarning(
                "Datos incompletos", "Código y nombre son obligatorios."
            )
            return
        if self.lista.buscar_por_codigo(datos["codigo"]):
            messagebox.showwarning(
                "Duplicado", f"Ya existe un medicamento con código {datos['codigo']}."
            )
            return
        ubicacion = estanterias.generar_ubicacion(datos["categoria"], self.lista)
        medicamento = Medicamento(**datos, ubicacion=ubicacion)
        self.lista.insertar(medicamento)
        self.arbol.insertar(medicamento)
        persistencia.guardar_medicamentos(self.lista)
        if medicamento.stock > 0:
            kardex.registrar_movimiento(
                medicamento.codigo,
                medicamento.nombre,
                "entrada",
                medicamento.stock,
                medicamento.stock,
                usuario=self.usuario_nombre,
                motivo="Alta de medicamento en catálogo",
            )
        self._refrescar_tabla()
        self._limpiar_formulario()
        messagebox.showinfo("Éxito", "Medicamento agregado correctamente.")

    def _actualizar(self):
        if not self.puede_editar:
            messagebox.showerror(
                "Acceso denegado", "Tu rol no tiene permiso para editar el catálogo."
            )
            return
        if not self.codigo_seleccionado:
            messagebox.showwarning(
                "Sin selección", "Selecciona un medicamento de la tabla."
            )
            return
        datos = self._leer_formulario()
        if datos is None:
            return
        med_anterior = self.lista.buscar_por_codigo(str(self.codigo_seleccionado))
        codigo_anterior = med_anterior.codigo if med_anterior else None
        nombre_anterior = med_anterior.nombre if med_anterior else None
        stock_anterior = med_anterior.stock if med_anterior else None
        categoria_anterior = med_anterior.categoria if med_anterior else None
        if categoria_anterior is not None and categoria_anterior != datos["categoria"]:
            nueva_ubicacion = estanterias.generar_ubicacion(datos["categoria"], self.lista)
        else:
            nueva_ubicacion = med_anterior.ubicacion if med_anterior else None
        self.lista.actualizar(
            str(self.codigo_seleccionado),
            nombre=datos["nombre"],
            principio_activo=datos["principio_activo"],
            precio=datos["precio"],
            stock=datos["stock"],
            categoria=datos["categoria"],
            fecha_vencimiento=datos["fecha_vencimiento"],
            ubicacion=nueva_ubicacion,
        )
        if codigo_anterior and nombre_anterior:
            self.arbol.eliminar(codigo_anterior, nombre_anterior)
        med_actualizado = self.lista.buscar_por_codigo(str(self.codigo_seleccionado))
        if med_actualizado:
            self.arbol.insertar(med_actualizado)
        persistencia.guardar_medicamentos(self.lista)
        if med_actualizado and stock_anterior is not None and stock_anterior != datos["stock"]:
            diferencia = datos["stock"] - stock_anterior
            kardex.registrar_movimiento(
                med_actualizado.codigo,
                med_actualizado.nombre,
                "entrada" if diferencia > 0 else "salida",
                abs(diferencia),
                datos["stock"],
                usuario=self.usuario_nombre,
                motivo="Ajuste manual de stock desde catálogo",
            )
        self._refrescar_tabla()
        self._limpiar_formulario()
        messagebox.showinfo("Éxito", "Medicamento actualizado.")

    def _eliminar(self):
        if not self.puede_editar:
            messagebox.showerror(
                "Acceso denegado", "Tu rol no tiene permiso para editar el catálogo."
            )
            return
        if not self.codigo_seleccionado:
            messagebox.showwarning(
                "Sin selección", "Selecciona un medicamento de la tabla."
            )
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar este medicamento?"):
            return
        med = self.lista.buscar_por_codigo(str(self.codigo_seleccionado))
        if med:
            self.arbol.eliminar(med.codigo, med.nombre)
            if med.stock > 0:
                kardex.registrar_movimiento(
                    med.codigo,
                    med.nombre,
                    "salida",
                    med.stock,
                    0,
                    usuario=self.usuario_nombre,
                    motivo="Eliminación de medicamento del catálogo",
                )
        self.lista.eliminar(str(self.codigo_seleccionado))
        persistencia.guardar_medicamentos(self.lista)
        self._refrescar_tabla()
        self._limpiar_formulario()

    def _cerrar(self):
        if self.al_cerrar:
            self.al_cerrar()
        self.destroy()
