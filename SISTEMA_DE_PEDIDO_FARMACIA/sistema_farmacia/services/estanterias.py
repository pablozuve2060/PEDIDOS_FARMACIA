"""
Gestión de estanterías del almacén de la farmacia.

Cada CATEGORÍA de medicamento tiene asignado un estante (una letra: A, B,
C...). Dentro de cada estante, los medicamentos se ubican de forma
secuencial: A-01, A-02, A-03, etc. La asignación categoría -> estante se
persiste en data/estanterias.json y es estable: una vez que una categoría
recibe una letra, siempre usará esa misma letra.

Con esto se puede saber en qué estante físico está un medicamento
(ubicacion_de_medicamento), listar todo lo que hay en un estante
(medicamentos_por_estante) y generar automáticamente la siguiente
ubicación libre al dar de alta un medicamento nuevo (generar_ubicacion),
ya sea de una categoría nueva o de una que ya existía.
"""

import json
import os

RUTA_ESTANTERIAS = os.path.join("data", "estanterias.json")

LETRAS_DISPONIBLES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _cargar_mapa_categorias():
    if not os.path.exists(RUTA_ESTANTERIAS):
        return {}
    with open(RUTA_ESTANTERIAS, "r", encoding="utf-8") as f:
        return json.load(f)


def _guardar_mapa_categorias(mapa):
    os.makedirs(os.path.dirname(RUTA_ESTANTERIAS), exist_ok=True)
    with open(RUTA_ESTANTERIAS, "w", encoding="utf-8") as f:
        json.dump(mapa, f, ensure_ascii=False, indent=4)


def _siguiente_letra_libre(mapa):
    usadas = set(mapa.values())
    for letra in LETRAS_DISPONIBLES:
        if letra not in usadas:
            return letra
    # Si se agotan las 26 letras individuales, se combinan de a dos (AA, AB...)
    for primera in LETRAS_DISPONIBLES:
        for segunda in LETRAS_DISPONIBLES:
            letra = primera + segunda
            if letra not in usadas:
                return letra
    return "ZZ"


def obtener_estante_categoria(categoria):
    """Devuelve la letra de estante asignada a una categoría. Si es la
    primera vez que se ve esa categoría, le asigna la siguiente letra
    disponible en la secuencia y lo guarda de forma permanente."""
    categoria = (categoria or "General").strip() or "General"
    mapa = _cargar_mapa_categorias()
    if categoria not in mapa:
        mapa[categoria] = _siguiente_letra_libre(mapa)
        _guardar_mapa_categorias(mapa)
    return mapa[categoria]


def mapa_estanterias():
    """Devuelve el diccionario completo {categoria: estante}."""
    return _cargar_mapa_categorias()


def generar_ubicacion(categoria, lista_medicamentos):
    """Genera la siguiente ubicación libre (formato 'ESTANTE-NN') para un
    medicamento de la categoría indicada. Si la categoría ya tenía
    medicamentos ubicados, continúa la secuencia de numeración del mismo
    estante; si es una categoría nueva, se le asigna un estante nuevo y
    arranca en 01."""
    estante = obtener_estante_categoria(categoria)
    numeros_ocupados = []
    for med in lista_medicamentos.a_lista():
        if not med.ubicacion or "-" not in med.ubicacion:
            continue
        estante_med, _, numero_med = med.ubicacion.partition("-")
        if estante_med == estante:
            try:
                numeros_ocupados.append(int(numero_med))
            except ValueError:
                continue
    siguiente_numero = max(numeros_ocupados, default=0) + 1
    return f"{estante}-{siguiente_numero:02d}"


def ubicacion_de_medicamento(codigo, lista_medicamentos):
    """Devuelve el estante donde está ubicado un medicamento según su
    código, o None si el medicamento no existe o no tiene ubicación."""
    med = lista_medicamentos.buscar_por_codigo(codigo)
    return med.ubicacion if med else None


def medicamentos_por_estante(estante, lista_medicamentos):
    """Devuelve la lista de medicamentos ubicados en un estante dado
    (por ejemplo, 'A'), ordenados por su número dentro del estante."""
    estante = (estante or "").strip().upper()
    resultado = [
        med for med in lista_medicamentos.a_lista()
        if med.ubicacion and med.ubicacion.partition("-")[0] == estante
    ]
    resultado.sort(key=lambda m: m.ubicacion)
    return resultado


def resumen_por_estante(lista_medicamentos):
    """Agrupa todos los medicamentos ubicados por estante. Devuelve un
    diccionario {estante: [medicamentos...]} ordenado alfabéticamente
    por estante y, dentro de cada uno, por número de ubicación."""
    resumen = {}
    for med in lista_medicamentos.a_lista():
        if not med.ubicacion or "-" not in med.ubicacion:
            continue
        estante = med.ubicacion.partition("-")[0]
        resumen.setdefault(estante, []).append(med)
    for estante in resumen:
        resumen[estante].sort(key=lambda m: m.ubicacion)
    return dict(sorted(resumen.items()))


def asegurar_ubicaciones(lista_medicamentos):
    """Recorre la lista de medicamentos y asigna ubicación a los que no
    la tengan (por ejemplo, medicamentos guardados con una versión
    anterior del sistema, antes de que existieran las estanterías).
    Devuelve True si se asignó alguna ubicación nueva, para saber si
    hace falta volver a guardar el archivo de medicamentos."""
    huerfanos = [
        med for med in lista_medicamentos.a_lista() if not med.ubicacion
    ]
    for med in huerfanos:
        med.ubicacion = generar_ubicacion(med.categoria, lista_medicamentos)
    return len(huerfanos) > 0
