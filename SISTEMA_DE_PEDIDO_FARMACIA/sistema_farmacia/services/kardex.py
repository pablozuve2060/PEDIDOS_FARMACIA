import json
import os
from datetime import datetime

from services.pila_movimientos import PilaDeshacerKardex

RUTA_KARDEX = os.path.join("data", "kardex.json")

TIPOS = ("entrada", "salida", "ajuste")

_pila_deshacer = PilaDeshacerKardex()


def registrar_movimiento(
    codigo_medicamento,
    nombre_medicamento,
    tipo,
    cantidad,
    stock_resultante,
    usuario="Sistema",
    motivo="",
    _permitir_deshacer=True,
):
    if tipo not in TIPOS:
        raise ValueError(f"Tipo de movimiento inválido: {tipo}")
    if not isinstance(cantidad, int) or cantidad < 0:
        raise ValueError("La cantidad del movimiento debe ser un entero mayor o igual a 0.")
    if not isinstance(stock_resultante, int) or stock_resultante < 0:
        raise ValueError("El stock resultante no puede ser negativo.")
    movimientos = cargar_movimientos()
    registro = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "codigo_medicamento": codigo_medicamento,
        "nombre_medicamento": nombre_medicamento,
        "tipo": tipo,
        "cantidad": cantidad,
        "stock_resultante": stock_resultante,
        "usuario": usuario,
        "motivo": motivo,
    }
    movimientos.append(registro)
    os.makedirs(os.path.dirname(RUTA_KARDEX), exist_ok=True)
    with open(RUTA_KARDEX, "w", encoding="utf-8") as f:
        json.dump(movimientos, f, ensure_ascii=False, indent=4)
    if _permitir_deshacer:
        _pila_deshacer.push(registro)


def hay_movimiento_para_deshacer():
    return not _pila_deshacer.esta_vacia()


def ver_movimiento_pendiente_deshacer():
    return _pila_deshacer.ver_tope()


def cantidad_pendientes_deshacer():
    return len(_pila_deshacer)


def deshacer_ultimo_movimiento(lista_medicamentos):
    if _pila_deshacer.esta_vacia():
        raise IndexError("No hay movimientos registrados para deshacer.")
    movimiento = _pila_deshacer.pop()
    med = lista_medicamentos.buscar_por_codigo(movimiento["codigo_medicamento"])
    if med is None:
        raise ValueError(
            f"El medicamento {movimiento['codigo_medicamento']} ya no existe en el "
            "catálogo; no se puede deshacer este movimiento."
        )
    if movimiento["tipo"] == "entrada":
        stock_anterior = movimiento["stock_resultante"] - movimiento["cantidad"]
    else:
        stock_anterior = movimiento["stock_resultante"] + movimiento["cantidad"]
    if stock_anterior < 0:
        raise ValueError(
            "Deshacer este movimiento dejaría el stock en un valor negativo; operación cancelada."
        )
    lista_medicamentos.actualizar(med.codigo, stock=stock_anterior)
    tipo_inverso = "salida" if movimiento["tipo"] == "entrada" else "entrada"
    registrar_movimiento(
        movimiento["codigo_medicamento"],
        movimiento["nombre_medicamento"],
        tipo_inverso,
        movimiento["cantidad"],
        stock_anterior,
        usuario=movimiento.get("usuario", "Sistema"),
        motivo=f"Deshacer: {movimiento.get('motivo', '')}",
        _permitir_deshacer=False,
    )
    return movimiento, stock_anterior


def cargar_movimientos():
    if not os.path.exists(RUTA_KARDEX):
        return []
    with open(RUTA_KARDEX, "r", encoding="utf-8") as f:
        return json.load(f)


def filtrar_movimientos(movimientos, codigo=None, fecha_inicio=None, fecha_fin=None, tipo=None):
    resultado = movimientos
    if codigo:
        codigo = codigo.strip().lower()
        resultado = [m for m in resultado if codigo in m["codigo_medicamento"].lower()]
    if tipo:
        resultado = [m for m in resultado if m["tipo"] == tipo]
    if fecha_inicio:
        resultado = [m for m in resultado if m["fecha"][:10] >= fecha_inicio]
    if fecha_fin:
        resultado = [m for m in resultado if m["fecha"][:10] <= fecha_fin]
    return resultado
