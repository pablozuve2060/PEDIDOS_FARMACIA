import hashlib
import json
import os
import secrets
from models.medicamento import Medicamento
from models.pedido import Pedido

RUTA_MEDICAMENTOS = os.path.join("data", "medicamentos.json")
RUTA_USUARIOS = os.path.join("data", "usuarios.json")
RUTA_COLA_PEDIDOS = os.path.join("data", "cola_pedidos.json")
RUTA_HISTORIAL_PEDIDOS = os.path.join("data", "historial_pedidos.json")


def guardar_medicamentos(lista_enlazada):
    medicamentos = [med.a_diccionario() for med in lista_enlazada.a_lista()]
    os.makedirs(os.path.dirname(RUTA_MEDICAMENTOS), exist_ok=True)
    with open(RUTA_MEDICAMENTOS, "w", encoding="utf-8") as f:
        json.dump(medicamentos, f, ensure_ascii=False, indent=4)


def cargar_medicamentos(lista_enlazada, arbol_busqueda):
    if not os.path.exists(RUTA_MEDICAMENTOS):
        return
    with open(RUTA_MEDICAMENTOS, "r", encoding="utf-8") as f:
        datos = json.load(f)
    for item in datos:
        medicamento = Medicamento.desde_diccionario(item)
        lista_enlazada.insertar(medicamento)
        arbol_busqueda.insertar(medicamento)
    from services import estanterias

    if estanterias.asegurar_ubicaciones(lista_enlazada):
        guardar_medicamentos(lista_enlazada)


def guardar_cola_pedidos(cola_pedidos):
    datos = {
        "contador": cola_pedidos._contador_pedidos,
        "pedidos": [pedido.a_diccionario() for pedido in cola_pedidos.a_lista()],
    }
    os.makedirs(os.path.dirname(RUTA_COLA_PEDIDOS), exist_ok=True)
    with open(RUTA_COLA_PEDIDOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)


def cargar_cola_pedidos(cola_pedidos):
    if not os.path.exists(RUTA_COLA_PEDIDOS):
        return
    with open(RUTA_COLA_PEDIDOS, "r", encoding="utf-8") as f:
        datos = json.load(f)
    for item in datos.get("pedidos", []):
        pedido = Pedido.desde_diccionario(item)
        cola_pedidos.cargar_pedido_existente(pedido)
    contador_guardado = datos.get("contador", 0)
    if contador_guardado > cola_pedidos._contador_pedidos:
        cola_pedidos._contador_pedidos = contador_guardado


def agregar_a_historial(pedido):
    historial = cargar_historial()
    historial.append(pedido.a_diccionario())
    os.makedirs(os.path.dirname(RUTA_HISTORIAL_PEDIDOS), exist_ok=True)
    with open(RUTA_HISTORIAL_PEDIDOS, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=4)


def cargar_historial():
    if not os.path.exists(RUTA_HISTORIAL_PEDIDOS):
        return []
    with open(RUTA_HISTORIAL_PEDIDOS, "r", encoding="utf-8") as f:
        return json.load(f)


def _hashear_clave(clave, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    resultado = hashlib.sha256((salt + clave).encode("utf-8")).hexdigest()
    return resultado, salt


def _verificar_clave(clave, salt, hash_guardado):
    resultado, _ = _hashear_clave(clave, salt)
    return secrets.compare_digest(resultado, hash_guardado)


def cargar_usuarios():
    if not os.path.exists(RUTA_USUARIOS):
        return []
    with open(RUTA_USUARIOS, "r", encoding="utf-8") as f:
        usuarios = json.load(f)
    requiere_migracion = False
    for u in usuarios:
        if "clave" in u:
            hash_resultado, salt = _hashear_clave(u.pop("clave"))
            u["clave_hash"] = hash_resultado
            u["salt"] = salt
            requiere_migracion = True
    if requiere_migracion:
        guardar_usuarios(usuarios)
    return usuarios


def guardar_usuarios(usuarios):
    os.makedirs(os.path.dirname(RUTA_USUARIOS), exist_ok=True)
    with open(RUTA_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=4)


def verificar_credenciales(usuario_nombre, clave):
    for u in cargar_usuarios():
        if u["usuario"] == usuario_nombre:
            if _verificar_clave(clave, u["salt"], u["clave_hash"]):
                return u
            return None
    return None


def crear_usuario(usuario_nombre, clave, rol, nombre):
    usuarios = cargar_usuarios()
    if any(u["usuario"] == usuario_nombre for u in usuarios):
        return False
    hash_resultado, salt = _hashear_clave(clave)
    usuarios.append(
        {
            "usuario": usuario_nombre,
            "clave_hash": hash_resultado,
            "salt": salt,
            "rol": rol,
            "nombre": nombre,
        }
    )
    guardar_usuarios(usuarios)
    return True


def actualizar_usuario(usuario_nombre, nueva_clave=None, rol=None, nombre=None):
    usuarios = cargar_usuarios()
    for u in usuarios:
        if u["usuario"] == usuario_nombre:
            if nueva_clave:
                hash_resultado, salt = _hashear_clave(nueva_clave)
                u["clave_hash"] = hash_resultado
                u["salt"] = salt
            if rol:
                u["rol"] = rol
            if nombre:
                u["nombre"] = nombre
            guardar_usuarios(usuarios)
            return True
    return False


def eliminar_usuario(usuario_nombre):
    usuarios = cargar_usuarios()
    nuevos = [u for u in usuarios if u["usuario"] != usuario_nombre]
    if len(nuevos) == len(usuarios):
        return False
    guardar_usuarios(nuevos)
    return True
