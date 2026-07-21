from datetime import datetime

UMBRAL_DIAS_POR_VENCER = 30


class Medicamento:

    def __init__(
        self,
        codigo,
        nombre,
        principio_activo,
        precio,
        stock,
        categoria="General",
        fecha_vencimiento=None,
        ubicacion=None,
    ):
        self.codigo = codigo
        self.nombre = nombre
        self.principio_activo = principio_activo
        self.precio = precio
        self.stock = stock
        self.categoria = categoria
        self.fecha_vencimiento = fecha_vencimiento or None
        self.ubicacion = ubicacion or None
        self.siguiente = None

    def dias_para_vencer(self):
        if not self.fecha_vencimiento:
            return None
        try:
            fecha = datetime.strptime(self.fecha_vencimiento, "%Y-%m-%d")
        except ValueError:
            return None
        return (fecha.date() - datetime.now().date()).days

    def estado_vencimiento(self, umbral_dias=UMBRAL_DIAS_POR_VENCER):
        dias = self.dias_para_vencer()
        if dias is None:
            return "sin_fecha"
        if dias < 0:
            return "vencido"
        if dias <= umbral_dias:
            return "por_vencer"
        return "vigente"

    def a_diccionario(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "principio_activo": self.principio_activo,
            "precio": self.precio,
            "stock": self.stock,
            "categoria": self.categoria,
            "fecha_vencimiento": self.fecha_vencimiento,
            "ubicacion": self.ubicacion,
        }

    @staticmethod
    def desde_diccionario(data):
        return Medicamento(
            codigo=data["codigo"],
            nombre=data["nombre"],
            principio_activo=data["principio_activo"],
            precio=data["precio"],
            stock=data["stock"],
            categoria=data.get("categoria", "General"),
            fecha_vencimiento=data.get("fecha_vencimiento"),
            ubicacion=data.get("ubicacion"),
        )

    def __repr__(self):
        return f"<Medicamento {self.codigo} - {self.nombre} (stock: {self.stock})>"
