class NodoArbol:

    def __init__(self, clave, medicamento):
        self.clave = clave
        self.medicamento = medicamento
        self.izquierdo = None
        self.derecho = None

    def __repr__(self):
        return f"<NodoArbol clave={self.clave}>"
