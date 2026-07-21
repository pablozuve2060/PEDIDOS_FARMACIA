from gui.estilos import crear_ventana_principal
from gui.login import VentanaLogin
from gui.dashboard import Dashboard


def iniciar_sesion(usuario):
    for widget in ventana.winfo_children():
        widget.destroy()
    Dashboard(ventana, usuario)


if __name__ == "__main__":
    ventana = crear_ventana_principal("Sistema de Farmacia")
    VentanaLogin(ventana, al_iniciar_sesion=iniciar_sesion)
    ventana.mainloop()
