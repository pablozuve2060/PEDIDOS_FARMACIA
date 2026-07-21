import json
import os

RUTA_PILA = os.path.join("data", "pila_deshacer.json")


class PilaDeshacerKardex:

    def __init__(self):
        self.items = []
        self._cargar()

    def push(self, movimiento):
        self.items.append(movimiento)
        self._guardar()

    def pop(self):
        if self.esta_vacia():
            raise IndexError("No hay movimientos en la pila: no hay nada que deshacer.")
        movimiento = self.items.pop()
        self._guardar()
        return movimiento

    def ver_tope(self):
        if self.esta_vacia():
            return None
        return self.items[-1]

    def esta_vacia(self):
        return len(self.items) == 0

    def vaciar(self):
        self.items = []
        self._guardar()

    def __len__(self):
        return len(self.items)

    def _cargar(self):
        if not os.path.exists(RUTA_PILA):
            self.items = []
            return
        with open(RUTA_PILA, "r", encoding="utf-8") as f:
            self.items = json.load(f)

    def _guardar(self):
        os.makedirs(os.path.dirname(RUTA_PILA), exist_ok=True)
        with open(RUTA_PILA, "w", encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False, indent=4)
