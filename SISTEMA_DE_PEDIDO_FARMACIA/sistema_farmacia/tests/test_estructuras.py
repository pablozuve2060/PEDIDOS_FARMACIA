import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.medicamento import Medicamento
from services.lista_enlazada import ListaEnlazadaMedicamentos
from services.arbol_busqueda import ArbolBusquedaMedicamentos
from services.cola_pedidos import ColaPedidos
from services.pila_movimientos import PilaDeshacerKardex

fallos = []


def verificar(nombre, condicion):
    estado = "OK " if condicion else "FALLÓ"
    print(f"[{estado}] {nombre}")
    if not condicion:
        fallos.append(nombre)


def medicamento_prueba(codigo="MED999", nombre="Paracetamol 500mg", stock=20):
    return Medicamento(
        codigo=codigo,
        nombre=nombre,
        principio_activo="Paracetamol",
        precio=1.5,
        stock=stock,
        categoria="Analgésico",
        fecha_vencimiento="2027-01-01",
    )


print("\n========== 1. LISTA ENLAZADA ==========")

print("--- Caso 1: flujo normal ---")
lista = ListaEnlazadaMedicamentos()
lista.insertar(medicamento_prueba("MED001", "Paracetamol 500mg"))
lista.insertar(medicamento_prueba("MED002", "Ibuprofeno 400mg"))
verificar("insertar agrega elementos", len(lista) == 2)
encontrado = lista.buscar_por_codigo("MED002")
verificar("buscar_por_codigo encuentra el elemento correcto", encontrado is not None and encontrado.nombre == "Ibuprofeno 400mg")
verificar("eliminar quita un elemento existente", lista.eliminar("MED001") is True and len(lista) == 1)

print("--- Caso 2: caso límite (lista vacía) ---")
lista_vacia = ListaEnlazadaMedicamentos()
verificar("longitud de lista vacía es 0", len(lista_vacia) == 0)
verificar("buscar en lista vacía retorna None", lista_vacia.buscar_por_codigo("X") is None)
verificar("eliminar en lista vacía retorna False", lista_vacia.eliminar("X") is False)

print("--- Caso 3: dato inválido ---")
verificar("buscar código inexistente retorna None", lista.buscar_por_codigo("NOEXISTE") is None)
verificar("eliminar código inexistente retorna False", lista.eliminar("NOEXISTE") is False)
verificar("actualizar código inexistente retorna False", lista.actualizar("NOEXISTE", stock=5) is False)


print("\n========== 2. ÁRBOL BINARIO DE BÚSQUEDA ==========")

print("--- Caso 1: flujo normal ---")
arbol = ArbolBusquedaMedicamentos()
for cod, nom in [("MED010", "Amoxicilina 500mg"), ("MED011", "Loratadina 10mg"), ("MED012", "Omeprazol 20mg")]:
    arbol.insertar(medicamento_prueba(cod, nom))
verificar("buscar por nombre encuentra el medicamento", arbol.buscar("Loratadina 10mg") is not None)
verificar("buscar por código encuentra el medicamento", arbol.buscar_por_codigo("MED012") is not None)
verificar("recorrido inorden retorna todos los nodos ordenados", len(arbol.recorrido_inorden()) == 3)
resultados_prefijo = arbol.buscar_por_prefijo("amox")
verificar("búsqueda por prefijo encuentra coincidencias", len(resultados_prefijo) == 1)
arbol.eliminar("MED011", "Loratadina 10mg")
verificar("eliminar reduce el recorrido inorden", len(arbol.recorrido_inorden()) == 2)

print("--- Caso 2: caso límite (árbol vacío / un solo nodo) ---")
arbol_vacio = ArbolBusquedaMedicamentos()
verificar("buscar en árbol vacío retorna None", arbol_vacio.buscar("cualquiera") is None)
verificar("recorrido inorden de árbol vacío es lista vacía", arbol_vacio.recorrido_inorden() == [])
arbol_vacio.insertar(medicamento_prueba("MED020", "Único"))
verificar("árbol con un solo nodo se busca correctamente", arbol_vacio.buscar("Único") is not None)

