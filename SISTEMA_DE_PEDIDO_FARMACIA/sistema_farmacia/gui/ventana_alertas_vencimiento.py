import ttkbootstrap as tb
from ttkbootstrap.constants import *
from gui.estilos import aplicar_favicon, centrar_ventana, FUENTE_TITULO, FUENTE_NORMAL


class VentanaAlertasVencimiento(tb.Toplevel):

    def __init__(self, parent, lista_medicamentos):
        super().__init__(parent)
        self.title("Alertas de Vencimiento")
        aplicar_favicon(self)
        self.lista = lista_medicamentos
        self._construir_ui()
        self._refrescar()
        centrar_ventana(self, 700, 520)

    def _construir_ui(self):
        tb.Label(
            self, text="⏰ Alertas de Vencimiento", font=FUENTE_TITULO
        ).pack(pady=(15, 5))
        controles = tb.Frame(self)
        controles.pack(pady=(0, 10))
        tb.Label(controles, text="Alertar si vence en:", font=FUENTE_NORMAL).pack(
            side="left", padx=(0, 8)
        )
        self.umbral = tb.IntVar(value=30)
        self.combo_umbral = tb.Combobox(
            controles,
            textvariable=self.umbral,
            values=[7, 15, 30, 60, 90],
            width=6,
            state="readonly",
        )
        self.combo_umbral.pack(side="left")
        tb.Label(controles, text="días", font=FUENTE_NORMAL).pack(
            side="left", padx=(6, 0)
        )
        self.combo_umbral.bind("<<ComboboxSelected>>", lambda e: self._refrescar())
        self.label_resumen = tb.Label(self, text="", font=FUENTE_NORMAL, bootstyle="secondary")
        self.label_resumen.pack(pady=(0, 10))
        columnas = ("codigo", "nombre", "vencimiento", "dias", "estado")
        self.tabla = tb.Treeview(
            self, columns=columnas, show="headings", bootstyle="danger", height=16
        )
        encabezados = [
            ("codigo", "Código", 70),
            ("nombre", "Nombre", 200),
            ("vencimiento", "Vencimiento", 100),
            ("dias", "Días restantes", 110),
            ("estado", "Estado", 100),
        ]
        for col, txt, w in encabezados:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.tabla.tag_configure("vencido", foreground="#FFFFFF", background="#D9534F")
        self.tabla.tag_configure("por_vencer", foreground="#B8860B")

    def _refrescar(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        umbral = int(self.umbral.get())
        alertas = []
        for med in self.lista.a_lista():
            estado = med.estado_vencimiento(umbral_dias=umbral)
            if estado in ("vencido", "por_vencer"):
                alertas.append((med, estado))
        alertas.sort(key=lambda par: par[0].dias_para_vencer())
        vencidos = sum(1 for _, estado in alertas if estado == "vencido")
        por_vencer = sum(1 for _, estado in alertas if estado == "por_vencer")
        self.label_resumen.config(
            text=f"🔴 {vencidos} vencido(s)   🟡 {por_vencer} por vencer"
        )
        for med, estado in alertas:
            dias = med.dias_para_vencer()
            texto_estado = "VENCIDO" if estado == "vencido" else "Por vencer"
            texto_dias = f"{dias} días" if dias >= 0 else f"{abs(dias)} días atrás"
            self.tabla.insert(
                "",
                "end",
                values=(med.codigo, med.nombre, med.fecha_vencimiento, texto_dias, texto_estado),
                tags=(estado,),
            )
        if not alertas:
            self.tabla.insert(
                "",
                "end",
                values=("—", "No hay medicamentos vencidos ni por vencer ✅", "", "", ""),
            )
