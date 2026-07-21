# Sistema de Farmacia

Proyecto final de Estructura de Datos — Ing. César Stalin Villavicencio Palacios, Mg.
Facultad de Ciencias de la Vida y Tecnologías — Carrera de Software — ULEAM
Periodo académico 2026-1.

Sistema de escritorio para la gestión de una farmacia: catálogo de medicamentos,
cola de pedidos, kardex de movimientos de inventario, ubicación en estanterías,
alertas de vencimiento y reportes en PDF.

## Estructuras de datos implementadas

| Estructura | Clase | Ubicación | Uso dentro del sistema |
|---|---|---|---|
| Lista enlazada | `ListaEnlazadaMedicamentos` | `services/lista_enlazada.py` | Catálogo maestro de medicamentos (insertar, eliminar, actualizar, buscar por código) |
| Árbol binario de búsqueda | `ArbolBusquedaMedicamentos` | `services/arbol_busqueda.py` | Búsqueda rápida por nombre, código y prefijo (autocompletar) |
| Cola (FIFO) | `ColaPedidos` | `services/cola_pedidos.py` | Atención de pedidos por orden de llegada (encolar, atender, cancelar) |
| Pila (LIFO) | `PilaDeshacerKardex` | `services/pila_movimientos.py` | Deshacer el último movimiento de inventario registrado en el kardex |

## Requisitos

- Python 3.10 o superior
- Dependencias:

```bash
pip install ttkbootstrap reportlab
```

## Ejecución

```bash
cd sistema_farmacia
python main.py
```

Se abrirá la ventana de inicio de sesión. Las credenciales de prueba están en
`data/usuarios.json`.

## Pruebas

El proyecto incluye una suite de pruebas con **3 casos por cada estructura de
datos** (flujo normal, caso límite y dato inválido), tal como exige la guía de
evaluación:

```bash
cd sistema_farmacia
python tests/test_estructuras.py
```

También se incluye `test_rapido.py` con una demostración manual end-to-end del
flujo normal del sistema (catálogo, búsqueda, cola de pedidos y recursividad).

## Estructura del proyecto

```
sistema_farmacia/
├── main.py                     # Punto de entrada
├── models/                     # Medicamento, Pedido, NodoArbol
├── services/                   # Lógica de negocio y estructuras de datos
│   ├── lista_enlazada.py       # Lista enlazada
│   ├── arbol_busqueda.py       # Árbol binario de búsqueda (ABB)
│   ├── cola_pedidos.py         # Cola FIFO
│   ├── pila_movimientos.py     # Pila LIFO (deshacer)
│   ├── kardex.py               # Registro de movimientos de inventario
│   ├── estanterias.py          # Ubicación física de medicamentos
│   ├── recursividad.py         # Funciones recursivas de apoyo
│   ├── persistencia.py         # Lectura/escritura en JSON, usuarios y login
│   └── reportes_pdf.py         # Generación de reportes PDF (ReportLab)
├── gui/                        # Ventanas de la interfaz (ttkbootstrap)
├── data/                       # Persistencia en archivos JSON
├── assets/                     # Íconos y recursos gráficos
├── utils/                      # Utilidades (ventanas con scroll, etc.)
└── tests/
    └── test_estructuras.py     # Pruebas de las 4 estructuras de datos
```

## Funcionalidad de "Deshacer" (pila)

Cada vez que el sistema registra un movimiento de inventario (venta, cancelación
de pedido, alta, ajuste manual o eliminación de un medicamento), el movimiento
se apila automáticamente en `PilaDeshacerKardex`. Desde la ventana **Kardex de
Movimientos** el usuario puede pulsar **"↩️ Deshacer último movimiento"** para
revertir (LIFO) el movimiento más reciente: se restaura el stock anterior y se
registra en el kardex un movimiento inverso de auditoría.

## Repositorio

> Reemplazar con el enlace real antes de la entrega:
> `https://github.com/<usuario>/sistema-farmacia`
