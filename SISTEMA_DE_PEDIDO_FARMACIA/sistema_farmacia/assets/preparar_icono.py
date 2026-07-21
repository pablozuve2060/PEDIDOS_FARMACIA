import os
from PIL import Image

RUTA_LOGO = os.path.join(os.path.dirname(__file__), "logo_uleam.png")
RUTA_ICONOS = os.path.join(os.path.dirname(__file__), "icons")
RUTA_FAVICON = os.path.join(RUTA_ICONOS, "favicon.png")


def generar_favicon(tamano=128):
    if not os.path.exists(RUTA_LOGO):
        print(f"❌ No se encontró {RUTA_LOGO}")
        print("   Descarga el logo oficial desde https://www.uleam.edu.ec/logos-uleam/")
        print("   y guárdalo como 'assets/logo_uleam.png'")
        return
    os.makedirs(RUTA_ICONOS, exist_ok=True)
    imagen = Image.open(RUTA_LOGO).convert("RGBA")
    ancho, alto = imagen.size
    lado = min(ancho, alto)
    izquierda = (ancho - lado) // 2
    arriba = (alto - lado) // 2
    imagen_cuadrada = imagen.crop((izquierda, arriba, izquierda + lado, arriba + lado))
    imagen_cuadrada = imagen_cuadrada.resize((tamano, tamano), Image.LANCZOS)
    imagen_cuadrada.save(RUTA_FAVICON)
    print(f"✅ Favicon generado en: {RUTA_FAVICON}")


if __name__ == "__main__":
    generar_favicon()