print("--- Caso 3: dato inválido (búsqueda inexistente) ---")
verificar("buscar nombre inexistente retorna None", arbol.buscar("Medicamento Que No Existe") is None)
verificar("buscar código inexistente retorna None", arbol.buscar_por_codigo("NOEXISTE") is None)
verificar("búsqueda por prefijo sin coincidencias retorna lista vacía", arbol.buscar_por_prefijo("zzz") == [])


print("\n========== 3. COLA DE PEDIDOS (FIFO) ==========")

print("--- Caso 1: flujo normal ---")
cola = ColaPedidos()
p1 = cola.encolar(cliente="Juan Pérez")
p1.agregar_item("MED001", "Paracetamol 500mg", 2, 1.5)
p2 = cola.encolar(cliente="María Cedeño")
p2.agregar_item("MED002", "Ibuprofeno 400mg", 1, 2.0)
verificar("encolar agrega pedidos en orden", len(cola) == 2)
verificar("ver_frente retorna el primer pedido (FIFO)", cola.ver_frente().cliente == "Juan Pérez")
atendido = cola.atender()
verificar("atender retorna y remueve el primero de la cola", atendido.cliente == "Juan Pérez" and len(cola) == 1)

print("--- Caso 2: caso límite (cola vacía) ---")
cola_vacia = ColaPedidos()
verificar("cola vacía tiene longitud 0", len(cola_vacia) == 0)
verificar("esta_vacia() detecta la cola vacía", cola_vacia.esta_vacia() is True)
verificar("atender en cola vacía retorna None", cola_vacia.atender() is None)
verificar("ver_frente en cola vacía retorna None", cola_vacia.ver_frente() is None)

print("--- Caso 3: dato inválido (cancelar número inexistente) ---")
verificar("cancelar un número de pedido inexistente retorna None", cola.cancelar(9999) is None)


print("\n========== 4. PILA DE DESHACER (KARDEX) ==========")

print("--- Caso 1: flujo normal ---")
pila = PilaDeshacerKardex()
pila.vaciar()
pila.push({"codigo_medicamento": "MED001", "tipo": "entrada", "cantidad": 5, "stock_resultante": 15})
pila.push({"codigo_medicamento": "MED002", "tipo": "salida", "cantidad": 2, "stock_resultante": 8})
verificar("push agrega elementos a la pila", len(pila) == 2)
verificar("ver_tope muestra el último insertado (LIFO)", pila.ver_tope()["codigo_medicamento"] == "MED002")
tope = pila.pop()
verificar("pop retorna y remueve el último insertado (LIFO)", tope["codigo_medicamento"] == "MED002" and len(pila) == 1)

print("--- Caso 2: caso límite (pila vacía / un solo elemento) ---")
pila.pop()
verificar("pila queda vacía tras sacar todos los elementos", pila.esta_vacia() is True)
pila.push({"codigo_medicamento": "MED003", "tipo": "entrada", "cantidad": 1, "stock_resultante": 1})
verificar("pila con un solo elemento: tope es ese elemento", pila.ver_tope()["codigo_medicamento"] == "MED003")
pila.pop()

print("--- Caso 3: dato inválido (pop/ver_tope sobre pila vacía) ---")
verificar("ver_tope en pila vacía retorna None", pila.ver_tope() is None)
try:
    pila.pop()
    verificar("pop en pila vacía lanza IndexError", False)
except IndexError:
    verificar("pop en pila vacía lanza IndexError", True)


print("\n========================================")
if fallos:
    print(f"❌ {len(fallos)} prueba(s) fallaron: {fallos}")
    sys.exit(1)
else:
    print("✅ Todas las pruebas se ejecutaron correctamente (12 casos: 3 por estructura).")
    sys.exit(0)
