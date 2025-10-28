import httpx

API_URL = "http://127.0.0.1:8000/ventas"

# 📝 Registrar una venta
def registrar_venta(cliente_id: int, productos: list, total: float) -> bool:
    venta_data = {
        "cliente_id": cliente_id,
        "productos": [
            {"producto_id": p[0], "cantidad": p[1], "precio_unitario": p[2]}
            for p in productos
        ],
        "total": total
    }
    try:
        response = httpx.post(f"{API_URL}/", json=venta_data)
        response.raise_for_status()
        return response.status_code == 201
    except httpx.RequestError as e:
        print(f"Error en registrar_venta: {e}")
        return False

# 📋 Obtener todas las ventas
def obtener_ventas():
    try:
        response = httpx.get(f"{API_URL}/")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        print(f"Error en obtener_ventas: {e}")
        return []

# 🔍 Obtener detalles de una venta
def obtener_detalles_venta(venta_id: int):
    try:
        response = httpx.get(f"{API_URL}/{venta_id}")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        print(f"Error en obtener_detalles_venta: {e}")
        return []