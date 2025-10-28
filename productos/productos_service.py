import httpx

API_URL = "http://127.0.0.1:8000/productos"

#  Crear producto
def crear_producto(nombre: str, descripcion: str, precio: float, stock: int, talla: str, categoria: str) -> bool:
    producto_data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "stock": stock,
        "talla": talla,
        "categoria": categoria
    }
    try:
        response = httpx.post(f"{API_URL}/", json=producto_data)
        response.raise_for_status()
        return response.status_code == 201
    except httpx.RequestError as e:
        print(f"Error en crear_producto: {e}")
        return False

#  Obtener todos los productos
def obtener_productos():
    try:
        response = httpx.get(f"{API_URL}/")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        print(f"Error en obtener_productos: {e}")
        return []

#  Buscar producto por ID
def obtener_producto_por_id(producto_id: int):
    try:
        response = httpx.get(f"{API_URL}/{producto_id}")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        print(f"Error en obtener_producto_por_id: {e}")
        return None

#  Actualizar producto
def actualizar_producto(producto_id: int, nombre: str, descripcion: str, precio: float, stock: int, talla: str, categoria: str) -> bool:
    producto_data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "stock": stock,
        "talla": talla,
        "categoria": categoria
    }
    try:
        response = httpx.put(f"{API_URL}/{producto_id}", json=producto_data)
        response.raise_for_status()
        return response.status_code == 200
    except httpx.RequestError as e:
        print(f"Error en actualizar_producto: {e}")
        return False

#  Eliminar producto
def eliminar_producto(producto_id: int) -> bool:
    try:
        response = httpx.delete(f"{API_URL}/{producto_id}")
        response.raise_for_status()
        return response.status_code == 200
    except httpx.RequestError as e:
        print(f"Error en eliminar_producto: {e}")
        return False