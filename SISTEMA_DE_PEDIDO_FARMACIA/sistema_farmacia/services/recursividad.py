def calcular_total_recursivo(items, indice=0):
    if indice >= len(items):
        return 0
    return items[indice].subtotal + calcular_total_recursivo(items, indice + 1)


def contar_medicamentos_bajo_stock_recursivo(lista_medicamentos, umbral=10, indice=0):
    if indice >= len(lista_medicamentos):
        return 0
    extra = 1 if lista_medicamentos[indice].stock < umbral else 0
    return extra + contar_medicamentos_bajo_stock_recursivo(
        lista_medicamentos, umbral, indice + 1
    )


def altura_arbol_recursiva(nodo):
    if nodo is None:
        return 0
    altura_izquierda = altura_arbol_recursiva(nodo.izquierdo)
    altura_derecha = altura_arbol_recursiva(nodo.derecho)
    return 1 + max(altura_izquierda, altura_derecha)


def contar_nodos_arbol_recursivo(nodo):
    if nodo is None:
        return 0
    return (
        1
        + contar_nodos_arbol_recursivo(nodo.izquierdo)
        + contar_nodos_arbol_recursivo(nodo.derecho)
    )


def buscar_pedido_por_numero_recursivo(nodo_pedido, numero_buscado):
    if nodo_pedido is None:
        return None
    if nodo_pedido.numero_pedido == numero_buscado:
        return nodo_pedido
    return buscar_pedido_por_numero_recursivo(nodo_pedido.siguiente, numero_buscado)
