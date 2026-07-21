from datetime import datetime


class ItemPedido:

    def __init__(
        self, codigo_medicamento, nombre_medicamento, cantidad, precio_unitario
    ):
        self.codigo_medicamento = codigo_medicamento
        self.nombre_medicamento = nombre_medicamento
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario


class Pedido:
    ESTADOS = ("en_cola", "atendiendo", "despachado", "cancelado")

    def __init__(self, numero_pedido, cliente=None):
        self.numero_pedido = numero_pedido
        self.cliente = cliente
        self.items = []
        self.estado = "en_cola"
        self.hora_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.hora_despacho = None
        self.siguiente = None

    def agregar_item(
        self, codigo_medicamento, nombre_medicamento, cantidad, precio_unitario
    ):
        self.items.append(
            ItemPedido(
                codigo_medicamento, nombre_medicamento, cantidad, precio_unitario
            )
        )

    @property
    def total(self):
        return sum((item.subtotal for item in self.items))

    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado not in self.ESTADOS:
            raise ValueError(f"Estado inválido: {nuevo_estado}")
        self.estado = nuevo_estado
        if nuevo_estado == "despachado":
            self.hora_despacho = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def a_diccionario(self):
        return {
            "numero_pedido": self.numero_pedido,
            "cliente": self.cliente,
            "estado": self.estado,
            "hora_registro": self.hora_registro,
            "hora_despacho": self.hora_despacho,
            "items": [
                {
                    "codigo_medicamento": item.codigo_medicamento,
                    "nombre_medicamento": item.nombre_medicamento,
                    "cantidad": item.cantidad,
                    "precio_unitario": item.precio_unitario,
                }
                for item in self.items
            ],
        }

    @staticmethod
    def desde_diccionario(data):
        pedido = Pedido(numero_pedido=data["numero_pedido"], cliente=data.get("cliente"))
        pedido.estado = data.get("estado", "en_cola")
        pedido.hora_registro = data.get("hora_registro", pedido.hora_registro)
        pedido.hora_despacho = data.get("hora_despacho")
        for item in data.get("items", []):
            pedido.agregar_item(
                item["codigo_medicamento"],
                item["nombre_medicamento"],
                item["cantidad"],
                item["precio_unitario"],
            )
        return pedido

    def __repr__(self):
        return (
            f"<Pedido #{self.numero_pedido} - {self.estado} - Total: ${self.total:.2f}>"
        )
