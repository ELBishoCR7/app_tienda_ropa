from fastapi import APIRouter, HTTPException, status
from .db_services import db_registrar_venta, db_obtener_ventas, db_obtener_detalles_venta
from .schemas import VentaCreate

router = APIRouter()

@router.get("/")
async def listar_ventas():
    return db_obtener_ventas()

@router.get("/{venta_id}")
async def detalles_venta(venta_id: int):
    return db_obtener_detalles_venta(venta_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def nueva_venta(venta: VentaCreate):
    # Extraer la lista de tuplas del modelo Pydantic
    productos_tuplas = [(p['producto_id'], p['cantidad'], p['precio_unitario']) for p in venta.productos]
    if db_registrar_venta(venta.cliente_id, productos_tuplas, venta.total):
        return {"mensaje": "Venta registrada correctamente"}
    raise HTTPException(status_code=400, detail="No se pudo registrar la venta")