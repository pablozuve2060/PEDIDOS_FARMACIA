import os
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.style import Style, ThemeDefinition

# ---------------------------------------------------------------------------
# Paleta "Netflix" — fondo casi negro, acentos en rojo, tarjetas oscuras.
# ---------------------------------------------------------------------------
TEMA = "netflix"

NF_ROJO = "#E50914"
NF_ROJO_HOVER = "#F6121D"
NF_NEGRO = "#000000"
NF_FONDO = "#141414"
NF_TARJETA = "#1F1F1F"
NF_TARJETA_HOVER = "#2B2B2B"
NF_BORDE = "#333333"
NF_BLANCO = "#FFFFFF"
NF_GRIS_TEXTO = "#B3B3B3"
NF_VERDE = "#46D369"
NF_AMBAR = "#F5B400"
NF_AZUL = "#54B4D3"

_COLORES_TEMA_NETFLIX = {
    "primary": NF_ROJO,
    "secondary": "#5A5A5A",
    "success": NF_VERDE,
    "info": NF_AZUL,
    "warning": NF_AMBAR,
    "danger": "#E5342E",
    "light": NF_GRIS_TEXTO,
    "dark": NF_NEGRO,
    "bg": NF_FONDO,
    "fg": NF_BLANCO,
    "selectbg": "#3A3A3A",
    "selectfg": NF_BLANCO,
    "border": NF_BORDE,
    "inputfg": NF_BLANCO,
    "inputbg": NF_TARJETA,
    "active": NF_TARJETA_HOVER,
}

RUTA_LOGO = os.path.join("assets", "logo_farmacia.png")
RUTA_LOGO_ULEAM = os.path.join("assets", "escudo_uleam.png")
RUTA_LOGO_ULEAM_COMPLETO = os.path.join("assets", "logo_uleam.png")
RUTA_ICONO = os.path.join("assets", "icons", "favicon.png")
COLOR_PRIMARIO = NF_ROJO
COLOR_PELIGRO = "#E5342E"
COLOR_EXITO = NF_VERDE
COLOR_TEXTO_SECUNDARIO = NF_GRIS_TEXTO
FUENTE_TITULO = ("Segoe UI", 21, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 12)
FUENTE_NORMAL = ("Segoe UI", 10)
FUENTE_BOTON = ("Segoe UI", 10, "bold")


def _registrar_tema_netflix(style):
    """Registra (una sola vez) el tema oscuro personalizado 'netflix'."""
    if "netflix" not in style.theme_names():
        style.register_theme(
            ThemeDefinition(name="netflix", colors=_COLORES_TEMA_NETFLIX, themetype="dark")
        )


def crear_ventana_principal(titulo="Sistema de Farmacia"):
    # Importante: la ventana Tk real debe crearse ANTES de tocar el Style,
    # de lo contrario ttkbootstrap crea una raíz oculta "huérfana" y falla
    # más adelante (p. ej. al crear un Separator) con RuntimeError en
    # versiones recientes de Python/Tkinter.
    ventana = tb.Window(themename="darkly")
    _registrar_tema_netflix(ventana.style)
    ventana.style.theme_use(TEMA)
    ventana.title(titulo)
    ventana.configure(background=NF_FONDO)
    aplicar_favicon(ventana)
    return ventana


def aplicar_favicon(ventana):
    ruta_icono = RUTA_ICONO if os.path.exists(RUTA_ICONO) else RUTA_LOGO_ULEAM
    try:
        if os.path.exists(ruta_icono):
            icono = tb.PhotoImage(file=ruta_icono)
            ventana.iconphoto(True, icono)
            ventana._icono_ref = icono
    except Exception:
        pass


def cargar_logo_uleam(alto_deseado=60):
    if not os.path.exists(RUTA_LOGO_ULEAM):
        return None
    try:
        from PIL import Image
        import ttkbootstrap as tb

        imagen = Image.open(RUTA_LOGO_ULEAM)
        proporcion = alto_deseado / imagen.height
        nuevo_ancho = int(imagen.width * proporcion)
        imagen = imagen.resize((nuevo_ancho, alto_deseado), Image.LANCZOS)
        from PIL import ImageTk

        return ImageTk.PhotoImage(imagen)
    except Exception:
        return None


def valores_combo_medicamentos(lista_medicamentos, solo_con_stock=False):
    """Construye la lista de strings 'CODIGO - Nombre' para poblar un
    Combobox de selección de medicamentos, a partir de la lista enlazada.

    Si solo_con_stock=True, se excluyen los medicamentos con stock 0
    (útil en pantallas donde se va a descontar stock, como Pedidos).
    """
    medicamentos = lista_medicamentos.a_lista()
    if solo_con_stock:
        medicamentos = [m for m in medicamentos if m.stock > 0]
    medicamentos.sort(key=lambda m: m.nombre.lower())
    return [f"{m.codigo} - {m.nombre}" for m in medicamentos]


