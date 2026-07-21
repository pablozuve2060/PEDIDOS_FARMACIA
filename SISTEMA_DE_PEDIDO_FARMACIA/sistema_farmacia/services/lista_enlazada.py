from models.medicamento import Medicamento


class ListaEnlazadaMedicamentos:

    def __init__(self):
        self.cabeza = None
        self._tamano = 0

    def insertar(self, medicamento: Medicamento):
        nuevo_nodo = medicamento
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente is not None:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
        self._tamano += 1

    def eliminar(self, codigo):
        actual = self.cabeza
        anterior = None
        while actual is not None:
            if actual.codigo == codigo:
                if anterior is None:
                    self.cabeza = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                self._tamano -= 1
                return True
            anterior = actual
            actual = actual.siguiente
        return False

    def actualizar(self, codigo, **campos):
        med = self.buscar_por_codigo(codigo)
        if med is None:
            return False
        for campo, valor in campos.items():
            if hasattr(med, campo):
                setattr(med, campo, valor)
        return True

    def buscar_por_codigo(self, codigo):
        actual = self.cabeza
        while actual is not None:
            if actual.codigo == codigo:
                return actual
            actual = actual.siguiente
        return None

    def a_lista(self):
        resultado = []
        actual = self.cabeza
        while actual is not None:
            resultado.append(actual)
            actual = actual.siguiente
        return resultado

    def __len__(self):
        return self._tamano
