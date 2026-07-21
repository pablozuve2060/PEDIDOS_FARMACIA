import ttkbootstrap as tb
from ttkbootstrap.constants import *
from gui.estilos import aplicar_favicon, centrar_ventana, FUENTE_TITULO, FUENTE_NORMAL


class VentanaBusqueda(tb.Toplevel):

    def __init__(self, parent, arbol_medicamentos, lista_medicamentos):
        super().__init__(parent)
        self.title("Búsqueda de Medicamentos")
        aplicar_favicon(self)
        self.arbol = arbol_medicamentos
        self.lista = lista_medicamentos
        self._construir_ui()
        centrar_ventana(self, 680, 520)

    def _construir_ui(self):
        tb.Label(self, text="🔎 Búsqueda de Medicamentos", font=FUENTE_TITULO).pack(
            pady=(15, 5)
        )
        controles = tb.Frame(self)
        controles.pack(pady=(0, 10))
        tb.Label(
            controles,
            text="Buscar por:",
            font=FUENTE_NORMAL,
        ).pack(side="left", padx=(0, 8))
        self.criterio = tb.StringVar(value="nombre_codigo")
        tb.Radiobutton(
            controles,
            text="Nombre / Código",
            variable=self.criterio,
            value="nombre_codigo",
            bootstyle="toolbutton",
            command=self._buscar_en_vivo,
        ).pack(side="left", padx=3)
        tb.Radiobutton(
            controles,
            text="Principio Activo",
            variable=self.criterio,
            value="principio_activo",
            bootstyle="toolbutton",
            command=self._buscar_en_vivo,
        ).pack(side="left", padx=3)
        self.label_ayuda = tb.Label(
            self,
            text="Escribe el nombre o el código (completo o parcial) — autocompletar en vivo",
            font=FUENTE_NORMAL,
            bootstyle="secondary",
        )
        self.label_ayuda.pack(pady=(0, 10))
        self.entry_buscar = tb.Entry(self, width=40, font=("Segoe UI", 12))
        self.entry_buscar.pack(pady=(0, 15))
        self.entry_buscar.bind("<KeyRelease>", self._buscar_en_vivo)
        columnas = ("codigo", "nombre", "principio_activo", "precio", "stock", "ubicacion")
        self.tabla = tb.Treeview(
            self, columns=columnas, show="headings", bootstyle="info", height=14
        )
        encabezados = [
            ("codigo", "Código", 65),
            ("nombre", "Nombre", 160),
            ("principio_activo", "Principio Activo", 135),
            ("precio", "Precio", 65),
            ("stock", "Stock", 55),
            ("ubicacion", "Estante", 70),
        ]
        for col, txt, w in encabezados:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self._mostrar_todos()

    def _mostrar_todos(self):
        resultados = self.arbol.recorrido_inorden()
        self._llenar_tabla(resultados)

    def _buscar_en_vivo(self, event=None):
        texto = self.entry_buscar.get().strip()
        if self.criterio.get() == "principio_activo":
            self.label_ayuda.config(
                text="Escribe parte del principio activo — coincide en cualquier posición"
            )
            if not texto:
                self._mostrar_todos()
                return
            resultados = self._buscar_por_principio_activo(texto)
        else:
            self.label_ayuda.config(
                text="Escribe el nombre o el código (completo o parcial) — autocompletar en vivo"
            )
            if not texto:
                self._mostrar_todos()
                return
            resultados = self.arbol.buscar_por_prefijo(texto)
        self._llenar_tabla(resultados)

    def _buscar_por_principio_activo(self, texto):
        texto = texto.lower()
        resultados = [
            med for med in self.lista.a_lista() if texto in med.principio_activo.lower()
        ]
        resultados.sort(key=lambda med: med.nombre.lower())
        return resultados

    def _llenar_tabla(self, medicamentos):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for med in medicamentos:
            self.tabla.insert(
                "",
                "end",
                values=(
                    med.codigo,
                    med.nombre,
                    med.principio_activo,
                    f"${med.precio:.2f}",
                    med.stock,
                    med.ubicacion or "—",
                ),
            )
