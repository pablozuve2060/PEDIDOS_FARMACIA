from services.lista_enlazada import ListaEnlazadaMedicamentos
from services.cola_pedidos import ColaPedidos
from services.arbol_busqueda import ArbolBusquedaMedicamentos
from services import persistencia
from services import recursividad

print("=== 1. Cargando catálogo (Lista Enlazada + Árbol) ===")
lista = ListaEnlazadaMedicamentos()
arbol = ArbolBusquedaMedicamentos()
persistencia.cargar_medicamentos(lista, arbol)
print(f"Medicamentos cargados en lista: {len(lista)}")
for med in lista.a_lista():
    print(" -", med)
print("\n=== 2. Búsqueda en Árbol Binario ===")
encontrado = arbol.buscar("Ibuprofeno 400mg")
print("Buscando 'Ibuprofeno 400mg':", encontrado)
print("\n=== 3. Búsqueda por prefijo (autocompletar) ===")
resultados = arbol.buscar_por_prefijo("amox")
print("Resultados para 'amox':", resultados)
print("\n=== 4. Cola de Pedidos (FIFO) ===")
cola = ColaPedidos()
pedido1 = cola.encolar(cliente="Juan Pérez")
pedido1.agregar_item("MED001", "Paracetamol 500mg", 2, 1.5)
pedido1.agregar_item("MED003", "Amoxicilina 500mg", 1, 3.75)
pedido2 = cola.encolar(cliente="María Cedeño")
pedido2.agregar_item("MED002", "Ibuprofeno 400mg", 3, 2.0)
print(f"Pedidos en cola: {len(cola)}")
for p in cola.a_lista():
    print(" -", p, "| Items:", len(p.items), "| Total:", p.total)
print("\nAtendiendo pedido (FIFO)...")
atendido = cola.atender()
print("Atendido:", atendido, "-> nuevo tamaño de cola:", len(cola))
print("\n=== 5. Recursividad ===")
total_recursivo = recursividad.calcular_total_recursivo(pedido1.items)
print(f"Total recursivo del pedido #{pedido1.numero_pedido}: ${total_recursivo:.2f}")
bajo_stock = recursividad.contar_medicamentos_bajo_stock_recursivo(
    lista.a_lista(), umbral=10
)
print(f"Medicamentos con stock < 10: {bajo_stock}")
altura = recursividad.altura_arbol_recursiva(arbol.raiz_nombre)
print(f"Altura del árbol de búsqueda: {altura}")
print("\n✅ Todas las pruebas se ejecutaron correctamente.")