def codigo_desde_valor_combo(valor):
    """Extrae el código de medicamento de un valor con formato
    'CODIGO - Nombre' mostrado en un Combobox. Si no hay separador,
    devuelve el valor tal cual (limpio de espacios)."""
    if not valor:
        return ""
    return valor.split(" - ", 1)[0].strip()


def centrar_ventana(ventana, ancho, alto):
    ventana.update_idletasks()
    x = ventana.winfo_screenwidth() // 2 - ancho // 2
    y = ventana.winfo_screenheight() // 2 - alto // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


# ---------------------------------------------------------------------------
# Componentes visuales estilo Netflix (tarjetas redondeadas con hover)
# ---------------------------------------------------------------------------

def _redondear(canvas, x1, y1, x2, y2, radio, **kwargs):
    puntos = [
        x1 + radio, y1,
        x2 - radio, y1,
        x2, y1,
        x2, y1 + radio,
        x2, y2 - radio,
        x2, y2,
        x2 - radio, y2,
        x1 + radio, y2,
        x1, y2,
        x1, y2 - radio,
        x1, y1 + radio,
        x1, y1,
    ]
    return canvas.create_polygon(puntos, smooth=True, **kwargs)


class TarjetaKPI(tk.Canvas):
    """Tarjeta oscura tipo Netflix para métricas del panel principal."""

    def __init__(self, parent, icono, titulo, valor, color_acento=NF_ROJO, ancho=190, alto=90):
        super().__init__(parent, width=ancho, height=alto, bg=NF_FONDO,
                          highlightthickness=0, bd=0)
        self.ancho, self.alto = ancho, alto
        self.color_acento = color_acento
        self._dibujar(icono, titulo, valor)

    def _dibujar(self, icono, titulo, valor):
        self.delete("all")
        _redondear(self, 1, 1, self.ancho - 1, self.alto - 1, 14, fill=NF_TARJETA, outline="")
        self.create_rectangle(0, 10, 5, self.alto - 10, fill=self.color_acento, outline="")
        self.create_text(18, self.alto / 2, text=icono, font=("Segoe UI", 18),
                          fill=self.color_acento, anchor="w")
        self.create_text(50, self.alto / 2 - 13, text=valor, font=("Segoe UI", 18, "bold"),
                          fill=NF_BLANCO, anchor="w")
        self.create_text(50, self.alto / 2 + 15, text=titulo, font=("Segoe UI", 8),
                          fill=NF_GRIS_TEXTO, anchor="w", width=self.ancho - 55)

    def actualizar(self, icono, titulo, valor):
        self._dibujar(icono, titulo, valor)


class TarjetaMenu(tk.Canvas):
    """Tarjeta grande de navegación estilo 'tile' de Netflix, con efecto hover."""

    def __init__(self, parent, icono, titulo, subtitulo, color_acento, comando,
                 ancho=340, alto=78):
        super().__init__(parent, width=ancho, height=alto, bg=NF_FONDO,
                          highlightthickness=0, bd=0, cursor="hand2")
        self.ancho, self.alto = ancho, alto
        self.color_acento = color_acento
        self.comando = comando
        self._resaltada = False
        self._icono, self._titulo, self._subtitulo = icono, titulo, subtitulo
        self._dibujar()
        self.bind("<Enter>", self._al_entrar)
        self.bind("<Leave>", self._al_salir)

    def _dibujar(self):
        self.delete("all")
        fondo = NF_TARJETA_HOVER if self._resaltada else NF_TARJETA
        borde = self.color_acento if self._resaltada else NF_BORDE
        _redondear(self, 1, 1, self.ancho - 1, self.alto - 1, 12,
                   fill=fondo, outline=borde, width=1.4)
        cx, cy, r = 34, self.alto / 2, 20
        self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=self.color_acento, outline="")
        self.create_text(cx, cy, text=self._icono, font=("Segoe UI", 15))
        self.create_text(66, cy - 11 if self._subtitulo else cy, text=self._titulo,
                          font=("Segoe UI", 11, "bold"), fill=NF_BLANCO, anchor="w")
        if self._subtitulo:
            self.create_text(66, cy + 11, text=self._subtitulo, font=("Segoe UI", 8),
                              fill=NF_GRIS_TEXTO, anchor="w", width=self.ancho - 100)
        self.create_text(self.ancho - 20, cy, text="›", font=("Segoe UI", 16, "bold"),
                          fill=self.color_acento, anchor="e")
        for item in self.find_all():
            self.tag_bind(item, "<Button-1>", lambda e: self.comando())
            self.tag_bind(item, "<Enter>", self._al_entrar)
            self.tag_bind(item, "<Leave>", self._al_salir)

    def _al_entrar(self, event=None):
        if not self._resaltada:
            self._resaltada = True
            self._dibujar()

    def _al_salir(self, event=None):
        if self._resaltada:
            self._resaltada = False
            self._dibujar()
