from models.nodo_arbol import NodoArbol


class ArbolBusquedaMedicamentos:

    def __init__(self):
        self.raiz_nombre = None
        self.raiz_codigo = None

    def insertar(self, medicamento):
        self.raiz_nombre = self._insertar_recursivo(
            self.raiz_nombre, medicamento.nombre.lower(), medicamento
        )
        self.raiz_codigo = self._insertar_recursivo(
            self.raiz_codigo, medicamento.codigo.lower(), medicamento
        )

    def _insertar_recursivo(self, nodo, clave, medicamento):
        if nodo is None:
            return NodoArbol(clave, medicamento)
        if clave < nodo.clave:
            nodo.izquierdo = self._insertar_recursivo(
                nodo.izquierdo, clave, medicamento
            )
        elif clave > nodo.clave:
            nodo.derecho = self._insertar_recursivo(nodo.derecho, clave, medicamento)
        else:
            nodo.medicamento = medicamento
        return nodo

    def buscar(self, nombre):
        return self._buscar_recursivo(self.raiz_nombre, nombre.lower())

    def buscar_por_codigo(self, codigo):
        return self._buscar_recursivo(self.raiz_codigo, codigo.lower())

    def _buscar_recursivo(self, nodo, clave):
        if nodo is None:
            return None
        if clave == nodo.clave:
            return nodo.medicamento
        elif clave < nodo.clave:
            return self._buscar_recursivo(nodo.izquierdo, clave)
        else:
            return self._buscar_recursivo(nodo.derecho, clave)

    def buscar_por_prefijo(self, prefijo):
        prefijo = prefijo.lower()
        resultados = []
        vistos = set()
        self._recorrer_prefijo(self.raiz_nombre, prefijo, resultados, vistos)
        self._recorrer_prefijo(self.raiz_codigo, prefijo, resultados, vistos)
        resultados.sort(key=lambda med: med.nombre.lower())
        return resultados

    def _recorrer_prefijo(self, nodo, prefijo, resultados, vistos):
        if nodo is None:
            return
        self._recorrer_prefijo(nodo.izquierdo, prefijo, resultados, vistos)
        if nodo.clave.startswith(prefijo) and nodo.medicamento.codigo not in vistos:
            resultados.append(nodo.medicamento)
            vistos.add(nodo.medicamento.codigo)
        self._recorrer_prefijo(nodo.derecho, prefijo, resultados, vistos)

    def eliminar(self, codigo, nombre):
        self.raiz_nombre = self._eliminar_recursivo(self.raiz_nombre, nombre.lower())
        self.raiz_codigo = self._eliminar_recursivo(self.raiz_codigo, codigo.lower())

    def _eliminar_recursivo(self, nodo, clave):
        if nodo is None:
            return None
        if clave < nodo.clave:
            nodo.izquierdo = self._eliminar_recursivo(nodo.izquierdo, clave)
        elif clave > nodo.clave:
            nodo.derecho = self._eliminar_recursivo(nodo.derecho, clave)
        else:
            if nodo.izquierdo is None:
                return nodo.derecho
            if nodo.derecho is None:
                return nodo.izquierdo
            sucesor = self._minimo(nodo.derecho)
            nodo.clave = sucesor.clave
            nodo.medicamento = sucesor.medicamento
            nodo.derecho = self._eliminar_recursivo(nodo.derecho, sucesor.clave)
        return nodo

    def _minimo(self, nodo):
        while nodo.izquierdo is not None:
            nodo = nodo.izquierdo
        return nodo

    def recorrido_inorden(self):
        resultados = []
        self._inorden_recursivo(self.raiz_nombre, resultados)
        return resultados

    def _inorden_recursivo(self, nodo, resultados):
        if nodo is None:
            return
        self._inorden_recursivo(nodo.izquierdo, resultados)
        resultados.append(nodo.medicamento)
        self._inorden_recursivo(nodo.derecho, resultados)
