from models.pedido import Pedido


class ColaPedidos:

    def __init__(self):
        self.frente = None
        self.final = None
        self._tamano = 0
        self._contador_pedidos = 0

    def encolar(self, cliente=None) -> Pedido:
        self._contador_pedidos += 1
        nuevo_pedido = Pedido(numero_pedido=self._contador_pedidos, cliente=cliente)
        if self.final is None:
            self.frente = nuevo_pedido
            self.final = nuevo_pedido
        else:
            self.final.siguiente = nuevo_pedido
            self.final = nuevo_pedido
        self._tamano += 1
        return nuevo_pedido

    def cargar_pedido_existente(self, pedido: Pedido):
        pedido.siguiente = None
        if self.final is None:
            self.frente = pedido
            self.final = pedido
        else:
            self.final.siguiente = pedido
            self.final = pedido
        self._tamano += 1
        if pedido.numero_pedido > self._contador_pedidos:
            self._contador_pedidos = pedido.numero_pedido

    def atender(self) -> Pedido:
        if self.frente is None:
            return None
        pedido_atendido = self.frente
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        pedido_atendido.siguiente = None
        pedido_atendido.cambiar_estado("despachado")
        self._tamano -= 1
        return pedido_atendido

    def cancelar(self, numero_pedido) -> Pedido:
        actual = self.frente
        anterior = None
        while actual is not None:
            if actual.numero_pedido == numero_pedido:
                if anterior is None:
                    self.frente = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                if actual is self.final:
                    self.final = anterior
                actual.cambiar_estado("cancelado")
                actual.siguiente = None
                self._tamano -= 1
                return actual
            anterior = actual
            actual = actual.siguiente
        return None

    def ver_frente(self) -> Pedido:
        return self.frente

    def a_lista(self):
        resultado = []
        actual = self.frente
        while actual is not None:
            resultado.append(actual)
            actual = actual.siguiente
        return resultado

    def esta_vacia(self):
        return self.frente is None

    def __len__(self):
        return self._tamano
