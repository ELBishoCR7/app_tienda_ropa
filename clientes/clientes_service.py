import httpx

API_URL = "http://127.0.0.1:8000/clientes"

#  Crear cliente
def crear_cliente(nombre: str, correo: str, telefono: str, direccion: str) -> bool:
    cliente_data = {"nombre": nombre, "correo": correo, "telefono": telefono, "direccion": direccion}
    try:
        response = httpx.post(f"{API_URL}/", json=cliente_data)
        response.raise_for_status()  # Lanza una excepción para errores 4xx/5xx
        return response.status_code == 201
    except httpx.RequestError as e:
        print(f"Error en crear_cliente: {e}")
        return False

#  Obtener todos los clientes
def obtener_clientes():
    try:
        response = httpx.get(f"{API_URL}/")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        print(f"Error en obtener_clientes: {e}")
        return []

#  Buscar cliente por ID
def obtener_cliente_por_id(cliente_id: int):
    try:
        response = httpx.get(f"{API_URL}/{cliente_id}")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        print(f"Error en obtener_cliente_por_id: {e}")
        return None

#  Actualizar cliente
def actualizar_cliente(cliente_id: int, nombre: str, correo: str, telefono: str, direccion: str) -> bool:
    cliente_data = {"nombre": nombre, "correo": correo, "telefono": telefono, "direccion": direccion}
    try:
        response = httpx.put(f"{API_URL}/{cliente_id}", json=cliente_data)
        response.raise_for_status()
        return response.status_code == 200
    except httpx.RequestError as e:
        print(f"Error en actualizar_cliente: {e}")
        return False

#  Eliminar cliente
def eliminar_cliente(cliente_id: int) -> bool:
    try:
        response = httpx.delete(f"{API_URL}/{cliente_id}")
        response.raise_for_status()
        return response.status_code == 200
    except httpx.RequestError as e:
        print(f"Error en eliminar_cliente: {e}")
        return False