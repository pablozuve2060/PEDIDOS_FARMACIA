import ttkbootstrap as tb
from gui.estilos import aplicar_favicon


def crear_toplevel_scrollable(parent, titulo, ancho=700, alto=500):
    ventana = tb.Toplevel(parent)
    ventana.title(titulo)
    ventana.geometry(f"{ancho}x{alto}")
    aplicar_favicon(ventana)
    contenedor = tb.Frame(ventana)
    contenedor.pack(fill="both", expand=True)
    canvas = tb.Canvas(contenedor, highlightthickness=0)
    scrollbar = tb.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    frame_contenido = tb.Frame(canvas)
    frame_contenido.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=frame_contenido, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    return (ventana, frame_contenido)
