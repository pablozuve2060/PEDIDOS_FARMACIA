import ttkbootstrap as tb
from ttkbootstrap.constants import *
from gui.estilos import aplicar_favicon, centrar_ventana, FUENTE_TITULO, FUENTE_NORMAL
from services import estanterias


class VentanaEstanterias(tb.Toplevel):
    """Mapa de estanterías: qué categoría tiene cada estante y qué
    medicamentos están ubicados en cada uno."""

    def __init__(self, parent, lista_medicamentos):
        super().__init__(parent)
        self.title("Estanterías del Almacén")
        aplicar_favicon(self)
        self.lista = lista_medicamentos
        self._construir_ui()
        self._refrescar()
        centrar_ventana(self, 780, 560)

    def _construir_ui(self):
        tb.Label(self, text="🗄️ Estanterías del Almacén", font=FUENTE_TITULO).pack(
            pady=(15, 5)
        )
        tb.Label(
            self,
            text="Cada categoría de medicamento tiene asignado un estante fijo. "
                 "Selecciona uno para ver qué hay ubicado ahí.",
            font=FUENTE_NORMAL,
            bootstyle="secondary",
        ).pack(pady=(0, 10))

        buscador = tb.Frame(self)
        buscador.pack(fill="x", padx=15, pady=(0, 10))
        tb.Label(buscador, text="Buscar medicamento (nombre o código):", font=FUENTE_NORMAL).pack(
            side="left", padx=(0, 8)
        )
        self.entry_buscar = tb.Entry(buscador, width=30)
        self.entry_buscar.pack(side="left", padx=(0, 8))
        self.entry_buscar.bind("<KeyRelease>", lambda e: self._buscar_medicamento())
        self.label_resultado_busqueda = tb.Label(
            buscador, text="", font=FUENTE_NORMAL, bootstyle="info"
        )
        self.label_resultado_busqueda.pack(side="left")

        cuerpo = tb.Frame(self)
        cuerpo.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        panel_estantes = tb.Labelframe(cuerpo, text="Estantes", padding=10, bootstyle="secondary")
        panel_estantes.pack(side="left", fill="y", padx=(0, 10))
        self.lista_estantes = tb.Treeview(
            panel_estantes,
            columns=("estante", "categoria", "cantidad"),
            show="headings",
            height=18,
            bootstyle="secondary",
        )
        for col, txt, w in [
            ("estante", "Estante", 55),
            ("categoria", "Categoría", 130),
            ("cantidad", "Ítems", 45),
        ]:
            self.lista_estantes.heading(col, text=txt)
            self.lista_estantes.column(col, width=w, anchor="center")
        self.lista_estantes.pack(fill="y", expand=True)
        self.lista_estantes.bind("<<TreeviewSelect>>", self._al_seleccionar_estante)

        panel_detalle = tb.Labelframe(
            cuerpo, text="Medicamentos en el estante seleccionado", padding=10, bootstyle="primary"
        )
        panel_detalle.pack(side="left", fill="both", expand=True)
        self.tabla_detalle = tb.Treeview(
            panel_detalle,
            columns=("ubicacion", "codigo", "nombre", "stock"),
            show="headings",
            height=18,
            bootstyle="primary",
        )
        for col, txt, w in [
            ("ubicacion", "Ubicación", 75),
            ("codigo", "Código", 70),
            ("nombre", "Nombre", 180),
            ("stock", "Stock", 60),
        ]:
            self.tabla_detalle.heading(col, text=txt)
            self.tabla_detalle.column(col, width=w, anchor="center")
        self.tabla_detalle.pack(fill="both", expand=True)

    def _refrescar(self):
        for fila in self.lista_estantes.get_children():
            self.lista_estantes.delete(fila)
        mapa_categorias = estanterias.mapa_estanterias()
        resumen = estanterias.resumen_por_estante(self.lista)
        # Estante -> categoría (invertimos el mapa categoria->estante)
        categoria_por_estante = {v: k for k, v in mapa_categorias.items()}
        for estante in sorted(set(mapa_categorias.values()) | set(resumen.keys())):
            categoria = categoria_por_estante.get(estante, "—")
            cantidad = len(resumen.get(estante, []))
            self.lista_estantes.insert(
                "", "end", iid=estante, values=(estante, categoria, cantidad)
            )
        self._limpiar_detalle()

    def _limpiar_detalle(self):
        for fila in self.tabla_detalle.get_children():
            self.tabla_detalle.delete(fila)

    def _al_seleccionar_estante(self, event=None):
        seleccion = self.lista_estantes.selection()
        if not seleccion:
            return
        estante = seleccion[0]
        self._mostrar_estante(estante)

    def _mostrar_estante(self, estante):
        self._limpiar_detalle()
        for med in estanterias.medicamentos_por_estante(estante, self.lista):
            self.tabla_detalle.insert(
                "",
                "end",
                values=(med.ubicacion, med.codigo, med.nombre, med.stock),
            )

    def _buscar_medicamento(self):
        texto = self.entry_buscar.get().strip().lower()
        if not texto:
            self.label_resultado_busqueda.config(text="")
            return
        encontrado = None
        for med in self.lista.a_lista():
            if texto in med.codigo.lower() or texto in med.nombre.lower():
                encontrado = med
                break
        if encontrado is None:
            self.label_resultado_busqueda.config(text="No encontrado", bootstyle="danger")
            return
        if not encontrado.ubicacion:
            self.label_resultado_busqueda.config(
                text=f"{encontrado.nombre}: sin ubicación asignada", bootstyle="warning"
            )
            return
        self.label_resultado_busqueda.config(
            text=f"{encontrado.nombre} está en el estante {encontrado.ubicacion}",
            bootstyle="success",
        )
        estante = encontrado.ubicacion.split("-")[0]
        if self.lista_estantes.exists(estante):
            self.lista_estantes.selection_set(estante)
            self.lista_estantes.see(estante)
            self._mostrar_estante(estante)
