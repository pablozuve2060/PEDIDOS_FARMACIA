import ttkbootstrap as tb
from ttkbootstrap.constants import *
from gui.estilos import (
    aplicar_favicon,
    centrar_ventana,
    cargar_logo_uleam,
    FUENTE_TITULO,
    FUENTE_NORMAL,
    FUENTE_BOTON,
    COLOR_PELIGRO,
)
from services import persistencia


class VentanaLogin(tb.Frame):

    def __init__(self, parent, al_iniciar_sesion):
        super().__init__(parent, padding=30)
        self.parent = parent
        self.al_iniciar_sesion = al_iniciar_sesion
        self.pack(fill="both", expand=True)
        self._construir_ui()
        centrar_ventana(parent, 420, 530)

    def _construir_ui(self):
        contenedor = tb.Frame(self, padding=20)
        contenedor.pack(expand=True)
        logo_uleam = cargar_logo_uleam(alto_deseado=110)
        if logo_uleam is not None:
            label_logo = tb.Label(contenedor, image=logo_uleam)
            label_logo.image = logo_uleam
            label_logo.pack(pady=(0, 10))
        tb.Label(contenedor, text="Farmacia", font=FUENTE_TITULO).pack(pady=(10, 0))
        tb.Label(
            contenedor,
            text="Sistema de Pedidos",
            font=FUENTE_NORMAL,
            bootstyle="secondary",
        ).pack(pady=(0, 25))
        tb.Label(contenedor, text="Usuario", font=FUENTE_NORMAL).pack(anchor="w")
        self.entry_usuario = tb.Entry(contenedor, width=30)
        self.entry_usuario.pack(pady=(2, 15), ipady=4)
        tb.Label(contenedor, text="Contraseña", font=FUENTE_NORMAL).pack(anchor="w")
        self.entry_clave = tb.Entry(contenedor, width=30, show="•")
        self.entry_clave.pack(pady=(2, 5), ipady=4)
        self.label_error = tb.Label(
            contenedor, text="", font=FUENTE_NORMAL, bootstyle="danger"
        )
        self.label_error.pack(pady=(0, 10))
        tb.Button(
            contenedor,
            text="Iniciar Sesión",
            bootstyle="success",
            width=25,
            command=self._validar_login,
        ).pack(pady=5, ipady=4)
        self.entry_clave.bind("<Return>", lambda e: self._validar_login())

    def _validar_login(self):
        usuario = self.entry_usuario.get().strip()
        clave = self.entry_clave.get().strip()
        u = persistencia.verificar_credenciales(usuario, clave)
        if u:
            self.label_error.config(text="")
            self.al_iniciar_sesion(u)
            return
        self.label_error.config(text="Usuario o contraseña incorrectos")
